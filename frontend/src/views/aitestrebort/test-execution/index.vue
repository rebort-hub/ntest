<template>
  <div class="test-execution-history">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" style="margin-right: 16px;">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div>
          <h1 class="page-title">测试执行历史</h1>
          <p class="page-description">查看和管理测试套件的执行历史记录</p>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-container">
      <!-- 统计卡片 -->
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="总执行次数" :value="statistics.total_executions" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card success">
              <el-statistic title="成功次数" :value="statistics.success_count" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card danger">
              <el-statistic title="失败次数" :value="statistics.failed_count" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="平均耗时" :value="statistics.avg_duration" suffix="秒" />
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 搜索和筛选 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索套件名称..."
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.status"
          placeholder="执行状态"
          style="width: 120px; margin-left: 12px"
          clearable
          @change="handleSearch"
        >
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="部分成功" value="partial" />
          <el-option label="已取消" value="cancelled" />
          <el-option label="执行中" value="running" />
        </el-select>

        <el-date-picker
          v-model="searchForm.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="margin-left: 12px"
          @change="handleSearch"
        />
      </div>

      <!-- 执行历史列表 -->
      <el-table :data="executions" v-loading="loading" @row-click="viewExecution">
        <el-table-column prop="suite_name" label="测试套件" min-width="200">
          <template #default="{ row }">
            <el-link @click="viewExecution(row)" :underline="false">{{ row.suite_name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="执行状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="120" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress"
              :status="row.status === 'failed' ? 'exception' : undefined"
              :stroke-width="6"
            />
          </template>
        </el-table-column>
        <el-table-column label="执行结果" width="150" align="center">
          <template #default="{ row }">
            <div class="result-stats">
              <span class="success">成功: {{ row.success_count }}</span>
              <span class="failed">失败: {{ row.failed_count }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" align="center">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="executor_name" label="执行者" width="100" align="center" />
        <el-table-column prop="start_time" label="开始时间" width="150" align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="150" align="center">
          <template #default="{ row }">
            {{ row.end_time ? formatDateTime(row.end_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="text" @click.stop="viewExecution(row)">查看详情</el-button>
            <el-button type="text" @click.stop="viewReport(row)" v-if="row.status !== 'running'">查看报告</el-button>
            <el-button
              type="text"
              @click.stop="cancelExecution(row)"
              v-if="row.status === 'running'"
              style="color: #f56c6c;"
            >
              取消执行
            </el-button>
            <el-button type="text" @click.stop="deleteExecution(row)" style="color: #f56c6c;">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="searchForm.page"
          v-model:page-size="searchForm.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadExecutions"
          @current-change="loadExecutions"
        />
      </div>
    </div>

    <!-- 执行详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="执行详情"
      width="1000px"
    >
      <div v-if="selectedExecution" class="execution-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="测试套件">{{ selectedExecution.suite_name }}</el-descriptions-item>
            <el-descriptions-item label="执行状态">
              <el-tag :type="getStatusColor(selectedExecution.status)" size="small">
                {{ getStatusText(selectedExecution.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="执行进度">{{ selectedExecution.progress }}%</el-descriptions-item>
            <el-descriptions-item label="总耗时">{{ formatDuration(selectedExecution.duration) }}</el-descriptions-item>
            <el-descriptions-item label="执行者">{{ selectedExecution.executor_name }}</el-descriptions-item>
            <el-descriptions-item label="开始时间">{{ formatDateTime(selectedExecution.start_time) }}</el-descriptions-item>
            <el-descriptions-item label="结束时间">
              {{ selectedExecution.end_time ? formatDateTime(selectedExecution.end_time) : '未结束' }}
            </el-descriptions-item>
            <el-descriptions-item label="执行环境">{{ selectedExecution.environment || '默认环境' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 执行统计 -->
        <div class="detail-section">
          <h4>执行统计</h4>
          <el-row :gutter="16">
            <el-col :span="6">
              <el-card class="mini-stat-card success">
                <el-statistic title="成功" :value="selectedExecution.success_count" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="mini-stat-card danger">
                <el-statistic title="失败" :value="selectedExecution.failed_count" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="mini-stat-card warning">
                <el-statistic title="跳过" :value="selectedExecution.skipped_count || 0" />
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="mini-stat-card">
                <el-statistic title="总数" :value="selectedExecution.total_count" />
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 执行项详情 -->
        <div class="detail-section">
          <h4>执行项详情</h4>
          <el-table :data="executionItems" max-height="300">
            <el-table-column prop="name" label="名称" min-width="200" />
            <el-table-column prop="type" label="类型" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.type === 'testcase' ? 'primary' : 'success'" size="small">
                  {{ row.type === 'testcase' ? '测试用例' : '自动化脚本' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusColor(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="耗时" width="100" align="center">
              <template #default="{ row }">
                {{ row.duration ? formatDuration(row.duration) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="开始时间" width="150" align="center">
              <template #default="{ row }">
                {{ row.start_time ? formatDateTime(row.start_time) : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'failed'"
                  type="text"
                  @click="viewItemError(row)"
                >
                  查看错误
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Download, Search, ArrowLeft
} from '@element-plus/icons-vue'

// 获取项目ID
const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.projectId))

// 计算返回路径
const backPath = computed(() => {
  const from = route.query.from as string
  if (from === 'testcase') {
    return `/aitestrebort/project/${projectId.value}/testcase`
  } else if (from === 'test-suite') {
    return `/aitestrebort/project/${projectId.value}/test-suite`
  }
  return '/aitestrebort/project'
})

// 返回方法
const goBack = () => {
  router.push(backPath.value)
}

// 响应式数据
const loading = ref(false)
const showDetailDialog = ref(false)

const executions = ref([])
const executionItems = ref([])
const total = ref(0)
const selectedExecution = ref(null)

const statistics = ref({
  total_executions: 0,
  success_count: 0,
  failed_count: 0,
  avg_duration: 0
})

// 搜索表单
const searchForm = reactive({
  search: '',
  status: '',
  dateRange: null,
  page: 1,
  page_size: 20
})

// 方法
const loadExecutions = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    executions.value = [
      {
        id: '1',
        suite_name: '用户管理功能测试套件',
        status: 'success',
        progress: 100,
        success_count: 12,
        failed_count: 0,
        skipped_count: 1,
        total_count: 13,
        duration: 180000, // 3分钟
        executor_name: '张三',
        start_time: '2024-01-15T10:30:00Z',
        end_time: '2024-01-15T10:33:00Z',
        environment: '测试环境'
      },
      {
        id: '2',
        suite_name: '订单流程测试套件',
        status: 'failed',
        progress: 60,
        success_count: 8,
        failed_count: 3,
        skipped_count: 2,
        total_count: 13,
        duration: 240000, // 4分钟
        executor_name: '李四',
        start_time: '2024-01-15T09:15:00Z',
        end_time: '2024-01-15T09:19:00Z',
        environment: '测试环境'
      },
      {
        id: '3',
        suite_name: '支付功能测试套件',
        status: 'running',
        progress: 45,
        success_count: 5,
        failed_count: 1,
        skipped_count: 0,
        total_count: 12,
        duration: 120000, // 2分钟（进行中）
        executor_name: '王五',
        start_time: '2024-01-15T11:00:00Z',
        end_time: null,
        environment: '测试环境'
      }
    ]
    
    total.value = executions.value.length
    
    // 更新统计信息
    updateStatistics()
  } catch (error) {
    console.error('获取执行历史失败:', error)
    ElMessage.error('获取执行历史失败')
  } finally {
    loading.value = false
  }
}

const updateStatistics = () => {
  const completedExecutions = executions.value.filter(e => e.status !== 'running')
  
  statistics.value = {
    total_executions: executions.value.length,
    success_count: executions.value.filter(e => e.status === 'success').length,
    failed_count: executions.value.filter(e => e.status === 'failed').length,
    avg_duration: completedExecutions.length > 0 
      ? Math.round(completedExecutions.reduce((sum, e) => sum + e.duration, 0) / completedExecutions.length / 1000)
      : 0
  }
}

const handleSearch = () => {
  searchForm.page = 1
  loadExecutions()
}

const refreshData = () => {
  loadExecutions()
}

const exportReport = () => {
  ElMessage.info('导出报告功能开发中...')
}

const viewExecution = (execution) => {
  selectedExecution.value = execution
  loadExecutionItems(execution.id)
  showDetailDialog.value = true
}

const viewReport = (execution) => {
  // 跳转到独立的报告页面
  router.push(`/aitestrebort/project/${projectId.value}/test-execution/${execution.id}/report`)
}

const cancelExecution = async (execution) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消执行 "${execution.suite_name}" 吗？`,
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    execution.status = 'cancelled'
    execution.end_time = new Date().toISOString()
    
    ElMessage.success('执行已取消')
    updateStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消执行失败:', error)
      ElMessage.error('取消执行失败')
    }
  }
}

const deleteExecution = async (execution) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除执行记录 "${execution.suite_name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = executions.value.findIndex(e => e.id === execution.id)
    if (index > -1) {
      executions.value.splice(index, 1)
      total.value--
      updateStatistics()
    }
    
    ElMessage.success('执行记录删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除执行记录失败:', error)
      ElMessage.error('删除执行记录失败')
    }
  }
}

const loadExecutionItems = async (executionId) => {
  // 模拟加载执行项详情
  executionItems.value = [
    {
      id: '1',
      name: '用户注册功能测试',
      type: 'testcase',
      status: 'success',
      duration: 15000,
      start_time: '2024-01-15T10:30:00Z'
    },
    {
      id: '2',
      name: '用户登录功能测试',
      type: 'testcase',
      status: 'success',
      duration: 12000,
      start_time: '2024-01-15T10:30:15Z'
    },
    {
      id: '3',
      name: '用户注册UI自动化测试',
      type: 'script',
      status: 'failed',
      duration: 8000,
      start_time: '2024-01-15T10:30:30Z'
    }
  ]
}

const viewItemError = (item) => {
  ElMessageBox.alert(
    `执行失败原因：\n\n模拟错误信息：${item.name} 执行过程中发生异常，请检查测试环境和数据配置。\n\n错误堆栈：\nAssertionError: Expected element to be visible\n  at test.spec.js:25:10`,
    '错误详情',
    {
      confirmButtonText: '确定'
    }
  )
}

// 辅助方法
const getStatusColor = (status) => {
  const colors = {
    success: 'success',
    failed: 'danger',
    partial: 'warning',
    cancelled: 'info',
    running: 'primary'
  }
  return colors[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    success: '成功',
    failed: '失败',
    partial: '部分成功',
    cancelled: '已取消',
    running: '执行中'
  }
  return texts[status] || status
}

const formatDuration = (ms) => {
  if (!ms) return '-'
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes > 0) {
    return `${minutes}分${remainingSeconds}秒`
  }
  return `${remainingSeconds}秒`
}

const formatDateTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadExecutions()
})
</script>

<style scoped>
.test-execution-history {
  padding: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.content-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
}

.stat-card :deep(.el-statistic__content) {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-card.success :deep(.el-statistic__content) {
  color: #67C23A;
}

.stat-card.danger :deep(.el-statistic__content) {
  color: #F56C6C;
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.result-stats {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
}

.result-stats .success {
  color: #67C23A;
}

.result-stats .failed {
  color: #F56C6C;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.execution-detail {
  padding: 16px 0;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.mini-stat-card {
  text-align: center;
}

.mini-stat-card :deep(.el-statistic__content) {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
}

.mini-stat-card.success :deep(.el-statistic__content) {
  color: #67C23A;
}

.mini-stat-card.danger :deep(.el-statistic__content) {
  color: #F56C6C;
}

.mini-stat-card.warning :deep(.el-statistic__content) {
  color: #E6A23C;
}
</style>