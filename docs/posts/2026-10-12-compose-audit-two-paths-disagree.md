---
title: 我给工具写了两个数据源，然后它们吵起来了
date: 2026-10-12
category: 调试与排障
description: 为了安全卸载自建服务，写了个「删前体检」工具。它有两条取数路径，本该互相对照，结果一条报 18 个挂载、另一条报 16 个。被漏掉的 501 MB 里，有 265 MB 的向量库。五个真 bug 的排查过程都在这。
updates:
  - 2026-10-12 首版发布
---

<Lead :points="['两条取数路径本该互相印证，结果一个报 18 个挂载、一个报 16 个', '被漏掉的 501.3 MB 里，包括 265 MB 的向量库', '我一开始把责任归错了，独立实验才查清是两个 bug 各坏一处', '密钥判据要同时防漏判和误判，两边都踩了坑']" />

上一篇写的是「搭起来的工具修不完，所以卸掉」。卸载之前有个很实际的障碍：**我不知道该删什么。**

`docker compose down -v` 一条命令下去很爽，但它会连带删掉数据库、上传的文件、向量库索引，还有几十条只存在于 `.env` 里的密钥。所以我先写了个工具，让它替我把「哪些东西删了就回不来」列清楚。

工具跑通了，报告出来了。**然后我发现报告本身是错的。**

它在同一个项目上报了两个不同的答案。

<DiagramDataPaths />

这篇文章讲的就是这 5 个 bug。其中两个是解析错误（就是图里让两条路径吵架的那两个），另外三个都出在同一个地方：**「什么算密钥」这条判据。**

