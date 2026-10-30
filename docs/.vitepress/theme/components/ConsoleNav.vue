<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'
import { entryOn, onEntryChange } from '../consoleEntry.mjs'

defineProps({ mobile: { type: Boolean, default: false } })

// 默认不渲染：别人的浏览器里没有这个开关，HTML 里也就没有「控制台」三个字。
// 只有在 /console 页开过入口的那台浏览器上，这里才会把链接显示出来。
const show = ref(false)
let off = null

onMounted(() => {
  show.value = entryOn()
  off = onEntryChange(() => { show.value = entryOn() })
})
onBeforeUnmount(() => { if (off) off() })
</script>

<template>
  <a
    v-if="show"
    class="console-nav"
    :class="{ 'console-nav-mobile': mobile }"
    :href="withBase('/console')"
    title="打开博客控制台（本机程序，需先启动）"
  >控制台</a>
</template>
