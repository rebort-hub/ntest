<template>
  <div class="tool-item" @click="openThemeSettings">
    <el-tooltip content="主题设置" placement="bottom">
      <el-icon :size="16"><Setting /></el-icon>
    </el-tooltip>
  </div>
  <ThemeSettings ref="themeSettingsRef" />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Setting } from "@element-plus/icons-vue";
import ThemeSettings from "@/components/ThemeSettings/index.vue";

const themeSettingsRef = ref<any>(null);

const openThemeSettings = () => {
  themeSettingsRef.value?.openDrawer();
};
</script>

<style lang="scss" scoped>
.tool-item {
  width: 32px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--system-header-text-color);
  transition: background-color 0.2s ease, color 0.2s ease;
  &:hover {
    background-color: var(--system-header-item-hover-color);
    color: var(--el-color-primary);
  }
}
</style>
