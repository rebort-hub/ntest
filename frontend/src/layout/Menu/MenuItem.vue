<template>
  <template v-if="!menu.hideMenu">
    <el-sub-menu v-if="showMenuType === 2" :index="pathResolve" :show-timeout="0" :hide-timeout="0">
      <template #title>
        <!-- 混合图标系统：优先使用SVG，回退到字体图标 -->
        <SvgIcon 
          v-if="useSvgIcon(menu.meta.icon)"
          class="el-menu-item-icon" 
          :name="getSvgIconName(menu.meta.icon)"
          size="18px"
        />
        <i 
          v-else
          class="el-menu-item-icon sfont" 
          :class="getFontIcon(menu.meta.icon)" 
        ></i>
        <span>{{ menu.meta.title }}</span>
      </template>
      <menu-item v-for="(item, key) in menu.children" :key="key" :menu="item" :basePath="pathResolve" />
    </el-sub-menu>
    <app-link v-else-if="showMenuType === 1" :to="pathResolve">
      <el-menu-item :index="pathResolve" v-if="!menu.children[0].children || menu.children[0].children.length === 0">
        <!-- 混合图标系统 -->
        <SvgIcon 
          v-if="useSvgIcon(menu.children[0].meta.icon || menu.meta.icon)"
          class="el-menu-item-icon" 
          :name="getSvgIconName(menu.children[0].meta.icon || menu.meta.icon)"
          size="18px"
        />
        <i 
          v-else
          class="el-menu-item-icon sfont" 
          :class="getFontIcon(menu.children[0].meta.icon || menu.meta.icon)" 
        ></i>
        <template #title>{{ menu.children[0].meta.title }}</template>
      </el-menu-item>
      <el-sub-menu v-else :index="pathResolve" :show-timeout="0" :hide-timeout="0">
        <template #title>
          <!-- 混合图标系统 -->
          <SvgIcon 
            v-if="useSvgIcon(menu.children[0].meta.icon || menu.meta.icon)"
            class="el-menu-item-icon" 
            :name="getSvgIconName(menu.children[0].meta.icon || menu.meta.icon)"
            size="18px"
          />
          <i 
            v-else
            class="el-menu-item-icon sfont" 
            :class="getFontIcon(menu.children[0].meta.icon || menu.meta.icon)" 
          ></i>
          <span>{{ menu.children[0].meta.title }}</span>
        </template>
        <menu-item v-for="(item, key) in menu.children[0].children" :key="key" :menu="item" :basePath="pathResolve" />
      </el-sub-menu>
    </app-link>
    <app-link v-else :to="pathResolve">
      <el-menu-item :index="pathResolve">
        <!-- 混合图标系统 -->
        <SvgIcon 
          v-if="useSvgIcon(menu.meta.icon)"
          class="el-menu-item-icon" 
          :name="getSvgIconName(menu.meta.icon)"
          size="18px"
        />
        <i 
          v-else
          class="el-menu-item-icon sfont" 
          :class="getFontIcon(menu.meta.icon)" 
        ></i>
        <template #title>{{ menu.meta.title }}</template>
      </el-menu-item>
    </app-link>
  </template>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import appLink from './Link.vue'
import SvgIcon from '@/components/SvgIcon/index.vue'
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
    SvgIcon
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

    // 🎯 SVG图标优先列表 - 这些图标使用SVG，其他使用字体图标
    const svgIconList = [
      'api',           // 🔌 API接口
      'android',       // 📱 安卓
      'devices',       // 📱 设备
      'permissions',   // 🔐 权限
      'calendar',      // 📅 日历
      'alarm',         // ⚠️ 警告
      'branchTwo',     // 🌳 分支
      'bookOpen',      // 📚 书本
      'folderOpen',    // 📁 文件夹
      'tool',          // 🔧 工具
      'comment',       // 💬 评论
      'mindmapMap'     // 🗺️ 地图
    ]

    // 判断是否使用SVG图标
    const useSvgIcon = (iconName: string): boolean => {
      return iconName && svgIconList.includes(iconName)
    }

    // SVG图标名称映射
    const getSvgIconName = (iconName: string): string => {
      const svgMapping: { [key: string]: string } = {
        'api': 'api',
        'android': 'mobile',
        'devices': 'device',
        'permissions': 'permission',
        'calendar': 'calendar',
        'alarm': 'warning',
        'branchTwo': 'branch',
        'bookOpen': 'book',
        'folderOpen': 'folder',
        'tool': 'tool',
        'comment': 'comment',
        'mindmapMap': 'map'
      }
      return svgMapping[iconName] || 'tool'
    }

    // 字体图标映射 - 保留现有的完美匹配图标
    const getFontIcon = (iconName: string) => {
      if (!iconName) return 'system-shezhi'
      
      const fontIconMap: { [key: string]: string } = {
        // === 完美匹配的字体图标（保留） ===
        'home': 'system-home',           // ✅ 首页图标
        'system': 'system-shezhi',       // ✅ 系统设置图标
        'user': 'system-yonghu',         // ✅ 用户图标
        'people': 'system-yonghu',       // ✅ 人员图标
        'chartHistogram': 'system-chart',     // ✅ 图表图标
        'chartHistogramOne': 'system-chart',  // ✅ 图表图标
        'chartProportion': 'system-chart',    // ✅ 图表图标
        
        // === 设置相关 - 统一使用设置图标 ===
        'setting': 'system-shezhi',
        'settingTwo': 'system-shezhi',
        'settingThree': 'system-shezhi',
        
        // === 组件相关 - 统一使用组件图标 ===
        'cubeFive': 'system-component',
        'figmaComponent': 'system-component',
        
        // === 菜单相关 - 统一使用菜单图标 ===
        'hamburgerButton': 'system-menu',
        
        // === 其他保留的字体图标 ===
        // 注意：api, android, devices, permissions, calendar, alarm, branchTwo, 
        // bookOpen, folderOpen, tool, comment, mindmapMap 现在使用SVG图标
      }
      
      return fontIconMap[iconName] || 'system-shezhi'
    }

    return {
      showMenuType,
      pathResolve,
      isBackMenu,
      useSvgIcon,
      getSvgIconName,
      getFontIcon
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

/* 通用图标样式 - 适用于字体图标和SVG图标 */
.el-menu-item .el-menu-item-icon,
.el-sub-menu__title .el-menu-item-icon {
  padding-right: 8px;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 20px !important;
  height: 20px !important;
  font-size: 18px !important;
  flex-shrink: 0 !important;
  
  /* 字体图标样式 */
  &.sfont {
    font-family: "sfont" !important;
    font-style: normal;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  /* SVG图标样式 */
  &.svg-icon {
    fill: currentColor;
    color: inherit;
  }
}

/* 确保SVG图标继承颜色 */
:deep(.svg-icon) {
  color: inherit !important;
  fill: currentColor !important;
}
</style>
