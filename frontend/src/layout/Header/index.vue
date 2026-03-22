<template>
  <div class="header-box">
    <div class="header-left">
      <Collapse />
      <Breadcrumb />
    </div>
    <Toolbar />
  </div>
</template>

<script lang="ts" setup>
import Collapse from "./components/Collapse.vue";
import Breadcrumb from './Breadcrumb.vue'
import Toolbar from "./components/Toolbar.vue";
</script>

<style lang="scss" scoped>
.header-box {
  display: flex;
  align-items: center;
  height: $aside-header-height;
  width: 100%;
  background-color: var(--el-header-bg-color, var(--system-header-background));
  color: var(--theme-topBarColor, var(--system-header-text-color));
  padding-right: 14px;
  transition: all 0.3s ease;
}

.header-left {
  flex: 1;
  min-width: 0;
  height: 100%;
  display: flex;
  align-items: center;
  overflow: hidden;
  white-space: nowrap;
}
</style>
