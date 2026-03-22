<template>
  <div class="tool-item" @click="refreshPage">
    <el-tooltip content="刷新页面" placement="bottom">
      <el-icon :size="16"><Refresh /></el-icon>
    </el-tooltip>
  </div>
</template>

<script setup lang="ts">
import { Refresh } from "@element-plus/icons-vue";

const refreshPage = () => {
  window.location.reload();
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
