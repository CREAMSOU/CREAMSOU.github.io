# -*- coding: utf-8 -*-
"""
博客本地编辑器（零依赖：仅 Python 标准库）
- 只监听 127.0.0.1，仅本机可访问
- 功能：文章列表 / 新建 / 编辑 / 实时预览 / 保存 / 一键发布（git add + commit + push）
- 预览面板按博客实际排版渲染 Markdown（左侧写，右侧看，所见即所得）
启动：python editor/server.py  （或双击 blog/editor.bat）
"""
import json
import os
import re
import subprocess
import sys
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # blog/
POSTS_DIR = os.path.join(ROOT, 'docs', 'posts')
HOST, PORT = '127.0.0.1', 8891
SAFE_NAME = re.compile(r'^[0-9A-Za-z_\-]+\.md$')


def run_git(args):
    r = subprocess.run(['git'] + args, cwd=ROOT, capture_output=True,
                       text=True, encoding='utf-8', errors='replace', timeout=120)
    out = (r.stdout or '') + (r.stderr or '')
    return r.returncode, out.strip()


def compose_md(title, d, description, top, body):
    lines = ['---', f'title: {title}', f'date: {d}']
    if description:
        lines.append(f'description: {description}')
    if top:
        lines.append('top: true')
    lines += ['---', '']
    return '\n'.join(lines) + '\n' + body.strip() + '\n'


def parse_md(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.S)
    fm, body = {}, text
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                fm[k.strip()] = v.strip()
    return fm, body


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _html(self, text):
        data = text.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ('/', '/index.html'):
            return self._html(PAGE)
        if u.path == '/api/posts':
            items = []
            for f in sorted(os.listdir(POSTS_DIR)):
                if not f.endswith('.md'):
                    continue
                fm, body = parse_md(
                    open(os.path.join(POSTS_DIR, f), encoding='utf-8').read())
                items.append({'file': f, 'title': fm.get('title', ''),
                              'date': fm.get('date', ''),
                              'description': fm.get('description', '')})
            items.sort(key=lambda x: x['date'], reverse=True)
            return self._json(items)
        if u.path == '/api/post':
            f = parse_qs(u.query).get('file', [''])[0]
            if not SAFE_NAME.match(f):
                return self._json({'error': '非法文件名'}, 400)
            p = os.path.join(POSTS_DIR, f)
            if not os.path.exists(p):
                return self._json({'error': '文件不存在'}, 404)
            fm, body = parse_md(open(p, encoding='utf-8').read())
            return self._json({'file': f, 'title': fm.get('title', ''),
                               'date': fm.get('date', ''),
                               'description': fm.get('description', ''),
                               'top': fm.get('top') == 'true',
                               'body': body})
        if u.path == '/api/status':
            code, out = run_git(['status', '--short'])
            code2, out2 = run_git(['log', '--oneline', '-3'])
            return self._json({'git_status': out or '(工作区干净)',
                               'recent': out2})
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        u = urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        try:
            data = json.loads(self.rfile.read(length).decode('utf-8'))
        except Exception:
            return self._json({'error': '请求体不是合法 JSON'}, 400)

        if u.path == '/api/save':
            f = data.get('file', '')
            if not SAFE_NAME.match(f):
                return self._json({'error': '文件名只能含英文、数字、-、_'}, 400)
            md = compose_md(data.get('title', '无标题'), data.get('date') or
                            date.today().isoformat(),
                            data.get('description', ''),
                            bool(data.get('top')), data.get('body', ''))
            open(os.path.join(POSTS_DIR, f), 'w', encoding='utf-8',
                 newline='\n').write(md)
            return self._json({'ok': True, 'file': f})

        if u.path == '/api/publish':
            logs = []
            for args, msg in [(['add', '-A'], '加入暂存区'),
                              (['commit', '-m',
                                'update: ' + date.today().isoformat()],
                               '提交')]:
                code, out = run_git(args)
                logs.append(f'== {msg} ==\n{out or "(无输出)"}')
                if code != 0:
                    return self._json({'ok': False,
                                       'log': '\n'.join(logs)})
            # 先试常规 git push；网络不通时回退到 GitHub API 推送
            code, out = run_git(['push'])
            if code == 0:
                logs.append('== 推送到 GitHub ==\ngit push 成功')
            else:
                logs.append(f'== git push 失败，改走 API 推送 ==\n{out}')
                py = sys.executable
                r = subprocess.run([py, os.path.join(ROOT, 'editor',
                                                     'api_push.py'),
                                    '.', 'update: ' + date.today().isoformat()],
                                   cwd=ROOT, capture_output=True, text=True,
                                   encoding='utf-8', errors='replace',
                                   timeout=300)
                ok = 'PUSH_OK' in (r.stdout or '')
                logs.append(r.stdout[-600:] if ok else
                            (r.stdout + r.stderr)[-1200:])
                if not ok:
                    return self._json({'ok': False,
                                       'log': '\n'.join(logs)})
            return self._json({'ok': True, 'log': '\n'.join(logs)})

        if u.path == '/api/delete':
            f = data.get('file', '')
            if not SAFE_NAME.match(f):
                return self._json({'error': '非法文件名'}, 400)
            os.remove(os.path.join(POSTS_DIR, f))
            return self._json({'ok': True})

        self.send_response(404)
        self.end_headers()

    def log_message(self, *a):
        pass


