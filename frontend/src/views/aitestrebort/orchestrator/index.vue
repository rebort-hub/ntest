<template>
  <div class="orchestrator">
    <div class="page-header">
      <h2>智能编排</h2>
      <p>AI驱动的测试任务智能规划与执行系统</p>
    </div>

    <!-- 任务创建区域 -->
    <el-card class="task-creator" shadow="never">
      <template #header>
        <span>创建智能编排任务</span>
      </template>

      <el-form :model="taskForm" :rules="taskRules" ref="taskFormRef" label-width="120px">
        <el-form-item label="需求描述" prop="requirement">
          <el-input
            v-model="taskForm.requirement"
            type="textarea"
            :rows="4"
            placeholder="请详细描述您的测试需求，例如：为用户登录功能生成完整的测试用例"
          />
        </el-form-item>

        <el-form-item label="关联项目" prop="project_id">
          <el-select v-model="taskForm.project_id" placeholder="选择项目" style="width: 100%">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="用户备注">
          <el-input
            v-model="taskForm.user_notes"
            type="textarea"
            :rows="2"
            placeholder="可选：添加额外的说明或要求"
          />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="createTask"
            :loading="creating"
          >
            创建任务
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 任务列表 -->
    <el-card class="task-list" shadow="never">
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <div class="header-actions">
            <el-select v-model="filterStatus" placeholder="状态筛选" style="width: 120px; margin-right: 10px;">
              <el-option label="全部" value="" />
              <el-option label="等待中" value="pending" />
              <el-option label="规划中" value="planning" />
              <el-option label="等待确认" value="waiting_confirmation" />
              <el-option label="执行中" value="executing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-button @click="refreshTasks">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tasks" v-loading="tasksLoading" @row-click="viewTaskDetail">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="requirement" label="需求描述" min-width="300" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <div class="progress-info">
              <el-progress 
                :percentage="getTaskProgress(row)" 
                :status="row.status === 'failed' ? 'exception' : 'success'"
                :show-text="false"
              />
              <span class="progress-text">{{ getTaskProgress(row) }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="current_step" label="当前步骤" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click.stop="viewTaskDetail(row)"
            >
              查看详情
            </el-button>
            <el-button 
              v-if="row.status === 'waiting_confirmation'"
              type="success" 
              size="small" 
              @click.stop="confirmTask(row)"
            >
              确认执行
            </el-button>
            <el-button 
              v-if="['pending', 'planning', 'executing'].includes(row.status)"
              type="danger" 
              size="small" 
              @click.stop="cancelTask(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 任务详情对话框 -->
    <TaskDetailDialog 
      v-model="detailDialogVisible"
      :task-data="selectedTask"
      @refresh="refreshTasks"
    />

    <!-- 执行确认对话框 -->
    <ExecutionConfirmDialog
      v-model="confirmDialogVisible"
      :task-data="selectedTask"
      @confirm="handleExecutionConfirm"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import TaskDetailDialog from './components/TaskDetailDialog.vue'
import ExecutionConfirmDialog from './components/ExecutionConfirmDialog.vue'
import { orchestratorApi } from '@/api/aitestrebort/orchestrator'
import { projectApi } from '@/api/aitestrebort/project'
import { formatDateTime } from '@/utils/format'

// 响应式数据
const tasks = ref([])
const tasksLoading = ref(false)
const projects = ref([])
const creating = ref(false)
const filterStatus = ref('')
const detailDialogVisible = ref(false)
const confirmDialogVisible = ref(false)
const selectedTask = ref(null)

// 表单数据
const taskForm = reactive({
  requirement: '',
  project_id: null,
  user_notes: ''
})

const taskFormRef = ref()

// 表单验证规则
const taskRules = {
  requirement: [
    { required: true, message: '请输入需求描述', trigger: 'blur' },
    { min: 10, message: '需求描述至少10个字符', trigger: 'blur' }
  ],
  project_id: [
    { required: true, message: '请选择项目', trigger: 'change' }
  ]
}

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 计算属性
const filteredTasks = computed(() => {
  if (!filterStatus.value) return tasks.value
  return tasks.value.filter(task => task.status === filterStatus.value)
})

// 生命周期
onMounted(() => {
  loadProjects()
  loadTasks()
  startProgressPolling()
})

// 监听器
watch(filterStatus, () => {
  loadTasks()
})

// 方法
const loadProjects = async () => {
  try {
    const response = await projectApi.getProjects()
    projects.value = response.data || []
  } catch (error) {
    ElMessage.error('加载项目列表失败: ' + error.message)
  }
}

const loadTasks = async () => {
  tasksLoading.value = true
  try {
    const params = {
      status: filterStatus.value,
      page: pagination.page,
      page_size: pagination.pageSize
    }
    
    const response = await orchestratorApi.getTasks(params)
    tasks.value = response.data.items || []
    pagination.total = response.data.total || 0
  } catch (error) {
    ElMessage.error('加载任务列表失败: ' + error.message)
  } finally {
    tasksLoading.value = false
  }
}

const createTask = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    
    creating.value = true
    const response = await orchestratorApi.createTask(taskForm)
    
    ElMessage.success('任务创建成功')
    resetForm()
    loadTasks()
    
    // 自动打开任务详情
    selectedTask.value = response.data
    detailDialogVisible.value = true
    
  } catch (error) {
    if (error.message) {
      ElMessage.error('创建任务失败: ' + error.message)
    }
  } finally {
    creating.value = false
  }
}

