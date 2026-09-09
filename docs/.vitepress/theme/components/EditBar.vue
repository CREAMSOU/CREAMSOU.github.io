<script setup>
import { useData } from 'vitepress'
import { computed } from 'vue'

const { page, frontmatter } = useData()

// 只在本地开发模式且非首页时显示；线上访客看不到
const show = import.meta.env.DEV && frontmatter.value.layout !== 'home'

const editorUrl = computed(() => {
  const rp = page.value.relativePath || page.value.filePath || ''
  const name = rp.split('/').pop()
  return 'http://127.0.0.1:8891/?file=' + encodeURIComponent(name)
})
</script>

<template>
  <a v-if="show" class="edit-in-editor" :href="editorUrl" target="_blank">
    ✏ 编辑此页
  </a>
</template>
