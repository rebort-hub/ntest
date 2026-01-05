<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-code">404</div>
      <div class="error-message">页面未找到</div>
      <div class="error-description">
        <p>抱歉，您访问的页面不存在或已被移除。</p>
        <div class="debug-info" v-if="showDebugInfo">
          <h4>调试信息：</h4>
          <p><strong>当前路径：</strong>{{ currentPath }}</p>
          <p><strong>用户权限：</strong>{{ userPermissions }}</p>
          <p><strong>是否管理员：</strong>{{ isAdmin ? '是' : '否' }}</p>
        </div>
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上页</el-button>
        <el-button @click="toggleDebug" v-if="isDev">{{ showDebugInfo ? '隐藏' : '显示' }}调试信息</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const showDebugInfo = ref(false)

const isDev = import.meta.env.DEV
const currentPath = computed(() => route.fullPath)
const isAdmin = computed(() => localStorage.getItem('isAdmin') === '1')
const userPermissions = computed(() => {
  try {
    const permissions = localStorage.getItem('permissions')
    return permissions ? JSON.parse(permissions) : []
  } catch {
    return []
  }
})

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}

const toggleDebug = () => {
  showDebugInfo.value = !showDebugInfo.value
}
</script>

<style scoped>
.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.error-content {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  max-width: 600px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 20px;
}

.error-message {
  font-size: 24px;
  color: #303133;
  margin-bottom: 16px;
}

.error-description {
  color: #606266;
  margin-bottom: 32px;
  line-height: 1.6;
}

.debug-info {
  text-align: left;
  background: #f8f9fa;
  padding: 16px;
  border-radius: 4px;
  margin-top: 16px;
  border-left: 4px solid #409eff;
}

.debug-info h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.debug-info p {
  margin: 8px 0;
  font-family: monospace;
  font-size: 14px;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
</style>