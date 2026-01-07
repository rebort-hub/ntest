<template>
  <el-scrollbar>
    <el-menu
      class="layout-menu system-scrollbar"
      :background-color="menuBackgroundColor"
      :text-color="menuTextColor"
      :active-text-color="menuActiveTextColor"
      :default-active="activeMenu"
      :class="isCollapse? 'collapse': ''"
      :collapse="isCollapse"
      :collapse-transition="false"
      :unique-opened="expandOneMenu"
    >
      <menu-item v-for="(menu, key) in allRoutes" :key="key" :menu="menu" />
    </el-menu>
  </el-scrollbar>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import MenuItem from './MenuItem.vue'
export default defineComponent({
  components: {
    MenuItem
  },
  setup() {
    const isAdmin: string = localStorage.getItem('isAdmin') || '0'
    const userPermissions: Array = JSON.parse(localStorage.getItem('permissions') || '[]')  // 用户的权限
    const store = useStore()
    const isCollapse = computed(() => store.state.app.isCollapse)
    const expandOneMenu = computed(() => store.state.app.expandOneMenu)
    const allRoutes = useRouter().options.routes

    // 主题配置相关的计算属性
    const menuBackgroundColor = computed(() => {
      const root = document.documentElement;
      return getComputedStyle(root).getPropertyValue('--theme-menuBar') || '#2b2f3a';
    });
    
    const menuTextColor = computed(() => {
      const root = document.documentElement;
      return getComputedStyle(root).getPropertyValue('--theme-menuBarColor') || '#eaeaea';
    });
    
    const menuActiveTextColor = computed(() => {
      const root = document.documentElement;
      return getComputedStyle(root).getPropertyValue('--theme-menuBarActiveColor') || '#409eff';
    });

    // 把没有权限的菜单标记为隐藏，不展示给用户
    let menuPath = ''
    const filterMenu = (routes: any[]) => {
      if (routes instanceof Array){
        routes.forEach(menu => {
          // 检查路由meta中的hideMenu或hidden属性
          if (menu.meta && (menu.meta.hideMenu || menu.meta.hidden)) {
            menu.hideMenu = true
            return
          }
          
          if (menu.redirect){  // 一级菜单
            menuPath = menu.path
            if (isAdmin !== '1' && userPermissions.indexOf(menu.path) === -1){
              menu.hideMenu = true
            }
          }
          if (menu.children){  // 有子菜单
            menu.children.forEach((childMenu: any[]) => {
              filterMenu(childMenu)
            })
          }
        })
      }else {
        // 检查路由meta中的hideMenu或hidden属性
        if (routes.meta && (routes.meta.hideMenu || routes.meta.hidden)) {
          routes.hideMenu = true
          return
        }
        
        if (isAdmin !== '1' && userPermissions.indexOf(`${menuPath}/${routes.path}`) === -1){
          routes.hideMenu = true
        }
      }
    }
    filterMenu(allRoutes)

    // TODO 去除没有权限的路由地址
    const route = useRoute()
    const activeMenu: any = computed(() => {
      const { meta, path } = route;
      if (meta.activeMenu) {
        return meta.activeMenu;
      }
      return path;
    });
    onMounted(() => {

    })
    return {
      isCollapse,
      expandOneMenu,
      allRoutes,
      activeMenu,
      menuBackgroundColor,
      menuTextColor,
      menuActiveTextColor,
    }
  }
})
</script>