代码在 [CREAMSOU/compose-audit](https://github.com/CREAMSOU/compose-audit)，纯标准库、零依赖。

## 为什么会有两条取数路径

这不是设计出来的，是被逼出来的。

第一次跑的时候我本来打算直接用 `docker compose config --format json`——它会把 YAML 锚点、变量插值、profile 过滤全都处理好，输出一份规范化配置，我照着读就行。这是最省事也最准的路。

但它有个前提：**docker 守护进程得在跑。**

而实际情况是：

```
error during connect: this error may indicate that the docker daemon
is not running: Get "http://%2F%2F.%2Fpipe%2Fdocker_engine/...":
open //./pipe/docker_engine: The system cannot find the file specified.
```

命令行在，守护进程没起来。而我要审计的恰恰是一个**准备卸载的环境**——这种环境下让 docker 正常跑起来本身就是件麻烦事。

所以我写了第二条路：一个内置的轻量扫描器，纯标准库，自己读 compose 文件。它不追求成为通用 YAML 解析器，只认 compose 实际会用的那几种写法。

::: tip 兜底路径的意外收获
写第二条路本来只是为了「docker 不可用时也能跑」。但做完之后我意识到它带来了一个更值钱的东西：**两条独立实现的路径，可以作为彼此的对照组。**

同一份输入，两条路径给出不同结果 —— 那就说明至少有一条错了。这个信号不需要我知道正确答案是什么。
:::

两条路径的定位是这样分工的：

| | 路径 A：`docker compose config` | 路径 B：内置扫描器 |
| --- | --- | --- |
| 依赖 | docker 命令行（**不需要守护进程在跑**） | 纯标准库 |
| YAML 锚点 | docker 自己解析 | 我自己实现 |
| profile 过滤 | docker 自己过滤 | 我自己算 |
| 何时用 | 有 docker 时优先 | docker 不可用时的兜底 |

自检里专门有一项校验两条路径的一致性。**这项自检后来成了抓 bug 的主力。**

## 吵架现场

同一个项目，两条路径的输出：

| 指标 | 路径 A | 路径 B |
| --- | ---: | ---: |
| 宿主机挂载目录 | 18 | **16** |
| 疑似不可重建 | 5 | **3** |
| 不可重建体积 | 915.2 MB | **413.9 MB** |

差的 501.3 MB 是哪些目录：

| 目录 | 挂载到容器 | 体积 |
| --- | --- | ---: |
| `volumes/weaviate` | `/var/lib/weaviate` | 265.1 MB |
| `volumes/db/data` | `/var/lib/postgresql/data` | 236.2 MB |

**向量库（265.1 MB）和数据库（236.2 MB）在路径 B 的报告里消失得无影无踪。**

这就是整件事最危险的地方：路径 B 的报告**看起来完全正常**。它有结论、有体积、有分类，数字也不荒唐——16 个挂载、413.9 MB，谁看都觉得是一份合格的报告。如果我只跑了路径 B，我会拿着这份报告去归档，然后**在 `docker compose down -v` 之后才发现数据库没了。**

### 根因：变量没展开，两个服务被判"未启用"

查下来问题在 `COMPOSE_PROFILES` 这一行。Dify 的 compose 是这样写的：

```yaml
# docker-compose.yaml 片段
COMPOSE_PROFILES: ${VECTOR_STORE:-weaviate},${DB_TYPE:-postgresql},collaboration   [!code highlight]
```

`${VECTOR_STORE:-weaviate}` 的含义是「取环境变量 `VECTOR_STORE`，取不到就用 `weaviate`」。`weaviate` 和 `postgresql` 是后两个 profile 名。

我的扫描器拿这一行的时候**没做变量展开**，于是拿到的是字面量：

```text
"${VECTOR_STORE:-weaviate},${DB_TYPE:-postgresql},collaboration"
```

拆出来的 profile 名就成了 `${VECTOR_STORE:-weaviate}` 和 `${DB_TYPE:-postgresql}` —— 两个字符串，跟真实的服务名 `weaviate`、`postgres` 一个字都对不上。

结果：**这两个服务被判定为「profile 没启用」，整个服务连同它挂载的数据目录一起被排除在审计范围之外。**

修法就是把这一行交给已有的变量展开函数：

```python
# 错误写法：直接把字面量拿去拆   [!code --]
raw = env.get("COMPOSE_PROFILES") or ""
return {x.strip() for x in raw.split(",") if x.strip()}

# 正确写法：先展开 ${VAR:-默认值}，再拆   [!code ++]
raw = subst(env.get("COMPOSE_PROFILES") or "", env)
return {x.strip() for x in raw.split(",") if x.strip()}
```

修完，两条路径的第一个数字就对上了：**都是 18 个挂载、5 个不可重建。**

::: warning 这个 bug 的形状值得记住
展开之后，报告从「16 个挂载 / 413.9 MB」变成「18 个挂载 / 915.2 MB」，**多了整整一倍**。

但错的那一版没有任何异常特征：没报错、没空值、没崩溃，只是安静地少算了两项。**漏报和算错不一样——算错会被发现，漏报不会**，因为报告不会告诉你它漏了什么。

凡是「按条件筛选出一部分再统计」的逻辑，都要问一句：被筛掉的那些，是不是真的该被筛掉？
:::

## 我一开始归错了因

查完 profile 那个 bug，两条路径一致了，我以为完事了。

但自检里那条双路径校验还在跑，我又顺手做了个独立实验：**把工具按改动点拆成几个变体，一次只破坏一处，看哪个变体才能重现出错的那个结果。**

| 变体 | 破坏的地方 | 路径 B 的结果 |
| --- | --- | ---: |
| E1 | 不处理 YAML 锚点合并键 | 18 个挂载 / 5 个不可重建 |
| E2 | `COMPOSE_PROFILES` 不做插值 | **16 / 3** |
| E3 | 两个都破坏 | **16 / 3** |
| E4 | 不看变量值 | （密钥判据，另一条线） |

**E1 的结果是 18/5——和正确值一样。**

也就是说：**锚点那个 bug 根本不影响挂载数。**我之前把它和 profile 的问题混在一起谈，归错了责任。

那锚点 bug 到底坏了什么？换个指标量就看见了：

| | 修复前 | 修复后 |
| --- | ---: | ---: |
| 扫描到的 `env_file` 引用数 | 10 | **36** |

**少了 26 个环境变量文件的引用。**

原因在这里 —— Dify 的 compose 用 YAML 锚点把配置抽出来复用：

```yaml
# 先定义一份共享配置，起个名字
x-shared-api-worker-config: &shared-api-worker-config   [!code highlight]
  env_file:
    - ./envs/api.env
    - ./envs/worker.env
    # ... 一共 30 个

services:
  api:
    <<: *shared-api-worker-config   [!code highlight]
    image: langgenius/dify-api:1.0.0
```

`<<: *shared-api-worker-config` 是 YAML 的合并键，意思是「把那个锚点的内容并进来」。我的扫描器不认识 `<<`，直接跳过——**那 30 个 `env_file` 就全丢了。**

那为什么挂载数没受影响？因为 **`volumes` 是写在每个服务自己的配置里的，不在锚点里。**锚点里塞的全是 `env_file`。

::: tip 一个 bug 的两个症状，可能是两个 bug
我一开始认定「路径 B 少了 265 MB 是因为锚点没解析」。做了独立实验才发现，**这是两个 bug 各坏一处**：锚点坏的是 `env_file` 覆盖度，profile 插值坏的才是挂载和体积。

如果只修其中一个，另一个会继续潜伏——而且潜伏得很安静。**归因要靠实验，不能靠"看起来像"。**改动点拆分、一次只破坏一处，是这个实验里最有用的手法。
:::

## 另一条线：什么算密钥

修完解析，我把注意力转到密钥表上。

工具要列的是「哪些变量是密钥，归档时不能外传」。这条判据看起来简单，实际两边都是坑：**漏判会让密钥泄露，误判会让报告变成一团涂黑的噪音。**我两边都踩了。

先是漏判。修之前 JSON 输出里长这样：

```text
CELERY_BROKER_URL = redis://:difyai******@redis:6379/1      ← 明文口令
DB_PASSWORD       = ***REDACTED***
REDISCLI_AUTH     = ***REDACTED***
```

`CELERY_BROKER_URL` 这个变量名里**没有任何一个密钥词**——没有 PASSWORD、没有 SECRET、没有 TOKEN。所以按「变量名匹配关键词」的逻辑，它被判为普通配置，值原样输出。

但它的值里藏着东西：`redis://:口令@主机`。凭据嵌在连接串中间。

修法是加一条**按值判断**的路径：

```python
# 匹配 URL 里内嵌的凭据：//用户:口令@主机
_CRED_IN_URL = re.compile(r"://[^/\s:@]*:([^/\s:@]+)@")

def value_looks_secret(value: str) -> bool:
    """变量名可能完全人畜无害，值里却藏着口令。"""
    if _CRED_IN_URL.search(value):
        return True
    return bool(_SECRETISH_VALUE.search(value))
```

打码时也是保留结构、只挖掉口令，这样报告还能看出「这是个 redis 连接串」：

```python
# redis://:口令@redis:6379/1  →  redis://:***REDACTED***@redis:6379/1
s = _CRED_IN_URL.sub(lambda m: m.group(0).replace(m.group(1), "***REDACTED***"), s)
```

还有一类漏判：**变量名本身就是凭据名**，但值不是。比如 `REDISCLI_AUTH` —— redis 命令行工具的认证口令，变量名里既没有 PASSWORD 也没有 SECRET，只有 `AUTH`。

于是判据里加一组裸凭据名：

```python
BARE_CRED_NAME = re.compile(
    r"(PASSWORD|PASSWD|PASSPHRASE|SECRET|TOKEN|APIKEY|API_KEY|ACCESS_KEY|"
    r"PRIVATE_KEY|CREDENTIAL|AUTH(?!ENTICATION|ORIZATION|ORS)|PWD)",
    re.I,
)
```

注意那个 `AUTH(?!ENTICATION|ORIZATION|ORS)` —— 这是接下来这个故事的主角。

### 反方向的坑：判据太松

加上 `AUTH` 之后，密钥表炸了。

修之前 vs 修之后的对比：

| | 修复前 | 修复后 |
| --- | ---: | ---: |
| 被判定为密钥的条目 | 181 | 108 |
| 唯一变量名 | **48** | 29 |

多出来那 19 个变量名，全是**误判**。它们的名字里含有 `AUTHENTICATION` 或 `AUTHORIZATION` —— 因为 `AUTH` 是它们的前缀，但含义完全不同：

| 变量名 | 真实含义 | 被误判后果 |
| --- | --- | --- |
| `WEAVIATE_AUTHENTICATION_APIKEY_ENABLED` | 开关，值是 `true` | 报告显示 `***REDACTED***` |
| `WEAVIATE_AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED` | 开关，值是 `true` | 同上 |
| `AUTHORIZATION_ADMINLIST_ENABLED` | 开关 | 同上 |
| `WEAVIATE_ENABLE_TOKENIZER_GSE` | 开关，值是 `false` | 同上 |

被涂掉的这些值本来是无害的 `true` / `false`，但它们是**配置意图**：读者一眼就能看出「这个服务开了匿名访问」「那个服务关掉了分词」。涂成 `***REDACTED***` 之后，报告就变成了一堆黑块，什么也读不出来。

修法有两处。一是给 `AUTH` 加负向断言，把三个以它开头但不是凭据的词排掉：

```python
# AUTH 后面如果跟着 ENTICATION / ORIZATION / ORS，就不是凭据
AUTH(?!ENTICATION|ORIZATION|ORS)
```

二是加一份开关白名单 —— 名字里带 TOKEN/SECRET 但其实是开关或数值的：

```python
_NOT_SECRET_NAME = re.compile(
    r"(ENABLE|DISABLE|TOKENIZ|TOKEN_LIMIT|MAX_TOKENS?|_TOKENS?_|"
    r"ALLOW_PRIVATE|ALLOW_ANONYMOUS|AUTH_VERSION|_ENABLED$|_ENABLED_)",
    re.I,
)

def is_secret_pair(name: str, value: str = "") -> bool:
    if _NOT_SECRET_NAME.search(name):
        # 开关类名字直接放行，但值里内嵌凭据的仍然要打码
        return value_looks_secret(value)
    if SECRET_HINTS.search(name) or BARE_CRED_NAME.search(name):
        return True
    return value_looks_secret(value)
```

`TOKENIZATION`、`MAX_TOKENS`、`ENABLE_TOKENIZER_GSE` 都靠这份白名单放行。

::: warning 白名单那行有个细节别省
`_NOT_SECRET_NAME` 命中之后，我没有直接 `return False`，而是 `return value_looks_secret(value)`。

因为名字是开关、值里却塞口令这种事是存在的（上面那个 `CELERY_BROKER_URL` 就是活例子）。**白名单只该放过名字，不该放过值。**
:::

修完之后，四条判据合起来是这样分工的：

| 判据 | 抓什么 | 例子 |
| --- | --- | --- |
| 变量名含密钥词 | 最常见的一类 | `DB_PASSWORD`、`WEAVIATE_API_KEY` |
| 变量名是裸凭据名 | 名字里只有 AUTH/PWD | `REDISCLI_AUTH` |
| **值内嵌凭据** | 名字无害、值藏口令 | `CELERY_BROKER_URL` |
| 开关白名单 | 反向排除，防误判 | `WEAVIATE_ENABLE_TOKENIZER_GSE` |

## 修完之后

两条路径终于给出一致的答案。而且这个一致是**有内容的**——它的每一项都经过了对账：

| 指标 | 两条路径的结果 | 和手工核对 |
| --- | --- | --- |
| 已启用服务 | 13 | 对得上 |
| 宿主机挂载 | 18 | 对得上 |
| 不可重建 | 5 | 对得上 |
| 不可重建体积 | 915.2 MB | 四个目录单独量过，加起来正好 |

最后一行是这么对上的：`287.9 + 265.1 + 236.2 + 126.0 = 915.2 MB`。

## 事先的判断 vs 实际是什么

| 环节 | 我一开始的判断 | 实际是什么 |
| --- | --- | --- |
| 为什么要两条路径 | 怕 docker 不可用，做个兜底 | 兜底只是顺带，**互为对照组才是真价值** |
| 两条路径为什么会不一致 | 内置扫描器写得糙 | 是**两个独立的 bug**各坏一处 |
| 少了 265 MB 怪谁 | YAML 锚点没解析 | 锚点坏的是 `env_file`；**丢体积的是 profile 没插值** |
| 密钥判据难在哪 | 怕漏判，会把口令写进报告 | 漏判和误判**两头都难**，误判把报告变成黑块 |
| key 名字带 AUTH 就是密钥 | 是 | 不是。`AUTHENTICATION` / `AUTHORIZATION` 是开关 |
| 修完就能发布了吗 | 自检绿了就行 | 自检绿只说明**我想到的用例**过了 |

最后一行是这轮最实在的一条。37 项自检全绿之后，我还是靠两条路径对账才抓出那 26 个丢失的 `env_file` 引用——因为**自检里的用例都是我写的，我想不到的情况，它也测不到。**

## 三件事

1. **同一个东西用两条独立实现各算一遍，是最便宜的验错手段。**它不需要你预先知道正确答案，只需要你有个机制能发现"两个答案不一样"。这次五个 bug 里有三个是靠它暴露的。

2. **漏报比算错危险。**算错会崩、会报错、会有人发现；漏报只会安静地少一行。凡是"先筛掉一批再统计"的逻辑，都要单独问一句：被筛掉的那批，凭什么被筛掉。

3. **判据的两侧都要试。**密钥识别的判据，一侧是漏判（口令进了报告），另一侧是误判（报告全是黑块）。**只朝一个方向调，会一路调到另一个极端**——我加上 `AUTH` 之后，被误判的变量名从 0 涨到 19 个。

::: details 如果只想记三件事
1. 有条件就做两条独立取数路径，让它们互相核对。
2. `COMPOSE_PROFILES=${VAR:-default},...` 这种写法，**必须先展开变量再拆**，否则服务会被误判为未启用。
3. 判密钥不能只看变量名——`CELERY_BROKER_URL` 这种名字无害、值里藏口令的要按值判。
:::
