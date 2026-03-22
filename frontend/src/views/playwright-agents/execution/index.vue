<template>
  <div class="execution-page">
    <el-card class="header-card">
      <div class="header-title">
        <el-button 
          type="primary" 
          :icon="ArrowLeft" 
          @click="router.push('/playwright-agents/dashboard')"
          style="margin-right: 15px"
        >
          返回控制台
        </el-button>
        <div>
          <h2>执行记录</h2>
          <p>查看测试执行历史和结果</p>
        </div>
      </div>
    </el-card>

    <!-- 主内容区域 -->
    <el-card class="main-card">
      <div class="content-layout">
        <!-- 左侧：执行表单 -->
        <div class="left-section">
          <div class="section-header">
            <h3>执行测试</h3>
          </div>
          <el-form :model="executeForm" label-width="120px" class="execute-form">
        <el-form-item label="测试代码" required>
          <div style="display: flex; align-items: center; gap: 10px;">
            <el-button type="primary" @click="selectCodeDialogVisible = true">
              {{ selectedCodes.length > 0 ? `已选择 ${selectedCodes.length} 个测试代码` : '点击选择测试代码' }}
            </el-button>
            <el-button 
              v-if="selectedCodes.length > 0" 
              size="small" 
              @click="clearSelectedCodes"
            >
              清空
            </el-button>
          </div>
          <div v-if="selectedCodes.length > 0" style="margin-top: 10px;">
            <el-tag 
              v-for="code in selectedCodes" 
              :key="code.id" 
              closable 
              @close="removeCode(code)"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              #{{ code.id }} - {{ code.framework }} ({{ code.language }})
            </el-tag>
          </div>
        </el-form-item>
        <el-form-item label="MCP配置">
          <el-select v-model="executeForm.mcp_config_id" placeholder="选择MCP配置（可选）" clearable style="width: 300px">
            <el-option 
              v-for="config in mcpConfigs" 
              :key="config.id" 
              :label="config.name" 
              :value="config.id"
            />
          </el-select>
          <el-tooltip content="选择MCP配置后将使用MCP执行，并记录每个步骤的截图" placement="top">
            <el-icon style="margin-left: 5px; cursor: help;"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-form-item>
        <el-form-item label="浏览器">
          <el-select v-model="executeForm.browser" style="width: 200px">
            <el-option label="Chromium" value="chromium" />
            <el-option label="Firefox" value="firefox" />
            <el-option label="WebKit" value="webkit" />
          </el-select>
        </el-form-item>
        <el-form-item label="无头模式">
          <el-switch v-model="executeForm.headless" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="execute" :loading="executing" size="small">
            {{ executing ? '执行中...' : (selectedCodes.length > 1 ? `批量执行 (${selectedCodes.length}个)` : '执行测试') }}
          </el-button>
        </el-form-item>
      </el-form>
        </div>
        
        <!-- 右侧：执行测试进度 -->
        <div class="right-section">
          <div class="section-header">
            <h3>执行测试进度</h3>
          </div>
          <div class="progress-content">
            <TestExecutionProgressSteps 
              :status="executionStatus"
              :current-step="currentStep"
              :steps="progressSteps"
              :total-duration="totalDuration"
            />
          </div>
        </div>
      </div>
    </el-card>

    <!-- 选择测试代码对话框 -->
    <el-dialog v-model="selectCodeDialogVisible" title="选择测试代码" width="900px" top="5vh">
      <el-table 
        ref="codeTableRef"
        :data="testCodes" 
        @selection-change="handleCodeSelectionChange"
        style="width: 100%"
        max-height="500"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="framework" label="框架" width="180" />
        <el-table-column prop="language" label="语言" width="120" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getCodeStatusType(row.status)">
              {{ getCodeStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
      </el-table>
      <template #footer>
        <el-button @click="selectCodeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCodeSelect" :disabled="selectedCodes.length === 0">
          确定 {{ selectedCodes.length > 0 ? `(已选${selectedCodes.length}项)` : '' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行记录列表 -->
    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>执行记录</span>
          <div>
            <el-select v-model="filterStatus" placeholder="筛选状态" clearable size="small" style="width: 120px; margin-right: 10px">
              <el-option label="运行中" value="running" />
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
            </el-select>
            <el-button type="primary" size="small" @click="loadExecutions">刷新</el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="executions" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="测试代码" min-width="150">
          <template #default="{ row }">
            #{{ row.code_id }}
          </template>
        </el-table-column>
        <el-table-column prop="browser" label="浏览器" width="120" />
        <el-table-column label="无头模式" width="100">
          <template #default="{ row }">
            <el-tag :type="row.headless ? 'success' : 'info'" size="small">
              {{ row.headless ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration ? `${row.duration}s` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="执行时间" width="180" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" @click="viewLogs(row)">查看日志</el-button>
              <el-button size="small" type="info" @click="viewExecutionSteps(row)">执行详情</el-button>
              <el-button 
                size="small" 
                type="warning" 
                @click="healTest(row)"
                v-if="row.status === 'failed'"
              >
                自愈修复
              </el-button>
              <el-button size="small" type="danger" @click="deleteExecution(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next"
        @size-change="loadExecutions"
        @current-change="loadExecutions"
        style="margin-top: 20px"
      />
    </el-card>

    <!-- 日志查看对话框 -->
    <el-dialog v-model="logsVisible" title="执行日志" width="80%" top="5vh">
      <div v-if="currentLogs" class="logs-container">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="标准输出" name="stdout">
            <pre class="log-content">{{ currentLogs.stdout || '无输出' }}</pre>
          </el-tab-pane>
          <el-tab-pane label="错误输出" name="stderr">
            <pre class="log-content error">{{ currentLogs.stderr || '无错误' }}</pre>
          </el-tab-pane>
          <el-tab-pane label="详细信息" name="detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="执行ID">{{ currentLogs.execution_id }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(currentLogs.status)">
                  {{ getStatusText(currentLogs.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">{{ currentLogs.start_time }}</el-descriptions-item>
              <el-descriptions-item label="结束时间">{{ currentLogs.end_time }}</el-descriptions-item>
              <el-descriptions-item label="耗时">{{ currentLogs.duration }}s</el-descriptions-item>
              <el-descriptions-item label="退出码">{{ currentLogs.exit_code }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 执行详情对话框 - 使用虚拟滚动 -->
    <el-dialog v-model="stepsVisible" title="执行详情 - 步骤截图" width="90%" top="5vh">
      <div v-if="executionSteps.length" class="steps-container">
        <el-alert 
          title="提示" 
          type="info" 
          :closable="false"
          style="margin-bottom: 20px"
        >
          共 {{ executionSteps.length }} 个步骤，点击步骤可展开查看详情
        </el-alert>
        
        <!-- 虚拟滚动容器 -->
        <div 
          ref="virtualScrollContainer"
          class="virtual-scroll-container"
          @scroll="handleScroll"
        >
          <div :style="{ height: `${totalHeight}px`, position: 'relative' }">
            <div 
              v-for="step in visibleSteps" 
              :key="step.index"
              :style="{ 
                position: 'absolute', 
                top: `${step.offsetTop}px`, 
                left: 0, 
                right: 0,
                minHeight: `${itemHeight}px`
              }"
              class="virtual-step-item"
            >
              <el-card 
                shadow="hover" 
                :class="{ 'step-expanded': expandedStepIndex === step.index }"
                @click="toggleStep(step.index)"
                style="cursor: pointer; margin-bottom: 10px;"
              >
                <template #header>
                  <div class="step-header">
                    <span class="step-title">
                      <el-tag :type="step.data.status === 'success' ? 'success' : 'danger'" size="small">
                        步骤 {{ step.data.step_number }}
                      </el-tag>
                      <span style="margin-left: 10px; font-weight: 500;">{{ step.data.action }}</span>
                      <span style="margin-left: 10px; color: #909399;">{{ step.data.description }}</span>
                    </span>
                    <span style="display: flex; align-items: center; gap: 10px;">
                      <span v-if="step.data.duration" style="color: #909399; font-size: 12px;">
                        耗时: {{ step.data.duration.toFixed(2) }}秒
                      </span>
                      <el-icon :class="{ 'rotate-icon': expandedStepIndex === step.index }">
                        <ArrowDown />
                      </el-icon>
                    </span>
                  </div>
                </template>
                
                <!-- 展开的内容 -->
                <div v-show="expandedStepIndex === step.index" class="step-content">
                  <!-- 步骤信息 -->
                  <el-descriptions :column="2" size="small" border style="margin-bottom: 15px">
                    <el-descriptions-item label="操作类型">
                      {{ step.data.action }}
                    </el-descriptions-item>
                    <el-descriptions-item label="状态">
                      <el-tag :type="step.data.status === 'success' ? 'success' : 'danger'">
                        {{ step.data.status }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="时间戳" v-if="step.data.timestamp">
                      {{ new Date(step.data.timestamp).toLocaleString() }}
                    </el-descriptions-item>
                  </el-descriptions>

                  <!-- 截图对比 -->
                  <div class="screenshot-container">
                    <h4>截图对比:</h4>
                    <div class="screenshot-grid">
                      <!-- 操作前截图 -->
                      <div v-if="step.data.screenshot_before" class="screenshot-item">
                        <div class="screenshot-label">操作前</div>
                        <div class="screenshot-wrapper">
                          <img
                            v-if="expandedStepIndex === step.index"
                            :src="`data:image/jpeg;base64,${step.data.screenshot_before}`"
                            class="screenshot-image"
                            loading="lazy"
                          />
                        </div>
                      </div>
                      
                      <!-- 操作后截图 -->
                      <div v-if="step.data.screenshot_after" class="screenshot-item">
                        <div class="screenshot-label">操作后</div>
                        <div class="screenshot-wrapper">
                          <img
                            v-if="expandedStepIndex === step.index"
                            :src="`data:image/jpeg;base64,${step.data.screenshot_after}`"
                            class="screenshot-image"
                            loading="lazy"
                          />
                        </div>
                      </div>
                      
                      <!-- 无截图提示 -->
                      <div v-if="!step.data.screenshot_before && !step.data.screenshot_after" class="screenshot-item">
                        <div class="image-error">
                          <el-icon><Picture /></el-icon>
                          <span>该步骤无截图数据</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 错误信息 -->
                  <div v-if="step.data.error_message" class="error-message">
                    <el-alert
                      title="错误信息"
                      type="error"
                      :description="step.data.error_message"
                      :closable="false"
                    />
                  </div>
                </div>
              </el-card>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无执行步骤记录" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuestionFilled, ArrowLeft, ArrowDown } from '@element-plus/icons-vue'
import TestExecutionProgressSteps from '@/components/TestExecutionProgressSteps.vue'
import { 
  executeTest,
  getExecutions,
  getExecutionLogs,
  deleteExecution as deleteExecutionApi,
  getGeneratedCodes,
  getExecutionSteps
} from '@/api/playwright-agents'
import request from '@/utils/system/request'

interface StepInfo {
  title: string
  description: string
  status?: 'wait' | 'process' | 'success' | 'error'
  duration?: number
  info?: Record<string, any>
  error?: string
}

const route = useRoute()
const router = useRouter()

const executeForm = ref({
  code_id: undefined,
  mcp_config_id: undefined,
  browser: 'chromium',
  headless: true
})

const testCodes = ref([])
const mcpConfigs = ref([])
const executing = ref(false)
const loading = ref(false)
const executions = ref([])
const filterStatus = ref('')
const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0
})

// 选择测试代码对话框
const selectCodeDialogVisible = ref(false)
const selectedCodes = ref<any[]>([])
const codeTableRef = ref()

// 执行测试进度相关
const executionStatus = ref<'idle' | 'running' | 'completed' | 'failed'>('idle')
const currentStep = ref(0)
const progressSteps = ref<StepInfo[]>([])
const totalDuration = ref(0)

// 初始化执行测试步骤
const initializeExecutionSteps = () => {
  progressSteps.value = [
    {
      title: '准备执行',
      description: '初始化测试环境',
      status: 'wait'
    },
    {
      title: '启动浏览器',
      description: '启动指定的浏览器实例',
      status: 'wait'
    },
    {
      title: '加载测试代码',
      description: '读取并解析测试代码',
      status: 'wait'
    },
    {
      title: '执行测试',
      description: '运行 Playwright 测试',
      status: 'wait'
    },
    {
      title: '收集结果',
      description: '收集测试结果和日志',
      status: 'wait'
    },
    {
      title: '生成报告',
      description: '生成测试报告',
      status: 'wait'
    },
    {
      title: '完成',
      description: '测试执行完成',
      status: 'wait'
    }
  ]
  currentStep.value = 0
  totalDuration.value = 0
}

// 更新步骤状态
const updateStepStatus = (
  stepIndex: number, 
  status: 'wait' | 'process' | 'success' | 'error',
  description?: string,
  duration?: number,
  info?: Record<string, any>,
  error?: string
) => {
  if (stepIndex >= 0 && stepIndex < progressSteps.value.length) {
    const step = progressSteps.value[stepIndex]
    step.status = status
    if (description) step.description = description
    if (duration !== undefined) step.duration = duration
    if (info) step.info = info
    if (error) step.error = error
  }
}

const handleCodeSelectionChange = (selection: any[]) => {
  selectedCodes.value = selection
}

const confirmCodeSelect = () => {
  if (selectedCodes.value.length > 0) {
    selectCodeDialogVisible.value = false
    ElMessage.success(`已选择 ${selectedCodes.value.length} 个测试代码`)
  } else {
    ElMessage.warning('请至少选择一个测试代码')
  }
}

const clearSelectedCodes = () => {
  selectedCodes.value = []
  if (codeTableRef.value) {
    codeTableRef.value.clearSelection()
  }
}

const removeCode = (code: any) => {
  const index = selectedCodes.value.findIndex(c => c.id === code.id)
  if (index > -1) {
    selectedCodes.value.splice(index, 1)
  }
}

const getCodeStatusType = (status: string) => {
  const map: any = {
    pending: 'info',
    generating: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getCodeStatusText = (status: string) => {
  const map: any = {
    pending: '待生成',
    generating: '生成中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

const logsVisible = ref(false)
const currentLogs = ref(null)
const activeTab = ref('stdout')

const stepsVisible = ref(false)
const executionSteps = ref([])
const expandedStepIndex = ref<number | null>(null)

// 虚拟滚动相关
const virtualScrollContainer = ref<HTMLElement | null>(null)
const itemHeight = 120 // 折叠状态下每项的高度
const expandedItemHeight = 1000 // 展开状态下每项的高度（包含截图）
const bufferSize = 3 // 缓冲区大小
const scrollTop = ref(0)

// 计算总高度
const totalHeight = computed(() => {
  let height = 0
  executionSteps.value.forEach((_, index) => {
    height += expandedStepIndex.value === index ? expandedItemHeight : itemHeight
  })
  return height
})

// 计算可见的步骤
const visibleSteps = computed(() => {
  if (!executionSteps.value.length) return []
  
  const containerHeight = 700 // 容器高度
  const startIndex = Math.max(0, Math.floor(scrollTop.value / itemHeight) - bufferSize)
  const endIndex = Math.min(
    executionSteps.value.length,
    Math.ceil((scrollTop.value + containerHeight) / itemHeight) + bufferSize
  )
  
  const result = []
  let offsetTop = 0
  
  for (let i = 0; i < executionSteps.value.length; i++) {
    if (i >= startIndex && i < endIndex) {
      result.push({
        index: i,
        data: executionSteps.value[i],
        offsetTop
      })
    }
    offsetTop += expandedStepIndex.value === i ? expandedItemHeight : itemHeight
  }
  
  return result
})

const handleScroll = (e: Event) => {
  const target = e.target as HTMLElement
  scrollTop.value = target.scrollTop
}

const toggleStep = (index: number) => {
  expandedStepIndex.value = expandedStepIndex.value === index ? null : index
}

const loadTestCodes = async () => {
  try {
    const res = await getGeneratedCodes({ page_size: 100 })
    if (res.status === 200) {
      testCodes.value = res.data.items || []
    }
  } catch (error) {
    console.error('加载测试代码失败:', error)
  }
}

const loadMCPConfigs = async () => {
  try {
    const res = await request({
      url: '/api/aitestrebort/global/mcp-configs',
      method: 'get'
    })
    if (res.status === 200 || res.code === 200) {
      mcpConfigs.value = Array.isArray(res.data) ? res.data : []
      console.log('MCP配置列表:', mcpConfigs.value)
    }
  } catch (error) {
    console.error('加载MCP配置失败:', error)
  }
}

const execute = async () => {
  if (selectedCodes.value.length === 0) {
    ElMessage.warning('请选择测试代码')
    return
  }

  executing.value = true
  executionStatus.value = 'running'
  initializeExecutionSteps()
  
  const startTime = Date.now()
  
  try {
    let successCount = 0
    let failCount = 0
    
    // 步骤 1: 准备执行
    updateStepStatus(0, 'process', '正在初始化测试环境...')
    currentStep.value = 0
    await new Promise(resolve => setTimeout(resolve, 300))
    updateStepStatus(0, 'success', '测试环境初始化完成', 0.3)
    
    // 批量执行
    for (const code of selectedCodes.value) {
      try {
        // 步骤 2: 启动浏览器
        updateStepStatus(1, 'process', `正在启动 ${executeForm.value.browser} 浏览器...`)
        currentStep.value = 1
        await new Promise(resolve => setTimeout(resolve, 200))
        updateStepStatus(1, 'success', '浏览器启动完成', 0.2, {
          '浏览器': executeForm.value.browser,
          '无头模式': executeForm.value.headless ? '是' : '否'
        })
        
        // 步骤 3: 加载测试代码
        updateStepStatus(2, 'process', `正在加载测试代码 #${code.id}...`)
        currentStep.value = 2
        await new Promise(resolve => setTimeout(resolve, 200))
        updateStepStatus(2, 'success', '测试代码加载完成', 0.2, {
          '代码ID': code.id,
          '框架': code.framework,
          '语言': code.language
        })
        
        // 步骤 4: 执行测试
        updateStepStatus(3, 'process', '正在执行测试...')
        currentStep.value = 3
        
        const res = await executeTest({
          ...executeForm.value,
          code_id: code.id
        })
        
        if (res.status === 200) {
          successCount++
          updateStepStatus(3, 'success', '测试执行完成', undefined, {
            '执行ID': res.data.id
          })
          
          // 步骤 5: 收集结果
          updateStepStatus(4, 'process', '正在收集测试结果...')
          currentStep.value = 4
          await new Promise(resolve => setTimeout(resolve, 200))
          updateStepStatus(4, 'success', '测试结果收集完成', 0.2)
          
          // 步骤 6: 生成报告
          updateStepStatus(5, 'process', '正在生成测试报告...')
          currentStep.value = 5
          await new Promise(resolve => setTimeout(resolve, 200))
          updateStepStatus(5, 'success', '测试报告生成完成', 0.2)
        } else {
          failCount++
          throw new Error(res.message || '执行失败')
        }
      } catch (error: any) {
        failCount++
        const failedStepIndex = Math.min(currentStep.value, progressSteps.value.length - 1)
        updateStepStatus(failedStepIndex, 'error', '执行失败', undefined, undefined, error.message)
      }
    }
    
    // 步骤 7: 完成
    if (failCount === 0) {
      updateStepStatus(6, 'success', '所有测试执行完成！')
      currentStep.value = 6
      executionStatus.value = 'completed'
    } else {
      updateStepStatus(6, 'error', '部分测试执行失败', undefined, undefined, `成功 ${successCount} 个，失败 ${failCount} 个`)
      executionStatus.value = 'failed'
    }
    
    const endTime = Date.now()
    totalDuration.value = Math.round((endTime - startTime) / 1000)
    
    // 只在批量操作时显示汇总消息
    if (selectedCodes.value.length > 1) {
      if (failCount === 0) {
        ElMessage.success(`成功提交 ${successCount} 个测试执行`)
      } else {
        ElMessage.warning(`执行完成：成功 ${successCount} 个，失败 ${failCount} 个`)
      }
    }
    
    loadExecutions()
  } catch (error: any) {
    console.error('执行失败:', error)
    executionStatus.value = 'failed'
  } finally {
    executing.value = false
  }
}

const loadExecutions = async () => {
  loading.value = true
  try {
    const res = await getExecutions({
      page: pagination.value.page,
      page_size: pagination.value.page_size,
      status: filterStatus.value || undefined
    })
    if (res.status === 200) {
      executions.value = res.data.items || []
      pagination.value.total = res.data.total || 0
    }
  } catch (error) {
    console.error('加载执行记录失败:', error)
  } finally {
    loading.value = false
  }
}

const viewLogs = async (row: any) => {
  try {
    const res = await getExecutionLogs(row.id)
    if (res.status === 200) {
      currentLogs.value = res.data
      logsVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载日志失败')
  }
}

const viewExecutionSteps = async (row: any) => {
  try {
    loading.value = true
    const res = await getExecutionSteps(row.id)
    
    console.log('=== 执行步骤 API 完整响应 ===')
    console.log('res:', res)
    
    // 直接从响应中提取 steps
    let steps = []
    
    if (res.data && res.data.steps) {
      steps = res.data.steps
      console.log('✅ 从 res.data.steps 提取，数量:', steps.length)
    } else if (res.steps) {
      steps = res.steps
      console.log('✅ 从 res.steps 提取，数量:', steps.length)
    }
    
    console.log('提取到的步骤:', steps)
    
    // 强制创建新数组以触发响应式更新
    executionSteps.value = [...steps]
    
    console.log('设置后 executionSteps.value.length:', executionSteps.value.length)
    
    // 延迟显示对话框，确保数据已更新
    await nextTick()
    stepsVisible.value = true
    
    console.log('✅ 对话框已打开，步骤数量:', executionSteps.value.length)
    
    if (steps.length === 0) {
      ElMessage.warning('该执行记录暂无步骤详情')
    }
  } catch (error: any) {
    console.error('获取执行详情失败:', error)
    ElMessage.error(error.message || '获取执行详情失败')
  } finally {
    loading.value = false
  }
}

const isValidBase64 = (str: string) => {
  if (!str || typeof str !== 'string') {
    return false
  }
  // 检查是否已经包含 data:image 前缀
  if (str.startsWith('data:image')) {
    return true
  }
  // 检查是否是有效的 base64 字符串（降低阈值到 20 字符以支持测试数据）
  return str.length > 20
}

const getImageSrc = (base64: string) => {
  if (!base64) {
    return ''
  }
  // 如果已经包含 data:image 前缀，直接返回
  if (base64.startsWith('data:image')) {
    return base64
  }
  // 检查是否是 PNG 格式（以 iVBORw0KGgo 开头）
  // 或者是 JPEG 格式（以 /9j/ 开头）
  let mimeType = 'image/jpeg'  // 默认 JPEG
  if (base64.startsWith('iVBORw0KGgo')) {
    mimeType = 'image/png'
  } else if (base64.startsWith('/9j/')) {
    mimeType = 'image/jpeg'
  }
  
  return `data:${mimeType};base64,${base64}`
}

const healTest = (row: any) => {
  router.push({
    path: '/playwright-agents-healer/index',
    query: { execution_id: row.id }
  })
}

const deleteExecution = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条执行记录吗？', '提示', {
      type: 'warning'
    })
    const res = await deleteExecutionApi(row.id)
    if (res.status === 200) {
      // 不显示成功消息，因为 request 拦截器已经处理了
      loadExecutions()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      // 不显示错误消息，因为 request 拦截器已经处理了
      console.error('删除失败:', error)
    }
  }
}

const getStatusType = (status: string) => {
  const map: any = {
    pending: 'info',
    running: 'warning',
    success: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: any = {
    pending: '待执行',
    running: '运行中',
    success: '成功',
    failed: '失败'
  }
  return map[status] || status
}

watch(filterStatus, () => {
  pagination.value.page = 1
  loadExecutions()
})

onMounted(() => {
  initializeExecutionSteps()
  loadTestCodes()
  loadMCPConfigs()
  loadExecutions()
  
  if (route.query.code_id) {
    executeForm.value.code_id = Number(route.query.code_id)
  }
})
</script>

<style scoped lang="scss">
.execution-page {
  padding: 20px;

  .header-card {
    margin-bottom: 20px;
    
    .header-title {
      display: flex;
      align-items: center;
    }
    
    h2 {
      margin: 0 0 10px 0;
      font-size: 24px;
    }
    
    p {
      margin: 0;
      color: #909399;
    }
  }

  .main-card {
    margin-bottom: 20px;
    
    :deep(.el-card__body) {
      padding: 0;
    }
    
    .content-layout {
      display: flex;
      min-height: 500px;
      
      .left-section {
        width: 450px;
        flex-shrink: 0;
        padding: 24px;
        border-right: 1px solid #EBEEF5;
        
        .section-header {
          margin-bottom: 20px;
          
          h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #303133;
          }
        }
      }
      
      .right-section {
        flex: 1;
        padding: 24px;
        background: #FAFAFA;
        
        .section-header {
          margin-bottom: 20px;
          
          h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #303133;
          }
        }
        
        .progress-content {
          background: #fff;
          border-radius: 8px;
          padding: 20px;
          max-height: 450px;
          overflow-y: auto;
          
          /* 自定义滚动条 */
          &::-webkit-scrollbar {
            width: 6px;
          }
          
          &::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
          }
          
          &::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
            
            &:hover {
              background: #a8a8a8;
            }
          }
        }
      }
    }
  }

  .list-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
  
  .action-buttons {
    display: flex;
    gap: 6px;
    flex-wrap: nowrap;
    align-items: center;
    
    .el-button {
      padding: 5px 10px;
      font-size: 12px;
    }
  }
  
  // 表格选中行样式
  :deep(.el-table) {
    .el-table__row.current-row {
      background-color: #ecf5ff !important;
    }
    
    .el-table__body tr.current-row > td {
      background-color: #ecf5ff !important;
    }
  }

  .logs-container {
    .log-content {
      background: #1e1e1e;
      color: #d4d4d4;
      padding: 15px;
      border-radius: 4px;
      max-height: 500px;
      overflow: auto;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-wrap: break-word;
      
      &.error {
        color: #f48771;
      }
    }
  }

  .steps-container {
    .virtual-scroll-container {
      height: 70vh;
      overflow-y: auto;
      overflow-x: hidden;
      position: relative;
      
      /* 自定义滚动条样式 */
      &::-webkit-scrollbar {
        width: 8px;
      }
      
      &::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
      }
      
      &::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
        
        &:hover {
          background: #555;
        }
      }
    }
    
    .virtual-step-item {
      transition: all 0.3s ease;
    }
    
    .step-expanded {
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.15);
    }
    
    .step-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      user-select: none;
      
      .step-title {
        display: flex;
        align-items: center;
        flex: 1;
      }
      
      .rotate-icon {
        transform: rotate(180deg);
        transition: transform 0.3s ease;
      }
    }
    
    .step-content {
      padding: 15px 0;
      animation: fadeIn 0.3s ease;
      
      @keyframes fadeIn {
        from {
          opacity: 0;
          transform: translateY(-10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      
      .screenshot-container {
        margin-top: 15px;
        
        h4 {
          margin-bottom: 10px;
          color: #606266;
        }
        
        .screenshot-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 15px;
        }
        
        .screenshot-item {
          border: 1px solid #dcdfe6;
          border-radius: 4px;
          overflow: hidden;
          
          .screenshot-label {
            background: #f5f7fa;
            padding: 8px 12px;
            font-weight: 500;
            color: #606266;
            border-bottom: 1px solid #dcdfe6;
          }
          
          .screenshot-wrapper {
            width: 100%;
            min-height: 300px;
            max-height: 500px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f5f5f5;
            overflow: hidden;
          }
          
          .screenshot-image {
            max-width: 100%;
            max-height: 500px;
            height: auto;
            display: block;
            object-fit: contain;
          }
          
          .image-error {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 300px;
            color: #909399;
            background: #f5f7fa;
            
            .el-icon {
              font-size: 48px;
              margin-bottom: 10px;
            }
          }
        }
      }
      
      .error-message {
        margin-top: 15px;
      }
    }
  }
}

// 响应式设计
@media (max-width: 1400px) {
  .execution-page {
    .main-card {
      .content-layout {
        .left-section {
          width: 400px;
        }
      }
    }
  }
}

@media (max-width: 1200px) {
  .execution-page {
    .main-card {
      .content-layout {
        flex-direction: column;
        
        .left-section {
          width: 100%;
          border-right: none;
          border-bottom: 1px solid #EBEEF5;
        }
        
        .right-section {
          width: 100%;
        }
      }
    }
  }
}
</style>
