import {createApp} from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import {baidu} from './utils/system/statistics'
import 'element-plus/theme-chalk/display.css' // 引入基于断点的隐藏类
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'normalize.css' // css初始化
import './assets/style/common.scss' // 公共css
import './theme/modules/chinese/index.scss'
import "vue3-json-viewer/dist/index.css"

import uploader from 'vue-simple-uploader'
import 'vue-simple-uploader/dist/style.css'

import App from './App.vue'
import store from './store'
import router from './router'
import CodeDiff from 'v-code-diff'


// 初始化主题配置
const initThemeConfig = () => {
  const saved = localStorage.getItem('simpleThemeConfig');
  if (saved) {
    try {
      const config = JSON.parse(saved);
      // 将localStorage中的主题配置同步到Vuex store
      Object.keys(config).forEach(key => {
        store.commit('themeConfig/updateThemeConfig', { key, value: config[key] });
      });
    } catch (error) {
      console.warn('Failed to parse theme config:', error);
    }
  }
};

// if (import.meta.env.MODE !== 'development') { // 非开发环境调用百度统计
//     baidu()
// }

const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
// @ts-ignore
app.use(ElementPlus, {
    locale: zhCn,  // 全局配置，element ui展示中文
    size: store.state.app.elementSize
})
app.use(CodeDiff)
app.use(store)
app.use(uploader)
// 在store初始化后，立即初始化主题配置
initThemeConfig();

app.use(router)
// app.config.performance = true
app.mount('#app')
