<template>
  <el-config-provider :size="size">
    <router-view></router-view>
  </el-config-provider>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import FingerprintJS from '@fingerprintjs/fingerprintjs';

export default defineComponent({
  name: 'App',
  setup() {
    const store = useStore()
    const size = computed(() => store.state.app.elementSize)
    const fpPromise = FingerprintJS.load();

    // 获取设备id
    fpPromise.then(fp => fp.get()).then(result => {
      localStorage.setItem("deviceId", result.visitorId)
    });

    // 初始化主题配置
    onMounted(() => {
      // 简化的主题初始化 - 不需要复杂的逻辑，主题设置组件会自己处理
    });

    return {
      size,
    }
  }
})
</script>

<style>
/* 主题配置相关的CSS变量 */
:root {
  /* 主题色变量 */
  --theme-primary: #409eff;
  --theme-topBar: #ffffff;
  --theme-topBarColor: #606266;
  --theme-menuBar: #2b2f3a;
  --theme-menuBarColor: #eaeaea;
  --theme-menuBarActiveColor: rgba(0, 0, 0, 0.2);
  --theme-menuBar-light-1: #2f3349;
}

/* 深色模式 */
[data-theme="dark"] {
  --theme-topBar: #1f1f1f;
  --theme-topBarColor: #e5eaf3;
  --theme-menuBar: #191919;
  --theme-menuBarColor: #bfcbd9;
  --theme-menuBar-light-1: #2a2a2a;
  
  /* Element Plus 深色模式完整变量 */
  --el-bg-color: #141414;
  --el-bg-color-page: #0a0a0a;
  --el-bg-color-overlay: #1d1e1f;
  --el-text-color-primary: #e5eaf3;
  --el-text-color-regular: #cfd3dc;
  --el-text-color-secondary: #a3a6ad;
  --el-text-color-placeholder: #8d9095;
  --el-text-color-disabled: #6c6e72;
  --el-border-color: #4c4d4f;
  --el-border-color-light: #414243;
  --el-border-color-lighter: #363637;
  --el-border-color-extra-light: #2b2b2c;
  --el-border-color-dark: #58585b;
  --el-border-color-darker: #636466;
  --el-fill-color: #1d1e1f;
  --el-fill-color-light: #262727;
  --el-fill-color-lighter: #2c2c2c;
  --el-fill-color-extra-light: #191a1a;
  --el-fill-color-dark: #18181a;
  --el-fill-color-darker: #141414;
  --el-fill-color-blank: transparent;
  
  /* 表单组件深色模式 */
  --el-input-bg-color: #141414;
  --el-input-border-color: #4c4d4f;
  --el-input-hover-border-color: #636466;
  --el-input-text-color: #e5eaf3;
  --el-input-placeholder-color: #8d9095;
  
  /* 按钮深色模式 */
  --el-button-bg-color: #262727;
  --el-button-border-color: #4c4d4f;
  --el-button-hover-bg-color: #2c2c2c;
  --el-button-hover-border-color: #636466;
  --el-button-text-color: #e5eaf3;
  
  /* 表格深色模式 */
  --el-table-bg-color: #141414;
  --el-table-tr-bg-color: #141414;
  --el-table-header-bg-color: #1d1e1f;
  --el-table-row-hover-bg-color: #262727;
  --el-table-text-color: #e5eaf3;
  --el-table-header-text-color: #e5eaf3;
  --el-table-border-color: #4c4d4f;
  
  /* 弹窗深色模式 */
  --el-dialog-bg-color: #1d1e1f;
  --el-overlay-color: rgba(0, 0, 0, 0.8);
  --el-overlay-color-light: rgba(0, 0, 0, 0.7);
  --el-overlay-color-lighter: rgba(0, 0, 0, 0.5);
  
  /* 下拉菜单深色模式 */
  --el-dropdown-bg-color: #1d1e1f;
  --el-dropdown-border-color: #4c4d4f;
  
  /* 分页器深色模式 */
  --el-pagination-bg-color: #141414;
  --el-pagination-button-bg-color: #262727;
  
  /* 系统容器背景 */
  --system-container-background: #0a0a0a;
}

