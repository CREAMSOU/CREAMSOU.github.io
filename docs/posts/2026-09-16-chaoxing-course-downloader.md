---
title: 超星学习通课件批量下载：用 Python 标准库复用会话，绕开 vc3 加密
date: 2026-09-16
category: 工具与环境
description: 超星学习通没有一键下载全部课件的功能。从本机 cookie 库偷登录态走不通，改用 DevTools 复制会话，再踩了 vc3 被 URL 转义的坑，最后做成纯标准库脚本。
updates:
  - 2026-10-29 标题改为「做了什么 + 领域 + 方法 + 解决什么问题」的信息型写法
  - 2026-09-16 首版发布
---

<Lead :points="['超星没有一键下载全部课件的功能，课件散在章节任务和资料区', '新版 Chromium 的 App-Bound Encryption 让读本地 cookie 基本死路', '从 DevTools 复制带 cookie 的 curl 最省事', 'vc3 被 URL 转义，解码即登录失败，必须原样发']" />

> **项目地址**：[github.com/CREAMSOU/chaoxing-course-downloader](https://github.com/CREAMSOU/chaoxing-course-downloader) — MIT License，纯 Python 标准库，零第三方依赖。

想离线看一门超星学习通（泛雅）课程的课件。超星没有「一键下载全部」的按钮，课件分散在「章节任务点」和「资料区」两块，逐一点很烦。

目标很直接：写个脚本，喂课程参数加登录态，自动把整门课的 PPT / PDF / Word 扒到本地。

## 死路：从本机 cookie 库偷登录态

第一反应是用 `browser_cookie3` 读 Edge 的 cookie 库，再用 `requests` 伪装登录。这条路在新版 Chromium 上基本走不通：

- Chrome 127+ / Edge 132+ 启用了 **App-Bound Encryption**，cookie 加密密钥绑定到浏览器二进制路径，第三方库解出来全是空。
- 复制用户 profile 到其他目录再读？Edge 判定密钥失效，副本的 cookie 被清空为 0。
- 浏览器进程占用时 cookie 库被独占锁定，连复制都复制不了。

| 方案 | 结果 | 结论 |
| --- | --- | --- |
| 第三方库读 cookie 库 | 空 / 锁定 | 死路 |
| 复制 profile 再读 | cookie 被清空 | 死路 |
| DevTools 复制会话 | 完整可用 | **走它** |

结论很干脆：别和浏览器的安全机制硬刚，从已经登录好的浏览器里把会话导出来最省事。

## 转机：让浏览器把登录态交出来

浏览器里明明登录着，缺的只是「把登录态交给脚本」。最稳的办法是让浏览器自己把带 cookie 的请求导出来：

1. 打开课程页并登录
2. F12 → Network → 勾 `Disable cache` → F5 刷新
3. 左侧列表点最上面那条（`Type=document`，名字含 `stu?courseid=...`）
4. 右键 → 复制 ▶ → **以 cURL 格式复制 (bash)**

这条 curl 自带完整的 `Cookie` 头，包含 HttpOnly 的 `vc3`，脚本拿到就能以你的身份访问接口。

::: tip 拿不到 vc3 时
只想要 cookie 串、不要整条 curl，Console 里 `copy(document.cookie)` 也行。但 `vc3` 是 HttpOnly，`document.cookie` 读不到它，会登录失败。所以抓不到 `vc3` 时一律用上面的 curl 法。
:::

## 坑：vc3 被 URL 转义，解码即失败

这是最阴的一点。DevTools 复制出的 curl 里，`vc3` 值的 `+ / =` 被转义成了 `%2B %2F %3D`。

我一开始「顺手」用 `urllib.parse.unquote` 还原了它——结果服务端判定未登录，返回登录页。排查时对比请求响应长度发现：**原样发送（保留 `%2B`）能登录，解码后反而登录失败**。

::: warning vc3 别解码
把 cookie 整串原样当 `Cookie` 头发，绝不 URL 解码。超星服务端是按原始头字符串校验的，你还原了转义反而对不上。
:::

## 工具长什么样

整理成一个零依赖小工具，只用 Python 标准库，`python3 chaoxing_dl.py` 直接跑，无需 `pip install`。

流程：

1. `studentcourse` → 解析全部 `knowledgeid`（章节）
2. `knowledge/cards` → 每章任务点里的附件 `objectId`
3. `coursedata/stu-datalist` → 资料区文件 `objectId`
4. `ananas/status/{oid}` → 拿真实文件名加下载地址
5. 下载到本地目录

用法（参数都在课程页 URL 里）：

```bash
python3 chaoxing_dl.py \
  --course-id <课程ID> --clazz-id <班级ID> --cpi <cpi> \
  --curl "$(pbpaste)"          # 直接粘贴复制的 curl
  # 或 --cookie-file cookie.txt
  # 加 --ppt-only 只下 PPT
```

实测一门课的全部课件（PPT 加 Word 模板）全部下载成功。代码已整理成开源仓库并发布到 GitHub：<https://github.com/CREAMSOU/chaoxing-course-downloader>，登录态相关文件用 `.gitignore` 屏蔽了，不会误提交。

## 边界和下一步

做到的和没做到的：

1. **登录态是从你自己的浏览器复制的**，本质是复用会话，不是绕过鉴权。cookie 过期后重新复制一次就行。
2. **接口结构跟着超星当前版本走**。哪天它改了字段名，解析那几步要跟着改。
3. 现在只下附件，没做 PPT 内嵌视频的提取——需要的再说。

::: tip 一句结论
本地 cookie 库读不动就别硬读，DevTools 复制会话最稳；cookie 原样发，别手贱去 URL 解码。
:::
