<script setup>
import { onMounted, ref } from 'vue'
import { withBase } from 'vitepress'

defineProps({ mobile: { type: Boolean, default: false } })

// 入口常驻：点进去是 /console，那一页负责"连上了就嵌编辑器，没连上就给启动步骤"。
// 圆点只表示本机控制台此刻是否在跑（绿=在跑，灰=没跑），不影响能不能点。
const alive = ref(false)

onMounted(() => {
  const ctl = new AbortController()
  const timer = setTimeout(() => ctl.abort(), 1200)
  fetch('http://127.0.0.1:8891/api/ping', { signal: ctl.signal, cache: 'no-store' })
    .then((r) => (r.ok ? r.json() : null))
    .then((d) => { if (d && d.app === 'blog-editor') alive.value = true })
    .catch(() => { /* 没跑控制台：圆点保持灰色，入口照旧可点 */ })
    .finally(() => clearTimeout(timer))
})
</script>

<template>
  <a
    class="console-nav"
    :class="{ 'console-nav-mobile': mobile }"
    :href="withBase('/console')"
    :title="alive
      ? '本机控制台在运行，点开直接改文章'
      : '本机控制台没在运行，点开看怎么启动'"
  >
    <span class="console-dot" :class="{ off: !alive }"></span>控制台
  </a>
</template>
