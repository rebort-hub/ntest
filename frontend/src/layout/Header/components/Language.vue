<template>
  <div class="tool-item" @click="toggleLanguage">
    <el-tooltip content="语言切换" placement="bottom">
      <el-icon :size="16"><Switch /></el-icon>
    </el-tooltip>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { Switch } from "@element-plus/icons-vue";

const toggleLanguage = () => {
  ElMessage.info("语言切换功能即将开放");
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
