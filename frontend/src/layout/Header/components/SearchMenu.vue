<template>
  <div class="tool-item" @click="openSearch">
    <el-tooltip content="搜索菜单" placement="bottom">
      <el-icon :size="16"><Search /></el-icon>
    </el-tooltip>
  </div>
  <el-dialog class="search-dialog" v-model="showDialog" :width="560" :show-close="false" top="10vh">
    <el-input
      v-model="keyword"
      ref="inputRef"
      placeholder="菜单搜索：支持菜单名称、路径"
      size="large"
      clearable
      :prefix-icon="Search"
    />
    <div v-if="filteredMenus.length" class="menu-list">
      <div v-for="item in filteredMenus" :key="item.path" class="menu-item" @click="goMenu(item.path)">
        <span class="menu-title">{{ item.title }}</span>
        <span class="menu-path">{{ item.path }}</span>
      </div>
    </div>
    <el-empty v-else class="mt20 mb20" :image-size="100" description="暂无匹配菜单" />
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from "vue";
import type { InputInstance } from "element-plus";
import { Search } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";

const router = useRouter();
const showDialog = ref(false);
const keyword = ref("");
const inputRef = ref<InputInstance | null>(null);

type MenuNode = { path: string; title: string; children?: MenuNode[]; meta?: any };
const getMenus = (): MenuNode[] => {
  const rawRoutes: any[] = router.options.routes || [];
  const mapRoute = (route: any, parentPath = ""): MenuNode[] => {
    if (route.meta?.hideMenu || route.meta?.hidden) return [];
    const currentPath = route.path.startsWith("/")
      ? route.path
      : `${parentPath}/${route.path}`.replace(/\/+/g, "/");
    const title = route.meta?.title || "";
    const children = (route.children || []).flatMap((child: any) => mapRoute(child, currentPath));
    const self = title ? [{ path: currentPath, title, children, meta: route.meta }] : [];
    return [...self, ...children];
  };
  return rawRoutes.flatMap(route => mapRoute(route));
};

const menuPool = computed(() => getMenus());
const filteredMenus = computed(() => {
  const key = keyword.value.trim().toLowerCase();
  if (!key) return menuPool.value.slice(0, 12);
  return menuPool.value
    .filter(item => item.title.toLowerCase().includes(key) || item.path.toLowerCase().includes(key))
    .slice(0, 20);
});

const openSearch = () => {
  showDialog.value = true;
  nextTick(() => inputRef.value?.focus());
};

const goMenu = (path: string) => {
  showDialog.value = false;
  keyword.value = "";
  router.push(path);
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

.menu-list {
  max-height: 460px;
  margin-top: 14px;
  overflow: auto;
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  height: 42px;
  padding: 0 14px;
  margin: 8px 0;
  border: 1px solid var(--system-page-border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  &:hover {
    color: var(--el-color-primary);
    border-color: var(--el-color-primary-light-5);
    background: var(--el-color-primary-light-9);
  }
}

.menu-title {
  font-size: 14px;
}

.menu-path {
  font-size: 12px;
  color: var(--system-page-tip-color);
}
</style>
