<template>
  <el-dialog
    v-model="dialogVisible"
    title="任务详情"
    width="80%"
    :before-close="handleClose"
  >
    <div class="task-detail" v-if="taskData">
      <!-- 任务基本信息 -->
      <el-card class="basic-info" shadow="never">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag :type="getStatusColor(taskData.status)" size="large">
              {{ getStatusText(taskData.status) }}
            </el-tag>
          </div>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">
            {{ taskData.id }}
          </el-descriptions-item>
          <el-descriptions-item label="项目ID">
            {{ taskData.project_id }}
          </el-descriptions-item>
          <el-descriptions-item label="当前步骤">
            {{ taskData.current_step }} / 5
          </el-descriptions-item>
          <el-descriptions-item label="等待对象" v-if="taskData.waiting_for">
            {{ taskData.waiting_for }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(taskData.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间" v-if="taskData.started_at">
            {{ formatDateTime(taskData.started_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间" v-if="taskData.completed_at">
            {{ formatDateTime(taskData.completed_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="执行时长" v-if="taskData.started_at">
            {{ getExecutionDuration() }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 需求描述 -->
      <el-card class="requirement-card" shadow="never">
        <template #header>
          <span>需求描述</span>
        </template>
        <div class="requirement-content">
          {{ taskData.requirement }}
        </div>
      </el-card>

      <!-- 用户备注 -->
      <el-card class="notes-card" shadow="never" v-if="taskData.user_notes">
        <template #header>
          <span>用户备注</span>
        </template>
        <div class="notes-content">
          {{ taskData.user_notes }}
        </div>
      </el-card>

      <!-- 执行进度 -->
      <el-card class="progress-card" shadow="never">
        <template #header>
          <span>执行进度</span>
        </template>
        
        <div class="progress-info">
          <el-progress 
            :percentage="getTaskProgress()" 
            :status="taskData.status === 'failed' ? 'exception' : 'success'"
          />
          <div class="progress-text">
            {{ getTaskProgress() }}% - {{ getCurrentStepText() }}
          </div>
        </div>
      </el-card>

      <!-- 执行历史 -->
      <el-card class="history-card" shadow="never" v-if="taskData.execution_history && taskData.execution_history.length > 0">
        <template #header>
          <span>执行历史</span>
        </template>
        
        <el-timeline>
          <el-timeline-item
            v-for="(item, index) in taskData.execution_history"
            :key="index"
            :timestamp="formatDateTime(item.timestamp)"
            :type="getHistoryItemType(item.status)"
          >
            <div class="history-item">
              <div class="history-title">
                步骤 {{ item.step }}: {{ item.name }}
              </div>
              <div class="history-status">
                <el-tag :type="getHistoryStatusColor(item.status)" size="small">
                  {{ getHistoryStatusText(item.status) }}
                </el-tag>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <!-- 执行计划 -->
      <el-card class="plan-card" shadow="never" v-if="taskData.execution_plan">
        <template #header>
          <span>执行计划</span>
        </template>
        
        <div class="plan-content">
          <pre>{{ JSON.stringify(taskData.execution_plan, null, 2) }}</pre>
        </div>
      </el-card>

      <!-- 需求分析结果 -->
      <el-card class="analysis-card" shadow="never" v-if="taskData.requirement_analysis">
        <template #header>
          <span>需求分析结果</span>
        </template>
        
        <div class="analysis-content">
          <pre>{{ JSON.stringify(taskData.requirement_analysis, null, 2) }}</pre>
        </div>
      </el-card>

      <!-- 知识文档 -->
      <el-card class="knowledge-card" shadow="never" v-if="taskData.knowledge_docs && taskData.knowledge_docs.length > 0">
        <template #header>
          <span>检索的知识文档</span>
        </template>
        
        <el-table :data="taskData.knowledge_docs">
          <el-table-column prop="title" label="文档标题" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="relevance" label="相关度" width="100">
            <template #default="{ row }">
              <el-progress 
                :percentage="Math.round(row.relevance * 100)" 
                :show-text="false"
                :stroke-width="6"
              />
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 生成的测试用例 -->
      <el-card class="testcases-card" shadow="never" v-if="taskData.testcases && taskData.testcases.length > 0">
        <template #header>
          <div class="card-header">
            <span>生成的测试用例</span>
            <el-button type="primary" size="small" @click="exportTestCases">
              导出用例
            </el-button>
          </div>
        </template>
        
        <el-collapse v-model="activeTestCases">
          <el-collapse-item
            v-for="(testcase, index) in taskData.testcases"
            :key="index"
            :title="testcase.name"
            :name="index"
          >
            <div class="testcase-content">
              <div class="testcase-description">
                <strong>描述：</strong>{{ testcase.description }}
              </div>
              <div class="testcase-steps" v-if="testcase.steps">
                <strong>测试步骤：</strong>
                <ol>
                  <li v-for="step in testcase.steps" :key="step">{{ step }}</li>
                </ol>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>

      <!-- 错误信息 -->
      <el-card class="error-card" shadow="never" v-if="taskData.error_message">
        <template #header>
          <span>错误信息</span>
        </template>
        <div class="error-content">
          {{ taskData.error_message }}
        </div>
      </el-card>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button 
          v-if="taskData && taskData.status === 'waiting_confirmation'"
          type="primary" 
          @click="confirmExecution"
        >
          确认执行
        </el-button>
        <el-button 
          v-if="taskData && ['pending', 'planning', 'executing'].includes(taskData.status)"
          type="danger" 
          @click="cancelTask"
        >
          取消任务
        </el-button>
        <el-button type="info" @click="refreshTask">
          刷新状态
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { orchestratorApi } from '@/api/aitestrebort/orchestrator'
import { formatDateTime } from '@/utils/format'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  taskData: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'refresh'])

// 响应式数据
const activeTestCases = ref([])

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 方法
const confirmExecution = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要执行此任务吗？',
      '确认执行',
      {
        confirmButtonText: '确认执行',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    await orchestratorApi.executeTask(props.taskData.id, {
      task_id: props.taskData.id,
      confirm_plan: true
    })

    ElMessage.success('任务执行已确认')
    emit('refresh')

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('确认执行失败: ' + error.message)
    }
  }
}

const cancelTask = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消此任务吗？',
      '确认取消',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await orchestratorApi.cancelTask(props.taskData.id)
    ElMessage.success('任务已取消')
    emit('refresh')

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消任务失败: ' + error.message)
    }
  }
}

const refreshTask = async () => {
  try {
    const response = await orchestratorApi.getTask(props.taskData.id)
    // 更新任务数据
    Object.assign(props.taskData, response.data)
    ElMessage.success('状态已刷新')
  } catch (error) {
    ElMessage.error('刷新失败: ' + error.message)
  }
}

const exportTestCases = () => {
  // TODO: 实现测试用例导出功能
  ElMessage.info('测试用例导出功能开发中')
}

const handleClose = () => {
  dialogVisible.value = false
}

// 辅助方法
const getStatusColor = (status) => {
  const colors = {
    pending: 'info',
    planning: 'warning',
    waiting_confirmation: 'primary',
    executing: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return colors[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '等待中',
    planning: '规划中',
    waiting_confirmation: '等待确认',
    executing: '执行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const getTaskProgress = () => {
  if (!props.taskData) return 0
  
  const progressMap = {
    pending: 0,
    planning: 20,
    waiting_confirmation: 40,
    executing: 60,
    completed: 100,
    failed: 0,
    cancelled: 0
  }
  
  let baseProgress = progressMap[props.taskData.status] || 0
  
  // 如果是执行中，根据当前步骤计算更精确的进度
  if (props.taskData.status === 'executing' && props.taskData.current_step > 0) {
    const stepProgress = (props.taskData.current_step / 5) * 40 // 执行阶段占40%
    baseProgress = 60 + stepProgress
  }
  
  return Math.min(100, Math.round(baseProgress))
}

const getCurrentStepText = () => {
  if (!props.taskData) return ''
  
  const stepTexts = {
    pending: '等待开始',
    planning: '正在规划任务',
    waiting_confirmation: '等待用户确认',
    executing: `正在执行第 ${props.taskData.current_step} 步`,
    completed: '任务已完成',
    failed: '任务执行失败',
    cancelled: '任务已取消'
  }
  
  return stepTexts[props.taskData.status] || props.taskData.status
}

const getExecutionDuration = () => {
  if (!props.taskData.started_at) return '-'
  
  const startTime = new Date(props.taskData.started_at)
  const endTime = props.taskData.completed_at ? new Date(props.taskData.completed_at) : new Date()
  const duration = Math.floor((endTime - startTime) / 1000) // 秒
  
  if (duration < 60) return `${duration}秒`
  if (duration < 3600) return `${Math.floor(duration / 60)}分${duration % 60}秒`
  return `${Math.floor(duration / 3600)}小时${Math.floor((duration % 3600) / 60)}分`
}

const getHistoryItemType = (status) => {
  const types = {
    completed: 'success',
    failed: 'danger',
    running: 'primary'
  }
  return types[status] || 'info'
}

const getHistoryStatusColor = (status) => {
  const colors = {
    completed: 'success',
    failed: 'danger',
    running: 'warning'
  }
  return colors[status] || 'info'
}

const getHistoryStatusText = (status) => {
  const texts = {
    completed: '已完成',
    failed: '失败',
    running: '执行中'
  }
  return texts[status] || status
}
</script>

<style scoped>
.task-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.basic-info,
.requirement-card,
.notes-card,
.progress-card,
.history-card,
.plan-card,
.analysis-card,
.knowledge-card,
.testcases-card,
.error-card {
  margin-bottom: 20px;
}

.requirement-content,
.notes-content {
  line-height: 1.6;
  color: #606266;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 4px;
  white-space: pre-wrap;
}

.progress-info {
  margin-bottom: 16px;
}

.progress-text {
  margin-top: 8px;
  color: #606266;
  font-size: 14px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-title {
  font-weight: 500;
  color: #303133;
}

.plan-content,
.analysis-content {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  overflow-x: auto;
}

.testcase-content {
  padding: 16px;
}

.testcase-description {
  margin-bottom: 12px;
  line-height: 1.5;
}

.testcase-steps {
  line-height: 1.5;
}

.testcase-steps ol {
  margin: 8px 0 0 20px;
  padding: 0;
}

.testcase-steps li {
  margin-bottom: 4px;
}

.error-content {
  color: #f56c6c;
  background-color: #fef0f0;
  padding: 16px;
  border-radius: 4px;
  border-left: 4px solid #f56c6c;
  line-height: 1.5;
}

.dialog-footer {
  text-align: right;
}
</style>