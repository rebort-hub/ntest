<template>
  <div class="system-statistics">
    <!-- 总览统计 -->
    <div class="overview-stats">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-icon knowledge">
                <el-icon><Collection /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_knowledge_bases }}</div>
                <div class="stat-label">知识库总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-icon documents">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_documents }}</div>
                <div class="stat-label">文档总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-icon requirements">
                <el-icon><Tickets /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_requirements }}</div>
                <div class="stat-label">需求总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-icon chunks">
                <el-icon><Grid /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_chunks }}</div>
                <div class="stat-label">分块总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 详细统计 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 知识库统计 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>知识库统计</span>
              <el-button type="text" @click="refreshStats">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          
          <div class="knowledge-base-stats">
            <div class="stat-row">
              <span class="label">活跃知识库:</span>
              <span class="value">{{ stats.active_knowledge_bases }}</span>
            </div>
            <div class="stat-row">
              <span class="label">禁用知识库:</span>
              <span class="value">{{ stats.inactive_knowledge_bases }}</span>
            </div>
            <div class="stat-row">
              <span class="label">平均文档数:</span>
              <span class="value">{{ averageDocuments }}</span>
            </div>
            <div class="stat-row">
              <span class="label">平均分块数:</span>
              <span class="value">{{ averageChunks }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 文档处理统计 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>文档处理统计</span>
          </template>
          
          <div class="document-stats">
            <div class="stat-row">
              <span class="label">已处理文档:</span>
              <span class="value success">{{ stats.processed_documents }}</span>
            </div>
            <div class="stat-row">
              <span class="label">处理中文档:</span>
              <span class="value warning">{{ stats.processing_documents }}</span>
            </div>
            <div class="stat-row">
              <span class="label">失败文档:</span>
              <span class="value danger">{{ stats.failed_documents }}</span>
            </div>
            <div class="stat-row">
              <span class="label">处理成功率:</span>
              <span class="value">{{ processingSuccessRate }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 需求统计 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>需求类型分布</span>
          </template>
          
          <div class="requirement-type-stats">
            <div
              v-for="(count, type) in stats.requirement_type_distribution"
              :key="type"
              class="type-stat-item"
            >
              <div class="type-info">
                <el-tag :type="getTypeColor(type)" size="small">
                  {{ getTypeText(type) }}
                </el-tag>
                <span class="count">{{ count }}</span>
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  :style="{ width: (count / stats.total_requirements * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>需求优先级分布</span>
          </template>
          
          <div class="requirement-priority-stats">
            <div
              v-for="(count, priority) in stats.requirement_priority_distribution"
              :key="priority"
              class="priority-stat-item"
            >
              <div class="priority-info">
                <el-tag :type="getPriorityColor(priority)" size="small">
                  {{ getPriorityText(priority) }}
                </el-tag>
                <span class="count">{{ count }}</span>
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  :style="{ width: (count / stats.total_requirements * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统健康状态 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>系统健康状态</span>
          </template>
          
          <div class="health-status">
            <div class="health-item">
              <div class="health-indicator" :class="stats.system_status">
                <div class="indicator-dot"></div>
                <span class="status-text">{{ getSystemStatusText(stats.system_status) }}</span>
              </div>
            </div>
            
            <div class="health-details">
              <div class="detail-item">
                <span class="label">最后更新时间:</span>
                <span class="value">{{ formatDate(stats.last_updated) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">数据库连接:</span>
                <span class="value" :class="stats.database_status">{{ stats.database_status }}</span>
              </div>
              <div class="detail-item">
                <span class="label">向量数据库:</span>
                <span class="value" :class="stats.vector_db_status">{{ stats.vector_db_status }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Collection, Document, Tickets, Grid, Refresh } from '@element-plus/icons-vue'
import { requirementsApi } from '@/api/aitestrebort/requirements'

interface Props {
  projectId: number
}

interface SystemStats {
  total_knowledge_bases: number
  active_knowledge_bases: number
  inactive_knowledge_bases: number
  total_documents: number
  processed_documents: number
  processing_documents: number
  failed_documents: number
  total_requirements: number
  total_chunks: number
  requirement_type_distribution: Record<string, number>
  requirement_priority_distribution: Record<string, number>
  system_status: string
  database_status: string
  vector_db_status: string
  last_updated: string
}

const props = defineProps<Props>()

// 响应式数据
const loading = ref(false)
const stats = ref<SystemStats>({
  total_knowledge_bases: 0,
  active_knowledge_bases: 0,
  inactive_knowledge_bases: 0,
  total_documents: 0,
  processed_documents: 0,
  processing_documents: 0,
  failed_documents: 0,
  total_requirements: 0,
  total_chunks: 0,
  requirement_type_distribution: {},
  requirement_priority_distribution: {},
  system_status: 'healthy',
  database_status: 'connected',
  vector_db_status: 'connected',
  last_updated: new Date().toISOString()
})

// 计算属性
const averageDocuments = computed(() => {
  if (stats.value.total_knowledge_bases === 0) return 0
  return Math.round(stats.value.total_documents / stats.value.total_knowledge_bases)
})

const averageChunks = computed(() => {
  if (stats.value.total_documents === 0) return 0
  return Math.round(stats.value.total_chunks / stats.value.total_documents)
})

const processingSuccessRate = computed(() => {
  const total = stats.value.processed_documents + stats.value.failed_documents
  if (total === 0) return 100
  return Math.round((stats.value.processed_documents / total) * 100)
})

// 方法
const loadStats = async () => {
  loading.value = true
  try {
    const response = await requirementsApi.statistics.getProjectStatistics(props.projectId)
    
    if (response.data) {
      stats.value = {
        ...response.data,
        last_updated: new Date().toISOString()
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

const refreshStats = () => {
  loadStats()
  ElMessage.success('统计数据已刷新')
}

// 辅助方法
const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    functional: 'primary',
    'non-functional': 'success',
    business: 'warning',
    user: 'info',
    system: 'danger'
  }
  return colors[type] || 'info'
}

const getTypeText = (type: string) => {
  const texts: Record<string, string> = {
    functional: '功能需求',
    'non-functional': '非功能需求',
    business: '业务需求',
    user: '用户需求',
    system: '系统需求'
  }
  return texts[type] || type
}

const getPriorityColor = (priority: string) => {
  const colors: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return colors[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const texts: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[priority] || priority
}

const getSystemStatusText = (status: string) => {
  const texts: Record<string, string> = {
    healthy: '正常',
    warning: '警告',
    error: '错误'
  }
  return texts[status] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.system-statistics {
  padding: 16px;
}

.stat-card {
  height: 120px;
}

.stat-item {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.stat-icon.knowledge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.documents {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.requirements {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.chunks {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.knowledge-base-stats,
.document-stats {
  padding: 16px 0;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-row:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.label {
  color: #606266;
  font-size: 14px;
}

.value {
  font-weight: bold;
  color: #303133;
}

.value.success {
  color: #67c23a;
}

.value.warning {
  color: #e6a23c;
}

.value.danger {
  color: #f56c6c;
}

.requirement-type-stats,
.requirement-priority-stats {
  padding: 16px 0;
}

.type-stat-item,
.priority-stat-item {
  margin-bottom: 16px;
}

.type-info,
.priority-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.count {
  font-weight: bold;
  color: #303133;
}

.progress-bar {
  height: 6px;
  background-color: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
  transition: width 0.3s ease;
}

.health-status {
  padding: 16px 0;
}

.health-item {
  margin-bottom: 20px;
}

.health-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.indicator-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #67c23a;
}

.health-indicator.warning .indicator-dot {
  background-color: #e6a23c;
}

.health-indicator.error .indicator-dot {
  background-color: #f56c6c;
}

.status-text {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.health-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item .label {
  font-size: 12px;
  color: #909399;
}

.detail-item .value {
  font-size: 14px;
  font-weight: bold;
}

.detail-item .value.connected {
  color: #67c23a;
}

.detail-item .value.disconnected {
  color: #f56c6c;
}
</style>