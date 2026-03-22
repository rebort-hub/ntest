<template>
  <div class="header-right">
    <SearchMenu />
    <Dimension />
    <RefreshTool />
    <Dark />
    <Language />
    <FullScreen />
    <ThemeSetting />
    <User />
  </div>
</template>

<script setup lang="ts">
import User from "./User.vue";
import FullScreen from "./FullScreen.vue";
import Dark from "./Dark.vue";
import ThemeSetting from "./ThemeSetting.vue";
import RefreshTool from "./Refresh.vue";
import Dimension from "./Dimension.vue";
import Language from "./Language.vue";
import SearchMenu from "./SearchMenu.vue";
</script>

<style lang="scss" scoped>
.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-left: auto;
  gap: 1px;
}

@media screen and (max-width: 768px) {
  .header-right {
    gap: 0;
  }
}
</style>
