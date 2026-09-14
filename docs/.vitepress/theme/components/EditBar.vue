<script setup>
import { useData } from 'vitepress'
import { computed, onMounted, ref } from 'vue'

const { page, frontmatter } = useData()

// 本地开发模式：直接显示。
// 线上：探测本机 127.0.0.1:8891 上的编辑器，探测到才显示——别人打开这个页面是看不到的。
const alive = ref(import.meta.env.DEV)

const isHome = computed(() => frontmatter.value.layout === 'home')

const editorUrl = computed(() => {
  const rp = page.value.relativePath || page.value.filePath || ''
  const name = rp.split('/').pop() || ''
  return 'http://127.0.0.1:8891/' +
    (name.endsWith('.md') ? '?file=' + encodeURIComponent(name) : '')
})

onMounted(() => {
  if (alive.value) return
  // http://127.0.0.1 属于浏览器认可的"可信来源"，HTTPS 页面也能请求它，不会被 Mixed Content 拦住。
  // 编辑器那边在 /api/ping 上带了 CORS 与私网访问头。
  const ctl = new AbortController()
  const timer = setTimeout(() => ctl.abort(), 1200)
  fetch('http://127.0.0.1:8891/api/ping', { signal: ctl.signal, cache: 'no-store' })
    .then((r) => (r.ok ? r.json() : null))
    .then((d) => { if (d && d.app === 'blog-editor') alive.value = true })
    .catch(() => { /* 编辑器没运行：保持隐藏 */ })
    .finally(() => clearTimeout(timer))
})
</script>

<template>
  <a
    v-if="alive"
    class="edit-in-editor"
    :href="editorUrl"
    target="_blank"
    title="检测到本机正在运行博客编辑器"
  >
    {{ isHome ? '✏ 打开编辑器' : '✏ 编辑此页' }}
  </a>
</template>
