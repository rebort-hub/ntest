<template>
  <el-dropdown @command="handleSizeCommand" trigger="click">
    <div class="tool-item">
      <el-tooltip content="组件大小" placement="bottom">
        <el-icon :size="16"><Operation /></el-icon>
      </el-tooltip>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="large" :disabled="elementSize === 'large'">大</el-dropdown-item>
        <el-dropdown-item command="default" :disabled="elementSize === 'default'">默认</el-dropdown-item>
        <el-dropdown-item command="small" :disabled="elementSize === 'small'">小</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useStore } from "vuex";
import { Operation } from "@element-plus/icons-vue";

const store = useStore();
const elementSize = computed(() => store.state.app.elementSize || "default");

const handleSizeCommand = (command: "large" | "default" | "small") => {
  store.commit("app/stateChange", { name: "elementSize", value: command });
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
