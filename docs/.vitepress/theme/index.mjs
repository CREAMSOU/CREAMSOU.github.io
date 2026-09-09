import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import PostList from './components/PostList.vue'
import EditBar from './components/EditBar.vue'
import './styles/custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      // 在首页 hero 下方插入文章列表
      'home-features-after': () => h(PostList),
      // 文章页底部插入"编辑此页"入口（仅本地开发模式）
      'doc-after': () => h(EditBar)
    })
  }
}
