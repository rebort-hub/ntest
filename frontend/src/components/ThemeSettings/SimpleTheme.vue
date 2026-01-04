<template>
  <div class="theme-settings">
    <el-drawer 
      title="主题设置" 
      v-model="isDrawerOpen" 
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
              v-model="primaryColor" 
              size="default"
              @change="onColorChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">深色模式</div>
          <div class="setting-value">
            <el-switch 
              v-model="isDark" 
              size="small" 
              @change="onDarkModeChange"
            />
          </div>
        </div>

        <!-- 界面设置 -->
        <el-divider content-position="left">界面设置</el-divider>
        <div class="setting-item">
          <div class="setting-label">菜单折叠</div>
          <div class="setting-value">
            <el-switch
              v-model="isCollapse"
              size="small"
              @change="onCollapseChange"
            />
          </div>
        </div>

        <!-- 配置操作 -->
        <div class="config-actions">
          <el-alert title="精简版主题配置，只包含可用功能" type="info" :closable="false" />
          <el-button 
            size="default" 
            class="config-btn" 
            type="primary" 
            @click="onCopyConfig"
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
            @click="onResetConfig"
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
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { DocumentCopy, RefreshRight } from '@element-plus/icons-vue';
import { useStore } from 'vuex';
import { useChangeColor } from '../../utils/theme';

defineOptions({ name: "SimpleThemeSettings" });

const store = useStore();
const { getLightColor, getDarkColor } = useChangeColor();

// 响应式数据
const isDrawerOpen = ref(false);
const primaryColor = ref('#409eff');
const isDark = ref(false);
const isCollapse = computed({
  get: () => store.state.app.isCollapse,
  set: (value) => store.commit('app/isCollapseChange', value)
});

// 复制文本到剪贴板
const copyText = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success('复制成功');
  } catch (error) {
    ElMessage.error('复制失败');
  }
};

// 主题色更改
const onColorChange = () => {
  if (!primaryColor.value) return;
  
  // 更新Element Plus主题色
  document.documentElement.style.setProperty('--el-color-primary', primaryColor.value);
  document.documentElement.style.setProperty('--el-color-primary-dark-2', getDarkColor(primaryColor.value, 0.1));
  
  // 生成主题色的渐变色系
  for (let i = 1; i <= 9; i++) {
    document.documentElement.style.setProperty(`--el-color-primary-light-${i}`, getLightColor(primaryColor.value, i / 10));
  }
  
  saveConfig();
};

// 深色模式切换
const onDarkModeChange = () => {
  const body = document.documentElement;
  if (isDark.value) {
    body.classList.add('dark');
    body.setAttribute('data-theme', 'dark');
  } else {
    body.classList.remove('dark');
    body.setAttribute('data-theme', '');
  }
  saveConfig();
};

// 菜单折叠切换
const onCollapseChange = () => {
  // isCollapse是computed属性，会自动更新store
  saveConfig();
};

// 保存配置
const saveConfig = () => {
  const config = {
    primaryColor: primaryColor.value,
    isDark: isDark.value,
    isCollapse: isCollapse.value,
  };
  localStorage.setItem('simpleThemeConfig', JSON.stringify(config));
};

// 加载配置
const loadConfig = () => {
  const saved = localStorage.getItem('simpleThemeConfig');
  if (saved) {
    try {
      const config = JSON.parse(saved);
      primaryColor.value = config.primaryColor || '#409eff';
      isDark.value = config.isDark || false;
      
      // 应用配置
      onColorChange();
      onDarkModeChange();
    } catch (error) {
      console.warn('Failed to load theme config:', error);
    }
  }
};

// 复制配置
const onCopyConfig = () => {
  const config = {
    primaryColor: primaryColor.value,
    isDark: isDark.value,
    isCollapse: isCollapse.value,
  };
  copyText(JSON.stringify(config, null, 2));
};

// 恢复默认
const onResetConfig = () => {
  primaryColor.value = '#409eff';
  isDark.value = false;
  isCollapse.value = false;
  
  onColorChange();
  onDarkModeChange();
  
  localStorage.removeItem('simpleThemeConfig');
  ElMessage.success('已恢复默认设置');
};

// 关闭抽屉
const onDrawerClose = () => {
  isDrawerOpen.value = false;
};

// 打开抽屉
const openDrawer = () => {
  isDrawerOpen.value = true;
};

// 初始化
onMounted(() => {
  loadConfig();
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