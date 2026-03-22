<template>
  <el-dialog
    v-model="dialogVisible"
    title="确认执行"
    width="60%"
    :before-close="handleClose"
  >
    <div class="execution-confirm" v-if="taskData">
      <!-- 任务信息 -->
      <el-card class="task-info" shadow="never">
        <template #header>
          <span>任务信息</span>
        </template>
        
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务ID">
            {{ taskData.id }}
          </el-descriptions-item>
          <el-descriptions-item label="需求描述">
            {{ taskData.requirement }}
          </el-descriptions-item>
          <el-descriptions-item label="项目ID">
            {{ taskData.project_id }}
          </el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="getStatusColor(taskData.status)">
              {{ getStatusText(taskData.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 执行计划预览 -->
      <el-card class="execution-plan" shadow="never" v-if="taskData.execution_plan">
        <template #header>
          <span>执行计划预览</span>
        </template>
        
        <div class="plan-steps">
          <div 
            v-for="(step, index) in planSteps" 
            :key="index"
            class="plan-step"
          >
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <div class="step-title">{{ step.title }}</div>
              <div class="step-description">{{ step.description }}</div>
              <div class="step-estimated-time" v-if="step.estimatedTime">
                预计耗时: {{ step.estimatedTime }}
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 执行配置 -->
      <el-card class="execution-config" shadow="never">
        <template #header>
          <span>执行配置</span>
        </template>
        
        <el-form :model="confirmForm" label-width="120px">
          <el-form-item label="确认执行">
            <el-checkbox v-model="confirmForm.confirm_plan">
              我已仔细阅读执行计划，确认执行此任务
            </el-checkbox>
          </el-form-item>
          
          <el-form-item label="用户反馈">
            <el-input
              v-model="confirmForm.user_feedback"
              type="textarea"
              :rows="3"
              placeholder="可选：对执行计划的反馈或特殊要求"
            />
          </el-form-item>
          
          <el-form-item label="执行模式">
            <el-radio-group v-model="confirmForm.execution_mode">
              <el-radio value="auto">自动执行</el-radio>
              <el-radio value="step_by_step">分步确认</el-radio>
            </el-radio-group>
            <div class="mode-description">
              <span v-if="confirmForm.execution_mode === 'auto'">
                任务将自动执行所有步骤，无需人工干预
              </span>
              <span v-else>
                每个步骤执行前都会等待您的确认
              </span>
            </div>
          </el-form-item>
          
          <el-form-item label="通知设置">
            <el-checkbox-group v-model="confirmForm.notifications">
              <el-checkbox value="progress">进度通知</el-checkbox>
              <el-checkbox value="completion">完成通知</el-checkbox>
              <el-checkbox value="error">错误通知</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 风险提示 -->
      <el-card class="risk-warning" shadow="never">
        <template #header>
          <span>风险提示</span>
        </template>
        
        <el-alert
          title="执行风险提示"
          type="warning"
          :closable="false"
          show-icon
        >
          <template #default>
            <ul class="risk-list">
              <li>任务执行过程中可能会消耗大量计算资源</li>
              <li>执行时间可能因任务复杂度而有所不同</li>
              <li>请确保网络连接稳定，避免执行中断</li>
              <li>如有疑问，请先取消执行并联系管理员</li>
            </ul>
          </template>
        </el-alert>
      </el-card>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmExecution"
          :disabled="!confirmForm.confirm_plan"
          :loading="confirming"
        >
          确认执行
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

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
const emit = defineEmits(['update:modelValue', 'confirm'])

// 响应式数据
const confirming = ref(false)
const confirmForm = reactive({
  confirm_plan: false,
  user_feedback: '',
  execution_mode: 'auto',
  notifications: ['progress', 'completion', 'error']
})

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const planSteps = computed(() => {
  // 模拟执行计划步骤
  return [
    {
      title: '需求分析',
      description: '分析用户需求，提取关键信息',
      estimatedTime: '2-3分钟'
    },
    {
      title: '知识库检索',
      description: '从知识库中检索相关文档和信息',
      estimatedTime: '1-2分钟'
    },
    {
      title: '生成执行计划',
      description: '基于需求和知识生成详细的执行计划',
      estimatedTime: '3-5分钟'
    },
    {
      title: '执行任务',
      description: '按照计划执行具体的任务步骤',
      estimatedTime: '5-10分钟'
    },
    {
      title: '生成结果',
      description: '整理执行结果，生成最终输出',
      estimatedTime: '1-2分钟'
    }
  ]
})

// 方法
const confirmExecution = async () => {
  if (!confirmForm.confirm_plan) {
    ElMessage.warning('请先确认执行计划')
    return
  }

  confirming.value = true
  try {
    const confirmData = {
      task_id: props.taskData.id,
      confirm_plan: confirmForm.confirm_plan,
      user_feedback: confirmForm.user_feedback,
      execution_mode: confirmForm.execution_mode,
      notifications: confirmForm.notifications
    }

    emit('confirm', confirmData)
    handleClose()

  } catch (error) {
    ElMessage.error('确认失败: ' + error.message)
  } finally {
    confirming.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
  // 重置表单
  Object.assign(confirmForm, {
    confirm_plan: false,
    user_feedback: '',
    execution_mode: 'auto',
    notifications: ['progress', 'completion', 'error']
  })
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
</script>

<style scoped>
.execution-confirm {
  max-height: 60vh;
  overflow-y: auto;
}

.task-info,
.execution-plan,
.execution-config,
.risk-warning {
  margin-bottom: 20px;
}

.plan-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.plan-step {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background-color: #fafafa;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 16px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.step-description {
  color: #606266;
  line-height: 1.5;
  margin-bottom: 4px;
}

.step-estimated-time {
  color: #909399;
  font-size: 12px;
}

.mode-description {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}

.risk-list {
  margin: 0;
  padding-left: 20px;
}

.risk-list li {
  margin-bottom: 4px;
  line-height: 1.5;
}

.dialog-footer {
  text-align: right;
}
</style>