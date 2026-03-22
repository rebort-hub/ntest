<template>
  <div class="tool-item" @click="toggleDarkMode">
    <el-tooltip :content="isDark ? '切换为浅色' : '切换为深色'" placement="bottom">
      <el-icon :size="16">
        <Sunny v-if="isDark" />
        <Moon v-else />
      </el-icon>
    </el-tooltip>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { Moon, Sunny } from "@element-plus/icons-vue";

const isDark = ref(document.body.getAttribute("data-theme") === "dark");

const syncDarkState = () => {
  isDark.value = document.body.getAttribute("data-theme") === "dark";
};

const toggleDarkMode = () => {
  const nextDark = !isDark.value;
  window.dispatchEvent(new CustomEvent("toggle-theme-mode", {
    detail: { isDark: nextDark }
  }));
  isDark.value = nextDark;
};

onMounted(() => {
  window.addEventListener("theme-mode-changed", syncDarkState);
});

onBeforeUnmount(() => {
  window.removeEventListener("theme-mode-changed", syncDarkState);
});
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
