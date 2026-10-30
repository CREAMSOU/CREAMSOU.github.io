// 「控制台」入口在不在页面上，由这台浏览器自己的 localStorage 决定。
// 别人的浏览器里压根没有这个键 → 导航栏和文章页都不会出现控制台入口。
// 注意：这不是账号鉴权，只是「你看得见 / 别人看不见」；真正拦住人的是控制台自己的密码。

const KEY = 'blog-console-entry'
const EVT = 'blog-console-entry-change'

// localStorage 不可用（隐私模式等）时的兜底，只在本次页面生命周期内有效
let fallback = false

export function entryOn() {
  try {
    return localStorage.getItem(KEY) === '1'
  } catch {
    return fallback
  }
}

export function setEntry(on) {
  fallback = !!on
  try {
    if (on) localStorage.setItem(KEY, '1')
    else localStorage.removeItem(KEY)
  } catch {
    /* 存不进去就只在本页生效 */
  }
  window.dispatchEvent(new Event(EVT))
}

export function onEntryChange(fn) {
  window.addEventListener(EVT, fn)
  return () => window.removeEventListener(EVT, fn)
}

// 密钥链接：https://creamsou.github.io/#console-on
// # 后面的内容浏览器根本不会发给服务器，也不进 Referer、不进 GitHub 访问日志，
// 所以「谁用过这个链接」在服务端查不到。打开后立刻把 # 抹掉，地址栏不留痕。
function readHashKey() {
  const h = (window.location.hash || '').replace(/^#/, '')
  if (h !== 'console-on' && h !== 'console-off') return
  setEntry(h === 'console-on')
  history.replaceState(null, '', window.location.pathname + window.location.search)
}

if (typeof window !== 'undefined') {
  try {
    readHashKey()
  } catch {
    /* 忽略 */
  }
}
