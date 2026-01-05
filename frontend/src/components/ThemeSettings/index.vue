<template>
  <div class="theme-settings">
    <el-drawer 
      title="主题设置" 
      v-model="themeConfig.isDrawer" 
      direction="rtl" 
      destroy-on-close 
      size="350px"
      @close="onDrawerClose"
    >
      <template #header>
        <span>主题设置</span>
      </template>

      <el-scrollbar class="theme-settings-scrollbar">
        <!-- 全局主题 -->
        <el-divider content-position="left">全局主题</el-divider>
        <div class="setting-item">
          <div class="setting-label">主题色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.primary" 
              size="default"
              @change="onPrimaryColorChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">深色模式</div>
          <div class="setting-value">
            <el-switch 
              v-model="themeConfig.isDark" 
              size="small" 
              @change="onDarkModeChange"
            />
          </div>
        </div>

        <!-- 顶栏设置 -->
        <el-divider content-position="left">顶栏设置</el-divider>
        <div class="setting-item">
          <div class="setting-label">顶栏背景色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.topBar" 
              size="default"
              @change="onTopBarColorChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">顶栏字体颜色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.topBarColor" 
              size="default"
              @change="onTopBarTextColorChange"
            />
          </div>
        </div>

        <!-- 菜单设置 -->
        <el-divider content-position="left">菜单设置</el-divider>
        <div class="setting-item">
          <div class="setting-label">菜单背景色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.menuBar" 
              size="default"
              @change="onMenuBarColorChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">菜单字体颜色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.menuBarColor" 
              size="default"
              @change="onMenuBarTextColorChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">菜单高亮色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.menuBarActiveColor" 
              size="default"
              @change="onMenuBarActiveColorChange"
            />
          </div>
        </div>

        <!-- 界面设置 -->
        <el-divider content-position="left">界面设置</el-divider>
        <div class="setting-item">
          <div class="setting-label">菜单折叠</div>
          <div class="setting-value">
            <el-switch
              v-model="themeConfig.isCollapse"
              size="small"
              @change="onCollapseChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">侧边栏 Logo</div>
          <div class="setting-value">
            <el-switch 
              v-model="themeConfig.isShowLogo" 
              size="small" 
              @change="onIsShowLogoChange"
            />
          </div>
        </div>
        <div class="setting-item" v-if="themeConfig.isShowLogo">
          <div class="setting-label">Logo 文字</div>
          <div class="setting-value">
            <el-input 
              v-model="themeConfig.logoText" 
              size="small"
              placeholder="请输入Logo文字"
              @input="onLogoTextChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">面包屑导航</div>
          <div class="setting-value">
            <el-switch
              v-model="themeConfig.isBreadcrumb"
              size="small"
              @change="onIsBreadcrumbChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">标签页导航</div>
          <div class="setting-value">
            <el-switch
              v-model="themeConfig.showTabs"
              size="small"
              @change="onShowTabsChange"
            />
          </div>
        </div>

        <!-- 特殊效果 -->
        <el-divider content-position="left">特殊效果</el-divider>
        <div class="setting-item">
          <div class="setting-label">灰色模式</div>
          <div class="setting-value">
            <el-switch 
              v-model="themeConfig.isGrayscale" 
              size="small" 
              @change="onGrayscaleChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">色弱模式</div>
          <div class="setting-value">
            <el-switch 
              v-model="themeConfig.isInvert" 
              size="small" 
              @change="onInvertChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">水印功能</div>
          <div class="setting-value">
            <el-switch 
              v-model="themeConfig.isWartermark" 
              size="small" 
              @change="onWatermarkChange"
            />
          </div>
        </div>
        <div class="setting-item" v-if="themeConfig.isWartermark">
          <div class="setting-label">水印文案</div>
          <div class="setting-value">
            <el-input 
              v-model="themeConfig.wartermarkText" 
              size="small"
              placeholder="请输入水印文案"
              @input="onWatermarkTextChange"
            />
          </div>
        </div>

        <!-- 配置操作 -->
        <div class="config-actions">
          <el-alert title="主题配置功能" type="info" :closable="false" />
          <el-button 
            size="default" 
            class="config-btn" 
            type="primary" 
            @click="onCopyConfigClick"
          >
            <el-icon class="mr5">
              <DocumentCopy />
            </el-icon>
            复制配置
          </el-button>
          <el-button 
            size="default" 
            class="config-btn-reset" 
            type="info" 
            @click="onResetConfigClick"
          >
            <el-icon class="mr5">
              <RefreshRight />
            </el-icon>
            恢复默认
          </el-button>
        </div>
      </el-scrollbar>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { reactive, nextTick, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { DocumentCopy, RefreshRight } from '@element-plus/icons-vue';
import { useStore } from 'vuex';
import { useChangeColor } from '../../utils/theme';
import Watermark from '../../utils/watermark';

defineOptions({ name: "ThemeSettings" });

const store = useStore();
const { getLightColor, getDarkColor } = useChangeColor();

// 主题配置
const themeConfig = reactive({
  isDrawer: false,
  primary: '#409eff',
  isDark: false,
  topBar: '#ffffff',
  topBarColor: '#606266',
  menuBar: '#2b2f3a',
  menuBarColor: '#eaeaea',
  menuBarActiveColor: '#409eff',
  isCollapse: false,
  isShowLogo: true,
  logoText: 'N-Tester平台',
  isBreadcrumb: true,
  showTabs: false, // 标签页显示状态，默认关闭
  isGrayscale: false,
  isInvert: false,
  isWartermark: false,
  wartermarkText: 'N-Tester平台',
});

// 工具函数
const copyText = async (text: string): Promise<void> => {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success('复制成功');
  } catch (error) {
    ElMessage.error('复制失败');
    throw error;
  }
};

