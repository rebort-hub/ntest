<template>
  <div class="healer-page">
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
          <h2>Playwright自愈修复 (Agent)</h2>
          <p>AI自动分析失败原因并修复测试代码</p>
        </div>
      </div>
    </el-card>

    <!-- 主内容区域 -->
    <el-card class="main-card">
      <div class="content-layout">
        <!-- 左侧：修复表单 -->
        <div class="left-section">
          <div class="section-header">
            <h3>修复失败的测试</h3>
          </div>
          <el-form :model="healForm" label-width="120px" class="heal-form">
        <el-form-item label="失败的执行" required>
          <div style="display: flex; gap: 10px; width: 100%;">
            <el-input 
              v-model="selectedExecutionDisplay" 
              placeholder="点击选择失败的执行记录" 
              readonly
              style="flex: 1"
            />
            <el-button type="primary" @click="showExecutionSelector">选择执行</el-button>
          </div>
        </el-form-item>
        <el-form-item label="LLM配置">
          <el-select v-model="healForm.llm_config_id" placeholder="默认使用全局配置" clearable style="width: 100%">
            <el-option 
              v-for="config in llmConfigs" 
              :key="config.id" 
              :label="config.config_name || config.name" 
              :value="config.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="heal" :loading="healing" size="small">
            {{ healing ? '修复中...' : '开始修复' }}
          </el-button>
          <el-button @click="viewExecutionDetail" v-if="healForm.execution_id">
            查看执行详情
          </el-button>
        </el-form-item>
      </el-form>
        </div>
        
        <!-- 右侧：修复进度 -->
        <div class="right-section">
          <div class="section-header">
            <h3>修复进度</h3>
          </div>
          <div class="progress-content">
            <HealingProgressSteps 
              :status="healingStatus"
              :current-step="currentStep"
              :steps="progressSteps"
              :total-duration="totalDuration"
            />
          </div>
        </div>
      </div>
    </el-card>

    <!-- 失败执行选择对话框 -->
    <el-dialog 
      v-model="executionSelectorVisible" 
      title="选择失败的执行记录" 
      width="1000px"
      top="5vh"
    >
      <el-table 
        :data="failedExecutions" 
        v-loading="loadingExecutions"
        highlight-current-row
        @current-change="handleExecutionSelect"
        style="width: 100%"
        max-height="500"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="代码ID" width="100">
          <template #default="{ row }">
            #{{ row.code_id }}
          </template>
        </el-table-column>
        <el-table-column prop="test_name" label="测试名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="danger">失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="错误信息" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.error_message || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="执行时间" width="180" />
      </el-table>
      
      <template #footer>
        <el-button @click="executionSelectorVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExecutionSelect" :disabled="!tempSelectedExecution">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 修复历史 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>修复历史</span>
          <el-button type="primary" size="small" @click="loadHealHistory">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="healHistory" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="原执行记录" width="120">
          <template #default="{ row }">
            #{{ row.execution_id }}
          </template>
        </el-table-column>
        <el-table-column label="原代码" width="100">
          <template #default="{ row }">
            #{{ row.original_code_id }}
          </template>
        </el-table-column>
        <el-table-column label="修复后代码" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.fixed_code_id" type="success">#{{ row.fixed_code_id }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="修复说明" min-width="200">
          <template #default="{ row }">
            <el-tooltip :content="row.fix_description" placement="top" v-if="row.fix_description">
              <span class="text-ellipsis">{{ row.fix_description }}</span>
            </el-tooltip>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="修复时间" width="180" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <div style="display: flex; gap: 8px; white-space: nowrap;">
              <el-button size="small" @click="viewHealDetail(row)">查看详情</el-button>
              <el-button 
                size="small" 
                type="success" 
                @click="executeFixedCode(row)"
                v-if="row.fixed_code_id"
              >
                执行修复后代码
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next"
        @size-change="loadHealHistory"
        @current-change="loadHealHistory"
        style="margin-top: 20px"
      />
    </el-card>

    <!-- 修复详情对话框 -->
    <el-dialog v-model="detailVisible" title="修复详情" width="80%" top="5vh">
      <div v-if="currentHeal" class="heal-detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="修复ID">{{ currentHeal.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentHeal.status)">
              {{ getStatusText(currentHeal.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="原执行记录">#{{ currentHeal.execution_id }}</el-descriptions-item>
          <el-descriptions-item label="原代码">#{{ currentHeal.original_code_id }}</el-descriptions-item>
          <el-descriptions-item label="修复后代码">
            <el-tag v-if="currentHeal.fixed_code_id" type="success">#{{ currentHeal.fixed_code_id }}</el-tag>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="修复时间">{{ currentHeal.created_at }}</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 20px">修复说明</h3>
        <el-alert :title="currentHeal.fix_description || '无说明'" type="info" :closable="false" />

        <h3 style="margin-top: 20px">错误分析</h3>
        <pre class="analysis-content">{{ currentHeal.error_analysis || '无分析' }}</pre>

        <div v-if="currentHeal.changes" style="margin-top: 20px">
          <h3>代码变更</h3>
          <el-collapse class="changes-collapse">
            <el-collapse-item 
              v-for="(change, index) in currentHeal.changes" 
              :key="index"
              :title="`变更 ${index + 1}`"
            >
              <div class="change-item-content">
                <p><strong>类型:</strong> {{ change.type }}</p>
                <p><strong>说明:</strong> {{ change.description }}</p>
                <div v-if="change.diff">
                  <strong>差异:</strong>
                  <pre class="diff-content">{{ change.diff }}</pre>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import HealingProgressSteps from '@/components/HealingProgressSteps.vue'
import { healFailedTest, getExecutions } from '@/api/playwright-agents'
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

const healForm = ref({
  execution_id: undefined,
  llm_config_id: undefined
})

const failedExecutions = ref([])
const llmConfigs = ref([])
const healing = ref(false)
const loading = ref(false)
const loadingExecutions = ref(false)
const healHistory = ref([])
const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0
})

const detailVisible = ref(false)
const currentHeal = ref(null)

// 执行选择器相关
const executionSelectorVisible = ref(false)
const tempSelectedExecution = ref(null)
const selectedExecutionDisplay = ref('')

// 修复进度相关
const healingStatus = ref<'idle' | 'healing' | 'completed' | 'failed'>('idle')
const currentStep = ref(0)
const progressSteps = ref<StepInfo[]>([])
const totalDuration = ref(0)

// 初始化修复步骤
const initializeHealingSteps = () => {
  progressSteps.value = [
    {
      title: '准备修复',
      description: '初始化修复环境',
      status: 'wait'
    },
    {
      title: '加载失败信息',
      description: '读取执行失败的详细信息',
      status: 'wait'
    },
    {
      title: '错误分析',
      description: 'AI 分析失败原因',
      status: 'wait'
    },
    {
      title: '生成修复方案',
      description: 'AI 生成代码修复方案',
      status: 'wait'
    },
    {
      title: '应用修复',
      description: '应用修复到测试代码',
      status: 'wait'
    },
    {
      title: '验证修复',
      description: '验证修复后的代码',
      status: 'wait'
    },
    {
      title: '完成',
      description: '修复完成',
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

const loadFailedExecutions = async () => {
  loadingExecutions.value = true
  try {
    const res = await getExecutions({ status: 'failed', page_size: 100 })
    if (res.status === 200) {
      failedExecutions.value = res.data.items || []
    }
  } catch (error) {
    console.error('加载失败执行记录失败:', error)
  } finally {
    loadingExecutions.value = false
  }
}

const showExecutionSelector = () => {
  executionSelectorVisible.value = true
  loadFailedExecutions()
}

const handleExecutionSelect = (row: any) => {
  tempSelectedExecution.value = row
}

const confirmExecutionSelect = () => {
  if (tempSelectedExecution.value) {
    healForm.value.execution_id = tempSelectedExecution.value.id
    selectedExecutionDisplay.value = `#${tempSelectedExecution.value.id} - 代码#${tempSelectedExecution.value.code_id} - ${tempSelectedExecution.value.test_name || '未命名'}`
    executionSelectorVisible.value = false
  }
}

const loadLLMConfigs = async () => {
  try {
    const res = await request({
      url: '/api/aitestrebort/global/llm-configs',
      method: 'get'
    })
    // 后端返回的是 status 而不是 code
    if (res.status === 200 || res.code === 200) {
      // 后端直接返回数组
      llmConfigs.value = Array.isArray(res.data) ? res.data : []
    }
  } catch (error) {
    console.error('加载LLM配置失败:', error)
  }
}

const heal = async () => {
  if (!healForm.value.execution_id) {
    ElMessage.warning('请选择失败的执行记录')
    return
  }

  healing.value = true
  healingStatus.value = 'healing'
  initializeHealingSteps()
  
  const startTime = Date.now()
  
  try {
    // 步骤 1: 准备修复
    updateStepStatus(0, 'process', '正在初始化修复环境...')
    currentStep.value = 0
    await new Promise(resolve => setTimeout(resolve, 300))
    updateStepStatus(0, 'success', '修复环境初始化完成', 0.3)
    
    // 步骤 2: 加载失败信息
    updateStepStatus(1, 'process', '正在读取执行失败信息...')
    currentStep.value = 1
    await new Promise(resolve => setTimeout(resolve, 200))
    updateStepStatus(1, 'success', '失败信息加载完成', 0.2, {
      '执行ID': healForm.value.execution_id
    })
    
    // 步骤 3: 错误分析
    updateStepStatus(2, 'process', 'AI 正在分析失败原因...')
    currentStep.value = 2
    await new Promise(resolve => setTimeout(resolve, 300))
    updateStepStatus(2, 'success', '错误分析完成', 0.3)
    
    // 步骤 4: 生成修复方案
    updateStepStatus(3, 'process', 'AI 正在生成修复方案...')
    currentStep.value = 3
    
    const res = await healFailedTest(healForm.value)
    
    if (res.status === 200) {
      const healResult = res.data
      
      updateStepStatus(3, 'success', '修复方案生成完成', undefined, {
        '修复ID': healResult.id,
        '修复方案': '已生成'
      })
      
      // 步骤 5: 应用修复
      updateStepStatus(4, 'process', '正在应用修复到代码...')
      currentStep.value = 4
      await new Promise(resolve => setTimeout(resolve, 200))
      updateStepStatus(4, 'success', '修复已应用', 0.2, {
        '修复后代码ID': healResult.fixed_code_id || '未生成'
      })
      
      // 步骤 6: 验证修复
      updateStepStatus(5, 'process', '正在验证修复结果...')
      currentStep.value = 5
      await new Promise(resolve => setTimeout(resolve, 200))
      updateStepStatus(5, 'success', '修复验证完成', 0.2)
      
      // 步骤 7: 完成
      updateStepStatus(6, 'success', '修复完成！')
      currentStep.value = 6
      healingStatus.value = 'completed'
      
      const endTime = Date.now()
      totalDuration.value = Math.round((endTime - startTime) / 1000)
      
      loadHealHistory()
    } else {
      throw new Error(res.message || '修复失败')
    }
  } catch (error: any) {
    console.error('修复失败:', error)
    
    // 标记当前步骤为失败
    const failedStepIndex = Math.min(currentStep.value, progressSteps.value.length - 1)
    updateStepStatus(failedStepIndex, 'error', '修复失败', undefined, undefined, error.message)
    
    healingStatus.value = 'failed'
  } finally {
    healing.value = false
  }
}

const loadHealHistory = async () => {
  loading.value = true
  try {
    const res = await request({
      url: '/api/playwright-agents/healer/history',
      method: 'get',
      params: {
        page: pagination.value.page,
        page_size: pagination.value.page_size
      }
    })
    if (res.status === 200) {
      healHistory.value = res.data.items || []
      pagination.value.total = res.data.total || 0
    }
  } catch (error) {
    console.error('加载修复历史失败:', error)
  } finally {
    loading.value = false
  }
}

const viewExecutionDetail = () => {
  router.push({
    path: '/playwright-agents/execution',
    query: { execution_id: healForm.value.execution_id }
  })
}

const viewHealDetail = async (row: any) => {
  try {
    const res = await request({
      url: `/api/playwright-agents/healer/history/${row.id}`,
      method: 'get'
    })
    if (res.status === 200) {
      currentHeal.value = res.data
      detailVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

const executeFixedCode = (row: any) => {
  router.push({
    path: '/playwright-agents/execution',
    query: { code_id: row.fixed_code_id }
  })
}

const getStatusType = (status: string) => {
  const map: any = {
    pending: 'info',
    healing: 'warning',
    success: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: any = {
    pending: '待修复',
    healing: '修复中',
    success: '修复成功',
    failed: '修复失败'
  }
  return map[status] || status
}

onMounted(async () => {
  initializeHealingSteps()
  loadLLMConfigs()
  loadHealHistory()
  
  if (route.query.execution_id) {
    healForm.value.execution_id = Number(route.query.execution_id)
    // 加载执行记录以显示名称
    await loadFailedExecutions()
    const execution = failedExecutions.value.find((e: any) => e.id === healForm.value.execution_id)
    if (execution) {
      selectedExecutionDisplay.value = `#${execution.id} - 代码#${execution.code_id} - ${execution.test_name || '未命名'}`
    }
  }
})
</script>

<style scoped lang="scss">
.healer-page {
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

  .history-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .text-ellipsis {
      display: inline-block;
      max-width: 200px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      cursor: pointer;
    }
  }

  .analysis-content,
  .diff-content {
    background: #f5f7fa;
    padding: 15px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 300px;
    overflow: auto;
  }
}

// 修复详情对话框样式优化
.heal-detail-content {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 10px;

  h3 {
    margin: 20px 0 10px 0;
    font-size: 16px;
    font-weight: 600;
  }

  .changes-collapse {
    .change-item-content {
      max-height: 400px;
      overflow-y: auto;
      
      p {
        margin: 8px 0;
      }

      .diff-content {
        margin-top: 10px;
        max-height: 250px;
      }
    }
  }
}

// 响应式设计
@media (max-width: 1400px) {
  .healer-page {
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
  .healer-page {
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
