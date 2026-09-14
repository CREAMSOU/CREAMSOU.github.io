import { defineConfig } from 'vitepress'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

// 小类默认是否收起：true = 点一下才展开；false = 跟着大类一起展开
const SUB_GROUP_COLLAPSED = false

type Post = { title: string; date: string; link: string }
type Group = { posts: Post[]; children: Map<string, Group> }

// 扫描 posts/ 自动生成左侧目录。分类写在每篇文章的 frontmatter 里：
//   category: 大类          → 一级分组
//   category: 大类/小类      → 两级分组
// 不写 category 的文章进「未分类」。发文零维护，push 上去目录自己长。
function postsSidebar() {
  const dir = join(process.cwd(), 'docs', 'posts')
  const root: Group = { posts: [], children: new Map() }

  for (const f of readdirSync(dir)) {
    if (!f.endsWith('.md')) continue
    const fm = (readFileSync(join(dir, f), 'utf-8').match(
      /^---\s*\n([\s\S]*?)\n---/) || ['', ''])[1]
    const pick = (k: string) =>
      ((fm.match(new RegExp('^' + k + ':\\s*(.+)$', 'm')) || [])[1] || '').trim()
    const title = pick('title') || f.replace(/\.md$/, '')
    const date = pick('date')
    const raw = pick('category').replace(/^["']|["']$/g, '')
    const cats = raw.split('/').map((s) => s.trim()).filter(Boolean)

    let node = root
    for (const name of (cats.length ? cats : ['未分类'])) {
      if (!node.children.has(name)) node.children.set(name, { posts: [], children: new Map() })
      node = node.children.get(name) as Group
    }
    node.posts.push({ title, date, link: '/posts/' + f.replace(/\.md$/, '') })
  }

  // 分组按「组内最新一篇的日期」倒序排，活跃的排前面
  const latest = (g: Group): string =>
    [...g.posts.map((p) => p.date), ...[...g.children.values()].map(latest)]
      .filter(Boolean).sort().pop() || ''

  const build = (g: Group, depth: number): any[] => {
    const out: any[] = [...g.children.entries()]
      .sort((a, b) => latest(b[1]).localeCompare(latest(a[1])))
      .map(([name, child]) => ({
        text: name,
        collapsed: depth > 0 && SUB_GROUP_COLLAPSED,
        items: build(child, depth + 1)
      }))
    for (const p of [...g.posts].sort((a, b) => b.date.localeCompare(a.date))) {
      out.push({ text: p.title, link: p.link })
    }
    return out
  }

  return build(root, 0)
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
    sidebar: postsSidebar(),
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
