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

// 估阅读时长：中文按 400 字/分钟，英文按 250 词/分钟
// 用原始 Markdown（src）算，因为 loader 返回的 html 字段在本版本里拿不到；
// 先扣掉 frontmatter、代码块、图片和链接的噪声
function toMinutes(src) {
  if (!src) return 0
  const text = String(src)
    .replace(/^---[\s\S]*?\n---/, ' ')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`[^`]*`/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/<[^>]+>/g, ' ')
    .replace(/:::+/g, ' ')
    .replace(/[|>#*\-_=~]/g, ' ')
  const cjk = (text.match(/[\u4e00-\u9fff]/g) || []).length
  const words = (text.replace(/[\u4e00-\u9fff]/g, ' ').match(/[A-Za-z0-9_][A-Za-z0-9_.\-]*/g) || []).length
  return Math.max(1, Math.round(cjk / 400 + words / 250))
}

// 修改记录：frontmatter 的 updates 是字符串数组，按时间倒序写（最新的放第一条），
// 例如 "2026-09-12 补上发布链路的配图"。这里统一成 {date, text} 结构。
function toUpdates(v) {
  if (!Array.isArray(v)) return []
  return v.map((raw) => {
    const s = String(raw).trim()
    const m = s.match(/^(\d{4}-\d{2}-\d{2})\s*[:：]?\s*(.*)$/)
    return m
      ? { date: m[1], text: m[2].trim() }
      : { date: '', text: s }
  })
}

export default createContentLoader('posts/*.md', {
  includeSrc: true,
  excerpt: true,
  transform(raw) {
    return raw
      .map((item) => {
        const updates = toUpdates(item.frontmatter.updates)
        return {
          url: item.url,
          title: String(item.frontmatter.title || ''),
          date: toDateStr(item.frontmatter.date),
          updated: updates[0]?.date || toDateStr(item.frontmatter.updated) || '',
          updates,
          description: String(item.frontmatter.description || ''),
          minutes: toMinutes(item.src),
          top: item.frontmatter.top === true
        }
      })
      .sort((a, b) => {
        if (a.top !== b.top) return a.top ? -1 : 1
        return b.date.localeCompare(a.date)
      })
  }
})

