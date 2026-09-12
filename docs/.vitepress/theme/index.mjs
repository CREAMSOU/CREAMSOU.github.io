import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import HomeHero from './components/HomeHero.vue'
import Lead from './components/Lead.vue'
import EditBar from './components/EditBar.vue'
import SidebarToggle from './components/SidebarToggle.vue'
import PostMeta from './components/PostMeta.vue'
import DiagramNarrative from './components/DiagramNarrative.vue'
import DiagramPublish from './components/DiagramPublish.vue'
import './styles/custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      // 文章页底部：先"发布于/最后更新/修改记录"，再"编辑此页"入口（后者仅本地开发模式）
      'doc-after': () => [h(PostMeta), h(EditBar)],
      // 左侧目录收起/展开按钮（全站，fixed 定位与插槽位置无关）
      'layout-bottom': () => h(SidebarToggle)
    })
  },
  enhanceApp({ app }) {
    // 首页 index.md 里直接用 <HomeHero />
    app.component('HomeHero', HomeHero)
    // 文章开头的"速览"卡片：<Lead :points="['…', '…']" />
    app.component('Lead', Lead)
    // 正文配图（自带配色，跟随亮/暗主题）：<DiagramPublish /> / <DiagramNarrative />
    app.component('DiagramPublish', DiagramPublish)
    app.component('DiagramNarrative', DiagramNarrative)
  }
}