PAGE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>博客编辑器</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Microsoft YaHei", sans-serif; background: #f5f6f7; color: #24292f; height: 100vh; display: flex; flex-direction: column; }
header { background: #24292f; color: #fff; padding: 10px 18px; display: flex; align-items: center; gap: 12px; }
header h1 { font-size: 15px; font-weight: 500; margin-right: auto; }
button { border: 1px solid #d0d7de; background: #fff; color: #24292f; border-radius: 6px; padding: 6px 14px; font-size: 13px; cursor: pointer; }
button:hover { border-color: #0969da; color: #0969da; }
button.primary { background: #0969da; border-color: #0969da; color: #fff; }
button.primary:hover { background: #0576e8; }
main { flex: 1; display: flex; min-height: 0; }
aside { width: 250px; background: #fff; border-right: 1px solid #d0d7de; overflow-y: auto; padding: 8px; }
aside a { display: block; padding: 8px 10px; border-radius: 6px; text-decoration: none; color: #24292f; font-size: 13px; }
aside a:hover { background: #eef1f4; }
aside a .d { display: block; color: #8c959f; font-size: 11px; margin-top: 2px; }
section { flex: 1; display: flex; flex-direction: column; padding: 14px 18px; gap: 10px; min-width: 0; }
.row { display: flex; gap: 10px; }
.row input[type=text] { flex: 1; min-width: 0; border: 1px solid #d0d7de; border-radius: 6px; padding: 7px 10px; font-size: 13px; }
#desc { width: 100%; border: 1px solid #d0d7de; border-radius: 6px; padding: 7px 10px; font-size: 13px; }
label.chk { display: flex; align-items: center; gap: 5px; font-size: 13px; white-space: nowrap; }
.split { flex: 1; display: flex; min-height: 0; }
textarea { flex: 1; min-width: 0; border: 1px solid #d0d7de; border-radius: 6px 0 0 6px; border-right: none; padding: 12px; font: 13px/1.7 Consolas, monospace; resize: none; min-height: 0; }
#preview { position: relative; flex: 1; min-width: 0; overflow-y: auto; background: #fff; border: 1px solid #d0d7de; border-radius: 0 6px 6px 0; padding: 30px 36px; }
#status { background: #24292f; color: #9fd29f; border-radius: 6px; padding: 8px 12px; font: 12px/1.6 Consolas, monospace; white-space: pre-wrap; max-height: 120px; overflow-y: auto; }
.empty { color: #8c959f; text-align: center; margin-top: 40px; font-size: 13px; }
/* ===== 预览区排版：对齐博客正文样式 ===== */
#preview h1 { font-size: 26px; letter-spacing: 0.02em; margin-bottom: 6px; color: #1f2328; }
#preview h2 { font-size: 20px; margin: 28px 0 12px; padding-bottom: 8px; border-bottom: 1px solid #eaecef; color: #1f2328; }
#preview h3 { font-size: 17px; margin: 22px 0 10px; color: #1f2328; }
#preview p { line-height: 1.85; font-size: 14.5px; color: #2a2f36; margin: 0 0 14px; }
#preview table { border-collapse: collapse; margin: 14px 0; width: 100%; font-size: 13.5px; }
#preview th, #preview td { border: 1px solid #d0d7de; padding: 7px 12px; text-align: left; line-height: 1.6; }
#preview th { background: #f6f8fa; font-weight: 600; }
#preview tr:nth-child(2n) td { background: #f9fafb; }
#preview ol, #preview ul { padding-left: 26px; line-height: 1.9; font-size: 14.5px; color: #2a2f36; margin: 0 0 14px; }
#preview li { margin-bottom: 4px; }
#preview code { background: #f0f1f3; border-radius: 4px; padding: 1px 6px; font: 12.5px/1.6 Consolas, monospace; color: #cf222e; }
#preview pre { background: #f6f8fa; border-radius: 8px; padding: 14px 16px; overflow-x: auto; margin: 0 0 14px; }
#preview pre code { background: none; padding: 0; color: #24292f; }
#preview blockquote { border-left: 3px solid #d0d7de; color: #6a737d; padding: 2px 14px; margin: 0 0 14px; background: #fafbfc; }
#preview a { color: #0969da; }
#preview hr { border: none; border-top: 1px solid #eaecef; margin: 20px 0; }
</style>
</head>
<body>
<header>
  <h1>博客编辑器（仅本机可访问）</h1>
  <button onclick="window.open('http://localhost:5173')">预览站点</button>
  <button onclick="newPost()">新建文章</button>
  <button class="primary" onclick="save(false)">保存</button>
  <button class="primary" onclick="save(true)">保存并发布</button>
</header>
<main>
  <aside id="list"></aside>
  <section>
    <div class="row">
      <input type="text" id="title" placeholder="文章标题">
      <input type="text" id="date" placeholder="日期" style="max-width:130px">
      <label class="chk"><input type="checkbox" id="top">置顶</label>
    </div>
    <input type="text" id="desc" placeholder="摘要（显示在首页卡片上）">
    <div class="split">
      <textarea id="body" placeholder="左边写 Markdown，右边实时预览博客效果。结构建议：## 分节标题 + 表格 + 有序列表。"></textarea>
      <div id="preview"></div>
    </div>
    <div id="status">就绪</div>
  </section>
</main>
<script>
let cur = null;
const $ = id => document.getElementById(id);  // 显式取元素，避免撞上 window.top / window.status 等内置属性
async function api(path, data) {
  try {
    const opt = data ? {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)} : {};
    const r = await fetch(path, opt);
    return await r.json();
  } catch (e) {
    alert('连接编辑器服务失败：请确认 server.py 正在运行（双击 blog 目录下的 editor.bat）');
    throw e;
  }
}
async function refresh() {
  const items = await api('/api/posts');
  const el = $('list');
  el.innerHTML = '';
  for (const p of items) {
    const a = document.createElement('a');
    a.href = 'javascript:openPost(\\'' + p.file + '\\')';
    a.innerHTML = p.title || p.file + '<span class=d>' + p.date + '</span>';
    el.appendChild(a);
  }
}
async function openPost(f) {
  const p = await api('/api/post?file=' + f);
  cur = p.file;
  $('title').value = p.title; $('date').value = p.date; $('desc').value = p.description;
  $('top').checked = p.top; $('body').value = p.body;
  renderPreview();
  $('status').textContent = '已打开 ' + f + '（未保存的改动在点保存前不会生效）';
}
function newPost() {
  const f = prompt('文件名（英文数字，建议 YYYY-MM-DD-标题）：', '2026-09-09-new-post');
  if (!f) return;
  cur = f.endsWith('.md') ? f : f + '.md';
  $('title').value = ''; $('date').value = new Date().toISOString().slice(0,10);
  $('desc').value = ''; $('top').checked = false; $('body').value = '';
  renderPreview();
  $('status').textContent = '新文章 ' + cur + '，填写后点"保存"';
}
async function save(publish) {
  if (!cur) { alert('先新建或从左侧选择一篇文章'); return; }
  $('status').textContent = '保存中...';
  const r = await api('/api/save', {file: cur, title: $('title').value, date: $('date').value,
    description: $('desc').value, top: $('top').checked, body: $('body').value});
  if (r.error) { $('status').textContent = '保存失败：' + r.error; return; }
  if (!publish) { $('status').textContent = '已保存（仅本地，未发布）'; refresh(); return; }
  $('status').textContent = '已保存，正在发布（add → commit → push）...';
  const p = await api('/api/publish', {});
  $('status').textContent = p.log + '\\n\\n' + (p.ok ? '✔ 发布完成，1-2 分钟后线上更新' : '✘ 发布失败（常见原因：还没配置 GitHub 远程仓库）');
  refresh();
}
/* ===== Markdown 渲染（覆盖博客文章常用语法） ===== */
function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function inline(s) {
  return s
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')
    .replace(/\\*([^*]+)\\*/g, '<em>$1</em>')
    .replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank">$1</a>');
}
function md2html(src) {
  const lines = src.split(/\\r?\\n/);
  const out = [], starts = [];  // starts[k] = 第 k 个内容块对应的源文件行号（用于光标同步滚动）
  const push = (html, ln) => { out.push(html); starts.push(ln); };
  let i = 0, inCode = false, code = [], codeStart = 0, list = null, listBuf = null, listStart = 0;
  const closeList = () => { if (list) { push('<' + list + '>' + listBuf.join('') + '</' + list + '>', listStart); list = null; listBuf = null; } };
  const cells = h => h.replace(/^\\||\\|$/g, '').split('|').map(c => inline(esc(c.trim())));
  while (i < lines.length) {
    const L = lines[i];
    if (/^```/.test(L)) {
      closeList();
      if (!inCode) { inCode = true; code = []; codeStart = i; }
      else { inCode = false; push('<pre><code>' + esc(code.join('\\n')) + '</code></pre>', codeStart); }
      i++; continue;
    }
    if (inCode) { code.push(L); i++; continue; }
    if (/^\\s*$/.test(L)) { closeList(); i++; continue; }
    let m = L.match(/^(#{1,6})\\s+(.*)/);
    if (m) { closeList(); const n = m[1].length; push('<h' + n + '>' + inline(esc(m[2])) + '</h' + n + '>', i); i++; continue; }
    if (/^\\|.*\\|/.test(L) && i + 1 < lines.length && /^\\|[\\s:\\-|]+\\|?\\s*$/.test(lines[i + 1])) {
      closeList();
      const head = cells(L); const tStart = i; i += 2;
      const rows = [];
      while (i < lines.length && /^\\|.*\\|/.test(lines[i])) { rows.push(cells(lines[i])); i++; }
      push('<table><thead><tr>' + head.map(c => '<th>' + c + '</th>').join('') + '</tr></thead><tbody>'
        + rows.map(r => '<tr>' + r.map(c => '<td>' + c + '</td>').join('') + '</tr>').join('') + '</tbody></table>', tStart);
      continue;
    }
    m = L.match(/^\\s*\\d+\\.\\s+(.*)/);
    if (m) { if (list !== 'ol') { closeList(); list = 'ol'; listBuf = []; listStart = i; } listBuf.push('<li>' + inline(esc(m[1])) + '</li>'); i++; continue; }
    m = L.match(/^\\s*[-*]\\s+(.*)/);
    if (m) { if (list !== 'ul') { closeList(); list = 'ul'; listBuf = []; listStart = i; } listBuf.push('<li>' + inline(esc(m[1])) + '</li>'); i++; continue; }
    if (/^>\\s?/.test(L)) { closeList(); push('<blockquote>' + inline(esc(L.replace(/^>\\s?/, ''))) + '</blockquote>', i); i++; continue; }
    closeList();
    const pStart = i;
    const para = [inline(esc(L))]; i++;
    while (i < lines.length && !/^\\s*$/.test(lines[i]) && !/^(#{1,6}\\s|```|\\||\\s*\\d+\\.\\s|\\s*[-*]\\s|>)/.test(lines[i])) {
      para.push(inline(esc(lines[i]))); i++;
    }
    push('<p>' + para.join('<br>') + '</p>', pStart);
  }
  closeList();
  if (inCode) push('<pre><code>' + esc(code.join('\\n')) + '</code></pre>', codeStart);
  return { html: out.join('\\n'), starts: starts };
}
let view = { starts: [], el: null };
function renderPreview() {
  view = md2html($('body').value);
  $('preview').innerHTML = view.html;
}
/* 光标同步：算出光标所在源码行 → 定位对应内容块 → 预览滚动过去 */
function syncPreview() {
  const ta = $('body');
  const curLine = ta.value.slice(0, ta.selectionStart).split('\\n').length - 1;
  const kids = $('preview').children;
  if (!kids.length) return;
  let idx = 0;
  for (let k = 0; k < view.starts.length; k++) { if (view.starts[k] <= curLine) idx = k; else break; }
  const el = kids[idx];
  if (el) $('preview').scrollTop = Math.max(0, el.offsetTop - $('preview').offsetTop - 28);
}
let pt = null;
$('body').addEventListener('input', () => { clearTimeout(pt); pt = setTimeout(() => { renderPreview(); syncPreview(); }, 250); });
$('body').addEventListener('click', syncPreview);
$('body').addEventListener('keyup', syncPreview);
refresh();
renderPreview();
// 支持 ?file=xxx.md 直接打开指定文章（从博客页"编辑此页"跳转过来）
{
  const q = new URLSearchParams(location.search).get('file');
  if (q) openPost(q.endsWith('.md') ? q : q + '.md');
}
setInterval(async () => {
  const s = await api('/api/status');
  if (s.git_status !== '(工作区干净)') {
    $('status').textContent = '⚠ 有未发布的本地改动：\\n' + s.git_status;
  }
}, 20000);
</script>
</body>
</html>'''

if __name__ == '__main__':
    os.makedirs(POSTS_DIR, exist_ok=True)
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f'博客编辑器运行在 http://{HOST}:{PORT} （Ctrl+C 停止）')
    webbrowser.open(f'http://{HOST}:{PORT}')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
