<script setup>
import { useData, withBase } from 'vitepress'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { entryOn, onEntryChange } from '../consoleEntry.mjs'

const { page, frontmatter } = useData()

// 文章页右下角：一键进控制台并定位到这一篇。
// 和导航栏入口同一个开关——只有在 /console 页开过入口的那台浏览器上才显示。
const show = ref(false)
let off = null
onMounted(() => {
  show.value = entryOn()
  off = onEntryChange(() => { show.value = entryOn() })
})
onBeforeUnmount(() => { if (off) off() })

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
    v-if="show && !isHome"
    class="edit-in-editor"
    :href="consoleUrl"
    title="在博客控制台里改这一篇（本机程序，需先启动）"
  >✏ 编辑此页</a>
</template>
