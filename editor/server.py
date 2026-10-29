# -*- coding: utf-8 -*-
"""
博客本地控制台（零依赖：仅 Python 标准库）
- 只监听 127.0.0.1，外网访问不到
- 首次打开设置一个密码，之后每次进控制台要登录（密码只存在本机 editor/.auth.json，不进仓库）
- 功能：分类看板（拖拽改分类）/ 批量移动 / 分类改名合并 / 文章编辑 / 实时预览 / 一键发布
- /api/ping 不需要登录：线上博客页靠它探测本机是否开着控制台
启动：python editor/server.py  （或双击 blog/editor.bat）
"""
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import time
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # blog/
POSTS_DIR = os.path.join(ROOT, 'docs', 'posts')
PAGE_FILE = os.path.join(HERE, 'index.html')
AUTH_FILE = os.path.join(HERE, '.auth.json')       # 密码哈希，已在 .gitignore
PREFS_FILE = os.path.join(HERE, '.prefs.json')     # 12 道写作偏好，本机
MATERIAL_DIR = os.path.join(HERE, '.material')     # 每篇的事实清单 / 口述稿，本机
HOST, PORT = '127.0.0.1', 8891
SAFE_NAME = re.compile(r'^[0-9A-Za-z_\-]+\.md$')
BAD_CAT = re.compile(r'[:#\n\r]')

# frontmatter 按这个顺序输出；不在这张表里的字段（比如 updates）原样保留
KNOWN_FM = ('title', 'date', 'category', 'description', 'top')
KEY_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*:')

SESSION_TTL = 7 * 24 * 3600
SESSIONS = {}          # token -> 过期时间戳
FAILS = {'n': 0, 'until': 0.0}
PBKDF2_ROUNDS = 200_000


# ---------------------------------------------------------------- git / md
def run_git(args):
    r = subprocess.run(['git'] + args, cwd=ROOT, capture_output=True,
                       text=True, encoding='utf-8', errors='replace', timeout=120)
    out = (r.stdout or '') + (r.stderr or '')
    return r.returncode, out.strip()


def split_frontmatter(text):
    """拆成 (frontmatter 原始行列表, 正文)"""
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text or '', re.S)
    if not m:
        return [], text or ''
    return m.group(1).splitlines(), m.group(2)


def fm_blocks(lines):
    """把 frontmatter 按顶层字段分段，每段保留原始文本。
    updates 这种多行字段（续行以空格 + - 开头）不会被拆散。"""
    blocks = []
    for line in lines:
        m = KEY_RE.match(line)
        if m:
            blocks.append((m.group(1), [line]))
        elif blocks and line.strip():
            blocks[-1][1].append(line)
    return blocks


def parse_md(text):
    """取字段值（多行字段只取首行）+ 正文"""
    lines, body = split_frontmatter(text)
    fm = {}
    for k, blk in fm_blocks(lines):
        fm[k] = blk[0].split(':', 1)[1].strip() if ':' in blk[0] else ''
    return fm, body


def render_md(old_text, values, body):
    """按规范顺序重写 frontmatter，未列出的字段（updates 等）原样搬运。
    values 里为空字符串的字段会被删掉。"""
    lines, _ = split_frontmatter(old_text)
    blocks = fm_blocks(lines)
    out = []
    for k in KNOWN_FM:
        v = (values.get(k) or '').strip()
        if v:
            out.append(f'{k}: {v}')
    for k, blk in blocks:
        if k not in KNOWN_FM:
            out.extend(blk)
    return '---\n' + '\n'.join(out) + '\n---\n\n' + (body or '').strip() + '\n'


def read_posts():
    items = []
    for f in sorted(os.listdir(POSTS_DIR)):
        if not f.endswith('.md'):
            continue
        try:
            fm, _ = parse_md(open(os.path.join(POSTS_DIR, f), encoding='utf-8').read())
        except Exception:
            continue
        items.append({'file': f, 'title': fm.get('title', ''), 'date': fm.get('date', ''),
                      'category': fm.get('category', ''), 'description': fm.get('description', ''),
                      'top': fm.get('top') == 'true'})
    items.sort(key=lambda x: (x['date'], x['file']), reverse=True)
    return items


def set_category(fname, cat):
    p = os.path.join(POSTS_DIR, fname)
    text = open(p, encoding='utf-8').read()
    fm, body = parse_md(text)
    open(p, 'w', encoding='utf-8', newline='\n').write(render_md(text, {
        'title': fm.get('title', ''), 'date': fm.get('date', ''),
        'category': cat, 'description': fm.get('description', ''),
        'top': 'true' if fm.get('top') == 'true' else ''
    }, body))


