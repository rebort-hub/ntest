<template>
  <el-dialog
    :model-value="modelValue"
    title="执行进度"
    width="800px"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="execution-progress">
      <!-- 总体进度 -->
      <div class="overall-progress">
        <h4>总体进度</h4>
        <el-progress
          :percentage="overallProgress"
          :status="getProgressStatus()"
          :stroke-width="20"
        >
          <template #default="{ percentage }">
            <span class="progress-text">{{ percentage }}%</span>
          </template>
        </el-progress>
        <div class="progress-info">
          <span>已完成: {{ completedCount }}</span>
          <span>总数: {{ totalCount }}</span>
          <span>耗时: {{ formatDuration(elapsedTime) }}</span>
        </div>
      </div>

      <!-- 执行状态统计 -->
      <div class="status-stats">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-card class="stat-card success">
              <el-statistic title="成功" :value="stats.success" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card danger">
              <el-statistic title="失败" :value="stats.failed" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card warning">
              <el-statistic title="跳过" :value="stats.skipped" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card info">
              <el-statistic title="运行中" :value="stats.running" />
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 详细执行列表 -->
      <div class="execution-details">
        <h4>执行详情</h4>
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
              {{ row.start_time ? formatTime(row.start_time) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row }">
              <el-button
                v-if="row.status === 'running'"
                type="text"
                @click="stopExecution(row)"
                style="color: #f56c6c;"
              >
                停止
              </el-button>
              <el-button
                v-if="row.status === 'failed'"
                type="text"
                @click="viewError(row)"
              >
                查看错误
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 实时日志 -->
      <div class="execution-logs">
        <h4>执行日志</h4>
        <div class="log-container">
          <div
            v-for="(log, index) in logs"
            :key="index"
            :class="['log-item', `log-${log.level}`]"
          >
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
      <el-button
        v-if="!isCompleted"
        type="danger"
        @click="stopAllExecution"
      >
        停止所有执行
      </el-button>
      <el-button
        v-if="isCompleted"
        type="primary"
        @click="viewReport"
      >
        查看报告
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Props {
  modelValue: boolean
  executionId: string
  projectId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// 响应式数据
const executionItems = ref([])
const logs = ref([])
const stats = ref({
  success: 0,
  failed: 0,
  skipped: 0,
  running: 0
})
const startTime = ref(Date.now())
const elapsedTime = ref(0)

// 定时器
let progressTimer: NodeJS.Timeout | null = null
let logTimer: NodeJS.Timeout | null = null

// 计算属性
const totalCount = computed(() => executionItems.value.length)
const completedCount = computed(() => 
  stats.value.success + stats.value.failed + stats.value.skipped
)
const overallProgress = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})
const isCompleted = computed(() => 
  completedCount.value === totalCount.value && stats.value.running === 0
)

// 方法
const initExecution = () => {
  // 模拟初始化执行项目
  executionItems.value = [
    {
      id: '1',
      name: '用户注册功能测试',
      type: 'testcase',
      status: 'pending',
      duration: null,
      start_time: null
    },
    {
      id: '2',
      name: '用户登录功能测试',
      type: 'testcase',
      status: 'pending',
      duration: null,
      start_time: null
    },
    {
      id: '3',
      name: '用户注册UI自动化测试',
      type: 'script',
      status: 'pending',
      duration: null,
      start_time: null
    },
    {
      id: '4',
      name: '用户登录API测试',
      type: 'script',
      status: 'pending',
      duration: null,
      start_time: null
    }
  ]

  // 开始模拟执行
  startExecution()
}

const startExecution = () => {
  startTime.value = Date.now()
  
  // 模拟执行进度
  progressTimer = setInterval(() => {
    updateProgress()
    elapsedTime.value = Date.now() - startTime.value
  }, 1000)

  // 模拟日志输出
  logTimer = setInterval(() => {
    addRandomLog()
  }, 2000)
}

const updateProgress = () => {
  // 模拟执行进度更新
  const pendingItems = executionItems.value.filter(item => item.status === 'pending')
  const runningItems = executionItems.value.filter(item => item.status === 'running')

  // 开始新的执行项
  if (pendingItems.length > 0 && runningItems.length < 2) {
    const item = pendingItems[0]
    item.status = 'running'
    item.start_time = new Date().toISOString()
  }

  // 完成正在执行的项
  runningItems.forEach(item => {
    if (Math.random() > 0.7) { // 30% 概率完成
      const success = Math.random() > 0.2 // 80% 成功率
      item.status = success ? 'success' : 'failed'
      item.duration = Math.floor(Math.random() * 30000) + 5000 // 5-35秒
    }
  })

  // 更新统计
  updateStats()

  // 检查是否全部完成
  if (isCompleted.value && progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
    addLog('info', '所有执行项已完成')
  }
}

