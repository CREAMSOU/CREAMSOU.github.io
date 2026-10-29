<script setup>
import { computed, onMounted, ref } from 'vue'

// 这个页面长在线上博客里，真正干活的服务在本机 127.0.0.1:8891。
// 新版 Chrome 默认不允许网页直接访问本机服务（Local Network Access），
// 所以这里不自动探测：默认给「新窗口打开」，用户点一下才尝试嵌进本页。
const LOCAL = 'http://127.0.0.1:8891/'
const STATE = ref('idle')   // idle | checking | on | off
const frameKey = ref(0)
const file = ref('')

const localUrl = computed(() =>
  file.value ? LOCAL + '?file=' + encodeURIComponent(file.value) : LOCAL)

const stateText = computed(() => ({
  idle: '控制台是在这台电脑上单独跑的程序',
  checking: '正在连接…',
  on: '已连上本机控制台 · 数据不出这台电脑',
  off: '浏览器没放行这次访问，用新窗口打开'
}[STATE.value]))

async function embed() {
  STATE.value = 'checking'
  const ctl = new AbortController()
  const t = setTimeout(() => ctl.abort(), 2500)
  try {
    const r = await fetch(LOCAL + 'api/ping', { signal: ctl.signal, cache: 'no-store' })
    const d = r.ok ? await r.json() : null
    if (d && d.app === 'blog-editor') { STATE.value = 'on'; frameKey.value++ }
    else STATE.value = 'off'
  } catch {
    STATE.value = 'off'
  } finally {
    clearTimeout(t)
  }
}

onMounted(() => {
  file.value = new URLSearchParams(location.search).get('file') || ''
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
    </div>
  </div>
</template>
