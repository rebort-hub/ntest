<template>
  <el-container style="height: 100vh">
    <div
        class="mask"
        v-show="!isCollapse && !contentFullScreen"
        @click="hideMenu"
    ></div>
    <el-aside
        :width="isCollapse ? '60px' : '200px'"
        :class="isCollapse ? 'hide-aside' : 'show-side'"
        v-show="!contentFullScreen"
    >
      <!-- 菜单上面的logo -->
      <Logo />
      <Menu/>
    </el-aside>

    <el-container>
      <el-header v-show="!contentFullScreen">
        <Header/>
      </el-header>
      <!-- 打开页面的tabs -->
      <Tabs v-show="showTabs && !contentFullScreen"/>

      <el-main>
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
.el-header {
  padding-left: 0;
  padding-right: 0;
}

.el-aside {
  display: flex;
  flex-direction: column;
  transition: 0.2s;
  overflow-x: hidden;
  transition: 0.3s;
  background-color: var(--theme-menuBar, var(--system-menu-background));

  &::-webkit-scrollbar {
    width: 0 !important;
  }
}

.el-main {
  background-color: var(--system-container-background);
  height: 100%;
  padding: 0;
  overflow-x: hidden;
}

:deep(.el-main-box) {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  box-sizing: border-box;
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
