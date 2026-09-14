import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import HomeHero from './components/HomeHero.vue'
import Lead from './components/Lead.vue'
import EditBar from './components/EditBar.vue'
import SidebarToggle from './components/SidebarToggle.vue'
import PostMeta from './components/PostMeta.vue'
import DiagramNarrative from './components/DiagramNarrative.vue'
import DiagramPublish from './components/DiagramPublish.vue'
import DemoLagrange from './components/DemoLagrange.vue'
import DemoError from './components/DemoError.vue'
import './styles/custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      // 文章页底部：发布于/最后更新/修改记录
      'doc-after': () => h(PostMeta),
      // 全站右下角：目录收起按钮 + 编辑器入口（有编辑器时显示"编辑此页"，本地开发模式一直显示）
      'layout-bottom': () => [h(SidebarToggle), h(EditBar)]
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
    // 正文可交互演示（canvas，跟随亮/暗主题）：<DemoLagrange /> / <DemoError />
    app.component('DemoLagrange', DemoLagrange)
    app.component('DemoError', DemoError)
  }
}