// 应用CSS变量
const applyCSSVariables = () => {
  const root = document.documentElement;
  
  // 主题色
  root.style.setProperty('--el-color-primary', themeConfig.primary);
  root.style.setProperty('--theme-primary', themeConfig.primary);
  
  // 生成主题色的渐变色系
  for (let i = 1; i <= 9; i++) {
    root.style.setProperty(`--el-color-primary-light-${i}`, getLightColor(themeConfig.primary, i / 10));
  }
  root.style.setProperty('--el-color-primary-dark-2', getDarkColor(themeConfig.primary, 0.1));
  
  // 深色模式处理
  if (themeConfig.isDark) {
    // 设置深色模式属性
    root.setAttribute('data-theme', 'dark');
    document.body.classList.add('dark-mode');
    
    // Element Plus 深色模式完整变量
    root.style.setProperty('--el-bg-color', '#141414');
    root.style.setProperty('--el-bg-color-page', '#0a0a0a');
    root.style.setProperty('--el-bg-color-overlay', '#1d1e1f');
    root.style.setProperty('--el-text-color-primary', '#e5eaf3');
    root.style.setProperty('--el-text-color-regular', '#cfd3dc');
    root.style.setProperty('--el-text-color-secondary', '#a3a6ad');
    root.style.setProperty('--el-text-color-placeholder', '#8d9095');
    root.style.setProperty('--el-text-color-disabled', '#6c6e72');
    root.style.setProperty('--el-border-color', '#4c4d4f');
    root.style.setProperty('--el-border-color-light', '#414243');
    root.style.setProperty('--el-border-color-lighter', '#363637');
    root.style.setProperty('--el-border-color-extra-light', '#2b2b2c');
    root.style.setProperty('--el-border-color-dark', '#58585b');
    root.style.setProperty('--el-border-color-darker', '#636466');
    root.style.setProperty('--el-fill-color', '#1d1e1f');
    root.style.setProperty('--el-fill-color-light', '#262727');
    root.style.setProperty('--el-fill-color-lighter', '#2c2c2c');
    root.style.setProperty('--el-fill-color-extra-light', '#191a1a');
    root.style.setProperty('--el-fill-color-dark', '#18181a');
    root.style.setProperty('--el-fill-color-darker', '#141414');
    root.style.setProperty('--el-fill-color-blank', 'transparent');
    
    // 表单组件深色模式
    root.style.setProperty('--el-input-bg-color', '#141414');
    root.style.setProperty('--el-input-border-color', '#4c4d4f');
    root.style.setProperty('--el-input-hover-border-color', '#636466');
    root.style.setProperty('--el-input-focus-border-color', themeConfig.primary);
    root.style.setProperty('--el-input-text-color', '#e5eaf3');
    root.style.setProperty('--el-input-placeholder-color', '#8d9095');
    
    // 按钮深色模式
    root.style.setProperty('--el-button-bg-color', '#262727');
    root.style.setProperty('--el-button-border-color', '#4c4d4f');
    root.style.setProperty('--el-button-hover-bg-color', '#2c2c2c');
    root.style.setProperty('--el-button-hover-border-color', '#636466');
    root.style.setProperty('--el-button-text-color', '#e5eaf3');
    
    // 表格深色模式
    root.style.setProperty('--el-table-bg-color', '#141414');
    root.style.setProperty('--el-table-tr-bg-color', '#141414');
    root.style.setProperty('--el-table-header-bg-color', '#1d1e1f');
    root.style.setProperty('--el-table-row-hover-bg-color', '#262727');
    root.style.setProperty('--el-table-text-color', '#e5eaf3');
    root.style.setProperty('--el-table-header-text-color', '#e5eaf3');
    root.style.setProperty('--el-table-border-color', '#4c4d4f');
    
    // 弹窗深色模式
    root.style.setProperty('--el-dialog-bg-color', '#1d1e1f');
    root.style.setProperty('--el-overlay-color', 'rgba(0, 0, 0, 0.8)');
    root.style.setProperty('--el-overlay-color-light', 'rgba(0, 0, 0, 0.7)');
    root.style.setProperty('--el-overlay-color-lighter', 'rgba(0, 0, 0, 0.5)');
    
    // 下拉菜单深色模式
    root.style.setProperty('--el-dropdown-bg-color', '#1d1e1f');
    root.style.setProperty('--el-dropdown-border-color', '#4c4d4f');
    
    // 分页器深色模式
    root.style.setProperty('--el-pagination-bg-color', '#141414');
    root.style.setProperty('--el-pagination-button-bg-color', '#262727');
    root.style.setProperty('--el-pagination-hover-color', themeConfig.primary);
    
    // 深色模式下的主题颜色
    root.style.setProperty('--theme-topBar', '#1f1f1f');
    root.style.setProperty('--theme-topBarColor', '#e5eaf3');
    root.style.setProperty('--theme-menuBar', '#191919');
    root.style.setProperty('--theme-menuBarColor', '#bfcbd9');
    root.style.setProperty('--theme-menuBar-light-1', '#2a2a2a');
    
    // 系统容器背景色
    root.style.setProperty('--system-container-background', '#0a0a0a');
  } else {
    // 移除深色模式
    root.removeAttribute('data-theme');
    document.body.classList.remove('dark-mode');
    
    // 恢复浅色模式变量
    const lightModeVars = [
      '--el-bg-color', '--el-bg-color-page', '--el-bg-color-overlay',
      '--el-text-color-primary', '--el-text-color-regular', '--el-text-color-secondary',
      '--el-text-color-placeholder', '--el-text-color-disabled',
      '--el-border-color', '--el-border-color-light', '--el-border-color-lighter',
      '--el-border-color-extra-light', '--el-border-color-dark', '--el-border-color-darker',
      '--el-fill-color', '--el-fill-color-light', '--el-fill-color-lighter',
      '--el-fill-color-extra-light', '--el-fill-color-dark', '--el-fill-color-darker',
      '--el-input-bg-color', '--el-input-border-color', '--el-input-hover-border-color',
      '--el-input-focus-border-color', '--el-input-text-color', '--el-input-placeholder-color',
      '--el-button-bg-color', '--el-button-border-color', '--el-button-hover-bg-color',
      '--el-button-hover-border-color', '--el-button-text-color',
      '--el-table-bg-color', '--el-table-tr-bg-color', '--el-table-header-bg-color',
      '--el-table-row-hover-bg-color', '--el-table-text-color', '--el-table-header-text-color',
      '--el-table-border-color', '--el-dialog-bg-color', '--el-overlay-color',
      '--el-overlay-color-light', '--el-overlay-color-lighter',
      '--el-dropdown-bg-color', '--el-dropdown-border-color',
      '--el-pagination-bg-color', '--el-pagination-button-bg-color', '--el-pagination-hover-color'
    ];
    
    lightModeVars.forEach(varName => {
      root.style.removeProperty(varName);
    });
    
    // 使用用户配置的颜色或默认颜色
    root.style.setProperty('--theme-topBar', themeConfig.topBar);
    root.style.setProperty('--theme-topBarColor', themeConfig.topBarColor);
    root.style.setProperty('--theme-menuBar', themeConfig.menuBar);
    root.style.setProperty('--theme-menuBarColor', themeConfig.menuBarColor);
    root.style.setProperty('--theme-menuBar-light-1', getLightColor(themeConfig.menuBar, 0.05));
    
    // 恢复默认容器背景色
    root.style.setProperty('--system-container-background', '#f5f5f5');
  }
  
  // 如果不是深色模式，使用用户自定义的颜色
  if (!themeConfig.isDark) {
    root.style.setProperty('--theme-topBar', themeConfig.topBar);
    root.style.setProperty('--theme-topBarColor', themeConfig.topBarColor);
    root.style.setProperty('--theme-menuBar', themeConfig.menuBar);
    root.style.setProperty('--theme-menuBarColor', themeConfig.menuBarColor);
  }
  
  // 菜单高亮色（深色和浅色模式都使用）
  root.style.setProperty('--theme-menuBarActiveColor', themeConfig.menuBarActiveColor);
  
  // 系统变量设置
  root.style.setProperty('--system-header-background', getComputedStyle(root).getPropertyValue('--theme-topBar'));
  root.style.setProperty('--system-header-text-color', getComputedStyle(root).getPropertyValue('--theme-topBarColor'));
  root.style.setProperty('--system-header-breadcrumb-text-color', getComputedStyle(root).getPropertyValue('--theme-topBarColor'));
  root.style.setProperty('--system-header-item-hover-color', getLightColor(getComputedStyle(root).getPropertyValue('--theme-topBar') || '#ffffff', 0.1));
  
  // 菜单相关的CSS变量
  root.style.setProperty('--system-menu-background', getComputedStyle(root).getPropertyValue('--theme-menuBar'));
  root.style.setProperty('--system-menu-text-color', getComputedStyle(root).getPropertyValue('--theme-menuBarColor'));
  root.style.setProperty('--system-menu-active-color', themeConfig.menuBarActiveColor);
  root.style.setProperty('--system-menu-hover-background', getComputedStyle(root).getPropertyValue('--theme-menuBar-light-1'));
  
  // Logo相关变量
  root.style.setProperty('--system-logo-background', getComputedStyle(root).getPropertyValue('--theme-menuBar'));
  root.style.setProperty('--system-logo-color', getComputedStyle(root).getPropertyValue('--theme-menuBarColor'));
  
  // 强制更新所有页面元素的样式
  nextTick(() => {
    // 触发页面重新计算样式
    document.body.style.display = 'none';
    document.body.offsetHeight; // 触发重排
    document.body.style.display = '';
  });
};