<style lang="scss" scoped>
.el-scrollbar {
  background-color: var(--theme-menuBar, #2b2f3a);
}

.layout-menu {
  width: 100%;
  border: none;
  background-color: var(--theme-menuBar, #2b2f3a);
  
  &.collapse {
    margin-left: 0px;
    
    :deep(.el-menu-item) {
      padding: 0 20px !important;
      justify-content: center;
      
      .el-menu-item-icon,
      .icon-park-icon {
        margin-right: 0 !important;
        padding-right: 0 !important;
        width: 24px !important;
        height: 24px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        flex-shrink: 0 !important;
        
        /* 字体图标样式 */
        &.sfont {
          font-family: "sfont" !important;
          font-style: normal;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
        
        /* 强制显示SVG */
        svg {
          display: block !important;
          width: 18px !important;
          height: 18px !important;
          fill: currentColor !important;
          stroke: currentColor !important;
        }
      }
      
      .el-tooltip__trigger {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
      }
    }
    
    :deep(.el-sub-menu) {
      .el-sub-menu__title {
        padding: 0 20px !important;
        justify-content: center;
        
        .el-menu-item-icon,
        .icon-park-icon {
          margin-right: 0 !important;
          padding-right: 0 !important;
          width: 24px !important;
          height: 24px !important;
          display: inline-flex !important;
          align-items: center !important;
          justify-content: center !important;
          font-size: 18px !important;
          flex-shrink: 0 !important;
          
          /* 字体图标样式 */
          &.sfont {
            font-family: "sfont" !important;
            font-style: normal;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }
          
          /* 强制显示SVG */
          svg {
            display: block !important;
            width: 18px !important;
            height: 18px !important;
            fill: currentColor !important;
            stroke: currentColor !important;
          }
        }
        
        .el-sub-menu__icon-arrow {
          display: none;
        }
      }
    }
  }
  
  :deep() {
    .el-menu-item, .el-sub-menu {
      background-color: var(--theme-menuBar, #2b2f3a) !important;
      color: var(--theme-menuBarColor, #eaeaea) !important;
    }
    
    .el-menu-item i, 
    .el-menu-item-group__title, 
    .el-sub-menu__title i,
    .el-menu-item .el-menu-item-icon,
    .el-sub-menu__title .el-menu-item-icon {
      color: var(--theme-menuBarColor, #eaeaea) !important;
    }
    
    .el-sub-menu__title {
      color: var(--theme-menuBarColor, #eaeaea) !important;
    }
    
    .el-menu-item-icon {
      width: 20px;
      height: 20px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      margin-right: 8px;
      flex-shrink: 0;
      
      /* 字体图标样式 */
      &.sfont {
        font-family: "sfont" !important;
        font-style: normal;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }
    }
    
    .el-menu-item, .el-sub-menu__title {
      &.is-active {
        background-color: var(--theme-menuBarActiveColor, #409eff) !important;
        color: #ffffff !important;
        
        i, .el-menu-item-icon {
          color: #ffffff !important;
        }
        
        &:hover {
          background-color: var(--theme-menuBarActiveColor, #409eff) !important;
          color: #ffffff !important;
        }
      }
      
      &:hover {
        background-color: var(--theme-menuBar-light-1, #2f3349) !important;
      }
    }
    
    .el-sub-menu {
      &.is-active {
        > .el-sub-menu__title, 
        > .el-sub-menu__title i, 
        > .el-sub-menu__title .el-menu-item-icon {
          color: var(--theme-menuBarActiveColor, #409eff) !important;
        }
      }
      
      .el-menu-item {
        background-color: var(--theme-menuBar-light-1, #2f3349) !important;
        
        &.is-active {
          background-color: var(--theme-menuBarActiveColor, #409eff) !important;
          color: #ffffff !important;
          
          i, .el-menu-item-icon {
            color: #ffffff !important;
          }
          
          &:hover {
            background-color: var(--theme-menuBarActiveColor, #409eff) !important;
            color: #ffffff !important;
          }
        }
        
        &:hover {
          background-color: var(--theme-menuBar-light-1, #2f3349) !important;
        }
      }
      
      .el-sub-menu {
        .el-sub-menu__title {
          background-color: var(--theme-menuBar-light-1, #2f3349) !important;
          
          &:hover {
            background-color: var(--theme-menuBar-light-1, #2f3349) !important;
          }
        }
      }
    }
  }
}
</style>
