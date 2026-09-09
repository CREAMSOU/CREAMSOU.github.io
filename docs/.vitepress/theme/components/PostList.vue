<script setup>
import { data as posts } from '../../posts.data.mjs'

const sorted = [...posts].sort((a, b) => {
  if (a.top !== b.top) return a.top ? -1 : 1
  return (b.date || '').localeCompare(a.date || '')
})

function formatDate(d) {
  if (!d) return ''
  return d.replace(/T.*$/, '')
}
</script>

<template>
  <div class="post-section">
    <a v-for="p in sorted" :key="p.url" :href="p.url" class="post-card">
      <div class="post-card-head">
        <span class="post-card-title">
          {{ p.title }}
          <span v-if="p.top" class="post-pin">置顶</span>
        </span>
      </div>
      <div class="post-card-meta">
        <span>发表于 {{ formatDate(p.date) }}</span>
      </div>
      <p v-if="p.description" class="post-card-desc">{{ p.description }}</p>
      <span class="post-card-more">阅读全文 »</span>
    </a>
    <p v-if="!sorted.length" class="post-card-desc">还没有文章，去 posts/ 目录写第一篇吧。</p>
  </div>
</template>
