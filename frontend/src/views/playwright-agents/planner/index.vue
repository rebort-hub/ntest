<template>
  <div class="planner-page">
    <el-card class="header-card">
      <div class="header-content">
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
            <h2>Playwright测试规划 (Agent)</h2>
            <p>AI自动探索你的应用，生成完整的测试计划</p>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 主内容区域 -->
    <el-card class="main-card">
      <div class="content-layout">
        <!-- 左侧：创建表单 -->
        <div class="left-section">
          <div class="section-header">
            <h3>创建新的测试计划</h3>
          </div>
          <el-form :model="planForm" label-width="120px" class="create-form">
        <el-form-item label="应用URL" required>
          <el-input 
            v-model="planForm.url" 
            placeholder="https://example.com"
            clearable
          />
          <div class="form-tip">
            只输入纯URL地址，不要包含测试需求描述
          </div>
        </el-form-item>
        <el-form-item label="测试需求描述">
          <el-input 
            v-model="planForm.requirements" 
            type="textarea"
            :rows="3"
            placeholder="描述你想要测试的场景，例如：点击输入框，输入rebort，点击百度搜索"
            clearable
          />
          <div class="form-tip">
            可选：描述具体的测试步骤和场景，AI 会根据这些需求生成测试计划
          </div>
        </el-form-item>
        <el-form-item label="LLM配置">
          <div style="width: 100%;">
            <el-select v-model="planForm.llm_config_id" placeholder="选择LLM配置（默认使用全局配置）" clearable style="width: 100%;">
              <el-option 
                v-for="config in llmConfigs" 
                :key="config.id" 
                :label="config.config_name || config.name" 
                :value="config.id"
              />
            </el-select>
          </div>
        </el-form-item>
        <el-form-item label="MCP配置">
          <div style="width: 100%;">
            <el-select v-model="planForm.mcp_config_id" placeholder="选择MCP配置（可选，用于远程浏览器）" clearable style="width: 100%;">
              <el-option 
                v-for="config in mcpConfigs" 
                :key="config.id" 
                :label="config.name" 
                :value="config.id"
              >
                <span>{{ config.name }}</span>
                <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">
                  {{ config.url }}
                </span>
              </el-option>
            </el-select>
            <div class="form-tip" style="margin-top: 5px;">
              <el-icon><InfoFilled /></el-icon>
              优先使用MCP远程浏览器，失败时自动降级到本地浏览器或LLM推理
            </div>
          </div>
        </el-form-item>
        <el-form-item label="探索深度">
          <el-input-number v-model="planForm.max_depth" :min="1" :max="5" />
          <span class="form-tip">建议2-3层，过深会增加探索时间</span>
        </el-form-item>
        <el-form-item label="超时时间(秒)">
          <el-input-number v-model="planForm.timeout" :min="30" :max="300" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="startExplore" :loading="exploring" size="small">
            {{ exploring ? '正在探索...' : '开始探索' }}
          </el-button>
        </el-form-item>
      </el-form>
        </div>
        
        <!-- 右侧：探索进度 -->
        <div class="right-section">
          <div class="section-header">
            <h3>探索进度</h3>
          </div>
          <div class="progress-content">
            <ExplorationProgressSteps 
              :status="explorationStatus"
              :current-step="currentStep"
              :steps="progressSteps"
              :total-duration="totalDuration"
            />
          </div>
        </div>
      </div>
    </el-card>

    <!-- 测试计划列表 -->
    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>测试计划列表</span>
          <el-button type="primary" size="small" @click="loadPlans">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="plans" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="url" label="应用URL" min-width="200" />
        <el-table-column label="探索深度" width="100">
          <template #default="{ row }">
            {{ row.max_depth || 2 }}层
          </template>
        </el-table-column>
        <el-table-column label="测试场景数" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.test_scenarios?.length || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="350" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">查看详情</el-button>
            <el-button size="small" type="info" @click="viewExplorationSteps(row)">探索过程</el-button>
            <el-button size="small" type="primary" @click="generateCode(row)">生成代码</el-button>
            <el-button size="small" type="danger" @click="deletePlan(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadPlans"
        @current-change="loadPlans"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="测试计划详情" width="80%" top="5vh">
      <div v-if="currentPlan" class="plan-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="应用URL">{{ currentPlan.url }}</el-descriptions-item>
          <el-descriptions-item label="探索深度">{{ currentPlan.max_depth }}层</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentPlan.status)">
              {{ getStatusText(currentPlan.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentPlan.created_at }}</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 20px">测试场景 ({{ currentPlan.test_scenarios?.length || 0 }})</h3>
        <div class="scenarios-scroll-container">
          <el-collapse v-if="currentPlan.test_scenarios?.length">
            <el-collapse-item 
              v-for="(scenario, index) in currentPlan.test_scenarios" 
              :key="index"
              :title="`场景 ${index + 1}: ${scenario.name}`"
            >
              <p><strong>描述:</strong> {{ scenario.description }}</p>
              <p><strong>优先级:</strong> 
                <el-tag 
                  size="small" 
                  :type="getPriorityType(scenario.priority)"
                >
                  {{ getPriorityText(scenario.priority) }}
                </el-tag>
              </p>
              <div v-if="scenario.steps?.length">
                <strong>测试步骤:</strong>
                <ol>
                  <li v-for="(step, idx) in scenario.steps" :key="idx">{{ step }}</li>
                </ol>
              </div>
            </el-collapse-item>
          </el-collapse>
          <el-empty v-else description="暂无测试场景" />
        </div>
      </div>
    </el-dialog>

    <!-- 探索过程对话框 -->
    <el-dialog v-model="explorationVisible" title="探索过程" width="90%" top="5vh">
      <div v-if="explorationSteps.length" class="exploration-steps">
        <div class="exploration-scroll-container">
          <el-timeline>
            <el-timeline-item
              v-for="(step, index) in explorationSteps"
              :key="index"
              :timestamp="`步骤 ${step.step_number}`"
              placement="top"
            >
              <el-card>
                <template #header>
                  <div class="step-header">
                    <span class="step-title">
                      <el-tag :type="step.status === 'success' ? 'success' : 'danger'">
                        {{ step.action }}
                      </el-tag>
                      <span style="margin-left: 10px">{{ step.description }}</span>
                    </span>
                    <span v-if="step.duration" class="step-duration">
                      耗时: {{ step.duration.toFixed(2) }}秒
                    </span>
                  </div>
                </template>
                
                <div class="step-content">
                  <el-descriptions :column="2" size="small" border>
                    <el-descriptions-item label="页面标题" v-if="step.page_title">
                      {{ step.page_title }}
                    </el-descriptions-item>
                    <el-descriptions-item label="页面URL" v-if="step.url">
                      <el-link :href="step.url" target="_blank" type="primary">
                        {{ step.url }}
                      </el-link>
                    </el-descriptions-item>
                    <el-descriptions-item label="发现元素" v-if="step.elements_found">
                      链接: {{ step.elements_found.links || 0 }} 个 | 
                      按钮: {{ step.elements_found.buttons || 0 }} 个 | 
                      输入框: {{ step.elements_found.inputs || 0 }} 个
                    </el-descriptions-item>
                    <el-descriptions-item label="状态">
                      <el-tag :type="step.status === 'success' ? 'success' : 'danger'">
                        {{ step.status }}
                      </el-tag>
                    </el-descriptions-item>
                  </el-descriptions>

                  <!-- 截图 -->
                  <div v-if="step.screenshot" class="screenshot-container">
                    <h4>页面截图:</h4>
                    <el-image
                      :src="`data:image/png;base64,${step.screenshot}`"
                      :preview-src-list="[`data:image/png;base64,${step.screenshot}`]"
                      fit="contain"
                      style="max-width: 100%; max-height: 500px; border: 1px solid #ddd; border-radius: 4px;"
                      loading="lazy"
                    />
                  </div>

                  <!-- 错误信息 -->
                  <div v-if="step.error_message" class="error-message">
                    <el-alert
                      title="错误信息"
                      type="error"
                      :description="step.error_message"
                      :closable="false"
                    />
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      <el-empty v-else description="暂无探索步骤记录" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled, ArrowLeft } from '@element-plus/icons-vue'
import ExplorationProgressSteps from '@/components/ExplorationProgressSteps.vue'
import { 
  exploreAndPlan, 
  getTestPlans, 
  getTestPlanDetail, 
  deleteTestPlan,
  getExplorationSteps
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

const router = useRouter()

const planForm = ref({
  url: '',
  requirements: '',
  llm_config_id: undefined,
  mcp_config_id: undefined,
  max_depth: 2,
  timeout: 60
})

const llmConfigs = ref([])
const mcpConfigs = ref([])
const exploring = ref(false)
const loading = ref(false)
const plans = ref([])
const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0
})

