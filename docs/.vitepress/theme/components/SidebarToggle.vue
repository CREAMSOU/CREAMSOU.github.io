<script setup>
import { onMounted, ref } from 'vue'

const collapsed = ref(false)

function toggle() {
  collapsed.value = !collapsed.value
  document.documentElement.classList.toggle('sb-hide', collapsed.value)
  try { localStorage.setItem('sb-hide', collapsed.value ? '1' : '0') } catch (e) {}
}

onMounted(() => {
  try { collapsed.value = localStorage.getItem('sb-hide') === '1' } catch (e) { return }
  if (collapsed.value) document.documentElement.classList.add('sb-hide')
})
</script>

<template>
  <button
    class="sb-toggle"
    :class="{ collapsed }"
    aria-label="收起/展开目录"
    title="收起/展开目录"
    @click="toggle"
  >
    <span class="sb-arrow" />
  </button>
</template>
