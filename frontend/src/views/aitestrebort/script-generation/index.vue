<template>
  <div class="script-generation">
    <el-card class="page-header">
      <div class="header-content">
        <el-button @click="goBack" style="margin-right: 16px;">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div>
          <h2>智能脚本生成</h2>
          <p>基于录制步骤自动生成Playwright测试脚本和测试用例模板</p>
        </div>
      </div>
    </el-card>

    <el-tabs v-model="activeTab" type="card">
      <!-- Playwright脚本生成 -->
      <el-tab-pane label="Playwright脚本生成" name="playwright">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>脚本配置</span>
              </template>

              <el-form :model="playwrightForm" label-width="120px">
                <el-form-item label="测试用例名称" required>
                  <el-input v-model="playwrightForm.test_case_name" placeholder="输入测试用例名称" />
                </el-form-item>

                <el-form-item label="目标URL">
                  <el-input v-model="playwrightForm.target_url" placeholder="https://example.com" />
                </el-form-item>

                <el-form-item label="测试描述">
                  <el-input
                    v-model="playwrightForm.description"
                    type="textarea"
                    :rows="3"
                    placeholder="描述这个测试的目的和预期行为"
                  />
                </el-form-item>

                <el-form-item label="高级设置">
                  <el-row :gutter="16">
                    <el-col :span="8">
                      <div style="display: flex; align-items: center; height: 32px;">
                        <span style="margin-right: 8px; font-size: 13px; color: #606266;">超时时间:</span>
                        <el-input-number
                          v-model="playwrightForm.timeout_seconds"
                          :min="5"
                          :max="300"
                          style="width: 100px;"
                        />
                        <span style="margin-left: 4px; font-size: 13px; color: #909399;">秒</span>
                      </div>
                    </el-col>
                    <el-col :span="8">
                      <div style="display: flex; align-items: center; height: 32px; padding-left: 16px;">
                        <el-switch
                          v-model="playwrightForm.headless"
                          active-text="无头模式"
                        />
                      </div>
                    </el-col>
                    <el-col :span="8">
                      <div style="display: flex; align-items: center; height: 32px; padding-left: 16px;">
                        <el-switch
                          v-model="playwrightForm.use_pytest"
                          active-text="使用pytest"
                        />
                      </div>
                    </el-col>
                  </el-row>
                </el-form-item>

                <el-form-item>
                  <el-button 
                    type="primary" 
                    @click="generatePlaywrightScript"
                    :loading="playwrightLoading"
                    style="width: 100%"
                  >
                    生成Playwright脚本
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>

            <!-- 录制步骤 -->
            <el-card style="margin-top: 20px">
              <template #header>
                <div class="card-header">
                  <span>录制步骤 ({{ recordedSteps.length }})</span>
                  <div>
                    <el-button size="small" @click="addStep">添加步骤</el-button>
                    <el-button size="small" @click="importSteps">导入步骤</el-button>
                  </div>
                </div>
              </template>

              <div class="recorded-steps">
                <div
                  v-for="(step, index) in recordedSteps"
                  :key="index"
                  class="step-item"
                >
                  <div class="step-header">
                    <span class="step-number">{{ index + 1 }}</span>
                    <span class="step-tool">{{ step.tool_name }}</span>
                    <el-button 
                      size="small" 
                      type="danger" 
                      @click="removeStep(index)"
                    >
                      删除
                    </el-button>
                  </div>
                  <div class="step-content">
                    <div class="step-input">
                      <strong>输入:</strong>
                      <pre>{{ JSON.stringify(step.tool_input, null, 2) }}</pre>
                    </div>
                    <div v-if="step.description" class="step-description">
                      <strong>描述:</strong> {{ step.description }}
                    </div>
                  </div>
                </div>

                <div v-if="recordedSteps.length === 0" class="no-steps">
                  <el-empty description="暂无录制步骤，请添加或导入步骤" />
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card class="script-result-card">
              <template #header>
                <div class="card-header">
                  <span>生成的脚本</span>
                  <div v-if="playwrightResult">
                    <el-button size="small" @click="copyScript">复制脚本</el-button>
                    <el-button size="small" @click="downloadScript">下载脚本</el-button>
                  </div>
                </div>
              </template>

              <div v-if="playwrightResult" class="script-content">
                <div class="script-info">
                  <el-tag type="success">{{ playwrightResult.test_case_name }}</el-tag>
                  <el-tag type="info">{{ playwrightResult.step_count }} 步骤</el-tag>
                  <el-tag v-if="playwrightResult.use_pytest" type="warning">pytest</el-tag>
                </div>
                
                <div class="script-code">
                  <pre><code>{{ playwrightResult.script }}</code></pre>
                </div>
              </div>

              <div v-else class="no-script">
                <el-empty description="暂无生成的脚本" />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 测试用例模板生成 -->
      <el-tab-pane label="测试用例模板生成" name="template">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>需求输入</span>
              </template>

              <el-form :model="templateForm" label-width="120px">
                <el-form-item label="需求描述" required>
                  <el-input
                    v-model="templateForm.requirement"
                    type="textarea"
                    :rows="6"
                    placeholder="请详细描述功能需求，包括用户场景、预期行为等..."
                  />
                </el-form-item>

                <el-form-item label="知识库">
                  <el-select 
                    v-model="templateForm.knowledge_base_id" 
                    placeholder="选择知识库（可选）"
                    style="width: 100%"
                    clearable
                  >
                    <el-option
                      v-for="kb in knowledgeBases"
                      :key="kb.id"
                      :label="kb.name"
                      :value="kb.id"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item>
                  <el-button 
                    type="primary" 
                    @click="generateTestCaseTemplate"
                    :loading="templateLoading"
                    style="width: 100%"
                  >
                    生成测试用例模板
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>

            <!-- 相似测试用例 -->
            <el-card style="margin-top: 20px">
              <template #header>
                <div class="card-header">
                  <span>相似测试用例参考</span>
                  <el-button size="small" @click="searchSimilarCases">搜索</el-button>
                </div>
              </template>

              <div class="similar-cases">
                <div
                  v-for="(case_item, index) in similarCases"
                  :key="index"
                  class="case-item"
                >
                  <div class="case-header">
                    <span class="case-name">{{ case_item.name }}</span>
                    <el-tag size="small">{{ case_item.priority }}</el-tag>
                  </div>
                  <div class="case-description">{{ case_item.description }}</div>
                </div>

                <div v-if="similarCases.length === 0" class="no-cases">
                  <el-empty description="暂无相似测试用例" />
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card class="template-result-card">
              <template #header>
                <div class="card-header">
                  <span>生成的测试用例模板</span>
                  <div v-if="templateResult">
                    <el-button size="small" @click="copyTemplate">复制模板</el-button>
                    <el-button size="small" @click="saveTemplate">保存模板</el-button>
                  </div>
                </div>
              </template>

              <div v-if="templateResult" class="template-content">
                <div class="template-info">
                  <el-descriptions :column="2" border>
                    <el-descriptions-item label="名称">{{ templateResult.name }}</el-descriptions-item>
                    <el-descriptions-item label="优先级">
                      <el-tag :type="getPriorityType(templateResult.priority)">
                        {{ templateResult.priority }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="类型">{{ templateResult.type }}</el-descriptions-item>
                    <el-descriptions-item label="预估时间">{{ templateResult.estimated_time }}</el-descriptions-item>
                  </el-descriptions>
                </div>

                <div class="template-description">
                  <h4>描述</h4>
                  <p>{{ templateResult.description }}</p>
                </div>

                <div class="template-preconditions">
                  <h4>前置条件</h4>
                  <ul>
                    <li v-for="(condition, index) in templateResult.preconditions" :key="index">
                      {{ condition }}
                    </li>
                  </ul>
                </div>

                <div class="template-steps">
                  <h4>测试步骤</h4>
                  <el-table :data="templateResult.test_steps" style="width: 100%">
                    <el-table-column prop="step_number" label="步骤" width="60" />
                    <el-table-column prop="action" label="操作" />
                    <el-table-column prop="expected_result" label="预期结果" />
                  </el-table>
                </div>

                <div class="template-tags">
                  <h4>标签</h4>
                  <el-tag
                    v-for="tag in templateResult.tags"
                    :key="tag"
                    style="margin-right: 8px"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>

              <div v-else class="no-template">
                <el-empty description="暂无生成的测试用例模板" />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加步骤对话框 -->
    <el-dialog v-model="stepDialogVisible" title="添加录制步骤" width="600px">
      <el-form :model="newStep" label-width="100px">
        <el-form-item label="工具名称" required>
          <el-select v-model="newStep.tool_name" placeholder="选择工具" style="width: 100%">
            <el-option label="导航到页面" value="browser_navigate" />
            <el-option label="点击元素" value="browser_click" />
            <el-option label="填写表单" value="browser_fill" />
            <el-option label="输入文本" value="browser_type" />
            <el-option label="选择选项" value="browser_select" />
            <el-option label="悬停元素" value="browser_hover" />
            <el-option label="等待时间" value="browser_wait" />
            <el-option label="按键操作" value="browser_press" />
            <el-option label="截图保存" value="browser_screenshot" />
          </el-select>
        </el-form-item>

        <el-form-item label="工具输入" required>
          <el-input
            v-model="stepInputText"
            type="textarea"
            :rows="4"
            placeholder="JSON格式的工具输入参数"
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="newStep.description" placeholder="步骤描述（可选）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="stepDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddStep">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { advancedFeaturesApi } from '@/api/aitestrebort/advanced-features'
import type { 
  ScriptGenerationRequest,
  ScriptGenerationResponse,
  TestCaseGenerationRequest,
  TestCaseTemplate
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
const activeTab = ref('playwright')
const playwrightLoading = ref(false)
const templateLoading = ref(false)
const stepDialogVisible = ref(false)

const playwrightForm = reactive<ScriptGenerationRequest>({
  recorded_steps: [],
  test_case_name: '',
  target_url: '',
  timeout_seconds: 30,
  headless: true,
  use_pytest: true,
  description: ''
})

const templateForm = reactive<TestCaseGenerationRequest>({
  requirement: '',
  knowledge_base_id: undefined,
  similar_cases: []
})

const recordedSteps = ref<Array<{
  tool_name: string
  tool_input: Record<string, any>
  description?: string
}>>([])

const newStep = reactive({
  tool_name: '',
  tool_input: {},
  description: ''
})

const stepInputText = ref('')

const playwrightResult = ref<ScriptGenerationResponse | null>(null)
const templateResult = ref<TestCaseTemplate | null>(null)

const knowledgeBases = ref<Array<{
  id: string
  name: string
  description: string
}>>([])

const similarCases = ref<Array<{
  name: string
  description: string
  priority: string
}>>([])

// 方法
const loadKnowledgeBases = async () => {
  try {
    console.log('开始加载知识库列表，项目ID:', projectId)
    const response = await advancedFeaturesApi.langGraph.getProjectKnowledgeBases(projectId)
    console.log('知识库API完整响应:', response)
    
    // 更安全的响应处理
    if (response && (response.status === 200 || response.status === 'success')) {
      let data = null
      if (response.data) {
        if (response.data.status === 'success' && response.data.data) {
          data = response.data.data
        } else if (Array.isArray(response.data)) {
          data = response.data
        } else {
          data = response.data
        }
      } else {
        data = response
      }
      
      knowledgeBases.value = Array.isArray(data) ? data : []
      console.log('成功加载知识库:', knowledgeBases.value.length, '个')
    } else {
      console.warn('获取知识库失败:', response?.data?.message || response?.message)
    }
  } catch (error) {
    console.error('加载知识库失败:', error)
  }
}

const generatePlaywrightScript = async () => {
  if (!playwrightForm.test_case_name.trim()) {
    ElMessage.warning('请输入测试用例名称')
    return
  }

  if (recordedSteps.value.length === 0) {
    ElMessage.warning('请添加至少一个录制步骤')
    return
  }

  playwrightLoading.value = true
  try {
    const requestData = {
      ...playwrightForm,
      recorded_steps: recordedSteps.value
    }

    console.log('发送脚本生成请求:', requestData)
    console.log('请求URL:', `/api/aitestrebort/advanced/projects/${projectId}/generate-playwright-script`)
    
    const response = await advancedFeaturesApi.scriptGeneration.generatePlaywrightScript(
      projectId, 
      requestData
    )
    
    console.log('脚本生成API完整响应:', response)
    console.log('响应类型:', typeof response)
    console.log('响应是否为null:', response === null)
    console.log('响应是否为undefined:', response === undefined)
    
    // 如果响应是undefined或null，说明请求可能被拦截器处理了
    if (response === undefined || response === null) {
      console.error('API响应为空，可能是网络错误或服务器错误')
      ElMessage.error('脚本生成失败：服务器无响应，请检查网络连接和服务器状态')
      return
    }
    
    // 更安全的响应处理
    if (response && (response.status === 200 || response.status === 'success')) {
      // 尝试多种可能的数据结构
      let data = null
      if (response.data) {
        if (response.data.status === 'success' && response.data.data) {
          data = response.data.data
        } else if (response.data.script) {
          data = response.data
        } else {
          data = response.data
        }
      } else {
        data = response
      }
      
      console.log('解析后的数据:', data)
      
      if (data && data.script) {
        playwrightResult.value = data
        ElMessage.success('Playwright脚本生成成功')
      } else {
        console.error('响应数据格式异常:', data)
        ElMessage.error('脚本生成失败：响应数据格式异常')
      }
    } else {
      const errorMsg = response?.data?.message || response?.message || '脚本生成失败'
      console.error('脚本生成失败:', errorMsg)
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('脚本生成失败 - 完整错误信息:', error)
    console.error('错误类型:', error.constructor.name)
    console.error('错误消息:', error.message)
    console.error('错误堆栈:', error.stack)
    
    if (error.response) {
      console.error('HTTP响应错误:', error.response.status, error.response.data)
      ElMessage.error(`脚本生成失败：HTTP ${error.response.status} - ${error.response.data?.message || '服务器错误'}`)
    } else if (error.request) {
      console.error('网络请求错误:', error.request)
      ElMessage.error('脚本生成失败：网络请求失败，请检查网络连接')
    } else {
      ElMessage.error(`脚本生成失败：${error.message || '未知错误'}`)
    }
  } finally {
    playwrightLoading.value = false
  }
}

const generateTestCaseTemplate = async () => {
  if (!templateForm.requirement.trim()) {
    ElMessage.warning('请输入需求描述')
    return
  }

  templateLoading.value = true
  try {
    const requestData = {
      ...templateForm,
      similar_cases: similarCases.value
    }

    console.log('发送模板生成请求:', requestData)
    const response = await advancedFeaturesApi.scriptGeneration.generateTestCaseTemplate(
      projectId,
      requestData
    )
    
    console.log('模板生成API完整响应:', response)
    
    // 更安全的响应处理
    if (response && (response.status === 200 || response.status === 'success')) {
      // 尝试多种可能的数据结构
      let data = null
      if (response.data) {
        if (response.data.status === 'success' && response.data.data) {
          data = response.data.data
        } else if (response.data.name) {
          data = response.data
        } else {
          data = response.data
        }
      } else {
        data = response
      }
      
      if (data && data.name) {
        templateResult.value = data
        ElMessage.success('测试用例模板生成成功')
      } else {
        console.error('响应数据格式异常:', data)
        ElMessage.error('模板生成失败：响应数据格式异常')
      }
    } else {
      const errorMsg = response?.data?.message || response?.message || '模板生成失败'
      console.error('模板生成失败:', errorMsg)
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('模板生成失败:', error)
    ElMessage.error(`模板生成失败：${error.message || '请重试'}`)
  } finally {
    templateLoading.value = false
  }
}

const addStep = () => {
  newStep.tool_name = ''
  newStep.description = ''
  stepInputText.value = ''
  stepDialogVisible.value = true
}

const confirmAddStep = () => {
  if (!newStep.tool_name) {
    ElMessage.warning('请选择工具名称')
    return
  }

  try {
    const toolInput = stepInputText.value.trim() ? JSON.parse(stepInputText.value) : {}
    
    recordedSteps.value.push({
      tool_name: newStep.tool_name,
      tool_input: toolInput,
      description: newStep.description || undefined
    })

    stepDialogVisible.value = false
    ElMessage.success('步骤添加成功')
  } catch (error) {
    ElMessage.error('工具输入格式错误，请输入有效的JSON')
  }
}

const removeStep = (index: number) => {
  recordedSteps.value.splice(index, 1)
  ElMessage.success('步骤已删除')
}

const importSteps = () => {
  // 模拟导入步骤 - 使用后端支持的工具名格式
  const sampleSteps = [
    {
      tool_name: 'browser_navigate',
      tool_input: { url: 'https://example.com' },
      description: '打开网站首页'
    },
    {
      tool_name: 'browser_click',
      tool_input: { selector: '#login-button' },
      description: '点击登录按钮'
    },
    {
      tool_name: 'browser_fill',
      tool_input: { selector: '#username', value: 'testuser' },
      description: '输入用户名'
    },
    {
      tool_name: 'browser_fill',
      tool_input: { selector: '#password', value: 'testpass' },
      description: '输入密码'
    },
    {
      tool_name: 'browser_click',
      tool_input: { selector: '#submit-button' },
      description: '点击提交按钮'
    }
  ]
  
  recordedSteps.value = sampleSteps
  ElMessage.success('示例步骤导入成功')
}

const searchSimilarCases = () => {
  // 模拟搜索相似测试用例
  similarCases.value = [
    {
      name: '用户登录功能测试',
      description: '验证用户使用正确的用户名和密码登录系统',
      priority: 'High'
    },
    {
      name: '用户注册功能测试',
      description: '验证新用户注册流程的完整性',
      priority: 'Medium'
    }
  ]
  ElMessage.success('找到相似测试用例')
}

const copyScript = () => {
  if (playwrightResult.value) {
    navigator.clipboard.writeText(playwrightResult.value.script)
    ElMessage.success('脚本已复制到剪贴板')
  }
}

const downloadScript = () => {
  if (playwrightResult.value) {
    const blob = new Blob([playwrightResult.value.script], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${playwrightResult.value.test_case_name}.py`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('脚本下载成功')
  }
}

const copyTemplate = () => {
  if (templateResult.value) {
    const templateText = JSON.stringify(templateResult.value, null, 2)
    navigator.clipboard.writeText(templateText)
    ElMessage.success('模板已复制到剪贴板')
  }
}

const saveTemplate = () => {
  if (templateResult.value) {
    ElMessage.success('模板保存成功')
  }
}

const getPriorityType = (priority: string) => {
  switch (priority.toLowerCase()) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'success'
    default: return 'info'
  }
}

// 生命周期
onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped>
.script-generation {
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

.script-result-card,
.template-result-card {
  height: 600px;
  overflow: hidden;
}

.recorded-steps {
  max-height: 400px;
  overflow-y: auto;
}

.step-item {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin-bottom: 10px;
  padding: 10px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.step-number {
  background-color: #409EFF;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.step-tool {
  font-weight: bold;
  color: #67C23A;
}

.step-content {
  font-size: 12px;
}

.step-input {
  margin-bottom: 8px;
}

.step-input pre {
  background-color: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  margin: 5px 0;
  max-height: 100px;
  overflow-y: auto;
}

.step-description {
  color: #606266;
}

.no-steps,
.no-script,
.no-template,
.no-cases {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.script-content,
.template-content {
  height: 520px;
  overflow-y: auto;
  padding: 10px;
}

.script-info {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
}

.script-code {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
}

.script-code pre {
  margin: 0;
  font-size: 12px;
  line-height: 1.4;
}

.template-info {
  margin-bottom: 20px;
}

.template-description,
.template-preconditions,
.template-steps,
.template-tags {
  margin-bottom: 20px;
}

.template-description h4,
.template-preconditions h4,
.template-steps h4,
.template-tags h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.template-preconditions ul {
  margin: 0;
  padding-left: 20px;
}

.similar-cases {
  max-height: 300px;
  overflow-y: auto;
}

.case-item {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.case-name {
  font-weight: bold;
}

.case-description {
  color: #606266;
  font-size: 12px;
}
</style>