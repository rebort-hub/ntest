<template>
  <el-container class="layout-shell-container">
    <div
        class="mask"
        v-show="!isCollapse && !contentFullScreen"
        @click="hideMenu"
    ></div>
    <el-aside
        class="layout-aside"
        :width="isCollapse ? '56px' : '200px'"
        :class="isCollapse ? 'hide-aside' : 'show-side'"
        v-show="!contentFullScreen"
    >
      <!-- 菜单上面的logo -->
      <Logo />
      <el-scrollbar class="layout-scrollbar">
        <Menu/>
      </el-scrollbar>
    </el-aside>

    <el-container>
      <el-header class="layout-header" v-show="!contentFullScreen">
        <Header/>
      </el-header>
      <!-- 打开页面的tabs -->
      <Tabs v-show="showTabs && !contentFullScreen"/>

      <el-main class="layout-main">
        <router-view v-slot="{ Component, route }">
            <transition :name="route.meta.transition || 'fade-transform'" mode="out-in">
              <keep-alive v-if="keepAliveComponentsName" :include="keepAliveComponentsName">
                <component :is="Component" :key="route.fullPath"/>
              </keep-alive>
              <component v-else :is="Component" :key="route.fullPath"/>
            </transition>
          </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script lang="ts">
import {defineComponent, computed, onBeforeMount, ref, watch} from "vue";
import {useStore} from "vuex";
import {useRouter} from "vue-router";
import {useEventListener} from "@vueuse/core";
import Menu from "./Menu/index.vue";
import Logo from "./Logo/index.vue";
import Header from "./Header/index.vue";
import Tabs from "./Tabs/index.vue";

export default defineComponent({
  components: {
    Menu,
    Logo,
    Header,
    Tabs,
  },
  setup() {
    const store = useStore();
    const showTabsRef = ref(false);
    
    // computed
    const isCollapse = computed(() => store.state.app.isCollapse);
    const contentFullScreen = computed(() => store.state.app.contentFullScreen);
    
    // Logo显示状态从localStorage读取
    const showLogo = computed(() => {
      const savedConfig = localStorage.getItem('simpleThemeConfig');
      if (savedConfig) {
        try {
          const config = JSON.parse(savedConfig);
          return config.isShowLogo !== false; // 默认显示
        } catch (error) {
          return true;
        }
      }
      return true;
    });
    
    // 标签页显示状态 - 响应式更新
    const updateShowTabs = () => {
      const savedConfig = localStorage.getItem('simpleThemeConfig');
      if (savedConfig) {
        try {
          const config = JSON.parse(savedConfig);
          showTabsRef.value = config.showTabs === true;
        } catch (error) {
          showTabsRef.value = false;
        }
      } else {
        showTabsRef.value = false;
      }
    };
    
    const showTabs = computed(() => showTabsRef.value);
    
    // 监听localStorage变化
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'simpleThemeConfig') {
        updateShowTabs();
      }
    };
    
    // 监听自定义事件（主题设置组件触发）
    const handleThemeChange = () => {
      updateShowTabs();
    };
    
    const keepAliveComponentsName = computed(() => store.getters['keepAlive/keepAliveComponentsName']);
    
    // 页面宽度变化监听后执行的方法
    const resizeHandler = () => {
      if (document.body.clientWidth <= 1000 && !isCollapse.value) {
        store.commit("app/isCollapseChange", true);
      } else if (document.body.clientWidth > 1000 && isCollapse.value) {
        store.commit("app/isCollapseChange", false);
      }
    };
    
    // 初始化调用
    resizeHandler();
    updateShowTabs();
    
    // beforeMount
    onBeforeMount(() => {
      // 监听页面变化
      useEventListener("resize", resizeHandler);
      // 监听localStorage变化
      useEventListener("storage", handleStorageChange);
      // 监听主题变化事件
      useEventListener("themeConfigChanged", handleThemeChange);
    });
    
    // methods
    // 隐藏菜单
    const hideMenu = () => {
      store.commit("app/isCollapseChange", true);
    };
    
    return {
      isCollapse,
      showLogo,
      showTabs,
      contentFullScreen,
      keepAliveComponentsName,
      hideMenu,
    };
  },
});
</script>

<style lang="scss" scoped>
/* 用 100% 替代 100vw，避免滚动条占位导致整页横向溢出与底部多一条横向滚动条 */
.layout-shell-container {
  width: 100%;
  max-width: 100%;
  height: 100vh;
  box-sizing: border-box;
  overflow-x: hidden;
}

.el-header {
  padding-left: 0;
  padding-right: 0;
}

.layout-aside {
  display: flex;
  flex-direction: column;
  z-index: $layout-aside-z-index;
  padding-left: $aside-menu-padding-left;
  padding-right: $aside-menu-padding-right;
  transition: 0.2s;
  overflow-x: hidden;
  transition: 0.3s;
  background-color: var(--el-menu-bg-color, var(--system-menu-background));
  box-shadow: $aside-menu-box-shadow;

  &::-webkit-scrollbar {
    width: 0 !important;
  }
}

.layout-header {
  height: $aside-header-height;
  background-color: var(--el-header-bg-color, var(--system-header-background));
}

.layout-scrollbar {
  width: 100%;
  height: calc(100vh - $aside-header-height);
}

.layout-main {
  background-color: var(--system-container-background);
  height: 100%;
  padding: 0;
  overflow-x: hidden;
}

:deep(.el-main-box) {
  width: 100%;
  max-width: 100%;
  height: 100%;
  min-height: 0;
  box-sizing: border-box;
  overflow-y: auto;
  /* 页面级横向溢出收口在此，宽表由内层 .el-table__body-wrapper 横向滚动 */
  overflow-x: hidden;
  scrollbar-gutter: stable;
  scrollbar-width: thin;
  scrollbar-color: rgba(144, 147, 153, 0.45) transparent;
}

:deep(.el-main-box)::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

:deep(.el-main-box)::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.35);
  border-radius: 6px;
}

:deep(.el-main-box)::-webkit-scrollbar-thumb:hover {
  background: rgba(144, 147, 153, 0.55);
}

@media screen and (max-width: 1000px) {
  .el-aside {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;

    &.hide-aside {
      left: -250px;
    }
  }
  .mask {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 999;
    background: rgba(0, 0, 0, 0.5);
  }
}
</style>
