<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

// 这个页面长在线上博客里，但真正干活的服务在本机 127.0.0.1:8891。
// 打开页面先探测一次：能连上就把控制台嵌进来，连不上就给出启动步骤并自动重试。
const STATE = ref('checking')   // checking | on | off
const frameKey = ref(0)
const file = ref('')
let timer = null
let tries = 0

const LOCAL = 'http://127.0.0.1:8891/'

const localUrl = computed(() =>
  file.value ? LOCAL + '?file=' + encodeURIComponent(file.value) : LOCAL)

const stateText = computed(() => ({
  checking: '正在连接本机控制台…',
  on: '已连接本机控制台 · 数据不出这台电脑',
  off: '没检测到本机控制台'
}[STATE.value]))

async function ping() {
  const ctl = new AbortController()
  const t = setTimeout(() => ctl.abort(), 1500)
  try {
    const r = await fetch(LOCAL + 'api/ping', { signal: ctl.signal, cache: 'no-store' })
    if (!r.ok) return false
    const d = await r.json()
    return d && d.app === 'blog-editor'
  } catch {
    return false
  } finally {
    clearTimeout(t)
  }
}

async function check() {
  if (STATE.value !== 'on') STATE.value = 'checking'
  const ok = await ping()
  STATE.value = ok ? 'on' : 'off'
  if (ok) {
    clearInterval(timer)
    timer = null
    frameKey.value++
  } else if (!timer) {
    // 打开页面后再去启动控制台，这里会自动接上，不用手动刷新
    tries = 0
    timer = setInterval(async () => {
      tries++
      if (await ping()) {
        clearInterval(timer)
        timer = null
        STATE.value = 'on'
        frameKey.value++
      } else if (tries >= 30) {
        clearInterval(timer)
        timer = null
      }
    }, 2000)
  }
}

onMounted(() => {
  file.value = new URLSearchParams(location.search).get('file') || ''
  check()
})
onBeforeUnmount(() => { if (timer) clearInterval(timer) })
</script>

<template>
  <div class="ce">
    <div class="ce-bar">
      <span class="ce-dot" :class="STATE"></span>
      <span class="ce-txt">{{ stateText }}</span>
      <span class="ce-grow"></span>
      <a class="ce-btn" :href="localUrl" target="_blank" rel="noreferrer">新窗口打开 ↗</a>
      <button class="ce-btn" @click="check">重新检测</button>
    </div>

    <iframe
      v-if="STATE === 'on'"
      :key="frameKey"
      class="ce-frame"
      :src="localUrl"
      title="博客控制台"
    ></iframe>

    <div v-else class="ce-off">
      <h2>{{ STATE === 'checking' ? '正在连接…' : '没连上本机控制台' }}</h2>
      <p v-if="STATE === 'off'">
        控制台只在这台电脑上跑。线上站点是静态页，自己连不上本机服务，得先把它启动起来。
      </p>
      <ol v-if="STATE === 'off'">
        <li>打开 <code>blog\editor</code> 文件夹</li>
        <li>双击 <code>editor.bat</code>，第一次会让你设一个密码</li>
        <li>回到这个页面——两秒内会自动接上，不用刷新</li>
      </ol>
      <p v-if="STATE === 'off'" class="ce-note">
        已经启动过还是连不上？多半是浏览器把网页请求本机的通道拦了。点下面按钮在新窗口打开，一定能进。
        这个页面只探测 <code>127.0.0.1:8891</code> 的通断，不会把文章或密码发到任何地方。
      </p>
      <div class="ce-actions">
        <a class="ce-btn ce-primary" :href="localUrl" target="_blank" rel="noreferrer">
          在新窗口打开控制台 ↗
        </a>
        <button class="ce-btn" @click="check">重新检测</button>
      </div>
    </div>
  </div>
</template>