# ---------------------------------------------------------------- 本机素材
def read_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def material_path(fname):
    if not SAFE_NAME.match(fname or ''):
        return None
    os.makedirs(MATERIAL_DIR, exist_ok=True)
    return os.path.join(MATERIAL_DIR, fname[:-3] + '.json')


# ---------------------------------------------------------------- 内容体检
# 强信号：出现就基本是套话
STRONG_PHRASES = [
    '值得注意的是', '需要注意的是', '值得一提的是', '综上所述', '总而言之', '总的来说',
    '这让我意识到', '这启示我们', '我们可以看到', '不难发现', '由此可见',
    '赋能', '抓手', '全方位', '多维度',
]
# 弱信号：单独看不致命，密集出现才是问题
WEAK_PHRASES = ['与此同时', '进一步', '从而', '更好地', '全面提升', '深刻', '显著', '有效地']
# 需要上下文才成立的（避免「随着光标移动」这种误伤）
PATTERNS = [
    (r'随着.{0,14}的(?:不断)?(?:发展|推进|普及|深入|成熟)', '随着…的不断发展', 'strong'),
    (r'具有重要的.{0,8}(?:意义|价值|作用)', '具有重要的…意义', 'strong'),
    (r'不仅.{0,30}?而且', '不仅…而且', 'strong'),
    (r'不是.{0,24}?而是', '不是…而是', 'weak'),
]
TITLE_RULE = '做了什么：领域 + 方法 + 解决什么问题'


def _plain_body(text):
    """去掉 frontmatter / 代码块 / 图片 / 容器标记，只留要读的正文"""
    _, body = parse_md(text)
    body = re.sub(r'```.*?```', '\n', body, flags=re.S)
    body = re.sub(r'`[^`]*`', '', body)
    body = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', body)
    body = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', body)
    body = re.sub(r'^\s*:::\s*\w*\s*.*$', '', body, flags=re.M)
    body = re.sub(r'^\s*#{1,6}\s+.*$', '', body, flags=re.M)
    body = re.sub(r'^\s*\|.*$', '', body, flags=re.M)
    body = re.sub(r'^\s*[-*+]\s+', '', body, flags=re.M)
    body = re.sub(r'[>*_#`]', '', body)
    return body.strip()


def _stats(nums):
    n = len(nums)
    if not n:
        return 0.0, 0.0
    mean = sum(nums) / n
    var = sum((x - mean) ** 2 for x in nums) / n
    return mean, var ** 0.5


