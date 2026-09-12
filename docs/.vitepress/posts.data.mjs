import { createContentLoader } from 'vitepress'

// frontmatter 里的 date 若未加引号，YAML 会解析成 Date 对象，
// 统一转成 YYYY-MM-DD 字符串，避免排序/显示出问题（Date 没有 localeCompare）
function toDateStr(v) {
  if (!v) return ''
  if (v instanceof Date) {
    const m = String(v.getMonth() + 1).padStart(2, '0')
    const d = String(v.getDate()).padStart(2, '0')
    return `${v.getFullYear()}-${m}-${d}`
  }
  return String(v)
}

export default createContentLoader('posts/*.md', {
  excerpt: true,
  transform(raw) {
    return raw
      .map((item) => ({
        url: item.url,
        title: String(item.frontmatter.title || ''),
        date: toDateStr(item.frontmatter.date),
        description: String(item.frontmatter.description || ''),
        top: item.frontmatter.top === true
      }))
      .sort((a, b) => {
        if (a.top !== b.top) return a.top ? -1 : 1
        return b.date.localeCompare(a.date)
      })
  }
})

