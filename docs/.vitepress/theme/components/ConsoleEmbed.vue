<script setup>
import { computed, onMounted, ref } from 'vue'
import { entryOn, setEntry } from '../consoleEntry.mjs'

// 这个页面长在线上博客里，真正干活的服务在本机 127.0.0.1:8891。
// 新版 Chrome 默认不允许网页直接访问本机服务（Local Network Access），
// 所以这里不自动探测：默认给「新窗口打开」，用户点一下才尝试嵌进本页。
const LOCAL = 'http://127.0.0.1:8891/'
const STATE = ref('idle')   // idle | checking | on | off
const frameKey = ref(0)
const file = ref('')
const entry = ref(false)
const COPIED = ref('')

const localUrl = computed(() =>
  file.value ? LOCAL + '?file=' + encodeURIComponent(file.value) : LOCAL)

const stateText = computed(() => ({
  idle: '控制台是在这台电脑上单独跑的程序',
  checking: '正在连接…',
  on: '已连上本机控制台 · 数据不出这台电脑',
  off: '浏览器没放行这次访问，用新窗口打开'
}[STATE.value]))

// 书签小工具：在任何一篇博客上点一下，直接打开控制台里那一篇。
const editBookmarklet = computed(() => {
  const js = "javascript:(function(){var m=location.pathname.match(/\\/posts\\/(.+)\\.html$/);" +
    "var f=m?decodeURIComponent(m[1])+'.md':'';" +
    "window.open('" + LOCAL + "'+(f?'?file='+encodeURIComponent(f):''),'_blank')})()"
  return js
})

async function embed() {
  STATE.value = 'checking'
  const ctl = new AbortController()
  const t = setTimeout(() => ctl.abort(), 2500)
  try {
    const r = await fetch(LOCAL + 'api/ping', { signal: ctl.signal, cache: 'no-store' })
    const d = r.ok ? await r.json() : null
    if (d && d.app === 'blog-editor') {
      STATE.value = 'on'
      frameKey.value++
      // 能连上本机控制台，基本可以确定就是本人：顺手把这台电脑的入口打开
      setEntry(true)
      entry.value = true
    } else {
      STATE.value = 'off'
    }
  } catch {
    STATE.value = 'off'
  } finally {
    clearTimeout(t)
  }
}

function toggleEntry() {
  entry.value = !entry.value
  setEntry(entry.value)
}

async function copy(text, tag) {
  try {
    await navigator.clipboard.writeText(text)
    COPIED.value = tag
    setTimeout(() => { if (COPIED.value === tag) COPIED.value = '' }, 1800)
  } catch {
    COPIED.value = ''
  }
}

// SSR 阶段没有 location，先给个占位，挂载后再换成真实域名
const origin = ref('https://creamsou.github.io')
const secretUrl = computed(() => origin.value + '/#console-on')

onMounted(() => {
  origin.value = location.origin
  const q = new URLSearchParams(location.search)
  file.value = q.get('file') || ''
  const nav = q.get('nav')
  if (nav === '1') setEntry(true)
  if (nav === '0') setEntry(false)
  entry.value = entryOn()
})
</script>

<template>
  <div class="ce">
    <div class="ce-bar">
      <span class="ce-dot" :class="STATE"></span>
      <span class="ce-txt">{{ stateText }}</span>
      <span class="ce-grow"></span>
      <button v-if="STATE !== 'on'" class="ce-btn" @click="embed">在本页嵌入</button>
      <a class="ce-btn" :href="localUrl" target="_blank" rel="noreferrer">新窗口打开 ↗</a>
    </div>

    <iframe
      v-if="STATE === 'on'"
      :key="frameKey"
      class="ce-frame"
      :src="localUrl"
      title="博客控制台"
    ></iframe>

    <div v-else class="ce-off">
      <h2>控制台跑在本机，线上博客启不动它</h2>
      <p>
        博客只是个静态页面。要改文章，得让这台电脑上的控制台程序跑起来，然后从本机打开它。
      </p>
      <ol>
        <li>打开 <code>blog\editor</code> 文件夹，双击 <code>editor.bat</code>（第一次会让你设密码）</li>
        <li>控制台会自己弹出一个浏览器标签页，那就是编辑界面</li>
        <li>想让它嵌回这个页面，点右上角「在本页嵌入」</li>
      </ol>
      <p class="ce-note">
        新版 Chrome 默认不许网页访问本机服务，会弹「本地网络访问」授权，点允许才能嵌。
        不授权也没关系——新窗口打开一样用，只是少一个页面框。
      </p>
      <div class="ce-actions">
        <a class="ce-btn ce-primary" :href="localUrl" target="_blank" rel="noreferrer">
          打开控制台 ↗
        </a>
        <button class="ce-btn" @click="embed">在本页嵌入</button>
      </div>

      <div class="ce-entry">
        <div class="ce-entry-row">
          <span class="ce-entry-txt">
            {{ entry
              ? '这台浏览器上显示「控制台」入口（别人的浏览器里不存在）'
              : '这台浏览器上不显示入口，别人自然也看不见' }}
          </span>
          <button class="ce-btn" @click="toggleEntry">
            {{ entry ? '关掉入口' : '开启入口' }}
          </button>
        </div>

        <p class="ce-hint">
          入口只记在本机浏览器里，不上传。下面两样东西比入口更好用，也永远不会出现在页面上：
        </p>

        <div class="ce-bm">
          <span class="ce-bm-label">① 拖到书签栏</span>
          <a class="ce-bm-link" :href="localUrl">控制台</a>
          <a class="ce-bm-link" :href="editBookmarklet" @click.prevent>编辑这页</a>
          <button class="ce-btn ce-btn-sm" @click="copy(editBookmarklet, 'bm')">
            {{ COPIED === 'bm' ? '已复制' : '复制书签代码' }}
          </button>
        </div>
        <p class="ce-hint">
          拖上去以后，在任何页面点「编辑这页」，就直接打开控制台并定位到当前这一篇。
          别人没有你的书签栏，也就没有任何入口。
        </p>

        <div class="ce-bm">
          <span class="ce-bm-label">② 密钥链接</span>
          <code class="ce-secret">{{ secretUrl }}</code>
          <button class="ce-btn ce-btn-sm" @click="copy(secretUrl, 'key')">
            {{ COPIED === 'key' ? '已复制' : '复制' }}
          </button>
        </div>
        <p class="ce-hint">
          换电脑、换手机、清了缓存时用这个链接打开一次，入口就回到导航栏。
          <code>#</code> 后面这段浏览器不会发给服务器，也不进 GitHub 的访问日志。
          想关掉入口就用 <code>#console-off</code>。
        </p>
      </div>
    </div>
  </div>
</template>