def audit_text(title, text):
    body = _plain_body(text)
    paras = [p.strip() for p in re.split(r'\n\s*\n', body) if len(p.strip()) >= 20]
    sents = [s.strip() for s in re.split(r'[。！？!?\n]+', body) if len(s.strip()) >= 6]

    p_lens = [len(p) for p in paras]
    s_lens = [len(s) for s in sents]
    p_mean, p_sd = _stats(p_lens)
    s_mean, s_sd = _stats(s_lens)

    hits = []
    for ph in STRONG_PHRASES:
        for m in re.finditer(re.escape(ph), body):
            ctx = body[max(0, m.start() - 10):m.end() + 14].replace('\n', ' ')
            hits.append({'word': ph, 'level': 'strong', 'ctx': ctx, 'score': 7})
    for ph in WEAK_PHRASES:
        c = len(re.findall(re.escape(ph), body))
        if c:
            hits.append({'word': ph, 'level': 'weak', 'ctx': '', 'score': min(8, c * 2), 'count': c})
    for pat, label, lv in PATTERNS:
        for m in re.finditer(pat, body):
            hits.append({'word': label, 'level': lv,
                         'ctx': body[m.start():m.end()].replace('\n', ' '),
                         'score': 7 if lv == 'strong' else 3})

    # 破折号：每千字超过 3 个就算多（你之前也提过这个）
    dash = body.count('——')
    if dash >= 3:
        per_k = dash * 1000 / max(1, len(body))
        if per_k > 3:
            hits.append({'word': '破折号', 'level': 'weak',
                         'ctx': '全文 %d 处，每千字 %.1f 个' % (dash, per_k),
                         'score': min(8, int(per_k))})

    # 句首雷同：只统计中文开头，出现 3 次以上算节奏单调
    opens = {}
    for s in sents:
        k = s.strip('“”"\'‘’ ,，、。！？!?；;：:')[0:2]
        if len(k) == 2 and re.match(r'^[\u4e00-\u9fff]{2}$', k):
            opens[k] = opens.get(k, 0) + 1
    repeat = sorted([(k, v) for k, v in opens.items() if v >= 3],
                    key=lambda x: -x[1])[:5]

    # 标题体检
    t = (title or '').strip()
    t_issues = []
    mm = re.match(r'^(.+?)[：:](.+)$', t)
    if not mm:
        t_issues.append('缺「：」，没写清做了什么/用什么方法解决什么问题')
    else:
        if len(mm.group(1).strip()) < 4:
            t_issues.append('冒号前太短，没写清做了什么')
        if len(mm.group(2).strip()) < 10:
            t_issues.append('冒号后太短，没写清方法或问题')
    if len(t) > 46:
        t_issues.append('超过 46 字，首页卡片会换行')

    score = min(40, sum(h['score'] for h in hits))
    if len(s_lens) >= 8:
        if s_sd < 8:
            score += 32
        elif s_sd < 11:
            score += 22
        elif s_sd < 14:
            score += 12
        elif s_sd >= 20:
            score -= 5
    if len(p_lens) >= 4 and p_mean:
        cv = p_sd / p_mean
        if cv < 0.3:
            score += 18
        elif cv < 0.45:
            score += 8
    score += min(15, sum(v - 2 for _, v in repeat) * 6)
    score = max(0, min(100, score))

    return {
        'title': title, 'chars': len(re.sub(r'\s', '', body)),
        'sents': len(sents), 'paras': len(paras),
        's_mean': round(s_mean, 1), 's_sd': round(s_sd, 1),
        'p_mean': round(p_mean, 1), 'p_cv': round((p_sd / p_mean) if p_mean else 0, 2),
        's_max': max(s_lens) if s_lens else 0,
        'hits': hits[:12], 'hit_total': len(hits),
        'repeat': [{'open': k, 'n': v} for k, v in repeat],
        'title_issues': t_issues, 'score': score,
    }


def audit_all():
    out = []
    for it in read_posts():
        p = os.path.join(POSTS_DIR, it['file'])
        try:
            text = open(p, encoding='utf-8').read()
        except Exception:
            continue
        a = audit_text(it['title'], text)
        a.update({'file': it['file'], 'category': it['category'] or '未分类', 'date': it['date']})
        out.append(a)
    out.sort(key=lambda x: -x['score'])
    return out



# ---------------------------------------------------------------- 鉴权
def load_auth():
    try:
        with open(AUTH_FILE, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def save_password(password):
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), PBKDF2_ROUNDS)
    with open(AUTH_FILE, 'w', encoding='utf-8') as f:
        json.dump({'salt': salt, 'hash': dk.hex(),
                   'created': date.today().isoformat()}, f)
    try:
        os.chmod(AUTH_FILE, 0o600)
    except Exception:
        pass


def check_password(password):
    a = load_auth()
    if not a:
        return False
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                             bytes.fromhex(a['salt']), PBKDF2_ROUNDS)
    return secrets.compare_digest(dk.hex(), a.get('hash', ''))


def new_session():
    tok = secrets.token_urlsafe(32)
    SESSIONS[tok] = time.time() + SESSION_TTL
    # 顺手清掉过期 token
    for k, exp in list(SESSIONS.items()):
        if exp < time.time():
            SESSIONS.pop(k, None)
    return tok


