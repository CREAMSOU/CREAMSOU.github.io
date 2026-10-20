---
title: Wallpaper Engine 打不开：托盘没图标、窗口不弹，真凶是权限不是显卡
date: 2026-10-12
category: 学习记录
description: 两轮误判都只解释了一半现象。真因是 CEF 的配置目录不可写，界面进程在建锁文件时就断言退出，连自己的日志都没来得及写。修法是补一条权限，不删任何东西。
top: false
updates:
  - 2026-10-12 首版发布，当时结论为「GPU 加速冲突」
  - 2026-10-20 结论更正为 NTFS 权限问题，正文按证据重写
---

<Lead :points="['界面打不开，但壁纸一直在正常播放', '前两轮判断（缺 WebView2、显卡冲突）各只解释了一半现象', '转折点是发现程序自己的日志在某天之后再没写过字', '真因是配置目录不可写，补一条权限就修好，不需要备份']" />

> **修复脚本**：[github.com/CREAMSOU/wallpaper-engine-ui-fix](https://github.com/CREAMSOU/wallpaper-engine-ui-fix) — MIT License，纯 PowerShell，无第三方依赖。先打印证据表，再决定修不修。

> **更正（2026-10-20）**：本文首版把原因判为「libcef 的 GPU 加速与显卡冲突」。那个结论是错的，只是碰巧让界面起来过几次。真实原因是 CEF 的配置目录不可写。正文已按证据重写；误判过程保留，因为它是这次最有价值的部分。

Wallpaper Engine 打不开了。右下角托盘没有图标，双击快捷方式没有反应，但桌面壁纸一直在正常播放。

这个组合很别扭：如果程序崩了，壁纸应该跟着停；如果程序正常，界面应该能打开。结果是壁纸活着、界面死了。

任务管理器里只有一个 `wallpaperservice64`。负责界面的 `wallpaperui.exe` 启动后几秒就消失，没有弹窗，没有报错。

## 第一轮：以为缺 WebView2

界面是用内置浏览器内核渲染的，所以第一反应是系统缺了运行时（WebView2）。这条因果链很顺：界面出不来 → 渲染引擎缺了 → 装一个就好。

于是查注册表（没找到）、下安装包、静默安装（被 UAC 拦）、换独立安装包（双击报「不兼容」，一看文件头是 32 位的）、最后换官方引导程序，它弹出一句：**已经安装了**。

WebView2 一直躺在 `C:\Program Files (x86)\Microsoft\EdgeWebView\Application\` 里。我第一遍只查了其中一个注册表位置，没命中就下了「没装」的结论。

::: warning 踩坑
「缺运行库」有完整因果链，看着最合理，也最容易一头扎进去。注册表查不到不等于没装，它有多个注册位置，还有安装目录本身。
:::

## 第二轮：查到 libcef，却判给了显卡

换个笨办法，直接问系统谁崩的：

```powershell
Get-WinEvent -FilterHashtable @{LogName='Application'; Id=1000; StartTime=(Get-Date).AddDays(-30)}
```

日志写得很清楚：出错模块 `libcef.dll`，异常代码 `0x80000003`。这是断点 / 断言类崩溃，Chromium 里最常见的触发点是 GPU 初始化。

最小验证也过了：手工加 `--disable-gpu` 启动 `wallpaperui.exe`，进程活下来了。于是把它写进 `config.json`，界面确实起来了。

**这个「修好了」只持续了三天。**

## 复发：三条排除线全断

第二次打不开时，配置里的两个开关还在（`uihardwareacceleration: false`、`cefcommandline: --disable-gpu`），说明不是配置被覆盖。

于是把 GPU 这条假设彻底压测一遍：

| 启动参数 | 结果 |
| --- | --- |
| `--disable-gpu` | 崩 |
| `--disable-gpu --disable-gpu-compositing` | 崩 |
| `--disable-gpu --use-angle=swiftshader`（纯软件渲染） | 崩 |
| `--no-sandbox` | 崩 |
| 全新 `--user-data-dir`（空配置） | 崩 |

完全禁用 GPU、纯软件渲染、不用沙箱、空 profile，四条路全崩。**那它就不是 GPU 的事。**

## 转折：程序自己的日志停在某天

`bin\wallpaperuilog.txt` 最后一行是 `2026-10-12 00:55 UI CEF shutdown`，此后再也没有新内容——包括之后每一次崩溃。

程序连自己的日志都写不出来，说明它死在日志文件打开之前。**是初始化最早期就失败，不是跑到一半出错。**

顺着这个方向查目录权限，拿到两个硬证据。

第一个是 ACL：

| 身份 | 对 `ui` 目录的权限 |
| --- | --- |
| `Authenticated Users` | 只读 |
| `Users` | 只读 |
| `SYSTEM` / `Administrators` | 完全控制 |
| 所有者 | `BUILTIN\Administrators` |

第二个是实测——ACL 可能骗人，所以直接写：

```powershell
$p = "E:\steam\steamapps\common\wallpaper_engine\ui\uicache\__probe.tmp"
try { [System.IO.File]::WriteAllText($p, "x"); "可写" } catch { "拒绝: $($_.Exception.Message)" }
```

结果：**访问被拒绝**。

## 因果链

CEF 启动时必须在配置目录里创建一个 `SingletonLock` 锁文件，防止同一个 profile 被两个进程同时打开。建不了锁文件，`ProcessSingleton` 初始化失败，libcef 断言失败直接断点退出。

```
ui\uicache 不可写
  → SingletonLock 创建失败（ERROR 5 拒绝访问）
  → ProcessSingleton 初始化失败
  → libcef 断言 → 0x80000003 → 进程立即退出
  → 主窗口 / 托盘图标都出不来
```

壁纸渲染是 `wallpaper64.exe` 干的活，它不碰这个目录。所以壁纸照常播放，只有界面没了。

<DiagramWeTroubleshoot />

三种解释各能说明什么，摊开对比就很清楚：

| 解释 | 能说明 | 说明不了 |
| --- | --- | --- |
| 缺 WebView2 | Web 类壁纸黑屏报错 | 界面进程秒退；而且本机早就装了 |
| 显卡 / 驱动冲突 | libcef 断言崩溃 | 纯软件渲染、无沙箱、空 profile 照样崩；也解释不了日志一个字没写 |
| 配置目录不可写 | 死在写日志之前、壁纸不受影响、实测被拒 | —— |

## 修复：加一条权限，不删任何东西

需要管理员权限，因为要改 DACL，而当前账户在那个目录上恰好只有读。

```batch
icacls "E:\steam\steamapps\common\wallpaper_engine\ui" /grant "%USERNAME%:(OI)(CI)F" /T /C /Q
```

跑完 `Successfully processed 2032 files; Failed 0`。重启后界面进程稳定存活，之后没再产生新的崩溃转储。

::: tip 为什么不需要先备份
`/grant` 是**追加**一条授权，原有权限条目一条都不改动。没有东西被删除，也就没有东西需要还原。
:::

真正会动到历史的做法是 `/reset`（把整棵树重置成继承状态），它才是必须先把 ACL 导出来备份的那种操作：

| 做法 | 要不要备份 | 处理范围 | 回退方式 |
| --- | --- | --- | --- |
| `icacls /reset /T` | 要，会删掉原有条目 | 整棵树，7.8 万个文件 | 只能靠备份还原 |
| **`icacls /grant` 追加** | **不要** | 只改目标目录，子项靠继承 | 一条 `/remove:g` |

顺带说一句：`icacls /save` 导出的是权限描述文本，不是文件副本，全树也就 27 MB、32 万行。真要备份也不占地方。

## 同一个病，Steam 库也中了

修完界面才发现，这台机器上 Steam 库也有一样的毛病：不以管理员身份运行 Steam，就无法更新游戏，提示没有权限。

| 位置 | 状态 |
| --- | --- |
| `E:\steam` | `Users` 完全控制，正常 |
| `E:\steam\steamapps` | **阻止继承 + `Users` 只读**，问题源头 |
| 下面 39 个游戏目录 | 34 个继承成只读 |

`steamapps` 这一层的所有者是当前用户，所以不需要提权就能把它拉回继承。改完之后只有顶层生效，子目录要靠 Windows 自动传递：

```batch
icacls "E:\steam\steamapps\common" /grant *S-1-5-32-545:(OI)(CI)M /C /Q
```

`*S-1-5-32-545` 是 `BUILTIN\Users` 的 SID，用 SID 可以避开中文系统上组名解析的坑。最后 39 个目录逐个实测写入，全部通过。

::: warning 别再以管理员身份运行 Steam
这两处权限坏掉，最可能的成因就是以管理员身份运行过 Steam / Wallpaper Engine。正常安装的 Steam 库，普通账户本来就能读写。用管理员跑一次，它重建目录时可能把所有者改成管理员组，之后就再也写不进去。
:::

## 一句结论

界面打不开、壁纸却正常，说明进程不是跑崩的，是**在初始化最早期就退出了**。去看它自己的日志有没有「停在某一天不动」，比猜驱动和运行库有效得多。

日志不写 + 目录写不进，就是权限。修法只需要加一条授权，不必重置，也不必备份。
