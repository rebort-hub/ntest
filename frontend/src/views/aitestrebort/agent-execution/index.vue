<template>
  <div class="agent-execution">
    <el-card class="page-header">
      <div class="header-content">
        <div>
          <h2>Agent执行</h2>
          <p>基于LangGraph的多步骤智能推理和任务执行系统</p>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 任务配置区域 -->
      <el-col :span="8">
        <el-card class="task-config-card">
          <template #header>
            <span>任务配置</span>
          </template>

          <el-form :model="taskForm" label-width="100px">
            <el-form-item label="执行目标" required>
              <el-input
                v-model="taskForm.goal"
                type="textarea"
                :rows="4"
                placeholder="请描述您希望Agent完成的任务..."
              />
            </el-form-item>

            <el-form-item label="会话ID">
              <el-input
                v-model="taskForm.session_id"
                placeholder="自动生成或手动输入"
              >
                <template #append>
                  <el-button @click="generateSessionId">生成</el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="最大步骤">
              <el-input-number
                v-model="taskForm.max_steps"
                :min="1"
                :max="100"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="可用工具">
              <el-select
                v-model="taskForm.tools"
                multiple
                placeholder="选择可用工具"
                style="width: 100%"
              >
                <el-option
                  v-for="tool in availableTools"
                  :key="tool.name"
                  :label="tool.description"
                  :value="tool.name"
                  :disabled="!tool.available"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="初始上下文">
              <el-input
                v-model="contextInput"
                type="textarea"
                :rows="3"
                placeholder="JSON格式的初始上下文（可选）"
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="executeTask"
                :loading="executing"
                style="width: 100%"
              >
                开始执行
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 工具状态 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>工具状态</span>
          </template>
          
          <div class="tool-status">
            <div
              v-for="tool in availableTools"
              :key="tool.name"
              class="tool-item"
            >
              <el-tag
                :type="tool.available ? 'success' : 'danger'"
                size="small"
              >
                {{ tool.name }}
              </el-tag>
              <span class="tool-desc">{{ tool.description }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 执行过程区域 -->
      <el-col :span="16">
        <el-card class="execution-card">
          <template #header>
            <div class="card-header">
              <span>执行过程</span>
              <div>
                <el-tag v-if="executionResult" :type="getStatusType(executionResult.status)">
                  {{ getStatusText(executionResult.status) }}
                </el-tag>
                <el-button 
                  v-if="executing" 
                  type="danger" 
                  size="small" 
                  @click="stopExecution"
                >
                  停止执行
                </el-button>
              </div>
            </div>
          </template>

          <!-- 执行步骤 -->
          <div class="execution-steps">
            <el-timeline v-if="executionHistory.length > 0">
              <el-timeline-item
                v-for="(step, index) in executionHistory"
                :key="index"
                :timestamp="formatTime(step.timestamp)"
                :type="getStepType(step.type)"
              >
                <div class="step-content">
                  <div class="step-title">{{ step.title }}</div>
                  <div class="step-description">{{ step.description }}</div>
                  <div v-if="step.result" class="step-result">
                    <el-collapse>
                      <el-collapse-item title="查看结果">
                        <pre>{{ JSON.stringify(step.result, null, 2) }}</pre>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>

            <div v-else-if="!executing" class="no-execution">
              <el-empty description="暂无执行记录" />
            </div>

            <div v-if="executing" class="executing-indicator">
              <el-icon class="is-loading">
                <Loading />
              </el-icon>
              <span>Agent正在思考和执行中...</span>
            </div>
          </div>

          <!-- 最终结果 -->
          <div v-if="executionResult && executionResult.response" class="final-result">
            <el-divider content-position="left">执行结果</el-divider>
            <div class="result-content">
              {{ executionResult.response }}
            </div>
            
            <div class="result-stats">
              <el-statistic title="执行步骤" :value="executionResult.steps" />
              <el-statistic title="任务ID" :value="executionResult.task_id" />
            </div>
          </div>

          <!-- 错误信息 -->
          <div v-if="executionResult && executionResult.error" class="error-result">
            <el-alert
              title="执行失败"
              :description="executionResult.error"
              type="error"
              show-icon
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 历史任务 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>历史任务</span>
              <el-button size="small" @click="loadTaskHistory">刷新</el-button>
            </div>
          </template>

          <el-table :data="taskHistory" style="width: 100%">
            <el-table-column prop="session_id" label="会话ID" width="200" />
            <el-table-column prop="goal" label="任务目标" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="steps" label="步骤数" width="80" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="viewTaskDetail(row)">查看</el-button>
                <el-button size="small" type="danger" @click="deleteTask(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, ArrowLeft } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { advancedFeaturesApi } from '@/api/aitestrebort/advanced-features'
import type { 
  AgentExecutionRequest, 
  AgentExecutionResponse,
  AvailableTool 
} from '@/api/aitestrebort/advanced-features'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.projectId)

// 计算返回路径
const backPath = computed(() => {
  const from = route.query.from as string
  if (from === 'testcase') {
    return `/aitestrebort/project/${projectId}/testcase`
  }
  return '/aitestrebort/project'
})

// 返回方法
const goBack = () => {
  router.push(backPath.value)
}

// 响应式数据
const executing = ref(false)
const availableTools = ref<AvailableTool[]>([])
const contextInput = ref('')