class Handler(BaseHTTPRequestHandler):
    # ---- 响应工具 ----
    def _cors(self):
        # 只给 /api/ping 用：线上博客页（https）请求本机服务探测。
        # http://127.0.0.1 属于浏览器认可的"可信来源"，不会被 Mixed Content 拦，
        # 剩下的是跨源放行 + Chrome 私网访问（PNA）预检。
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')

    def _json(self, obj, code=200, headers=None):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        if headers:
            for k, v in headers:
                self.send_header(k, v)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _html(self, text):
        data = text.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        # 只允许本站 / 本地开发 / 线上博客把它嵌进 iframe，别的网站嵌不了
        self.send_header('Content-Security-Policy',
                         "frame-ancestors 'self' https://creamsou.github.io "
                         "http://localhost:5173 http://127.0.0.1:5173 "
                         "http://localhost:4173 http://127.0.0.1:4173 "
                         "http://localhost:5199 http://127.0.0.1:5199")
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _token(self):
        for part in (self.headers.get('Cookie') or '').split(';'):
            k, _, v = part.strip().partition('=')
            if k == 'edt':
                return v
        return ''

    def _authed(self):
        tok = self._token()
        exp = SESSIONS.get(tok)
        return bool(exp and exp > time.time())

    def _need_auth(self):
        self._json({'error': '未登录', 'auth': False}, 401)
        return None

    def _body(self):
        length = int(self.headers.get('Content-Length', 0) or 0)
        raw = self.rfile.read(length) if length else b'{}'
        try:
            return json.loads(raw.decode('utf-8'))
        except Exception:
            return None

    def log_message(self, *a):
        pass

    # ---- 路由 ----
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '600')
        self.end_headers()

    def do_GET(self):
        u = urlparse(self.path)
        p = u.path

        if p in ('/', '/index.html'):
            return self._html(open(PAGE_FILE, encoding='utf-8').read())

        # 探测端点：不返回任何内容数据，不需要登录。
        # 必须带 CORS 头，否则线上博客（https://creamsou.github.io）的 fetch 会被浏览器拦掉，
        # 入口永远不会出现。
        if p == '/api/ping':
            return self._json({'ok': True, 'app': 'blog-editor',
                               'needSetup': load_auth() is None,
                               'loggedIn': self._authed()},
                              headers=[('Access-Control-Allow-Origin', '*'),
                                       ('Access-Control-Allow-Private-Network', 'true')])

        if p == '/api/auth':
            return self._json({'needSetup': load_auth() is None,
                               'loggedIn': self._authed()})

        if not self._authed():
            return self._need_auth()

        if p == '/api/posts':
            return self._json(read_posts())
        if p == '/api/audit':
            return self._json(audit_all())
        if p == '/api/prefs':
            return self._json(read_json(PREFS_FILE, {'answers': {}, 'updated': ''}))
        if p == '/api/material':
            f = parse_qs(u.query).get('file', [''])[0]
            mp = material_path(f)
            if not mp:
                return self._json({'error': '非法文件名'}, 400)
            return self._json(read_json(mp, {'facts': '', 'oral': '', 'updated': ''}))
        if p == '/api/post':
            f = parse_qs(u.query).get('file', [''])[0]
            if not SAFE_NAME.match(f):
                return self._json({'error': '非法文件名'}, 400)
            fp = os.path.join(POSTS_DIR, f)
            if not os.path.exists(fp):
                return self._json({'error': '文件不存在'}, 404)
            fm, body = parse_md(open(fp, encoding='utf-8').read())
            return self._json({'file': f, 'title': fm.get('title', ''),
                               'date': fm.get('date', ''), 'category': fm.get('category', ''),
                               'description': fm.get('description', ''),
                               'top': fm.get('top') == 'true', 'body': body})
        if p == '/api/status':
            _, st = run_git(['status', '--short'])
            _, lg = run_git(['log', '--oneline', '-3'])
            return self._json({'git_status': st or '(工作区干净)', 'recent': lg})

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        u = urlparse(self.path)
        p = u.path
        data = self._body()
        if data is None:
            return self._json({'error': '请求体不是合法 JSON'}, 400)

        # ---- 登录相关（无需已登录）----
        if p == '/api/auth/setup':
            if load_auth() is not None:
                return self._json({'error': '密码已设置，不能重复初始化'}, 400)
            pw = (data.get('password') or '').strip()
            if len(pw) < 6:
                return self._json({'error': '密码至少 6 位'}, 400)
            save_password(pw)
            tok = new_session()
            return self._json({'ok': True}, headers=[
                ('Set-Cookie', f'edt={tok}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_TTL}')])

        if p == '/api/auth/login':
            now = time.time()
            if FAILS['until'] > now:
                return self._json({'error': '试错次数太多，等一分钟再试'}, 429)
            pw = data.get('password') or ''
            if not check_password(pw):
                FAILS['n'] += 1
                if FAILS['n'] >= 5:
                    FAILS['n'] = 0
                    FAILS['until'] = now + 60
                return self._json({'error': '密码不对'}, 401)
            FAILS['n'] = 0
            tok = new_session()
            return self._json({'ok': True}, headers=[
                ('Set-Cookie', f'edt={tok}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_TTL}')])

        if p == '/api/auth/logout':
            SESSIONS.pop(self._token(), None)
            return self._json({'ok': True}, headers=[
                ('Set-Cookie', 'edt=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0')])

        if not self._authed():
            return self._need_auth()

        # ---- 保存文章 ----
        if p == '/api/save':
            f = data.get('file', '')
            if not SAFE_NAME.match(f):
                return self._json({'error': '文件名只能含英文、数字、-、_'}, 400)
            fp = os.path.join(POSTS_DIR, f)
            old = open(fp, encoding='utf-8').read() if os.path.exists(fp) else ''
            md = render_md(old, {
                'title': data.get('title') or '无标题',
                'date': data.get('date') or date.today().isoformat(),
                'category': data.get('category', ''),
                'description': data.get('description', ''),
                'top': 'true' if data.get('top') else ''
            }, data.get('body', ''))
            open(fp, 'w', encoding='utf-8', newline='\n').write(md)
            return self._json({'ok': True, 'file': f})

        # ---- 写作偏好（12 道选择题的答案）----
        if p == '/api/prefs':
            answers = data.get('answers')
            if not isinstance(answers, dict):
                return self._json({'error': 'answers 必须是对象'}, 400)
            write_json(PREFS_FILE, {'answers': answers,
                                    'updated': date.today().isoformat()})
            return self._json({'ok': True})

        # ---- 某篇文章的素材：事实清单 / 口述原文 ----
        if p == '/api/material':
            mp = material_path(data.get('file', ''))
            if not mp:
                return self._json({'error': '非法文件名'}, 400)
            write_json(mp, {
                'facts': str(data.get('facts') or '')[:200000],
                'oral': str(data.get('oral') or '')[:200000],
                'updated': date.today().isoformat(),
            })
            return self._json({'ok': True})

        # ---- 批量移动文章到某个分类 ----
        if p == '/api/post/move':
            files = data.get('files') or []
            cat = (data.get('category') or '').strip()
            if BAD_CAT.search(cat):
                return self._json({'error': '分类名不能含冒号或井号'}, 400)
            ok, bad = [], []
            for f in files:
                if not SAFE_NAME.match(str(f)):
                    bad.append(str(f))
                    continue
                try:
                    set_category(f, cat)
                    ok.append(f)
                except Exception:
                    bad.append(str(f))
            return self._json({'ok': True, 'changed': len(ok), 'failed': bad})

        # ---- 单篇删除 ----
        if p == '/api/delete':
            f = data.get('file', '')
            if not SAFE_NAME.match(f):
                return self._json({'error': '非法文件名'}, 400)
            fp = os.path.join(POSTS_DIR, f)
            if os.path.exists(fp):
                os.remove(fp)
            return self._json({'ok': True})

        # ---- 分类改名（new 为空 = 变成未分类）----
        if p == '/api/category/rename':
            old = (data.get('old') or '').strip()
            new = (data.get('new') or '').strip()
            if not old:
                return self._json({'error': '缺少原分类名'}, 400)
            if BAD_CAT.search(new):
                return self._json({'error': '分类名不能含冒号或井号'}, 400)
            changed = 0
            for it in read_posts():
                if (it['category'] or '未分类') != old:
                    continue
                set_category(it['file'], new)
                changed += 1
            return self._json({'ok': True, 'changed': changed})

        # ---- 发布 ----
        if p == '/api/publish':
            logs = []
            # 只提交 docs 目录：避免把工作区里的临时文件卷进仓库
            for args, msg in [(['add', '-A', 'docs'], '加入暂存区'),
                              (['commit', '-m', 'update: ' + date.today().isoformat()], '提交')]:
                code, out = run_git(args)
                logs.append(f'== {msg} ==\n{out or "(无输出)"}')
                if code != 0 and 'nothing to commit' not in out:
                    return self._json({'ok': False, 'log': '\n'.join(logs)})
            code, out = run_git(['push'])
            if code == 0:
                logs.append('== 推送到 GitHub ==\ngit push 成功')
            else:
                logs.append(f'== git push 失败，改走 API 推送 ==\n{out}')
                r = subprocess.run([sys.executable, os.path.join(HERE, 'api_push.py'),
                                    '.', 'update: ' + date.today().isoformat()],
                                   cwd=ROOT, capture_output=True, text=True,
                                   encoding='utf-8', errors='replace', timeout=300)
                ok = 'PUSH_OK' in (r.stdout or '')
                logs.append(r.stdout[-600:] if ok else (r.stdout + r.stderr)[-1200:])
                if not ok:
                    return self._json({'ok': False, 'log': '\n'.join(logs)})
            return self._json({'ok': True, 'log': '\n'.join(logs)})

        self.send_response(404)
        self.end_headers()


if __name__ == '__main__':
    os.makedirs(POSTS_DIR, exist_ok=True)
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f'博客控制台运行在 http://{HOST}:{PORT} （Ctrl+C 停止）')
    webbrowser.open(f'http://{HOST}:{PORT}')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
