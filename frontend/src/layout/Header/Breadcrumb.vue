<template>
  <div class="breadcrumb-box">
  <el-breadcrumb class="app-breadcrumb" :separator-icon="ArrowRight">
    <transition-group appear name="breadcrumb">
      <el-breadcrumb-item v-for="(item, index) in levelList" :key="item.path">
        <span
          v-if="item.redirect === 'noRedirect' || index == levelList.length - 1"
          class="no-redirect breadcrumb-title"
        >{{  item.meta.title }}</span>
        <span v-else class="breadcrumb-link breadcrumb-title" @click.prevent="handleLink(item)">{{ item.meta.title }}</span>
      </el-breadcrumb-item>
    </transition-group>
  </el-breadcrumb>
  </div>
</template>

<script lang="ts">
import { ref, defineComponent, watch, Ref } from "vue";
import { useRoute, useRouter, RouteLocationMatched } from "vue-router";
import { ArrowRight } from "@element-plus/icons-vue";
import { isBackMenu } from '@/config'
export default defineComponent({
  name: "BreadCrumb",
  setup() {
    const levelList: Ref<RouteLocationMatched[]> = ref([]);
    const route = useRoute();
    const router = useRouter();
    const getBreadcrumb = (): void => {
      let matched = route.matched.filter(item => item.meta && item.meta.title);
      const first = matched[0];
      levelList.value = matched.filter(
        item => item.meta && item.meta.title && item.meta.breadcrumb !== false
      );
    };
    getBreadcrumb();
    watch(
      () => route.path,
      () => getBreadcrumb()
    );
    const handleLink = (item: RouteLocationMatched): any => {
      const { redirect, path } = item;
      if (redirect) {
        router.push(redirect.toString());
        return;
      }
      router.push(path);
    };
    return { levelList, handleLink, isBackMenu, ArrowRight };
  }
});
</script>

<style lang="scss" scoped >
.breadcrumb-box {
  display: flex;
  align-items: center;
  margin-left: 2px;
  overflow: hidden;
  user-select: none;
}

.app-breadcrumb.el-breadcrumb {
  font-size: 13px;
  line-height: 16px;
  white-space: nowrap;
  .breadcrumb-title {
    font-weight: 400;
  }
  .no-redirect {
    color: var(--system-header-breadcrumb-text-color);
    cursor: text;
  }
  .breadcrumb-link {
    color: var(--system-header-text-color);
    cursor: pointer;
    &:hover {
      color: var(--el-color-primary);
    }
  }
  :deep(.el-breadcrumb__separator) {
    transform: translateY(-1px);
  }
}

.breadcrumb-enter-active {
  transition: all 0.2s;
}

.breadcrumb-enter-from,
.breadcrumb-leave-active {
  opacity: 0;
  transform: translateX(10px);
}

@media screen and (max-width: 768px) {
  .breadcrumb-box {
    display: none;
  }
}
</style>