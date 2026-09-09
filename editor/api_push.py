# -*- coding: utf-8 -*-
"""
通过 GitHub Git Data API 推送仓库（绕过 git HTTPS 通道）。
用法：python api_push.py <仓库目录> <commit_message>
令牌从环境变量 GH_TOKEN 或同目录 .gh_token.json 读取。
"""
import base64
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.abspath(sys.argv[1])
# 本机环境变量里的代理对 git/urllib 会挂，api.github.com 直连反而通——禁用代理
for k in ('http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY',
          'all_proxy', 'ALL_PROXY'):
    os.environ.pop(k, None)
MSG = sys.argv[2] if len(sys.argv) > 2 else 'update'
REPO = 'CREAMSOU/CREAMSOU.github.io'
API = f'https://api.github.com/repos/{REPO}'

token = os.environ.get('GH_TOKEN')
if not token:
    tf = os.path.join(os.path.dirname(ROOT), '.gh_token.json')
    if os.path.exists(tf):
        token = json.load(open(tf))['access_token']
if not token:
    sys.exit('no token')


def call(url, data=None, method=None):
    req = urllib.request.Request(
        url if url.startswith('http') else API + url,
        data=json.dumps(data).encode() if data is not None else None,
        headers={'Authorization': f'Bearer {token}',
                 'Accept': 'application/vnd.github+json',
                 'User-Agent': 'blog-push'},
        method=method or ('POST' if data is not None else 'GET'))
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace')[:200]
        raise SystemExit(f'HTTP {e.code} at {url}\n{body}')


files = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True,
                       text=True, check=True).stdout.split()
print(f'{len(files)} files to push')

# 空仓库上 Git Data API 会 409：先用 Contents API 引导出 main 分支
branches = call('/branches')
if not branches:
    readme = open(os.path.join(ROOT, 'README.md'), 'rb').read()
    call('/contents/README.md', {
        'message': 'bootstrap', 'branch': 'main',
        'content': base64.b64encode(readme).decode()}, 'PUT')
    print('bootstrap: main 分支已创建')

tree = []
for i, f in enumerate(files):
    p = os.path.join(ROOT, f)
    raw = open(p, 'rb').read()
    blob = call('/git/blobs', {'content': base64.b64encode(raw).decode(),
                               'encoding': 'base64'})
    tree.append({'path': f.replace('\\', '/'), 'mode': '100644',
                 'type': 'blob', 'sha': blob['sha']})
    print(f'[{i+1}/{len(files)}] {f}')

t = call('/git/trees', {'tree': tree})
base = call('/git/ref/heads/main')['object']['sha']

c = call('/git/commits', {'message': MSG, 'tree': t['sha'],
                          'parents': [base]})
call('/git/refs/heads/main', {'sha': c['sha'], 'force': False}, 'PATCH')
print('PUSH_OK', c['sha'][:10])
