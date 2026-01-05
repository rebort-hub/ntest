<template>
  <header>
    <div class="left-box">
      <!-- 收缩按钮 -->
      <div class="menu-icon" @click="opendStateChange">
        <i class="sfont head-fold" :class="isCollapse ? 'system-s-unfold' : 'system-s-fold'"></i>
      </div>
      <Breadcrumb/>
    </div>
    <div class="right-box">
      <!-- 快捷功能按钮 -->
      <div class="function-list">
        <div class="function-list-item hidden-sm-and-down">
          <el-tooltip content="全屏显示" placement="bottom">
            <el-icon class="function-icon" @click="toggleFullscreen">
              <FullScreen />
            </el-icon>
          </el-tooltip>
        </div>
        <div class="function-list-item hidden-sm-and-down">
          <el-tooltip content="系统公告" placement="bottom">
            <el-icon class="function-icon" @click="showAnnouncement">
              <Bell />
            </el-icon>
          </el-tooltip>
        </div>
        <div class="function-list-item hidden-sm-and-down">
          <el-tooltip content="主题设置" placement="bottom">
            <el-icon class="theme-settings-icon" @click="openThemeSettings">
              <Setting />
            </el-icon>
          </el-tooltip>
        </div>
      </div>
      <!-- 用户信息 -->
      <div class="user-info">
        <el-dropdown>
          <span class="el-dropdown-link">
            {{ userName }}
            <i class="sfont system-xiala"></i>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="resetPassword">重置密码</el-dropdown-item>
              <el-dropdown-item @click="showPasswordLayer">修改密码</el-dropdown-item>
              <el-dropdown-item @click="loginOut">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <password-layer :layer="layer" v-if="layer.show"/>
    </div>
    
    <!-- 主题设置组件 -->
    <ThemeSettings ref="themeSettingsRef" />
  </header>
</template>

<script lang="ts" setup>
import {defineComponent, computed, reactive, ref} from 'vue'
import {useStore} from 'vuex'
import {useRouter, useRoute} from 'vue-router'
import { Setting, FullScreen, Bell } from '@element-plus/icons-vue'
import FullScreenComponent from './functionList/fullscreen.vue'
// import SizeChange from './functionList/sizeChange.vue'
import Theme from './functionList/theme.vue'
import Breadcrumb from './Breadcrumb.vue'
import PasswordLayer from './passwordLayer.vue'
import ThemeSettings from '../../components/ThemeSettings/index.vue'
import {ResetPassword} from "@/api/system/user";

const store = useStore()
const router = useRouter()
const route = useRoute()
const themeSettingsRef = ref()

const layer = reactive({
  show: false,
  showButton: true
})
const userName = localStorage.getItem('userName')
const isCollapse = computed(() => store.state.app.isCollapse)

// isCollapse change to hide/show the sidebar
const opendStateChange = () => {
  store.commit('app/isCollapseChange', !isCollapse.value)
}

const loginOut = () => {
  // 只清除登录相关的localStorage项目，保留主题配置
  const itemsToRemove = [
    'id',
    'accessToken', 
    'refreshToken',
    'userName',
    'account',
    'permissions',
    'business',
    'isAdmin',
    'platform_name',
    'rememberedAccount'
  ];
  
  itemsToRemove.forEach(item => {
    localStorage.removeItem(item);
  });
  
  router.push('/login');
}

const showPasswordLayer = () => {
  layer.show = true
}

const resetPassword = () => {
  ResetPassword({id: localStorage.getItem("id")}).then(response => {})
}

// 打开主题设置
const openThemeSettings = () => {
  themeSettingsRef.value?.openDrawer()
}

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    }
  }
}

// 显示公告
const showAnnouncement = () => {
  // 这里可以后续添加公告功能
  console.log('显示系统公告')
}

</script>

<style lang="scss" scoped>
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  background-color: var(--theme-topBar, var(--system-header-background));
  color: var(--theme-topBarColor, var(--system-header-text-color));
  padding-right: 22px;
  transition: all 0.3s ease;
}

.left-box {
  height: 100%;
  display: flex;
  align-items: center;

  .menu-icon {
    width: 60px;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
    font-weight: 100;
    cursor: pointer;
    margin-right: 10px;

    &:hover {
      background-color: var(--system-header-item-hover-color);
    }

    i {
      color: var(--system-header-text-color);
    }
  }
}

.right-box {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-left: auto;

  .function-list {
    display: flex;

    .function-list-item {
      width: 40px;
      height: 40px;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
      border-radius: 4px;
      transition: background-color 0.3s;

      &:hover {
        background-color: var(--system-header-item-hover-color);
      }

      :deep(i) {
        color: var(--system-header-text-color);
      }

      .function-icon {
        font-size: 18px;
        color: var(--system-header-text-color);
        transition: color 0.3s;

        &:hover {
          color: var(--el-color-primary);
        }
      }

      .theme-settings-icon {
        font-size: 18px;
        color: var(--system-header-text-color);
        transition: color 0.3s;

        &:hover {
          color: var(--el-color-primary);
        }
      }
    }
  }

  .user-info {
    margin-left: 20px;

    .el-dropdown-link {
      color: var(--system-header-breadcrumb-text-color);
    }
  }
}

.head-fold {
  font-size: 20px;
}
</style>
