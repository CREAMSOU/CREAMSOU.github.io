<script setup>
import { data as posts } from '../../posts.data.mjs'

// 按月分组，倒序
const groups = (() => {
  const map = {}
  for (const p of [...posts].sort((a, b) => (b.date || '').localeCompare(a.date || ''))) {
    const month = (p.date || '').slice(0, 7) || '未知日期'
    ;(map[month] = map[month] || []).push(p)
  }
  return Object.entries(map).sort((a, b) => b[0].localeCompare(a[0]))
})()

function day(d) {
  return (d || '').slice(8, 10)
}
</script>

<template>
  <div class="archive">
    <h1 class="archive-title">归档</h1>
    <p class="archive-total">共 {{ posts.length }} 篇，写完一篇这里就多一行</p>
    <section v-for="[month, list] in groups" :key="month" class="archive-month">
      <h2>{{ month }}</h2>
      <a v-for="p in list" :key="p.url" :href="p.url" class="archive-item">
        <span class="archive-day">{{ day(p.date) }} 日</span>
        <span class="archive-name">{{ p.title }}
          <span v-if="p.top" class="post-pin">置顶</span>
        </span>
      </a>
    </section>
    <p v-if="!posts.length" class="archive-total">还没有文章。</p>
  </div>
</template>
