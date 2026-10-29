<script setup>
import { useData, withBase } from 'vitepress'
import { computed } from 'vue'

const { page, frontmatter } = useData()

// 文章页右下角：一键进控制台并定位到这一篇。
// 不做本机探测——新版 Chrome 会拦掉网页访问本机服务的请求，探了也是白探，还会在控制台刷一堆报错。
// 控制台本身在 /console 页说明怎么启动。
const isHome = computed(() =>
  (page.value.relativePath || '') === 'index.md' || frontmatter.value.layout === 'home')

const consoleUrl = computed(() => {
  const rp = page.value.relativePath || page.value.filePath || ''
  const name = rp.split('/').pop() || ''
  return withBase('/console') +
    (name.endsWith('.md') ? '?file=' + encodeURIComponent(name) : '')
})
</script>

<template>
  <a
    v-if="!isHome"
    class="edit-in-editor"
    :href="consoleUrl"
    title="在博客控制台里改这一篇（本机程序，需先启动）"
  >✏ 编辑此页</a>
</template>
