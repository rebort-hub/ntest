<template>
  <div class="test-execution-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-title">
          <h2>测试执行历史</h2>
          <p>查看和管理测试套件的执行历史记录</p>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="loadExecutions" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary">
          <el-icon><Document /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-number">{{ totalExecutions }}</div>
        <div class="stat-label">总执行次数</div>
      </div>
      <div class="stat-card success">
        <div class="stat-number">{{ successExecutions }}</div>
        <div class="stat-label">成功次数</div>
      </div>
      <div class="stat-card danger">
        <div class="stat-number">{{ failedExecutions }}</div>
        <div class="stat-label">失败次数</div>
      </div>
      <div class="stat-card info">
        <div class="stat-number">{{ averageDuration }}</div>
        <div class="stat-label">平均耗时</div>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <el-form :model="filters" inline>
        <el-form-item>
          <el-input
            v-model="filters.search"
            placeholder="搜索套件名称..."
            style="width: 300px"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-select v-model="filters.status" placeholder="执行状态" clearable @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="执行中" value="running" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="handleFilterChange"
          />
        </el-form-item>
      </el-form>
    </div>

    <!-- 执行历史表格 -->
    <div class="execution-table">
      <el-table :data="executions" v-loading="loading" stripe>
        <el-table-column prop="suite_name" label="测试套件" min-width="200" />
        <el-table-column prop="status" label="执行状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="150" align="center">
          <template #default="{ row }">
            <el-progress 
              :percentage="row.progress" 
              :color="getProgressColor(row.status)"
              :show-text="false"
              style="width: 100px"
            />
            <span style="margin-left: 8px; font-size: 12px;">{{ row.progress }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="执行结果" width="150" align="center">
          <template #default="{ row }">
            <div class="result-stats">
              <span class="success-count">成功: {{ row.passed_count || 0 }}</span>
              <span class="failed-count">失败: {{ row.failed_count || 0 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" align="center">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="text" @click="viewDetail(row)">查看详情</el-button>
            <el-button type="text" @click="viewReport(row)">查看报告</el-button>
            <el-button 
              v-if="row.status === 'running'" 
              type="text" 
              @click="cancelExecution(row)"
              style="color: #f56c6c;"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <div class="pagination-info">
        共 {{ pagination.total }} 条
      </div>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[20, 50, 100]"
        :total="pagination.total"
        layout="sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 执行详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="执行详情"
      width="600px"
    >
      <div v-if="selectedExecution">
        <p>测试套件: {{ selectedExecution.suite_name }}</p>
        <p>执行状态: {{ selectedExecution.status }}</p>
        <p>执行进度: {{ selectedExecution.progress }}%</p>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Refresh, Document, Search } from '@element-plus/icons-vue'
import { getExecutionHistory, cancelExecution as cancelExecutionApi } from '@/api/aitestrebort/testsuite'

const route = useRoute()
const router = useRouter()

// 路由参数
const projectId = computed(() => Number(route.params.projectId))
const suiteId = computed(() => route.query.suiteId ? Number(route.query.suiteId) : undefined)

// 响应式数据
const loading = ref(false)
const executions = ref([])
const showDetailDialog = ref(false)
const selectedExecution = ref(null)

// 筛选条件
const filters = ref({
  search: '',
  status: ''
})
const dateRange = ref([])

// 分页
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 计算属性
const totalExecutions = computed(() => executions.value.length)
const successExecutions = computed(() => executions.value.filter(e => e.status === 'completed' || e.status === 'success').length)
const failedExecutions = computed(() => executions.value.filter(e => e.status === 'failed').length)
const averageDuration = computed(() => {
  if (executions.value.length === 0) return '0秒'
  const total = executions.value.reduce((sum, e) => sum + (e.duration || 0), 0)
  const avg = Math.round(total / executions.value.length / 1000)
  return `${avg}秒`
})

// 方法
const loadExecutions = async () => {
  try {
    loading.value = true
    
    // 调用真实的API
    const response = await getExecutionHistory(projectId.value, undefined, {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      status: filters.value.status,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1],
      search: filters.value.search
    })
    
    if (response.status === 200 && response.data) {
      // 处理后端返回的数据，适配前端字段
      const rawExecutions = response.data.results || response.data
      executions.value = rawExecutions.map(execution => ({
        ...execution,
        duration: execution.execution_time, // 后端返回execution_time，前端期望duration
        start_time: execution.started_at, // 后端返回started_at，前端期望start_time
        progress: execution.status === 'completed' ? 100 : 
                 execution.status === 'running' ? 50 : 
                 execution.status === 'failed' ? 100 : 0, // 计算进度
        executor_name: `用户${execution.executor_id}` // 临时处理，后续可以通过用户ID获取用户名
      }))
      pagination.value.total = response.data.total || executions.value.length
    }
    
  } catch (error) {
    console.error('获取执行历史失败:', error)
    ElMessage.error('获取执行历史失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 实现搜索逻辑
  loadExecutions()
}

const handleFilterChange = () => {
  pagination.value.page = 1
  loadExecutions()
}

const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.page = 1
  loadExecutions()
}

const handleCurrentChange = (page: number) => {
  pagination.value.page = page
  loadExecutions()
}

const viewDetail = (execution) => {
  selectedExecution.value = execution
  showDetailDialog.value = true
}

const viewReport = (execution) => {
  router.push(`/aitestrebort/project/${projectId.value}/test-execution/${execution.id}/report`)
}

const cancelExecution = async (execution) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消这个执行吗？',
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 调用真实的取消API
    await cancelExecutionApi(projectId.value, execution.id)
    ElMessage.success('执行已取消')
    loadExecutions()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消执行失败:', error)
      ElMessage.error('取消执行失败')
    }
  }
}

const goBack = () => {
  if (route.query.from === 'test-suite') {
    router.push(`/aitestrebort/project/${projectId.value}/test-suite`)
  } else {
    router.back()
  }
}

// 辅助方法
const getStatusColor = (status: string) => {
  const colors = {
    success: 'success',
    completed: 'success',
    failed: 'danger',
    running: 'primary',
    cancelled: 'info',
    pending: 'warning'
  }
  return colors[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts = {
    success: '成功',
    completed: '已完成',
    failed: '失败',
    running: '执行中',
    cancelled: '已取消',
    pending: '等待中'
  }
  return texts[status] || status
}

const getProgressColor = (status: string) => {
  if (status === 'success' || status === 'completed') return '#67c23a'
  if (status === 'failed') return '#f56c6c'
  if (status === 'running') return '#409eff'
  return '#e6a23c'
}

const formatDuration = (ms: number) => {
  if (!ms) return '-'
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes > 0) {
    return `${minutes}分${remainingSeconds}秒`
  }
  return `${remainingSeconds}秒`
}

// 生命周期
onMounted(() => {
  loadExecutions()
})
</script>

<style scoped>
.test-execution-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.header-title p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.header-right {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #409eff;
}

.stat-card.success {
  border-left-color: #67c23a;
}

.stat-card.danger {
  border-left-color: #f56c6c;
}

.stat-card.info {
  border-left-color: #909399;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.filter-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.execution-table {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.result-stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
}

.success-count {
  color: #67c23a;
}

.failed-count {
  color: #f56c6c;
}

.pagination-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pagination-info {
  font-size: 14px;
  color: #606266;
}

.pagination-jump {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #606266;
}
</style>