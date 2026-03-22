<template>
  <div class="generator-page">
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
          <h2>Playwright代码生成器 (Agent)</h2>
          <p>将测试计划转换为可执行的 Playwright 测试代码</p>
        </div>
      </div>
    </el-card>

    <!-- 主内容区域 -->
    <el-card class="main-card">
      <div class="content-layout">
        <!-- 左侧：生成表单 -->
        <div class="left-section">
          <div class="section-header">
            <h3>生成测试代码</h3>
          </div>
          <el-form :model="generateForm" label-width="120px" class="generate-form">
        <el-form-item label="测试计划" required>
          <div style="display: flex; align-items: center; gap: 10px;">
            <el-button type="primary" @click="selectPlanDialogVisible = true">
              {{ selectedPlans.length > 0 ? `已选择 ${selectedPlans.length} 个测试计划` : '点击选择测试计划' }}
            </el-button>
            <el-button 
              v-if="selectedPlans.length > 0" 
              size="small" 
              @click="clearSelectedPlans"
            >
              清空
            </el-button>
          </div>
          <div v-if="selectedPlans.length > 0" style="margin-top: 10px;">
            <el-tag 
              v-for="plan in selectedPlans" 
              :key="plan.id" 
              closable 
              @close="removePlan(plan)"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              #{{ plan.id }} - {{ plan.url }}
            </el-tag>
          </div>
        </el-form-item>
        <el-form-item label="LLM配置">
          <el-select v-model="generateForm.llm_config_id" placeholder="默认使用全局配置" clearable style="width: 300px">
            <el-option 
              v-for="config in llmConfigs" 
              :key="config.id" 
              :label="config.config_name || config.name" 
              :value="config.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="测试框架">
          <el-radio-group v-model="generateForm.framework">
            <el-radio label="playwright">Playwright</el-radio>
            <el-radio label="playwright-python">Playwright (Python)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="编程语言">
          <el-radio-group v-model="generateForm.language">
            <el-radio label="typescript">TypeScript</el-radio>
            <el-radio label="javascript">JavaScript</el-radio>
            <el-radio label="python">Python</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="generate" :loading="generating" size="small">
            {{ generating ? '生成中...' : (selectedPlans.length > 1 ? `批量生成 (${selectedPlans.length}个)` : '生成代码') }}
          </el-button>
        </el-form-item>
      </el-form>
        </div>
        
        <!-- 右侧：代码生成进度 -->
        <div class="right-section">
          <div class="section-header">
            <h3>代码</h3>
          </div>
          <div class="progress-content">
            <CodeGenerationProgressSteps 
              :status="generationStatus"
              :current-step="currentStep"
              :steps="progressSteps"
              :total-duration="totalDuration"
            />
          </div>
        </div>
      </div>
    </el-card>

    <!-- 选择测试计划对话框 -->
    <el-dialog v-model="selectPlanDialogVisible" title="选择测试计划" width="1000px">
      <el-table 
        ref="planTableRef"
        :data="testPlans" 
        :row-class-name="tableRowClassName"
        @selection-change="handlePlanSelectionChange"
        style="width: 100%"
        max-height="500"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="url" label="应用URL" min-width="250" />
        <el-table-column label="测试场景数" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.test_scenarios?.length || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
      </el-table>
      <template #footer>
        <el-button @click="selectPlanDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmPlanSelect" :disabled="selectedPlans.length === 0">
          确定 {{ selectedPlans.length > 0 ? `(已选${selectedPlans.length}项)` : '' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 生成的代码列表 -->
    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>生成的代码列表</span>
          <div>
            <el-button 
              type="success" 
              size="small" 
              @click="batchExecute"
              :disabled="selectedCodes.length === 0"
              style="margin-right: 10px"
            >
              批量执行 {{ selectedCodes.length > 0 ? `(${selectedCodes.length})` : '' }}
            </el-button>
            <el-button type="primary" size="small" @click="loadCodes">刷新</el-button>
          </div>
        </div>
      </template>
      
      <el-table 
        ref="codeTableRef"
        :data="codes" 
        v-loading="loading" 
        stripe
        @selection-change="handleCodeSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="测试计划" min-width="150">
          <template #default="{ row }">
            #{{ row.plan_id }} - {{ row.plan_url }}
          </template>
        </el-table-column>
        <el-table-column prop="framework" label="框架" width="150" />
        <el-table-column prop="language" label="语言" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getCodeStatusType(row.status)">
              {{ getCodeStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewCode(row)">查看代码</el-button>
            <el-button size="small" type="success" @click="executeCode(row)">执行</el-button>
            <el-button size="small" type="primary" @click="downloadCode(row)">下载</el-button>
            <el-button size="small" type="danger" @click="deleteCode(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next"
        @size-change="loadCodes"
        @current-change="loadCodes"
        style="margin-top: 20px"
      />
    </el-card>

    <!-- 代码查看/编辑对话框 -->
    <el-dialog v-model="codeVisible" title="测试代码" width="80%" top="5vh">
      <div v-if="currentCode">
        <el-alert 
          v-if="isEditing"
          title="编辑模式" 
          type="warning" 
          :closable="false"
          style="margin-bottom: 15px"
        >
          您正在编辑代码，修改后请点击"保存修改"按钮保存
        </el-alert>
        
        <el-tabs v-model="activeTab">
          <el-tab-pane label="代码" name="code">
            <vue3-ace-editor
              v-model:value="editableCode"
              :lang="getEditorLang(currentCode.language)"
              theme="monokai"
              :options="{ readOnly: !isEditing, fontSize: 14 }"
              style="height: 500px"
            />
          </el-tab-pane>
          <el-tab-pane label="配置文件" name="config" v-if="currentCode.config_file">
            <vue3-ace-editor
              v-model:value="editableConfig"
              lang="json"
              theme="monokai"
              :options="{ readOnly: !isEditing, fontSize: 14 }"
              style="height: 500px"
            />
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <el-button 
              v-if="!isEditing" 
              type="warning" 
              @click="enableEdit"
            >
              编辑代码
            </el-button>
            <el-button 
              v-if="isEditing" 
              @click="cancelEdit"
            >
              取消编辑
            </el-button>
          </div>
          <div>
            <el-button @click="codeVisible = false">关闭</el-button>
            <el-button 
              v-if="isEditing" 
              type="primary" 
              @click="saveCode"
              :loading="saving"
            >
              保存修改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { VAceEditor as Vue3AceEditor } from 'vue3-ace-editor'
import CodeGenerationProgressSteps from '@/components/CodeGenerationProgressSteps.vue'
import 'ace-builds/src-noconflict/mode-typescript'
import 'ace-builds/src-noconflict/mode-javascript'
import 'ace-builds/src-noconflict/mode-python'
import 'ace-builds/src-noconflict/mode-json'
import 'ace-builds/src-noconflict/theme-monokai'
import { 
  generateTestCode, 
  getGeneratedCodes, 
  getGeneratedCodeDetail,
  updateGeneratedCode,
  deleteGeneratedCode,
  getTestPlans
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

const generateForm = ref({
  plan_id: undefined,
  llm_config_id: undefined,
  framework: 'playwright',
  language: 'typescript'
})

const testPlans = ref([])
const llmConfigs = ref([])
const generating = ref(false)
const loading = ref(false)
const codes = ref([])
const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0
})

const codeVisible = ref(false)
const currentCode = ref(null)
const activeTab = ref('code')
const isEditing = ref(false)
const editableCode = ref('')
const editableConfig = ref('')
const saving = ref(false)

// 选择测试计划对话框
const selectPlanDialogVisible = ref(false)
const selectedPlans = ref<any[]>([])
const planTableRef = ref()

// 选择代码列表
const selectedCodes = ref<any[]>([])
const codeTableRef = ref()

// 代码生成进度相关
const generationStatus = ref<'idle' | 'generating' | 'completed' | 'failed'>('idle')
const currentStep = ref(0)
const progressSteps = ref<StepInfo[]>([])
const totalDuration = ref(0)

// 初始化代码生成步骤
const initializeGenerationSteps = () => {
  progressSteps.value = [
    {
      title: '准备生成',
      description: '初始化代码生成环境',
      status: 'wait'
    },
    {
      title: '加载测试计划',
      description: '读取测试计划和场景',
      status: 'wait'
    },
    {
      title: 'LLM 分析',
      description: 'AI 分析测试场景结构',
      status: 'wait'
    },
    {
      title: '生成测试代码',
      description: '根据框架和语言生成代码',
      status: 'wait'
    },
    {
      title: '生成配置文件',
      description: '生成 Playwright 配置',
      status: 'wait'
    },
    {
      title: '代码优化',
      description: '优化代码结构和格式',
      status: 'wait'
    },
    {
      title: '完成',
      description: '代码生成完成',
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

const handlePlanSelectionChange = (selection: any[]) => {
  selectedPlans.value = selection
}

const confirmPlanSelect = () => {
  if (selectedPlans.value.length > 0) {
    selectPlanDialogVisible.value = false
    ElMessage.success(`已选择 ${selectedPlans.value.length} 个测试计划`)
  } else {
    ElMessage.warning('请至少选择一个测试计划')
  }
}

const clearSelectedPlans = () => {
  selectedPlans.value = []
  if (planTableRef.value) {
    planTableRef.value.clearSelection()
  }
}

const removePlan = (plan: any) => {
  const index = selectedPlans.value.findIndex(p => p.id === plan.id)
  if (index > -1) {
    selectedPlans.value.splice(index, 1)
  }
}

const handleCodeSelectionChange = (selection: any[]) => {
  selectedCodes.value = selection
}

const batchExecute = async () => {
  if (selectedCodes.value.length === 0) {
    ElMessage.warning('请选择要执行的代码')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要批量执行 ${selectedCodes.value.length} 个测试代码吗？`,
      '批量执行确认',
      {
        type: 'warning'
      }
    )
    
    ElMessage.info(`开始批量执行 ${selectedCodes.value.length} 个测试...`)
    
    // 跳转到执行记录页面
    router.push({
      path: '/playwright-agents/execution',
      query: { 
        batch: 'true',
        code_ids: selectedCodes.value.map(c => c.id).join(',')
      }
    })
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量执行失败:', error)
    }
  }
}

const tableRowClassName = ({ row, rowIndex }: any) => {
  return ''
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

const loadTestPlans = async () => {
  try {
    const res = await getTestPlans({ page_size: 100 })
    if (res.status === 200) {
      testPlans.value = res.data.items || []
    }
  } catch (error) {
    console.error('加载测试计划失败:', error)
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

const generate = async () => {
  if (selectedPlans.value.length === 0) {
    ElMessage.warning('请选择测试计划')
    return
  }

  generating.value = true
  generationStatus.value = 'generating'
  initializeGenerationSteps()
  
  const startTime = Date.now()
  
  try {
    let successCount = 0
    let failCount = 0
    
    // 步骤 1: 准备生成
    updateStepStatus(0, 'process', '正在初始化...')
    currentStep.value = 0
    await new Promise(resolve => setTimeout(resolve, 300))
    updateStepStatus(0, 'success', '初始化完成', 0.3)
    
    // 批量生成
    for (const plan of selectedPlans.value) {
      try {
        // 步骤 2: 加载测试计划
        updateStepStatus(1, 'process', `正在加载测试计划 #${plan.id}...`)
        currentStep.value = 1
        await new Promise(resolve => setTimeout(resolve, 200))
        updateStepStatus(1, 'success', '测试计划加载完成', 0.2, {
          '计划ID': plan.id,
          '测试场景': plan.test_scenarios?.length || 0
        })
        
        // 步骤 3: LLM 分析
        updateStepStatus(2, 'process', 'AI 正在分析测试场景...')
        currentStep.value = 2
        await new Promise(resolve => setTimeout(resolve, 300))
        updateStepStatus(2, 'success', 'AI 分析完成', 0.3)
        
        // 步骤 4: 生成测试代码
        updateStepStatus(3, 'process', '正在生成测试代码...')
        currentStep.value = 3
        
        const res = await generateTestCode({
          ...generateForm.value,
          plan_id: plan.id
        })
        
        if (res.status === 200) {
          successCount++
          updateStepStatus(3, 'success', '测试代码生成完成', undefined, {
            '框架': generateForm.value.framework,
            '语言': generateForm.value.language
          })
          
          // 步骤 5: 生成配置文件
          updateStepStatus(4, 'process', '正在生成配置文件...')
          currentStep.value = 4
          await new Promise(resolve => setTimeout(resolve, 200))
          updateStepStatus(4, 'success', '配置文件生成完成', 0.2)
          
          // 步骤 6: 代码优化
          updateStepStatus(5, 'process', '正在优化代码...')
          currentStep.value = 5
          await new Promise(resolve => setTimeout(resolve, 200))
          updateStepStatus(5, 'success', '代码优化完成', 0.2)
        } else {
          failCount++
          throw new Error(res.message || '生成失败')
        }
      } catch (error: any) {
        failCount++
        const failedStepIndex = Math.min(currentStep.value, progressSteps.value.length - 1)
        updateStepStatus(failedStepIndex, 'error', '生成失败', undefined, undefined, error.message)
      }
    }
    
    // 步骤 7: 完成
    if (failCount === 0) {
      updateStepStatus(6, 'success', '所有代码生成完成！')
      currentStep.value = 6
      generationStatus.value = 'completed'
    } else {
      updateStepStatus(6, 'error', '部分代码生成失败', undefined, undefined, `成功 ${successCount} 个，失败 ${failCount} 个`)
      generationStatus.value = 'failed'
    }
    
    const endTime = Date.now()
    totalDuration.value = Math.round((endTime - startTime) / 1000)
    
    // 只在批量操作时显示汇总消息
    if (selectedPlans.value.length > 1) {
      if (failCount === 0) {
        ElMessage.success(`成功生成 ${successCount} 个测试代码`)
      } else {
        ElMessage.warning(`生成完成：成功 ${successCount} 个，失败 ${failCount} 个`)
      }
    }
    
    loadCodes()
  } catch (error: any) {
    console.error('生成失败:', error)
    generationStatus.value = 'failed'
  } finally {
    generating.value = false
  }
}

const loadCodes = async () => {
  loading.value = true
  try {
    const res = await getGeneratedCodes({
      page: pagination.value.page,
      page_size: pagination.value.page_size
    })
    if (res.status === 200) {
      codes.value = res.data.items || []
      pagination.value.total = res.data.total || 0
    }
  } catch (error) {
    console.error('加载代码列表失败:', error)
  } finally {
    loading.value = false
  }
}

const viewCode = async (row: any) => {
  try {
    const res = await getGeneratedCodeDetail(row.id)
    if (res.status === 200) {
      currentCode.value = res.data
      editableCode.value = res.data.code || ''
      editableConfig.value = res.data.config_file || ''
      isEditing.value = false
      codeVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载代码失败')
  }
}

const enableEdit = () => {
  isEditing.value = true
  ElMessage.info('已进入编辑模式')
}

const cancelEdit = () => {
  isEditing.value = false
  // 恢复原始内容
  editableCode.value = currentCode.value?.code || ''
  editableConfig.value = currentCode.value?.config_file || ''
  ElMessage.info('已取消编辑')
}

const saveCode = async () => {
  if (!currentCode.value) return
  
  try {
    saving.value = true
    const res = await updateGeneratedCode(currentCode.value.id, {
      code: editableCode.value,
      config_file: editableConfig.value
    })
    
    if (res.status === 200) {
      // 不显示成功消息，因为 request 拦截器已经处理了
      currentCode.value.code = editableCode.value
      currentCode.value.config_file = editableConfig.value
      isEditing.value = false
      loadCodes() // 刷新列表
    }
  } catch (error: any) {
    // 不显示错误消息，因为 request 拦截器已经处理了
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

const executeCode = (row: any) => {
  router.push({
    path: '/playwright-agents/execution',
    query: { code_id: row.id }
  })
}

const downloadCode = (row: any) => {
  const ext = row.language === 'python' ? 'py' : 'ts'
  const blob = new Blob([row.code], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `test_${row.id}.${ext}`
  a.click()
  URL.revokeObjectURL(url)
}

const deleteCode = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个代码吗？', '提示', {
      type: 'warning'
    })
    const res = await deleteGeneratedCode(row.id)
    if (res.status === 200) {
      // 不显示成功消息，因为 request 拦截器已经处理了
      loadCodes()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      // 不显示错误消息，因为 request 拦截器已经处理了
      console.error('删除失败:', error)
    }
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

const getEditorLang = (language: string) => {
  const map: any = {
    typescript: 'typescript',
    javascript: 'javascript',
    python: 'python'
  }
  return map[language] || 'typescript'
}

onMounted(() => {
  initializeGenerationSteps()
  loadTestPlans()
  loadLLMConfigs()
  loadCodes()
  
  // 如果从测试计划页面跳转过来，自动填充plan_id
  if (route.query.plan_id) {
    generateForm.value.plan_id = Number(route.query.plan_id)
  }
})
</script>

<style scoped lang="scss">
.generator-page {
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
  
  // 表格选中行样式 - 加深颜色
  :deep(.el-table) {
    .el-table__row.current-row {
      background-color: #ecf5ff !important;
    }
    
    .el-table__body tr.current-row > td {
      background-color: #ecf5ff !important;
    }
    
    // 选中的checkbox行
    .el-table__row.el-table__row--striped.hover-row {
      background-color: #f5f7fa;
    }
  }
}

// 响应式设计
@media (max-width: 1400px) {
  .generator-page {
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
  .generator-page {
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
