<template>
  <div class="logo-container" v-if="isShowLogo">
    <div v-if="!isCollapse" class="logo-full">
      <!-- Logo图片和文字组合显示 -->
      <img v-if="logoImage" :src="logoImage" alt="Logo" class="logo-image" />
      <h1 class="logo-text">{{ logoText }}</h1>
    </div>
    <div v-else class="logo-icon">
      <img v-if="logoImage" :src="logoImage" alt="Logo" class="logo-image-small" />
      <span v-else>{{ logoText.charAt(0) }}</span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { GetConfigByCode } from "@/api/config/config-value";

export default defineComponent({
  setup() {
    const store = useStore()
    const isCollapse = computed(() => store.state.app.isCollapse)
    const logoImage = ref('')
    
    // 响应式获取Logo显示状态
    const isShowLogo = computed(() => {
      return store.state.themeConfig?.themeConfig?.isShowLogo !== false
    })
    
    // 响应式获取Logo文字
    const logoText = computed(() => {
      const configText = store.state.themeConfig?.themeConfig?.logoText;
      // 如果配置中的文字是空字符串，就使用空字符串，不使用默认值
      return configText !== undefined ? configText : 'N-Tester平台';
    })
    
    // 获取配置的Logo图片
    const loadLogoImage = async () => {
      try {
        const response = await GetConfigByCode({ code: 'platform_logo' })
        if (response.data && response.data.trim()) {
          logoImage.value = response.data
        }
      } catch (error) {
        console.log('未配置平台Logo，使用默认显示')
      }
    }
    
    onMounted(() => {
      loadLogoImage()
    })
    
    return {
      isCollapse,
      isShowLogo,
      logoText,
      logoImage
    }
  }
})
</script>

<style lang="scss" scoped>
.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  background-color: var(--system-logo-background, var(--theme-menuBar, #2b2f3a));
  border-bottom: 1px solid var(--theme-menuBar-light-1, #2f3349);
  
  .logo-full {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    
    .logo-text {
      font-size: 18px;
      white-space: nowrap;
      color: var(--system-logo-color, var(--theme-menuBarColor, #eaeaea));
      margin: 0;
      font-weight: 600;
    }
    
    .logo-image {
      max-height: 32px;
      max-width: 32px;
      object-fit: contain;
      flex-shrink: 0;
    }
  }
  
  .logo-icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    background-color: var(--theme-primary, #409eff);
    display: flex;
    align-items: center;
    justify-content: center;
    
    span {
      color: #ffffff;
      font-size: 20px;
      font-weight: bold;
    }
    
    .logo-image-small {
      width: 32px;
      height: 32px;
      object-fit: contain;
      border-radius: 4px;
    }
  }
}
</style>