// 保存配置到localStorage
const saveConfig = () => {
  localStorage.setItem('simpleThemeConfig', JSON.stringify(themeConfig));
  
  // 同时更新Vuex store中的主题配置
  Object.keys(themeConfig).forEach(key => {
    store.commit('themeConfig/updateThemeConfig', { key, value: themeConfig[key] });
  });
};

// 从localStorage加载配置
const loadConfig = () => {
  const saved = localStorage.getItem('simpleThemeConfig');
  if (saved) {
    try {
      const config = JSON.parse(saved);
      // 使用深度合并，确保空字符串也能被正确保存
      Object.keys(config).forEach(key => {
        if (config.hasOwnProperty(key)) {
          themeConfig[key] = config[key];
          // 同时更新Vuex store
          store.commit('themeConfig/updateThemeConfig', { key, value: config[key] });
        }
      });
    } catch (error) {
      console.warn('Failed to parse theme config:', error);
    }
  }
};

// 主题色变化
const onPrimaryColorChange = () => {
  if (!themeConfig.primary) return ElMessage.warning('主题色不能为空');
  applyCSSVariables();
  saveConfig();
};

// 顶栏背景色变化
const onTopBarColorChange = () => {
  applyCSSVariables();
  saveConfig();
};

// 顶栏字体颜色变化
const onTopBarTextColorChange = () => {
  applyCSSVariables();
  saveConfig();
};

