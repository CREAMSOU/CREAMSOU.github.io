# 我的博客

基于 VitePress + GitHub Pages，成本 0 元。

## 本地编辑器（推荐日常使用）

双击 `editor.bat`，浏览器自动打开 http://127.0.0.1:8891

- 左侧文章列表，点击加载
- 顶部"新建文章"：填文件名，写完点"保存"
- **保存**：只写入本地文件，不上线
- **保存并发布**：自动 git add → commit → push，push 成功后 1~2 分钟线上更新
- 只监听 127.0.0.1，仅本机能访问；零第三方依赖

## GitHub 网页编辑（应急/手机）

打开仓库 → `docs/posts` → 点文件 → 铅笔图标 → 修改 → Commit changes，自动部署。只有你的账号能改。

## 本地预览

双击 `dev.bat`（或命令行 `npm run dev`），浏览器打开 http://localhost:5173

## 写一篇新文章

1. 在 `docs/posts/` 新建 `YYYY-MM-DD-标题.md`
2. 文件开头写：

```markdown
---
title: 文章标题
date: 2026-09-09
description: 一两句话摘要（显示在首页卡片上）
---

正文……
```

3. 本地预览没问题后：`git add . && git commit -m "新文章" && git push`

## 上线（首次配置）

1. 在 GitHub 建一个仓库（若用用户名同名仓库 `CREAMSOU.github.io`，无需改 base；普通仓库需在 `docs/.vitepress/config.mts` 里设置 `base: '/仓库名/'`）
2. 推送代码：

```bash
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/CREAMSOU/仓库名.git
git push -u origin main
```

3. 仓库 Settings → Pages → Source 选 **GitHub Actions**
4. 之后每次 push 自动构建发布，地址：`https://creamsou.github.io/`

## 目录说明

```
blog/
├── docs/
│   ├── .vitepress/          # 配置与主题（config.mts 改站名/导航）
│   │   ├── theme/           # 自定义主题：首页文章卡片列表
│   │   └── posts.data.mjs   # 自动扫描 posts/ 生成列表
│   ├── public/              # 静态资源（banner 图放这里）
│   ├── index.md             # 首页（banner + 标题）
│   ├── about.md             # 关于页
│   └── posts/               # ★ 文章都放这里
├── dev.bat                  # 一键本地预览
└── build.bat                # 一键构建
```