const updateStats = () => {
  stats.value = {
    success: executionItems.value.filter(item => item.status === 'success').length,
    failed: executionItems.value.filter(item => item.status === 'failed').length,
    skipped: executionItems.value.filter(item => item.status === 'skipped').length,
    running: executionItems.value.filter(item => item.status === 'running').length
  }
}

const addRandomLog = () => {
  const messages = [
    '开始执行测试用例...',
    '正在初始化测试环境...',
    '执行断言检查...',
    '测试数据准备完成',
    '开始执行自动化脚本...',
    '页面元素定位成功',
    'API请求发送成功',
    '响应数据验证通过'
  ]
  
  const levels = ['info', 'success', 'warning']
  const level = levels[Math.floor(Math.random() * levels.length)]
  const message = messages[Math.floor(Math.random() * messages.length)]
  
  addLog(level, message)
}

const addLog = (level: string, message: string) => {
  logs.value.push({
    level,
    message,
    timestamp: new Date().toISOString()
  })
  
  // 限制日志数量
  if (logs.value.length > 100) {
    logs.value.shift()
  }
}

const stopExecution = async (item: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要停止执行 "${item.name}" 吗？`,
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    item.status = 'skipped'
    updateStats()
    addLog('warning', `已停止执行: ${item.name}`)
    ElMessage.success('执行已停止')
  } catch (error) {
    // 用户取消
  }
}

const stopAllExecution = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要停止所有正在执行的项目吗？',
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 停止所有运行中和待执行的项目
    executionItems.value.forEach(item => {
      if (item.status === 'running' || item.status === 'pending') {
        item.status = 'skipped'
      }
    })
    
    updateStats()
    addLog('warning', '所有执行已停止')
    
    // 清除定时器
    if (progressTimer) {
      clearInterval(progressTimer)
      progressTimer = null
    }
    if (logTimer) {
      clearInterval(logTimer)
      logTimer = null
    }
    
    ElMessage.success('所有执行已停止')
  } catch (error) {
    // 用户取消
  }
}

const viewError = (item: any) => {
  ElMessageBox.alert(
    `执行失败原因：\n\n模拟错误信息：${item.name} 执行过程中发生异常，请检查测试环境和数据配置。`,
    '错误详情',
    {
      confirmButtonText: '确定'
    }
  )
}

const viewReport = () => {
  ElMessage.info('跳转到执行报告页面...')
  emit('update:modelValue', false)
}

const getProgressStatus = () => {
  if (stats.value.failed > 0) return 'exception'
  if (isCompleted.value) return 'success'
  return undefined
}

const getStatusColor = (status: string) => {
  const colors = {
    pending: 'info',
    running: 'primary',
    success: 'success',
    failed: 'danger',
    skipped: 'warning'
  }
  return colors[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts = {
    pending: '待执行',
    running: '执行中',
    success: '成功',
    failed: '失败',
    skipped: '跳过'
  }
  return texts[status] || status
}

const formatDuration = (ms: number) => {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes > 0) {
    return `${minutes}分${remainingSeconds}秒`
  }
  return `${remainingSeconds}秒`
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN')
}

// 清理定时器
const cleanup = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  if (logTimer) {
    clearInterval(logTimer)
    logTimer = null
  }
}

// 监听对话框打开
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.executionId) {
    initExecution()
  } else {
    cleanup()
  }
})

// 组件卸载时清理
onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.execution-progress {
  padding: 16px 0;
}

.overall-progress {
  margin-bottom: 24px;
}

.overall-progress h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.progress-text {
  font-size: 14px;
  font-weight: bold;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
}

.status-stats {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
}

.stat-card.success :deep(.el-statistic__content) {
  color: #67c23a;
}

.stat-card.danger :deep(.el-statistic__content) {
  color: #f56c6c;
}

.stat-card.warning :deep(.el-statistic__content) {
  color: #e6a23c;
}

.stat-card.info :deep(.el-statistic__content) {
  color: #409eff;
}

.execution-details {
  margin-bottom: 24px;
}

.execution-details h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.execution-logs h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.log-container {
  max-height: 200px;
  overflow-y: auto;
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-item {
  display: flex;
  margin-bottom: 4px;
  line-height: 1.4;
}

.log-time {
  width: 80px;
  color: #909399;
  flex-shrink: 0;
}

.log-message {
  flex: 1;
  margin-left: 8px;
}

.log-info .log-message {
  color: #303133;
}

.log-success .log-message {
  color: #67c23a;
}

.log-warning .log-message {
  color: #e6a23c;
}

.log-error .log-message {
  color: #f56c6c;
}
</style>