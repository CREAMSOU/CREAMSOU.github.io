<script setup>
// 文章开头的"速览"卡片：给赶时间的人一眼看完要点
defineProps({
  title: { type: String, default: '速览' },
  points: { type: Array, default: () => [] }
})
</script>

<template>
  <div class="lead-card">
    <div class="lead-label">{{ title }}</div>
    <ul class="lead-list">
      <li v-for="(p, i) in points" :key="i">{{ p }}</li>
    </ul>
  </div>
</template>
