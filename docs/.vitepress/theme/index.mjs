import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import HomeHero from './components/HomeHero.vue'
import EditBar from './components/EditBar.vue'
import SidebarToggle from './components/SidebarToggle.vue'
import './styles/custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      // 文章页底部插入"编辑此页"入口（仅本地开发模式）
      'doc-after': () => h(EditBar),
      // 左侧目录收起/展开按钮（全站，fixed 定位与插槽位置无关）
      'layout-bottom': () => h(SidebarToggle)
    })
  },
  enhanceApp({ app }) {
    // 首页 index.md 里直接用 <HomeHero />
    app.component('HomeHero', HomeHero)
  }
}
