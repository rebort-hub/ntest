/**
 * @description 所有人可使用的参数配置列表
 * @params hideMenu: 是否隐藏当前路由结点不在导航中展示
 * @params alwayShow: 只有一个子路由时是否总是展示菜单，默认false
 */
import {reactive} from 'vue'
import {createRouter, createWebHashHistory, createWebHistory} from 'vue-router'
import store from '@/store'
import NProgress from '@/utils/system/nprogress'
import {changeTitle} from '@/utils/system/title'
import {ElMessage} from 'element-plus'

NProgress.configure({showSpinner: false})

// 引入不需要权限的modules
import Default from './modules/default'
import Dashboard from './modules/dashboard'
import ApiTest from './modules/api-test'
import UiTest from './modules/ui-test'
import AppTest from './modules/app-test'
import Script from './modules/script'
import Tools from './modules/tools'
import Assist from './modules/assist'
import TestManage from './modules/manage'
import Config from './modules/config'
import WHartTest from './modules/aitestrebort'
import Flowchart from './modules/flowchart'

import Debug from './modules/debug'
import System from './modules/system'
import Watermark from "@/utils/watermark";

/**
 * @name 初始化必须要的路由
 * @description 使用reactive属性使得modules可以在路由菜单里面实时响应，搞定菜单回显的问题
 * @detail 针对modules的任何修改，均会同步至菜单级别，记住，是针对变量名为：moduels的修改
 **/
let modules = reactive([
    ...Default, ...Dashboard, ...ApiTest, ...UiTest, ...AppTest, ...Script, ...Tools, ...Assist, ...TestManage,
    ...Config, ...WHartTest, ...Flowchart, ...System, ...Debug
])

const router = createRouter({
    // history: createWebHashHistory(),  // 路由地址带 #
    history: createWebHistory(),  // 路由地址不带 #
    routes: modules
})

// 未授权时可访问的白名单
const whiteList = [
    '/login',
    '/self-login',
    '/sso-login',
    '/assist/error-record',
    '/tools/examination',
    '/tools/make-user-info',
    '/test-manage/account',
    '/api-test/report-show',
    '/ui-test/report-show',
    '/app-test/report-show'
]

// 路由跳转前的监听操作
router.beforeEach((to, _from, next) => {
    NProgress.start();

    to.meta.title ? (changeTitle(to.meta.title)) : "" // 动态title
    
    // 白名单，直接放行（不包括首页）
    if (whiteList.indexOf(to.path) !== -1 || to.path.indexOf('report-show') > -1) {
        next()
        return
    }
    
    const hasToken = localStorage.getItem('accessToken')
    if (!hasToken) {
        next("/login")
        return
    }
    
    // 判断权限
    const isAdmin = localStorage.getItem('isAdmin') === '1'
    let permissions = []
    try {
        const permissionsStr = localStorage.getItem('permissions')
        permissions = permissionsStr ? JSON.parse(permissionsStr) : []
    } catch (error) {
        console.error('解析权限失败:', error)
        permissions = []
    }
    
    // 管理员直接放行
    if (isAdmin) {
        next()
        return
    }
    
    // 对于AiTestRebort的动态路由（包含项目ID的路由），如果有/aitestrebort/project权限就放行
    if (to.path.startsWith('/aitestrebort/project/') && /\/aitestrebort\/project\/\d+/.test(to.path)) {
        if (permissions.indexOf('/aitestrebort/project') !== -1 || permissions.indexOf('/aitestrebort') !== -1) {
            next()
        } else {
            ElMessage.error('没有权限访问此页面')
            next(_from.path || '/aitestrebort/project')
        }
        return
    }
    
    if (to.path === '/' || to.path === '/index') {
        next()
        return
    }
    
    // 普通路由权限检查
    if (permissions.indexOf(to.path) !== -1) {
        next()
    } else {
        ElMessage.error('没有权限访问此页面')
        next(_from.path || '/')
    }
});

// 路由跳转后的监听操作
router.afterEach((to, _from) => {
    const keepAliveComponentsName = store.getters['keepAlive/keepAliveComponentsName'] || []
    // @ts-ignore
    try {
        const component = to.matched[to.matched.length - 1]?.components?.default
        const name = component?.name || (typeof component === 'function' ? null : component?.name)
        if (to.meta && to.meta.cache && name && !keepAliveComponentsName.includes(name)) {
            store.commit('keepAlive/addKeepAliveComponentsName', name)
        }
    } catch (error) {
        console.warn('Failed to process keepAlive:', error)
    }

    // 根据主题配置决定是否加水印
    const savedConfig = localStorage.getItem('simpleThemeConfig');
    let shouldShowWatermark = false;
    let watermarkText = 'N-Tester平台';
    
    if (savedConfig) {
        try {
            const config = JSON.parse(savedConfig);
            shouldShowWatermark = config.isWartermark === true;
            watermarkText = config.wartermarkText || 'N-Tester平台';
        } catch (error) {
            console.warn('Failed to parse theme config for watermark:', error);
        }
    }
    
    if (shouldShowWatermark) {
        const userName = localStorage.getItem("userName");
        const finalText = userName ? `${watermarkText} - ${userName}` : watermarkText;
        Watermark.set(finalText);
    } else {
        Watermark.del(); // 如果配置关闭水印，则删除水印
    }
    
    NProgress.done()
});

export {
    modules
}

export default router
