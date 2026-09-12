import { defineConfig } from 'vitepress'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

// 自动扫描 posts/ 生成左侧目录：发文零维护，写完 push 目录自己长
function postsSidebar() {
  const dir = join(process.cwd(), 'docs', 'posts')
  const items = []
  for (const f of readdirSync(dir)) {
    if (!f.endsWith('.md')) continue
    const fm = (readFileSync(join(dir, f), 'utf-8').match(
      /^---\s*\n([\s\S]*?)\n---/) || ['', ''])[1]
    const title = ((fm.match(/^title:\s*(.+)$/m) || [])[1] || f.replace(/\.md$/, '')).trim()
    const date = ((fm.match(/^date:\s*(.+)$/m) || [])[1] || '').trim()
    items.push({ title, date, link: '/posts/' + f.replace(/\.md$/, '') })
  }
  items.sort((a, b) => b.date.localeCompare(a.date))
  return items.map(({ title, link }) => ({ text: title, link }))
}

export default defineConfig({
  lang: 'zh-CN',
  title: 'cream的学习记录',
  description: '做点东西，写点想法。项目复盘与学习笔记。',
  cleanDist: false,
  appearance: true,
  markdown: {
    // 提示块的默认标题改中文
    container: {
      tipLabel: '提示',
      warningLabel: '注意',
      dangerLabel: '危险',
      infoLabel: '说明',
      detailsLabel: '展开看细节'
    },
    image: {
      lazyLoading: true
    }
  },
  vite: {
    build: {
      emptyOutDir: false
    }
  },
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '归档', link: '/archive' },
      { text: '关于', link: '/about' }
    ],
    sidebar: [
      {
        text: '全部文章',
        items: postsSidebar()
      }
    ],
    outline: [2, 3],
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索文章', buttonAriaLabel: '搜索文章' },
          modal: {
            noResultsText: '没有找到相关内容',
            resetButtonTitle: '清空关键词',
            footer: { selectText: '打开', navigateText: '切换', closeText: '关闭' }
          }
        }
      }
    },
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