// 菜单背景色变化
const onMenuBarColorChange = () => {
  applyCSSVariables();
  saveConfig();
};

// 菜单字体颜色变化
const onMenuBarTextColorChange = () => {
  applyCSSVariables();
  saveConfig();
};

// 菜单高亮色变化
const onMenuBarActiveColorChange = () => {
  applyCSSVariables();
  saveConfig();
};

// 菜单折叠变化
const onCollapseChange = () => {
  store.commit('app/isCollapseChange', themeConfig.isCollapse);
  saveConfig();
};

// 深色模式变化
const onDarkModeChange = () => {
  applyCSSVariables();
  saveConfig();
  
  // 强制刷新页面样式
  nextTick(() => {
    // 触发页面重新渲染以确保所有组件都应用新的主题
    const event = new Event('themeChanged');
    window.dispatchEvent(event);
  });
};

// Logo显示变化
const onIsShowLogoChange = () => {
  // 更新主题配置store
  store.commit('themeConfig/updateThemeConfig', { 
    key: 'isShowLogo', 
    value: themeConfig.isShowLogo 
  });
  saveConfig();
};

// Logo文字变化
const onLogoTextChange = () => {
  // 更新主题配置store
  store.commit('themeConfig/updateThemeConfig', { 
    key: 'logoText', 
    value: themeConfig.logoText 
  });
  saveConfig();
};

