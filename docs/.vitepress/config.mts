import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: 'cream的学习记录',
  description: '做点东西，写点想法。项目复盘与学习笔记。',
  cleanDist: false,
  vite: {
    build: {
      emptyOutDir: false
    }
  },
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '关于', link: '/about' }
    ],
    outline: [2, 3],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/CREAMSOU' }
    ],
    footer: {
      message: '用 VitePress 搭的，托管在 GitHub Pages',
      copyright: '内容随便转载，注明出处就行'
    },
    docFooter: {
      prev: '上一篇',
      next: '下一篇'
    },
    lastUpdated: {
      text: '最后更新',
      formatOptions: {
        dateStyle: 'medium',
        timeStyle: 'short'
      }
    }
  },
  lastUpdated: true
})
