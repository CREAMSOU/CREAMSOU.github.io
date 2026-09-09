import { createContentLoader } from 'vitepress'

export default createContentLoader('posts/*.md', {
  excerpt: true,
  transform(raw) {
    return raw
      .map((item) => ({
        url: item.url,
        title: item.frontmatter.title,
        date: item.frontmatter.date || '',
        description: item.frontmatter.description || '',
        top: item.frontmatter.top || false
      }))
      .sort((a, b) => {
        if (a.top !== b.top) return a.top ? -1 : 1
        return b.date.localeCompare(a.date)
      })
  }
})
