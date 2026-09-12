<script setup>
// 文章底部的"发布于 / 最后更新 / 修改记录"。
// 数据来自 frontmatter 的 updates（按时间倒序写，最新一条在最前），
// 没写就只显示发布日期，不会报错。
import { useData } from 'vitepress'
import { computed } from 'vue'
import { data as posts } from '../../posts.data.mjs'

const { page } = useData()

const post = computed(() => {
  const rp = page.value.relativePath || ''
  if (!rp.startsWith('posts/')) return null
  const key = '/' + rp.replace(/\.md$/, '')
  return posts.find((p) => p.url === key || p.url === key + '.html') || null
})

const updates = computed(() => (post.value && post.value.updates) || [])
const updated = computed(() => (post.value && post.value.updated) || '')
</script>

<template>
  <div v-if="post" class="post-meta">
    <div class="post-meta-line">
      <span>发布于 {{ post.date }}</span>
      <template v-if="updated && updated !== post.date">
        <span class="post-meta-dot">·</span>
        <span>最后更新 {{ updated }}</span>
      </template>
      <template v-if="updates.length > 1">
        <span class="post-meta-dot">·</span>
        <span>改过 {{ updates.length }} 次</span>
      </template>
    </div>

    <details v-if="updates.length > 1" class="post-meta-log">
      <summary>看修改记录</summary>
      <ul>
        <li v-for="(u, i) in updates" :key="i">
          <span v-if="u.date" class="post-meta-date">{{ u.date }}</span>
          <span>{{ u.text }}</span>
        </li>
      </ul>
    </details>
  </div>
</template>
