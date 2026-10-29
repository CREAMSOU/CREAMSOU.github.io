<script setup>
import { onMounted, ref } from 'vue'
import { withBase } from 'vitepress'

defineProps({ mobile: { type: Boolean, default: false } })

// 只在探测到本机控制台时才出现。别人打开这个站点看不到这个入口。
const alive = ref(false)

onMounted(() => {
  const ctl = new AbortController()
  const timer = setTimeout(() => ctl.abort(), 1200)
  fetch('http://127.0.0.1:8891/api/ping', { signal: ctl.signal, cache: 'no-store' })
    .then((r) => (r.ok ? r.json() : null))
    .then((d) => { if (d && d.app === 'blog-editor') alive.value = true })
    .catch(() => { /* 没跑控制台：保持隐藏 */ })
    .finally(() => clearTimeout(timer))
})
</script>

<template>
  <a
    v-if="alive"
    class="console-nav"
    :class="{ 'console-nav-mobile': mobile }"
    :href="withBase('/console')"
    title="本机控制台已连接，点开直接改文章"
  >
    <span class="console-dot"></span>控制台
  </a>
</template>