const resetForm = () => {
  if (taskFormRef.value) {
    taskFormRef.value.resetFields()
  }
  Object.assign(taskForm, {
    requirement: '',
    project_id: null,
    user_notes: ''
  })
}

const viewTaskDetail = (task) => {
  selectedTask.value = task
  detailDialogVisible.value = true
}

const confirmTask = (task) => {
  selectedTask.value = task
  confirmDialogVisible.value = true
}

const handleExecutionConfirm = async (confirmData) => {
  try {
    await orchestratorApi.executeTask(selectedTask.value.id, confirmData)
    ElMessage.success('任务执行已确认')
    loadTasks()
  } catch (error) {
    ElMessage.error('确认执行失败: ' + error.message)
  }
}

const cancelTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消任务"${task.requirement.substring(0, 50)}..."吗？`,
      '确认取消',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await orchestratorApi.cancelTask(task.id)
    ElMessage.success('任务已取消')
    loadTasks()

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消任务失败: ' + error.message)
    }
  }
}

const refreshTasks = () => {
  loadTasks()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  loadTasks()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadTasks()
}

const startProgressPolling = () => {
  setInterval(async () => {
    // 只轮询执行中的任务
    const runningTasks = tasks.value.filter(task => 
      ['pending', 'planning', 'executing'].includes(task.status)
    )
    
    if (runningTasks.length === 0) return

    for (const task of runningTasks) {
      try {
        const response = await orchestratorApi.getTaskProgress(task.id)
        const progress = response.data

        // 更新任务状态
        const index = tasks.value.findIndex(t => t.id === task.id)
        if (index !== -1) {
          tasks.value[index] = { ...tasks.value[index], ...progress }
        }

        // 状态变化通知
        if (progress.status === 'completed' && task.status !== 'completed') {
          ElMessage.success(`任务"${task.requirement.substring(0, 30)}..."执行完成`)
        } else if (progress.status === 'failed' && task.status !== 'failed') {
          ElMessage.error(`任务"${task.requirement.substring(0, 30)}..."执行失败`)
        }
      } catch (error) {
        console.error('获取任务进度失败:', error)
      }
    }
  }, 5000) // 每5秒轮询一次
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

const getTaskProgress = (task) => {
  const progressMap = {
    pending: 0,
    planning: 20,
    waiting_confirmation: 40,
    executing: 60,
    completed: 100,
    failed: 0,
    cancelled: 0
  }
  
  let baseProgress = progressMap[task.status] || 0
  
  // 如果是执行中，根据当前步骤计算更精确的进度
  if (task.status === 'executing' && task.current_step > 0) {
    const stepProgress = (task.current_step / 5) * 40 // 执行阶段占40%
    baseProgress = 60 + stepProgress
  }
  
  return Math.min(100, Math.round(baseProgress))
}
</script>

<style scoped>
.orchestrator {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.task-creator,
.task-list {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 35px;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}
</style>