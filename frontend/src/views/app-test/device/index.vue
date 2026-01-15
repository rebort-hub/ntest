<template>
  <div class="layout-container">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-left">
        <div class="page-icon" :class="activeName">
          <el-icon v-if="activeName === 'server'"><Monitor /></el-icon>
          <el-icon v-else><Iphone /></el-icon>
        </div>
        <div class="page-info">
          <h3 class="page-title">APP自动化测试</h3>
          <span class="page-subtitle">
            {{ activeName === 'server' ? 'Appium服务器管理' : '手机设备管理' }}
          </span>
        </div>
        <div class="status-indicator">
          <el-tag :type="activeName === 'server' ? 'primary' : 'success'" size="small">
            {{ activeName === 'server' ? '服务器模式' : '设备模式' }}
          </el-tag>
        </div>
        <el-button 
          type="primary" 
          :icon="Plus" 
          @click="showAddDrawer"
          size="small"
          class="add-button"
        >
          添加{{ activeName === 'server' ? 'Appium服务器' : '手机设备' }}
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeName" style="margin: 10px">
      <el-tab-pane name="server" label="appium执行服务器">
        <serverView v-if="activeName === 'server'"/>
      </el-tab-pane>

      <el-tab-pane name="phone" label="手机设备管理">
        <phoneView v-if="activeName === 'phone'"/>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import {ref} from "vue";
import {Plus, Monitor, Iphone} from "@element-plus/icons-vue";
import {bus, busEvent} from "@/utils/bus-events";
import serverView from './server/index.vue'
import phoneView from './phone/index.vue'

const activeName = ref('server')
const showAddDrawer = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: `add-${activeName.value}`})
}
</script>

<style scoped lang="scss">
// 简洁的样式优化，保持Element Plus原生风格
.layout-container {
  .page-header {
    padding: 16px 20px;
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    margin-bottom: 0;

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;

      .page-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
        transition: all 0.3s ease;

        &.server {
          background: linear-gradient(135deg, #409eff, #67c23a);
        }

        &.phone {
          background: linear-gradient(135deg, #f093fb, #f5576c);
        }
      }

      .page-info {
        flex: 1;
        
        .page-title {
          margin: 0 0 4px 0;
          font-size: 18px;
          font-weight: 600;
          color: #303133;
        }

        .page-subtitle {
          font-size: 14px;
          color: #909399;
          transition: all 0.3s ease;
        }
      }

      .status-indicator {
        margin-right: 12px;
      }

      .add-button {
        margin-left: auto;
      }
    }
  }

  :deep(.el-tabs__header) {
    background: #fafafa;
    border-radius: 4px 4px 0 0;
    margin: 0;
  }
  
  :deep(.el-tabs__item) {
    &:hover {
      color: #409eff;
    }
  }
  
  :deep(.el-table) {
    border-radius: 4px;
    overflow: hidden;
    
    .el-table__header-wrapper {
      th {
        background: #f5f7fa;
      }
    }
    
    .el-table__body-wrapper {
      tr:hover > td {
        background-color: #f5f7fa !important;
      }
    }
  }
}
</style>