// 面包屑显示变化
const onIsBreadcrumbChange = () => {
  saveConfig();
};

// 标签页显示变化
const onShowTabsChange = () => {
  saveConfig();
  // 触发自定义事件，通知布局组件更新
  const event = new CustomEvent('themeConfigChanged');
  window.dispatchEvent(event);
};

// 灰色模式变化
const onGrayscaleChange = () => {
  if (themeConfig.isGrayscale) {
    themeConfig.isInvert = false;
  }
  
  const filter = themeConfig.isGrayscale ? 'grayscale(1)' : 'none';
  document.body.style.filter = filter;
  saveConfig();
};

// 色弱模式变化
const onInvertChange = () => {
  if (themeConfig.isInvert) {
    themeConfig.isGrayscale = false;
  }
  
  const filter = themeConfig.isInvert ? 'invert(80%)' : 'none';
  document.body.style.filter = filter;
  saveConfig();
};

// 水印功能变化
const onWatermarkChange = () => {
  if (themeConfig.isWartermark) {
    Watermark.set(themeConfig.wartermarkText);
  } else {
    Watermark.del();
  }
  saveConfig();
};

// 水印文案变化
const onWatermarkTextChange = () => {
  if (themeConfig.isWartermark && themeConfig.wartermarkText) {
    Watermark.set(themeConfig.wartermarkText);
  }
  saveConfig();
};

// 关闭抽屉
const onDrawerClose = () => {
  themeConfig.isDrawer = false;
  saveConfig();
};

// 打开抽屉
const openDrawer = () => {
  themeConfig.isDrawer = true;
};

// 复制配置
const onCopyConfigClick = () => {
  const configCopy = { ...themeConfig };
  configCopy.isDrawer = false;
  copyText(JSON.stringify(configCopy, null, 2));
};

// 恢复默认
const onResetConfigClick = () => {
  // 重置为默认值
  Object.assign(themeConfig, {
    isDrawer: false,
    primary: '#409eff',
    isDark: false,
    topBar: '#ffffff',
    topBarColor: '#606266',
    menuBar: '#2b2f3a',
    menuBarColor: '#eaeaea',
    menuBarActiveColor: '#409eff',
    isCollapse: false,
    isShowLogo: true,
    logoText: 'N-Tester平台',
    isBreadcrumb: true,
    showTabs: false, // 默认关闭标签页
    isGrayscale: false,
    isInvert: false,
    isWartermark: false,
    wartermarkText: 'N-Tester平台',
  });
  
  // 清除特殊效果
  document.body.style.filter = 'none';
  Watermark.del();
  
  // 应用默认样式
  applyCSSVariables();
  saveConfig();
  
  // 触发自定义事件，通知布局组件更新
  const event = new CustomEvent('themeConfigChanged');
  window.dispatchEvent(event);
  
  ElMessage.success('已恢复默认配置');
};

