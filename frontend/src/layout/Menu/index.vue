<template>
  <el-menu
    class="layout-menu"
    :background-color="menuBackgroundColor"
    :text-color="menuTextColor"
    :active-text-color="menuActiveTextColor"
    :default-active="activeMenu"
    :class="{ 'is-collapse': isCollapse }"
    :collapse="isCollapse"
    :collapse-transition="false"
    :unique-opened="expandOneMenu"
  >
    <menu-item
      v-for="(menu, index) in visibleRoutes"
      :key="`menu-${menu.path}-${index}`"
      :menu="menu"
    />
  </el-menu>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import MenuItem from './MenuItem.vue'

export default defineComponent({
  name: 'LayoutMenu',
  components: {
    MenuItem
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const store = useStore()
    
    // 状态管理
    const isCollapse = computed(() => store.state.app.isCollapse)
    const expandOneMenu = computed(() => store.state.app.expandOneMenu)
    
    // 权限相关
    const isAdmin = localStorage.getItem('isAdmin') === '1'
    const userPermissions = JSON.parse(localStorage.getItem('permissions') || '[]')
    
    // 主题配置
    const menuBackgroundColor = computed(() => {
      return getComputedStyle(document.documentElement)
        .getPropertyValue('--el-menu-bg-color') || '#2b2f3a'
    })
    
    const menuTextColor = computed(() => {
      return getComputedStyle(document.documentElement)
        .getPropertyValue('--el-menu-text-color') || '#eaeaea'
    })
    
    const menuActiveTextColor = computed(() => {
      return getComputedStyle(document.documentElement)
        .getPropertyValue('--el-menu-active-text-color') || '#ffffff'
    })
    
    // 过滤菜单权限
    const filterMenuByPermission = (routes: any[], parentPath = ''): void => {
      routes.forEach(route => {
        // 检查隐藏标记
        if (route.hideMenu || route.meta?.hideMenu || route.meta?.hidden) {
          route.hideMenu = true
          return
        }
        
        // 检查权限
        const fullPath = route.redirect ? route.path : `${parentPath}/${route.path}`.replace(/\/+/g, '/')
        if (!isAdmin && route.redirect && !userPermissions.includes(route.path)) {
          route.hideMenu = true
          return
        }
        
        if (!isAdmin && !route.redirect && !userPermissions.includes(fullPath)) {
          route.hideMenu = true
          return
        }
        
        // 递归处理子菜单
        if (route.children?.length) {
          filterMenuByPermission(route.children, route.path)
        }
      })
    }
    
    // 获取可见路由
    const visibleRoutes = computed(() => {
      const routes = JSON.parse(JSON.stringify(router.options.routes))
      filterMenuByPermission(routes)
      return routes.filter((route: any) => !route.hideMenu)
    })
    
    // 当前激活菜单
    const activeMenu = computed(() => {
      const { meta, path } = route
      return meta.activeMenu || path
    })
    
    return {
      isCollapse,
      expandOneMenu,
      visibleRoutes,
      activeMenu,
      menuBackgroundColor,
      menuTextColor,
      menuActiveTextColor
    }
  }
})
</script>

<style lang="scss" scoped>
// 菜单主容器
.layout-menu {
  width: 100%;
  min-height: calc(100vh - $aside-header-height);
  border: none;
  background-color: var(--el-menu-bg-color, #2b2f3a);
  
  // 折叠状态
  &.is-collapse {
    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      padding: 0 !important;
      justify-content: center;
      
      .el-icon {
        margin-right: 0 !important;
        width: 16px;
        height: 16px;
        font-size: 16px;
      }
      
      // 隐藏子菜单箭头
      .el-sub-menu__icon-arrow {
        display: none !important;
      }
      
      // 隐藏文字
      span {
        display: none;
      }
    }
    
    // 确保折叠状态下的弹出菜单正常显示
    :deep(.el-sub-menu__popup) {
      .el-menu-item,
      .el-sub-menu__title {
        padding: 0 20px !important;
        justify-content: flex-start;
        
        .el-icon {
          margin-right: 8px !important;
          width: 16px !important;
          height: 16px !important;
          font-size: 16px !important;
        }
        
        span {
          display: inline !important;
        }
      }
    }
  }
  
  // 全局菜单样式
  :deep() {
    .el-menu-item,
    .el-sub-menu__title {
      height: $aside-menu-height !important;
      border-radius: 6px;
      margin-bottom: 4px;
      font-weight: 500;
      user-select: none;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    // 菜单项基础样式
    .el-menu-item,
    .el-sub-menu {
      background-color: var(--el-menu-bg-color, #2b2f3a) !important;
      color: var(--el-menu-text-color, #eaeaea) !important;
    }
    
    // 图标样式 - 展开状态使用标准尺寸
    .el-icon {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      flex-shrink: 0 !important;
      width: 16px !important;
      height: 16px !important;
      margin-right: 8px !important;
      font-size: 16px !important;
      color: inherit !important;
      
      svg {
        display: block !important;
        width: 100% !important;
        height: 100% !important;
        fill: currentColor !important;
      }
    }
    
    // 菜单项图标颜色
    .el-menu-item .el-icon,
    .el-sub-menu__title .el-icon {
      color: var(--el-menu-text-color, #eaeaea) !important;
    }
    
    // 激活状态
    .el-menu-item.is-active,
    .el-sub-menu.is-active > .el-sub-menu__title {
      background-color: var(--el-menu-active-bg-color, rgba(64, 158, 255, 0.16)) !important;
      color: var(--el-menu-active-text-color, #ffffff) !important;
      
      .el-icon {
        color: var(--el-menu-active-text-color, #ffffff) !important;
      }
    }
    
    // 悬停状态
    .el-menu-item:hover,
    .el-sub-menu__title:hover {
      background-color: var(--el-menu-hover-bg-color, #2f3349) !important;
      color: var(--el-menu-hover-text-color, #ffffff) !important;
    }

    .el-menu-item.is-active::before {
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      border-left: 2px solid var(--el-menu-border-left-color);
      border-radius: 6px;
    }
    
    // 子菜单样式
    .el-sub-menu {
      :deep(.el-menu) {
        padding-left: 6px;
      }

      .el-menu-item {
        background-color: var(--el-menu-bg-color, #2b2f3a) !important;
        
        &.is-active {
          background-color: var(--el-menu-active-bg-color, rgba(64, 158, 255, 0.16)) !important;
          color: var(--el-menu-active-text-color, #ffffff) !important;
          
          .el-icon {
            color: var(--el-menu-active-text-color, #ffffff) !important;
          }
        }
      }
      
      // 子菜单展开箭头 - 单独控制大小为 12x12
      .el-sub-menu__icon-arrow {
        width: 12px !important;
        height: 12px !important;
        font-size: 12px !important;
        margin-left: auto !important;
      }
    }
    
    // 子菜单标题
    .el-sub-menu__title {
      color: var(--el-menu-text-color, #eaeaea) !important;
    }
  }
}
</style>
