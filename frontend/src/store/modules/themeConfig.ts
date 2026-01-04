/**
 * 主题配置 Store
 * 基于 fastapi-admin 的主题配置系统，适配平台
 */

export interface ThemeConfigState {
  themeConfig: {
    // 是否开启设置抽屉
    isDrawer: boolean;

    /**
     * 全局主题
     */
    // 默认 primary 主题颜色
    primary: string;
    // 是否开启深色模式
    isIsDark: boolean;

    /**
     * 顶栏设置
     */
    // 默认顶栏导航背景颜色
    topBar: string;
    // 默认顶栏导航字体颜色
    topBarColor: string;
    // 是否开启顶栏背景颜色渐变
    isTopBarColorGradual: boolean;

    /**
     * 菜单设置
     */
    // 默认菜单导航背景颜色
    menuBar: string;
    // 默认菜单导航字体颜色
    menuBarColor: string;
    // 默认菜单高亮背景色
    menuBarActiveColor: string;
    // 是否开启菜单背景颜色渐变
    isMenuBarColorGradual: boolean;

    /**
     * 界面设置
     */
    // 是否开启菜单水平折叠效果
    isCollapse: boolean;
    // 是否开启菜单手风琴效果
    isUniqueOpened: boolean;
    // 是否开启固定 Header
    isFixedHeader: boolean;
    // 初始化变量，用于更新菜单 el-scrollbar 的高度，请勿删除
    isFixedHeaderChange: boolean;
    // 是否开启自动锁屏
    isLockScreen: boolean;
    // 开启自动锁屏倒计时(s/秒)
    lockScreenTime: number;

    /**
     * 界面显示
     */
    // 是否开启侧边栏 Logo
    isShowLogo: boolean;
    // Logo文字
    logoText: string;
    // 初始化变量，用于 el-scrollbar 的高度更新，请勿删除
    isShowLogoChange: boolean;
    // 是否开启 Breadcrumb
    isBreadcrumb: boolean;
    // 是否开启 Breadcrumb 图标
    isBreadcrumbIcon: boolean;
    // 是否开启 TagsView
    isTagsview: boolean;
    // 是否开启 TagsView 图标
    isTagsviewIcon: boolean;
    // 是否开启 TagsView 缓存
    isCacheTagsView: boolean;
    // 是否开启 TagsView 拖拽
    isSortableTagsView: boolean;
    // 是否开启 Footer 底部版权信息
    isFooter: boolean;
    // 是否开启灰色模式
    isGrayscale: boolean;
    // 是否开启色弱模式
    isInvert: boolean;
    // 是否开启水印
    isWartermark: boolean;
    // 水印文案
    wartermarkText: string;

    /**
     * 其它设置
     */
    // 主页面切换动画：可选值"<default|slide-right|slide-left|opacitys>"，默认 default 没有动画效果
    animation: string;

    /**
     * 布局切换
     */
    // 布局切换：可选值"<default|classic|columns>"，默认 default
    layout: string;

    /**
     * 全局网站标题 / 副标题
     */
    // 网站主标题（菜单导航、浏览器当前网页标题）
    globalTitle: string;
    // 网站副标题（登录页顶部文字）
    globalViceTitle: string;
    // 网站副标题描述
    globalViceTitleMsg: string;
    // 默认全局组件大小，可选值"<large|default|small>"，默认 'small'
    globalComponentSize: string;
  };
}

const state = (): ThemeConfigState => ({
  themeConfig: {
    // 是否开启布局配置抽屉
    isDrawer: false,

    /**
     * 全局主题
     */
    // 默认 primary 主题颜色
    primary: '#409eff',
    // 是否开启深色模式
    isIsDark: false,

    /**
     * 顶栏设置
     */
    // 默认顶栏导航背景颜色
    topBar: '#ffffff',
    // 默认顶栏导航字体颜色
    topBarColor: '#606266',
    // 是否开启顶栏背景颜色渐变
    isTopBarColorGradual: false,

    /**
     * 菜单设置
     */
    // 默认菜单导航背景颜色
    menuBar: '#2b2f3a',
    // 默认菜单导航字体颜色
    menuBarColor: '#eaeaea',
    // 默认菜单高亮背景色
    menuBarActiveColor: 'rgba(0, 0, 0, 0.2)',
    // 是否开启菜单背景颜色渐变
    isMenuBarColorGradual: false,

    /**
     * 界面设置
     */
    // 是否开启菜单水平折叠效果
    isCollapse: false,
    // 是否开启菜单手风琴效果
    isUniqueOpened: true,
    // 是否开启固定 Header
    isFixedHeader: true,
    // 初始化变量，用于更新菜单 el-scrollbar 的高度，请勿删除
    isFixedHeaderChange: false,
    // 是否开启自动锁屏
    isLockScreen: false,
    // 开启自动锁屏倒计时(s/秒)
    lockScreenTime: 30,

    /**
     * 界面显示
     */
    // 是否开启侧边栏 Logo
    isShowLogo: true,
    // Logo文字
    logoText: 'N-Tester平台',
    // 初始化变量，用于 el-scrollbar 的高度更新，请勿删除
    isShowLogoChange: false,
    // 是否开启 Breadcrumb
    isBreadcrumb: true,
    // 是否开启 Breadcrumb 图标
    isBreadcrumbIcon: false,
    // 是否开启 TagsView
    isTagsview: false,
    // 是否开启 TagsView 图标
    isTagsviewIcon: false,
    // 是否开启 TagsView 缓存
    isCacheTagsView: false,
    // 是否开启 TagsView 拖拽
    isSortableTagsView: false,
    // 是否开启 Footer 底部版权信息
    isFooter: false,
    // 是否开启灰色模式
    isGrayscale: false,
    // 是否开启色弱模式
    isInvert: false,
    // 是否开启水印
    isWartermark: false,
    // 水印文案
    wartermarkText: 'N-Tester平台',

    /**
     * 其它设置
     */
    // 主页面切换动画：可选值"<default|slide-right|slide-left|opacitys>"，默认 default 没有动画效果
    animation: 'default',

    /**
     * 布局切换
     */
    // 布局切换：可选值"<default|classic|columns>"，默认 default
    layout: 'default',

    /**
     * 全局网站标题 / 副标题
     */
    // 网站主标题（菜单导航、浏览器当前网页标题）
    globalTitle: 'N-Tester平台',
    // 网站副标题（登录页顶部文字）
    globalViceTitle: 'N-Tester平台',
    // 网站副标题描述
    globalViceTitleMsg: '专业的AI驱动一体化测试管理平台',
    // 默认全局组件大小，可选值"<large|default|small>"，默认 'small'
    globalComponentSize: 'small',
  },
});

// mutations
const mutations = {
  setThemeConfig(state: ThemeConfigState, data: ThemeConfigState) {
    state.themeConfig = data.themeConfig;
  },
  updateThemeConfig(state: ThemeConfigState, payload: { key: string; value: any }) {
    (state.themeConfig as any)[payload.key] = payload.value;
  },
};

// actions
const actions = {
  setThemeConfig({ commit }: any, data: ThemeConfigState) {
    commit('setThemeConfig', data);
  },
  updateThemeConfig({ commit }: any, payload: { key: string; value: any }) {
    commit('updateThemeConfig', payload);
  },
};

export default {
  namespaced: true,
  state,
  actions,
  mutations,
};