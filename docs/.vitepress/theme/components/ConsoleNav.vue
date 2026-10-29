<script setup>
import { withBase } from 'vitepress'

defineProps({ mobile: { type: Boolean, default: false } })

// 常驻入口：不探测、不猜，点进去由 /console 页讲清楚怎么连。
// 原因：新版 Chrome 默认不允许网页直接访问本机服务（Local Network Access），
// 页面里自动探测在多数环境必定失败，入口就会时隐时现。
</script>

<template>
  <a
    class="console-nav"
    :class="{ 'console-nav-mobile': mobile }"
    :href="withBase('/console')"
    title="打开博客控制台（本机程序，需先启动）"
  >控制台</a>
</template>