const taskForm = reactive<AgentExecutionRequest>({
  goal: '',
  session_id: '',
  max_steps: 50,
  tools: [],
  initial_context: {}
})

const executionResult = ref<AgentExecutionResponse | null>(null)
const executionHistory = ref<Array<{
  type: 'thinking' | 'action' | 'result' | 'error'
  title: string
  description: string
  result?: any
  timestamp: Date
}>>([])

const taskHistory = ref<Array<{
  session_id: string
  goal: string
  status: string
  steps: number
  created_at: string
}>>([])

// 方法
const loadAvailableTools = async () => {
  try {
    const response = await advancedFeaturesApi.system.getAvailableTools(projectId)
    if (response.data) {
      availableTools.value = response.data
    }
  } catch (error) {
    console.error('加载工具列表失败:', error)
    ElMessage.error('加载工具列表失败')
  }
}

const generateSessionId = () => {
  taskForm.session_id = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

const executeTask = async () => {
  if (!taskForm.goal.trim()) {
    ElMessage.warning('请输入执行目标')
    return
  }

  if (!taskForm.session_id) {
    generateSessionId()
  }

  // 解析初始上下文
  try {
    if (contextInput.value.trim()) {
      taskForm.initial_context = JSON.parse(contextInput.value)
    }
  } catch (error) {
    ElMessage.error('初始上下文格式错误，请输入有效的JSON')
    return
  }

  executing.value = true
  executionHistory.value = []
  executionResult.value = null

  // 添加开始执行的记录
  executionHistory.value.push({
    type: 'thinking',
    title: '开始执行任务',
    description: `目标: ${taskForm.goal}`,
    timestamp: new Date()
  })

  try {
    const response = await advancedFeaturesApi.langGraph.agentExecution(projectId, taskForm)
    if (response.data) {
      executionResult.value = response.data
      
      // 添加执行步骤到历史
      if (response.data.history) {
        response.data.history.forEach((step, index) => {
          executionHistory.value.push({
            type: 'action',
            title: `步骤 ${index + 1}`,
            description: step,
            timestamp: new Date()
          })
        })
      }

      // 添加最终结果
      executionHistory.value.push({
        type: response.data.status === 'completed' ? 'result' : 'error',
        title: '执行完成',
        description: response.data.response || response.data.error || '任务执行结束',
        result: response.data,
        timestamp: new Date()
      })

      if (response.data.status === 'completed') {
        ElMessage.success('任务执行完成')
      } else {
        ElMessage.error('任务执行失败')
      }
    }
  } catch (error) {
    console.error('Agent执行失败:', error)
    ElMessage.error('执行失败，请重试')
    
    executionHistory.value.push({
      type: 'error',
      title: '执行错误',
      description: '任务执行过程中发生错误',
      timestamp: new Date()
    })
  } finally {
    executing.value = false
  }
}

const stopExecution = () => {
  executing.value = false
  ElMessage.info('已停止执行')
}

const loadTaskHistory = () => {
  // 模拟加载历史任务
  taskHistory.value = [
    {
      session_id: 'session_1234567890',
      goal: '生成用户登录的测试用例',
      status: 'completed',
      steps: 8,
      created_at: '2024-01-15 10:30:00'
    },
    {
      session_id: 'session_0987654321',
      goal: '分析需求文档并提取关键信息',
      status: 'failed',
      steps: 3,
      created_at: '2024-01-15 09:15:00'
    }
  ]
}

const viewTaskDetail = (task: any) => {
  ElMessage.info(`查看任务详情: ${task.session_id}`)
}

const deleteTask = async (task: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗？', '确认删除', {
      type: 'warning'
    })
    
    // 这里应该调用删除API
    ElMessage.success('任务已删除')
    loadTaskHistory()
  } catch {
    // 用户取消删除
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'failed': return 'danger'
    case 'running': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'failed': return '失败'
    case 'running': return '运行中'
    default: return '未知'
  }
}

const getStepType = (type: string) => {
  switch (type) {
    case 'thinking': return 'primary'
    case 'action': return 'success'
    case 'result': return 'success'
    case 'error': return 'danger'
    default: return 'info'
  }
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString()
}

// 生命周期
onMounted(() => {
  loadAvailableTools()
  loadTaskHistory()
  generateSessionId()
})
</script>

<style scoped>
.agent-execution {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  align-items: center;
}

.page-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #606266;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-config-card {
  height: fit-content;
}

.execution-card {
  height: 600px;
  overflow: hidden;
}

.tool-status {
  max-height: 200px;
  overflow-y: auto;
}

.tool-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 10px;
}

.tool-desc {
  font-size: 12px;
  color: #606266;
}

.execution-steps {
  height: 450px;
  overflow-y: auto;
  padding: 10px;
}

.step-content {
  padding: 10px;
}

.step-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.step-description {
  color: #606266;
  margin-bottom: 10px;
}

.step-result {
  margin-top: 10px;
}

.step-result pre {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.no-execution {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.executing-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  color: #409EFF;
}

.final-result {
  margin-top: 20px;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 4px;
}

.result-content {
  margin-bottom: 15px;
  line-height: 1.6;
}

.result-stats {
  display: flex;
  gap: 30px;
}

.error-result {
  margin-top: 20px;
}
</style>