// 初始化
onMounted(() => {
  nextTick(() => {
    // 加载保存的配置
    loadConfig();
    
    // 应用配置
    applyCSSVariables();
    
    // 应用特殊效果
    if (themeConfig.isGrayscale) {
      document.body.style.filter = 'grayscale(1)';
    } else if (themeConfig.isInvert) {
      document.body.style.filter = 'invert(80%)';
    }
    
    // 应用水印
    if (themeConfig.isWartermark) {
      Watermark.set(themeConfig.wartermarkText);
    }
  });
});

// 暴露方法
defineExpose({
  openDrawer,
});
</script>
<style scoped lang="scss">
.theme-settings-scrollbar {
  height: calc(100vh - 50px);
  padding: 0 15px;

  :deep(.el-scrollbar__view) {
    overflow-x: hidden !important;
  }

  .setting-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 15px;
    min-height: 32px;

    .setting-label {
      flex: 1;
      color: var(--el-text-color-primary);
      font-size: 14px;
      margin-right: 10px;
    }

    .setting-value {
      display: flex;
      align-items: center;
      flex-shrink: 0;
    }
  }

  .layout-switch-container {
    overflow: hidden;
    display: flex;
    flex-wrap: wrap;
    align-content: flex-start;
    margin: 0 -5px;

    .layout-item {
      width: 50%;
      height: 70px;
      cursor: pointer;
      border: 1px solid transparent;
      position: relative;
      padding: 5px;

      .layout-preview {
        height: 100%;
        display: flex;
        border-radius: 4px;
        overflow: hidden;
        border: 1px solid transparent;
        transition: all 0.3s ease-in-out;

        &.layout-classic {
          flex-direction: column;
        }

        .layout-aside {
          width: 20px;
          background-color: var(--el-color-info-light-7);
        }

        .layout-container {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .layout-header {
          height: 10px;
          background-color: var(--el-color-info-light-5);
        }

        .layout-main {
          flex: 1;
          background-color: var(--el-color-info-light-9);
        }
      }

      .layout-active {
        border: 1px solid var(--el-color-primary);
      }

      .layout-tips,
      .layout-tips-active {
        transition: all 0.3s ease-in-out;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        border: 1px solid var(--el-color-primary-light-5);
        border-radius: 50%;
        padding: 4px;

        .layout-tips-box {
          transition: inherit;
          width: 30px;
          height: 30px;
          z-index: 9;
          border: 1px solid var(--el-color-primary-light-5);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;

          .layout-tips-txt {
            transition: inherit;
            font-size: 12px;
            line-height: 1;
            color: var(--el-color-primary-light-5);
            text-align: center;
            margin: 0;
            background-color: var(--el-bg-color);
            padding: 2px 4px;
            border-radius: 2px;
          }
        }
      }

      .layout-tips-active {
        border: 1px solid var(--el-color-primary);

        .layout-tips-box {
          border: 1px solid var(--el-color-primary);

          .layout-tips-txt {
            color: var(--el-color-primary) !important;
          }
        }
      }

      &:hover {
        .layout-preview {
          transition: all 0.3s ease-in-out;
          border: 1px solid var(--el-color-primary);
        }

        .layout-tips {
          transition: all 0.3s ease-in-out;
          border-color: var(--el-color-primary);

          .layout-tips-box {
            transition: inherit;
            border-color: var(--el-color-primary);

            .layout-tips-txt {
              transition: inherit;
              color: var(--el-color-primary) !important;
            }
          }
        }
      }
    }
  }

  .config-actions {
    margin: 20px 0;

    .config-btn {
      width: 100%;
      margin-top: 15px;
    }

    .config-btn-reset {
      width: 100%;
      margin: 10px 0 0;
    }
  }
}

.mr5 {
  margin-right: 5px;
}
</style>