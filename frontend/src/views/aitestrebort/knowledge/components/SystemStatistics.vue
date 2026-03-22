<template>
  <div v-loading="loading" class="system-statistics">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #409eff;">
              <el-icon><Collection /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.total_knowledge_bases || 0 }}</div>
              <div class="stat-label">知识库总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #67c23a;">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.total_documents || 0 }}</div>
              <div class="stat-label">文档总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e6a23c;">
              <el-icon><Loading /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.processing_documents || 0 }}</div>
              <div class="stat-label">处理中文档</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #f56c6c;">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.total_chunks || 0 }}</div>
              <div class="stat-label">分块总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>系统状态</span>
          <el-button type="text" @click="loadStats">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div class="system-status">
        <el-tag
          :type="getStatusType(stats.system_status)"
          size="large"
        >
          {{ getStatusText(stats.system_status) }}
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Collection, Document, Loading, Grid, Refresh } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type SystemStatus } from '@/api/aitestrebort/knowledge-enhanced'

interface Props {
  projectId: number
}

defineProps<Props>()

const loading = ref(false)
const stats = ref<SystemStatus>({
  total_knowledge_bases: 0,
  total_documents: 0,
  processing_documents: 0,
  total_chunks: 0,
  system_status: 'healthy'
})

const loadStats = async () => {
  loading.value = true
  try {
    const response = await knowledgeEnhancedApi.system.getSystemStatus()
    if (response.data) {
      stats.value = response.data
    }
  } catch (error) {
    console.error('加载系统统计失败:', error)
    ElMessage.error('加载系统统计失败')
  } finally {
    loading.value = false
  }
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    healthy: 'success',
    warning: 'warning',
    error: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    healthy: '系统正常',
    warning: '系统警告',
    error: '系统异常'
  }
  return texts[status] || '未知状态'
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.system-statistics {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.system-status {
  text-align: center;
  padding: 20px;
}
</style>