/* 深色模式下的body样式 */
body.dark-mode {
  background-color: var(--el-bg-color-page, #0a0a0a) !important;
  color: var(--el-text-color-primary, #e5eaf3) !important;
}

/* 深色模式下的全局样式 */
[data-theme="dark"] {
  /* 确保所有容器都使用深色背景 */
  .el-main {
    background-color: var(--system-container-background, #0a0a0a) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  .app-container {
    background-color: var(--system-container-background, #0a0a0a) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 页面容器深色模式 */
  .page-container,
  .content-container,
  .main-content,
  .page-wrapper,
  .layout-container {
    background-color: var(--system-container-background, #0a0a0a) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 布局容器表单区域 */
  .layout-container-form,
  .layout-container-form-handle,
  .layout-container-form-search {
    background-color: transparent !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 强制菜单图标显示 */
  .el-menu-item .el-menu-item-icon,
  .el-sub-menu__title .el-menu-item-icon {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 20px !important;
    height: 20px !important;
    font-size: 18px !important;
    color: var(--theme-menuBarColor, #eaeaea) !important;
    flex-shrink: 0 !important;
    
    /* 字体图标样式 */
    &.sfont {
      font-family: "sfont" !important;
      font-style: normal;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      color: inherit !important;
    }
  }
  
  /* 表单区域深色模式 */
  .el-form {
    background-color: transparent !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  .el-form-item__label {
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  .el-form-item__content {
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 输入框深色模式 */
  .el-input__wrapper {
    background-color: var(--el-input-bg-color, #141414) !important;
    border-color: var(--el-input-border-color, #4c4d4f) !important;
  }
  
  .el-input__inner {
    background-color: transparent !important;
    color: var(--el-input-text-color, #e5eaf3) !important;
  }
  
  .el-textarea__inner {
    background-color: var(--el-input-bg-color, #141414) !important;
    border-color: var(--el-input-border-color, #4c4d4f) !important;
    color: var(--el-input-text-color, #e5eaf3) !important;
  }
  
  /* 选择器深色模式 */
  .el-select .el-input__wrapper {
    background-color: var(--el-input-bg-color, #141414) !important;
  }
  
  .el-select-dropdown {
    background-color: var(--el-dropdown-bg-color, #1d1e1f) !important;
    border-color: var(--el-dropdown-border-color, #4c4d4f) !important;
  }
  
  .el-select-dropdown__item {
    color: var(--el-text-color-primary, #e5eaf3) !important;
    
    &:hover {
      background-color: var(--el-fill-color-light, #262727) !important;
    }
    
    &.selected {
      background-color: var(--el-color-primary) !important;
      color: #ffffff !important;
    }
  }
  
  /* 卡片深色模式 */
  .el-card {
    background-color: var(--el-bg-color, #141414) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  .el-card__header {
    background-color: var(--el-fill-color-light, #262727) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  .el-card__body {
    background-color: var(--el-bg-color, #141414) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 表格深色模式 */
  .el-table {
    background-color: var(--el-table-bg-color, #141414) !important;
    color: var(--el-table-text-color, #e5eaf3) !important;
  }
  
  .el-table th.el-table__cell {
    background-color: var(--el-table-header-bg-color, #1d1e1f) !important;
    color: var(--el-table-header-text-color, #e5eaf3) !important;
    border-color: var(--el-table-border-color, #4c4d4f) !important;
  }
  
  .el-table td.el-table__cell {
    background-color: var(--el-table-tr-bg-color, #141414) !important;
    color: var(--el-table-text-color, #e5eaf3) !important;
    border-color: var(--el-table-border-color, #4c4d4f) !important;
  }
  
  .el-table__row:hover > td.el-table__cell {
    background-color: var(--el-table-row-hover-bg-color, #262727) !important;
  }
  
  .el-table__empty-block {
    background-color: var(--el-table-bg-color, #141414) !important;
  }
  
  .el-table__empty-text {
    color: var(--el-text-color-secondary, #a3a6ad) !important;
  }
  
  /* 分页器深色模式 */
  .el-pagination {
    color: var(--el-text-color-primary, #e5eaf3) !important;
    background-color: var(--system-container-background, #0a0a0a) !important;
  }
  
  .el-pagination .el-pager li {
    background-color: var(--el-pagination-button-bg-color, #262727) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  .el-pagination .el-pager li:hover {
    color: var(--el-color-primary) !important;
    background-color: var(--el-fill-color-light, #262727) !important;
  }
  
  .el-pagination .el-pager li.active {
    background-color: var(--el-color-primary) !important;
    color: #ffffff !important;
  }
  
  .el-pagination .btn-prev,
  .el-pagination .btn-next {
    background-color: var(--el-pagination-button-bg-color, #262727) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  .el-pagination .btn-prev:hover,
  .el-pagination .btn-next:hover {
    color: var(--el-color-primary) !important;
  }
  
  .el-pagination .el-pagination__sizes .el-select .el-input__wrapper {
    background-color: var(--el-input-bg-color, #141414) !important;
  }
  
  .el-pagination .el-pagination__jump {
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  .el-pagination .el-pagination__total {
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 按钮深色模式 */
  .el-button {
    &.el-button--default {
      background-color: var(--el-button-bg-color, #262727) !important;
      border-color: var(--el-button-border-color, #4c4d4f) !important;
      color: var(--el-button-text-color, #e5eaf3) !important;
      
      &:hover {
        background-color: var(--el-button-hover-bg-color, #2c2c2c) !important;
        border-color: var(--el-button-hover-border-color, #636466) !important;
      }
    }
  }
  
  /* 弹窗深色模式 */
  .el-dialog {
    background-color: var(--el-dialog-bg-color, #1d1e1f) !important;
  }
  
  .el-dialog__header {
    background-color: var(--el-fill-color-light, #262727) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  .el-dialog__body {
    background-color: var(--el-dialog-bg-color, #1d1e1f) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  .el-dialog__footer {
    background-color: var(--el-fill-color-light, #262727) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  /* 抽屉深色模式 */
  .el-drawer {
    background-color: var(--el-dialog-bg-color, #1d1e1f) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  .el-drawer__header {
    color: var(--el-text-color-primary, #e5eaf3) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  .el-drawer__body {
    background-color: var(--el-dialog-bg-color, #1d1e1f) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 消息提示深色模式 */
  .el-message {
    background-color: var(--el-fill-color-light, #262727) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  .el-notification {
    background-color: var(--el-fill-color-light, #262727) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 标签页深色模式 */
  .el-tabs__header {
    background-color: var(--el-fill-color-light, #262727) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  .el-tabs__nav {
    background-color: transparent !important;
  }
  
  .el-tabs__item {
    color: var(--el-text-color-regular, #cfd3dc) !important;
    
    &.is-active {
      color: var(--el-color-primary) !important;
    }
    
    &:hover {
      color: var(--el-color-primary) !important;
    }
  }
  
  .el-tabs__content {
    background-color: transparent !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 标签页面板深色模式 */
  .el-tab-pane {
    background-color: transparent !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 面包屑深色模式 */
  .el-breadcrumb {
    color: var(--el-text-color-regular, #cfd3dc) !important;
  }
  
  .el-breadcrumb__item {
    .el-breadcrumb__inner {
      color: var(--el-text-color-regular, #cfd3dc) !important;
      
      &:hover {
        color: var(--el-color-primary) !important;
      }
    }
    
    &:last-child .el-breadcrumb__inner {
      color: var(--el-text-color-primary, #e5eaf3) !important;
    }
  }
  
  /* 统计卡片深色模式 */
  .dashboard-card,
  .stat-card,
  .data-card {
    background-color: var(--el-bg-color, #141414) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 通用容器深色模式 */
  .container,
  .wrapper,
  .content,
  .panel,
  .section {
    background-color: transparent !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 开关组件深色模式 */
  .el-switch {
    .el-switch__core {
      background-color: var(--el-fill-color-darker, #141414) !important;
      border-color: var(--el-border-color, #4c4d4f) !important;
    }
    
    &.is-checked .el-switch__core {
      background-color: var(--el-color-primary) !important;
    }
  }
  
  /* 气泡确认框深色模式 */
  .el-popconfirm {
    background-color: var(--el-fill-color-light, #262727) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 气泡提示深色模式 */
  .el-popover {
    background-color: var(--el-fill-color-light, #262727) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 工具提示深色模式 */
  .el-tooltip__popper {
    background-color: var(--el-fill-color-light, #262727) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  /* 加载组件深色模式 */
  .el-loading-mask {
    background-color: rgba(0, 0, 0, 0.8) !important;
  }
  
  .el-loading-text {
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 空状态深色模式 */
  .el-empty {
    color: var(--el-text-color-secondary, #a3a6ad) !important;
  }
  
  .el-empty__description {
    color: var(--el-text-color-secondary, #a3a6ad) !important;
  }
  
  /* 文本颜色适配 */
  h1, h2, h3, h4, h5, h6 {
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  p, span, div {
    color: inherit !important;
  }
  
  /* 链接颜色适配 */
  a {
    color: var(--el-color-primary) !important;
    
    &:hover {
      color: var(--el-color-primary-light-3) !important;
    }
  }
  
  /* 图标颜色适配 */
  .el-icon {
    color: var(--el-text-color-regular, #cfd3dc) !important;
  }
  
  /* 拖拽按钮深色模式 */
  .drag-button {
    color: var(--el-text-color-regular, #cfd3dc) !important;
    
    &:hover {
      color: var(--el-color-primary) !important;
    }
  }
  
  /* 搜索表单区域深色模式 */
  .table-query-form {
    background-color: transparent !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 分割线深色模式 */
  .el-divider {
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  .el-divider__text {
    background-color: var(--system-container-background, #0a0a0a) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 滚动条深色模式 */
  .el-scrollbar__bar {
    .el-scrollbar__thumb {
      background-color: var(--el-fill-color-light, #262727) !important;
      
      &:hover {
        background-color: var(--el-fill-color-lighter, #2c2c2c) !important;
      }
    }
  }
  
  /* 步骤条深色模式 */
  .el-steps {
    .el-step__title {
      color: var(--el-text-color-primary, #e5eaf3) !important;
    }
    
    .el-step__description {
      color: var(--el-text-color-secondary, #a3a6ad) !important;
    }
    
    .el-step__icon {
      background-color: var(--el-fill-color-light, #262727) !important;
      border-color: var(--el-border-color, #4c4d4f) !important;
      color: var(--el-text-color-primary, #e5eaf3) !important;
    }
  }
  
  /* 进度条深色模式 */
  .el-progress-bar__outer {
    background-color: var(--el-fill-color-light, #262727) !important;
  }
  
  .el-progress__text {
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 时间选择器深色模式 */
  .el-date-editor {
    .el-input__wrapper {
      background-color: var(--el-input-bg-color, #141414) !important;
      border-color: var(--el-input-border-color, #4c4d4f) !important;
    }
    
    .el-input__inner {
      color: var(--el-input-text-color, #e5eaf3) !important;
    }
  }
  
  /* 时间面板深色模式 */
  .el-picker-panel {
    background-color: var(--el-dropdown-bg-color, #1d1e1f) !important;
    border-color: var(--el-dropdown-border-color, #4c4d4f) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 树形控件深色模式 */
  .el-tree {
    background-color: transparent !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  .el-tree-node__content {
    &:hover {
      background-color: var(--el-fill-color-light, #262727) !important;
    }
  }
  
  .el-tree-node__label {
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 强制所有白色背景元素使用深色背景 - 简化版本 */
  [data-theme="dark"] div[style*="background-color: rgb(255, 255, 255)"],
  [data-theme="dark"] div[style*="background-color: #ffffff"],
  [data-theme="dark"] div[style*="background-color: #fff"],
  [data-theme="dark"] div[style*="background-color: white"] {
    background-color: var(--system-container-background, #0a0a0a) !important;
  }
  
  [data-theme="dark"] div[style*="color: rgb(0, 0, 0)"],
  [data-theme="dark"] div[style*="color: #000000"],
  [data-theme="dark"] div[style*="color: #000"],
  [data-theme="dark"] div[style*="color: black"] {
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 报告页面特殊处理 */
  .report-container,
  .report-content,
  .report-detail,
  .report-panel {
    background-color: var(--system-container-background, #0a0a0a) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 代码编辑器深色模式 */
  .ace_editor {
    background-color: var(--el-bg-color, #141414) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  .ace_gutter {
    background-color: var(--el-fill-color-light, #262727) !important;
    color: var(--el-text-color-secondary, #a3a6ad) !important;
  }
  
  /* JSON编辑器深色模式 */
  .jsoneditor {
    background-color: var(--el-bg-color, #141414) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  .jsoneditor-menu {
    background-color: var(--el-fill-color-light, #262727) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  /* 所有可能的白色容器 */
  .white-bg,
  .bg-white,
  .background-white {
    background-color: var(--system-container-background, #0a0a0a) !important;
  }
  
  /* 强制覆盖内联样式 - 简化版本 */
  [data-theme="dark"] div[style*="background: white"],
  [data-theme="dark"] div[style*="background: #fff"],
  [data-theme="dark"] div[style*="background: #ffffff"],
  [data-theme="dark"] div[style*="background-color: white"],
  [data-theme="dark"] div[style*="background-color: #fff"],
  [data-theme="dark"] div[style*="background-color: #ffffff"] {
    background-color: var(--system-container-background, #0a0a0a) !important;
  }
  
  /* 特殊提示框背景色适配 */
  [data-theme="dark"] div[style*="background-color: #fff3cd"] {
    background-color: var(--el-fill-color-light, #262727) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  /* 所有可能的浅色背景都转换为深色 */
  [data-theme="dark"] div[style*="background-color: #f"],
  [data-theme="dark"] div[style*="background-color: #e"],
  [data-theme="dark"] div[style*="background-color: #d"] {
    background-color: var(--el-fill-color-light, #262727) !important;
  }
  
  /* 文本区域强制深色 */
  textarea,
  pre,
  code {
    background-color: var(--el-input-bg-color, #141414) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
    border-color: var(--el-border-color, #4c4d4f) !important;
  }
  
  /* 所有可能的内容区域 */
  .content-area,
  .main-area,
  .detail-area,
  .info-area,
  .data-area {
    background-color: var(--system-container-background, #0a0a0a) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 全局强制深色模式 - 简化版本避免兼容性问题 */
  body[data-theme="dark"] div[style*="background: white"],
  body[data-theme="dark"] div[style*="background: #fff"],
  body[data-theme="dark"] div[style*="background: #ffffff"] {
    background-color: var(--system-container-background, #0a0a0a) !important;
  }
  
  body[data-theme="dark"] div[style*="color: #000"],
  body[data-theme="dark"] div[style*="color: black"] {
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 特殊处理：确保所有可能的白色容器都被覆盖，但不影响布局 */
  .el-main,
  .main-container,
  .page-main,
  .content-main,
  .layout-main,
  .app-main {
    background-color: var(--system-container-background, #0a0a0a) !important;
    color: var(--el-text-color-primary, #e5eaf3) !important;
  }
  
  /* 确保Header布局不受影响 */
  header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
  }
  
  header .left-box {
    display: flex !important;
    align-items: center !important;
    flex: 0 0 auto !important;
  }
  
  header .right-box {
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;
    flex: 0 0 auto !important;
    margin-left: auto !important;
  }
}

/* 全局菜单图标样式保护 */
.el-menu-item .el-menu-item-icon,
.el-sub-menu__title .el-menu-item-icon {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 20px !important;
  height: 20px !important;
  font-size: 18px !important;
  flex-shrink: 0 !important;
  
  /* 字体图标样式 */
  &.sfont {
    font-family: "sfont" !important;
    font-style: normal;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
}

/* 菜单折叠时的图标样式 */
.el-menu.collapse .el-menu-item .el-menu-item-icon,
.el-menu.collapse .el-sub-menu__title .el-menu-item-icon {
  margin-right: 0 !important;
  padding-right: 0 !important;
  width: 24px !important;
  height: 24px !important;
  
  /* 字体图标样式 */
  &.sfont {
    font-family: "sfont" !important;
    font-style: normal;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /*text-align: center;*/
  color: #2c3e50;
  width: 100%;
  height: 100vh;
}

.app-container {
  padding: 5px;
}

.table-query-form {
  margin-top: 5px;

  .form-item {
    display: flex;
    align-items: center;
  }
}

/*
dialog上下左右在视口居中、内容高度过高过开启dialog内滚动（dialog最高100vh）
*/
.el-dialog {
  display: flex !important;
  flex-direction: column !important;
  margin: 0 !important;
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  /*//overflow-y: scroll !important;*/
  max-height: 100vh !important;
}

/*
拖动排序的动效
*/
.drag-button {
  cursor: move;
  transition: transform 0.2s ease;
}

.drag-dragging {
  opacity: 0.5;
}

.el-table__row {
  transition: transform 0.3s ease; /* 表格行平滑过渡 */
}
</style>
