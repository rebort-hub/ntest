<template>
  <template v-if="!menu.hideMenu">
    <el-sub-menu v-if="showMenuType === 2" :index="pathResolve" :show-timeout="0" :hide-timeout="0">
      <template #title>
        <!-- 使用 Element Plus 图标 -->
        <el-icon class="el-menu-item-icon">
          <component :is="getElementIcon(menu.meta.icon)" />
        </el-icon>
        <span>{{ menu.meta.title }}</span>
      </template>
      <menu-item v-for="(item, key) in menu.children" :key="key" :menu="item" :basePath="pathResolve" />
    </el-sub-menu>
    <app-link v-else-if="showMenuType === 1" :to="pathResolve">
      <el-menu-item :index="pathResolve" v-if="!menu.children[0].children || menu.children[0].children.length === 0">
        <!-- 使用 Element Plus 图标 -->
        <el-icon class="el-menu-item-icon">
          <component :is="getElementIcon(menu.children[0].meta.icon || menu.meta.icon)" />
        </el-icon>
        <template #title>{{ menu.children[0].meta.title }}</template>
      </el-menu-item>
      <el-sub-menu v-else :index="pathResolve" :show-timeout="0" :hide-timeout="0">
        <template #title>
          <!-- 使用 Element Plus 图标 -->
          <el-icon class="el-menu-item-icon">
            <component :is="getElementIcon(menu.children[0].meta.icon || menu.meta.icon)" />
          </el-icon>
          <span>{{ menu.children[0].meta.title }}</span>
        </template>
        <menu-item v-for="(item, key) in menu.children[0].children" :key="key" :menu="item" :basePath="pathResolve" />
      </el-sub-menu>
    </app-link>
    <app-link v-else :to="pathResolve">
      <el-menu-item :index="pathResolve">
        <!-- 使用 Element Plus 图标 -->
        <el-icon class="el-menu-item-icon">
          <component :is="getElementIcon(menu.meta.icon)" />
        </el-icon>
        <template #title>{{ menu.meta.title }}</template>
      </el-menu-item>
    </app-link>
  </template>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import appLink from './Link.vue'
// 导入 Element Plus 图标 - 使用确定存在的图标
import {
  Setting, HomeFilled, User, UserFilled, DataAnalysis, 
  Document, Folder, Calendar, Warning, Key,CreditCard,
  Tools, Connection, Bell, Menu as MenuIcon,FolderOpened,Refrigerator,
  Operation, Monitor, List, Grid, Microphone
} from '@element-plus/icons-vue'
import { isBackMenu } from '@/config'

export default defineComponent({
  name: 'menu-item',
  props: {
    menu: {
      type: Object,
      required: true
    },
    basePath: {
      type: String,
      default: ''
    }
  },
  components: {
    appLink,
    Setting, HomeFilled, User, UserFilled, DataAnalysis, 
    Document, Folder, Calendar, Warning, Key, 
    Tools, Connection, Bell, MenuIcon,
    Operation, Monitor, List, Grid, Microphone
  },
  setup(props) {
    const menu = props.menu
    
    // todo: 优化if结构
    const showMenuType = computed(() => { // 0: 无子菜单， 1：有1个子菜单， 2：显示上下级子菜单
      if (menu.children && (menu.children.length > 1 || (menu.children.length === 1 && menu.alwayShow))) {
        return 2
      } else if (menu.children && menu.children.length === 1 && !menu.alwayShow) {
        return 1
      } else {
        return 0
      }
    })
    
    // todo: 优化多层if
    const pathResolve = computed(() => {
      let path = ''
      if (showMenuType.value === 1) {
        if (menu.children[0].path.charAt(0) === '/') {
          path = menu.children[0].path
        } else {
          let char = '/'
          if (menu.path.charAt(menu.path.length - 1) === '/') {
            char = ''
          }
          path = menu.path + char + menu.children[0].path
        }
      } else {
        path = menu.path
      }
      path = props.basePath ? props.basePath + '/' + path : path
      return path
    })

    // Element Plus 图标映射 - 使用确定存在的图标
    const getElementIcon = (iconName: string): string => {
      const iconMapping: { [key: string]: string } = {
        // 配置管理相关
        'CreditCard': 'CreditCard',
        'settingTwo': 'Setting', 
        'settingThree': 'Setting',
        'mindmapMap': 'Grid',
        'hamburgerButton': 'MenuIcon',
        'comment': 'Bell',
        'key': 'Key',
        
        // 脚本和开发
        'code': 'Document',
        
        // 基础图标
        'home': 'HomeFilled',
        'user': 'User',
        'people': 'UserFilled',
        'system': 'Setting',
        
        // 图表相关
        'chartHistogram': 'DataAnalysis',
        'chartHistogramOne': 'DataAnalysis',
        'chartProportion': 'DataAnalysis',
        
        // UI测试相关
        'bookOpen': 'Document',
        'folderOpen': 'Folder',
        'cubeFive': 'Grid',
        'calendar': 'Calendar',
        
        // 工具相关
        'tool': 'Tools',
        'followUpDateSort': 'Calendar',
        'dataThree': 'DataAnalysis',
        'idCardH': 'User',
        'databaseEnter': 'Connection',
        'userPositioning': 'User',
        'fourArrows': 'Operation',
        
        // 系统管理相关
        'figmaComponent': 'Grid',
        'permissions': 'Key',
        'experiment': 'Tools',
        'alarm': 'Warning',
        
        // 测试管理相关
        'layers': 'Document',
        'leftAndRightBranch': 'Operation',
        'everyUser': 'UserFilled',
        'bug': 'Warning',
        'list': 'List',
        
        // AI驱动生成管理相关
        'Microphone': 'Microphone',
        'FolderOpened':'FolderOpened',
        'Refrigerator':'Refrigerator',
        
        // 其他
        'api': 'Connection',
        'android': 'Monitor',
        'devices': 'Monitor',
        'branchTwo': 'Operation'
      }
      
      return iconMapping[iconName] || 'Setting'
    }

    return {
      showMenuType,
      pathResolve,
      isBackMenu,
      getElementIcon
    }
  }
})
</script>

<style lang="scss" scoped>
.el-sub-menu {
  text-align: left;
}
.el-menu-item {
  text-align: left;
}

/* Element Plus 图标样式 */
.el-menu-item .el-icon,
.el-sub-menu__title .el-icon {
  margin-right: 8px;
  width: 20px;
  height: 20px;
  font-size: 18px;
}
</style>