const detailVisible = ref(false)
const currentPlan = ref(null)

const explorationVisible = ref(false)
const explorationSteps = ref([])

// 探索进度相关
const explorationStatus = ref<'idle' | 'exploring' | 'completed' | 'failed'>('idle')
const currentStep = ref(0)
const progressSteps = ref<StepInfo[]>([])
const totalDuration = ref(0)

// 初始化探索步骤
const initializeProgressSteps = () => {
  progressSteps.value = [
    {
      title: '准备探索',
      description: '初始化浏览器和配置',
      status: 'wait'
    },
    {
      title: '增强导航',
      description: '使用官方 Playwright MCP 导航到目标页面',
      status: 'wait'
    },
    {
      title: '页面快照',
      description: '获取页面的可访问性树结构',
      status: 'wait'
    },
    {
      title: '页面截图',
      description: '捕获页面视觉状态',
      status: 'wait'
    },
    {
      title: '网络分析',
      description: '分析网络请求和 API 调用',
      status: 'wait'
    },
    {
      title: '日志检查',
      description: '检查控制台日志和错误',
      status: 'wait'
    },
    {
      title: '历史记录',
      description: '记录导航历史和路径',
      status: 'wait'
    },
    {
      title: 'AI 分析',
      description: 'LLM 分析页面结构和生成测试计划',
      status: 'wait'
    },
    {
      title: '完成',
      description: '探索完成，测试计划已生成',
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

const loadLLMConfigs = async () => {
  try {
    console.log('开始加载LLM配置...')
    const res = await request({
      url: '/api/aitestrebort/global/llm-configs',
      method: 'get'
    })
    console.log('LLM配置响应:', res)
    // 后端返回的是 status 而不是 code
    if (res.status === 200 || res.code === 200) {
      // 后端直接返回数组
      llmConfigs.value = Array.isArray(res.data) ? res.data : []
      console.log('LLM配置列表:', llmConfigs.value)
    } else {
      console.error('LLM配置加载失败，响应:', res)
    }
  } catch (error) {
    console.error('加载LLM配置失败:', error)
  }
}

const loadMCPConfigs = async () => {
  try {
    console.log('开始加载MCP配置...')
    // AI测试代理模块是独立的，使用全局 MCP 配置
    const res = await request({
      url: '/api/aitestrebort/global/mcp-configs',
      method: 'get'
    })
    console.log('MCP配置响应:', res)
    if (res.status === 200 || res.code === 200) {
      mcpConfigs.value = Array.isArray(res.data?.items) ? res.data.items : (Array.isArray(res.data) ? res.data : [])
      console.log('MCP配置列表:', mcpConfigs.value)
    } else {
      console.error('MCP配置加载失败，响应:', res)
    }
  } catch (error) {
    console.error('加载MCP配置失败:', error)
    // MCP配置加载失败不影响使用，只是没有远程浏览器选项
    mcpConfigs.value = []
  }
}

const startExplore = async () => {
  if (!planForm.value.url) {
    ElMessage.warning('请输入应用URL')
    return
  }

  exploring.value = true
  explorationStatus.value = 'exploring'
  initializeProgressSteps()
  
  const startTime = Date.now()
  
  try {
    // 步骤 1: 准备探索
    updateStepStatus(0, 'process', '正在初始化...')
    currentStep.value = 0
    await new Promise(resolve => setTimeout(resolve, 500))
    updateStepStatus(0, 'success', '初始化完成', 0.5)
    
    // 步骤 2-7: 模拟探索过程
    for (let i = 1; i <= 6; i++) {
      updateStepStatus(i, 'process')
      currentStep.value = i
      await new Promise(resolve => setTimeout(resolve, 300))
    }
    
    // 步骤 8: AI 分析
    updateStepStatus(7, 'process', '正在分析页面结构...')
    currentStep.value = 7
    
    const res = await exploreAndPlan(planForm.value)
    
    if (res.status === 200) {
      // 更新步骤状态（基于实际探索结果）
      const plan = res.data
      
      if (plan.exploration_steps && plan.exploration_steps.length > 0) {
        const firstStep = plan.exploration_steps[0]
        
        // 更新各个步骤的详细信息
        updateStepStatus(1, 'success', '导航完成', firstStep.duration, {
          'URL': firstStep.url || planForm.value.url,
          '页面标题': firstStep.page_title || '已获取'
        })
        
        updateStepStatus(2, 'success', '快照获取完成', undefined, {
          '链接': firstStep.elements_found?.links || 0,
          '按钮': firstStep.elements_found?.buttons || 0,
          '输入框': firstStep.elements_found?.inputs || 0
        })
        
        updateStepStatus(3, 'success', '截图完成', undefined, {
          '截图': firstStep.screenshot ? '已获取' : '未获取'
        })
        
        updateStepStatus(4, 'success', '网络分析完成', undefined, {
          '网络请求': firstStep.network_requests || 0
        })
        
        updateStepStatus(5, 'success', '日志检查完成', undefined, {
          '控制台日志': firstStep.console_logs || 0
        })
        
        updateStepStatus(6, 'success', '历史记录完成', undefined, {
          '导航历史': firstStep.navigation_history || 0
        })
      } else {
        // 如果没有详细步骤，标记为成功
        for (let i = 1; i <= 6; i++) {
          updateStepStatus(i, 'success')
        }
      }
      
      updateStepStatus(7, 'success', 'AI 分析完成', undefined, {
        '测试场景': plan.test_scenarios?.length || 0
      })
      
      // 步骤 9: 完成
      updateStepStatus(8, 'success', '探索完成！')
      currentStep.value = 8
      
      const endTime = Date.now()
      totalDuration.value = Math.round((endTime - startTime) / 1000)
      
      explorationStatus.value = 'completed'
      
      planForm.value.url = ''
      planForm.value.requirements = ''
      loadPlans()
    } else {
      throw new Error(res.message || '探索失败')
    }
  } catch (error: any) {
    console.error('探索失败:', error)
    
    // 标记当前步骤为失败
    const failedStepIndex = Math.min(currentStep.value, progressSteps.value.length - 1)
    updateStepStatus(failedStepIndex, 'error', '探索失败', undefined, undefined, error.message)
    
    explorationStatus.value = 'failed'
  } finally {
    exploring.value = false
  }
}

const loadPlans = async () => {
  loading.value = true
  try {
    const res = await getTestPlans({
      page: pagination.value.page,
      page_size: pagination.value.page_size
    })
    if (res.status === 200) {
      plans.value = res.data.items || []
      pagination.value.total = res.data.total || 0
    }
  } catch (error) {
    console.error('加载测试计划失败:', error)
  } finally {
    loading.value = false
  }
}

const viewDetail = async (row: any) => {
  try {
    const res = await getTestPlanDetail(row.id)
    if (res.status === 200) {
      currentPlan.value = res.data
      detailVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

const viewExplorationSteps = async (row: any) => {
  try {
    loading.value = true
    const res = await getExplorationSteps(row.id)
    if (res.status === 200 && res.data) {
      explorationSteps.value = res.data.steps || []
      explorationVisible.value = true
      
      if (explorationSteps.value.length === 0) {
        ElMessage.warning('该计划暂无探索步骤记录')
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取探索步骤失败')
  } finally {
    loading.value = false
  }
}

const generateCode = (row: any) => {
  router.push({
    path: '/playwright-agents-generator/index',
    query: { plan_id: row.id }
  })
}

const deletePlan = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试计划吗？', '提示', {
      type: 'warning'
    })
    const res = await deleteTestPlan(row.id)
    if (res.status === 200) {
      // 不显示成功消息，因为 request 拦截器已经处理了
      loadPlans()
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
    exploring: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: any = {
    pending: '待处理',
    exploring: '探索中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

const getPriorityText = (priority: string) => {
  const map: any = {
    high: '高',
    medium: '中',
    low: '低',
    critical: '紧急',
    normal: '普通'
  }
  return map[priority?.toLowerCase()] || priority
}

const getPriorityType = (priority: string) => {
  const map: any = {
    high: 'danger',
    critical: 'danger',
    medium: 'warning',
    normal: 'info',
    low: 'info'
  }
  return map[priority?.toLowerCase()] || 'info'
}

onMounted(() => {
  initializeProgressSteps()
  loadLLMConfigs()
  loadMCPConfigs()
  loadPlans()
})
</script>

<style scoped lang="scss">
.planner-page {
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
        
        .create-form {
          .form-tip {
            margin-left: 10px;
            font-size: 12px;
            color: #909399;
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

  .plan-detail {
    h3 {
      margin: 20px 0 10px 0;
    }
    
    .scenarios-scroll-container {
      max-height: 60vh;
      overflow-y: auto;
      padding-right: 10px;
      
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
  }

  .exploration-steps {
    .exploration-scroll-container {
      max-height: 70vh;
      overflow-y: auto;
      padding-right: 10px;
      
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
    
    .step-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .step-title {
        display: flex;
        align-items: center;
        font-weight: 500;
      }
      
      .step-duration {
        color: #909399;
        font-size: 12px;
      }
    }
    
    .step-content {
      .screenshot-container {
        margin-top: 15px;
        
        h4 {
          margin-bottom: 10px;
          color: #606266;
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
  .planner-page {
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
  .planner-page {
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
