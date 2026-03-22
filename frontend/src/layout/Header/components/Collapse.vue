<template>
  <div class="collapse-btn" @click="changeCollapse">
    <el-icon :size="18">
      <Expand v-if="isCollapse" />
      <Fold v-else />
    </el-icon>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useStore } from "vuex";
import { Fold, Expand } from "@element-plus/icons-vue";

const store = useStore();
const isCollapse = computed(() => store.state.app.isCollapse);

const changeCollapse = () => {
  store.commit("app/isCollapseChange", !isCollapse.value);
};
</script>

<style lang="scss" scoped>
.collapse-btn {
  width: 36px;
  height: 36px;
  margin-left: 12px;
  margin-right: 10px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--system-header-text-color);
  transition: background-color 0.2s ease;

  &:hover {
    background-color: var(--system-header-item-hover-color);
  }
}
</style>
