<template>
  <div class="tool-item" @click="toggleFullscreen">
    <el-tooltip content="全屏显示" placement="bottom">
      <el-icon :size="16"><FullScreen /></el-icon>
    </el-tooltip>
  </div>
</template>

<script setup lang="ts">
import { FullScreen } from "@element-plus/icons-vue";

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else if (document.exitFullscreen) {
    document.exitFullscreen();
  }
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
