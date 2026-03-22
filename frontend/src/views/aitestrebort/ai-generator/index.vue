<template>
  <div class="aitestrebort-ai-generator">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item @click="$router.push('/aitestrebort/project')">项目管理</el-breadcrumb-item>
          <el-breadcrumb-item @click="$router.push(`/aitestrebort/project/${projectId}/testcase`)">{{ projectName }}</el-breadcrumb-item>
          <el-breadcrumb-item>AI 测试用例生成</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button @click="$router.push(`/aitestrebort/project/${projectId}/testcase`)">
            <el-icon><Document /></el-icon>
            测试用例
          </el-button>
          <el-button @click="$router.push(`/aitestrebort/project/${projectId}/automation`)">
            <el-icon><Setting /></el-icon>
            自动化脚本
          </el-button>
          <el-button @click="testConnection" :loading="testing">
            <el-icon><Link /></el-icon>
            测试连接
          </el-button>
        </el-button-group>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧生成表单 -->
      <el-col :span="12">
        <el-card class="generator-card">
          <template #header>
            <div class="card-header">
              <el-icon><MagicStick /></el-icon>
              <span>AI 测试用例生成</span>
            </div>
          </template>

          <el-form
            ref="formRef"
            :model="generateForm"
            :rules="formRules"
            label-width="100px"
          >
            <!-- 需求来源选择 -->
            <el-form-item label="需求来源" prop="source_type">
              <el-radio-group v-model="generateForm.source_type" @change="onSourceTypeChange">
                <el-radio-button label="manual">手动输入</el-radio-button>
                <el-radio-button label="document">需求文档</el-radio-button>
                <el-radio-button label="requirement">需求条目</el-radio-button>
                <el-radio-button label="module">需求模块</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <!-- 来源选择下拉框 -->
            <el-form-item 
              v-if="generateForm.source_type !== 'manual'" 
              label="选择来源" 
              prop="source_id"
            >
              <el-select
                v-model="generateForm.source_id"
                placeholder="请选择需求来源"
                filterable
                clearable
                style="width: 100%"
                @change="onSourceChange"
                :loading="loadingSources"
              >
                <el-option
                  v-for="source in filteredSources"
                  :key="source.id"
                  :label="source.name"
                  :value="source.id"
                >
                  <div class="source-option">
                    <div class="source-name">{{ source.name }}</div>
                    <div class="source-desc">{{ source.description }}</div>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <!-- 内容预览 -->
            <el-form-item 
              v-if="selectedSourceContent" 
              label="内容预览"
            >
              <el-input
                :model-value="selectedSourceContent"
                type="textarea"
                :rows="3"
                readonly
                placeholder="选择来源后显示内容预览"
              />
            </el-form-item>

            <el-form-item label="需求描述" prop="requirement">
              <el-input
                v-model="generateForm.requirement"
                type="textarea"
                :rows="generateForm.source_type === 'manual' ? 6 : 4"
                :placeholder="getRequirementPlaceholder()"
              />
            </el-form-item>

            <el-form-item label="所属模块" prop="module_id">
              <el-tree-select
                v-model="generateForm.module_id"
                :data="moduleTree"
                :props="treeProps"
                placeholder="请选择所属模块（可选）"
                clearable
              />
            </el-form-item>

            <el-form-item label="生成数量" prop="count">
              <el-input-number
                v-model="generateForm.count"
                :min="1"
                :max="10"
                placeholder="生成用例数量"
              />
            </el-form-item>

            <el-form-item label="上下文信息" prop="context">
              <el-input
                v-model="generateForm.context"
                type="textarea"
                :rows="3"
                placeholder="提供额外的上下文信息，如系统架构、业务规则等（可选）"
              />
            </el-form-item>

            <!-- LLM配置选择 -->
            <el-form-item label="LLM配置">
              <el-select
                v-model="generateForm.llm_config_id"
                placeholder="选择LLM配置（可选，默认使用项目配置）"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="config in llmConfigs"
                  :key="config.id"
                  :label="`${config.name} (${config.provider})`"
                  :value="config.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="generateTestCases" :loading="generating">
                <el-icon><MagicStick /></el-icon>
                生成测试用例
              </el-button>
              <el-button @click="generateSuggestions" :loading="suggesting">
                <el-icon><Star /></el-icon>
                生成建议
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 批量生成 -->
        <el-card class="batch-generator-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <el-icon><Folder /></el-icon>
              <span>批量生成</span>
            </div>
          </template>

          <el-form label-width="100px">
            <el-form-item label="需求列表">
              <el-input
                v-model="batchForm.requirementsText"
                type="textarea"
                :rows="8"
                placeholder="请输入多个需求，每行一个需求，例如：&#10;用户注册功能&#10;用户登录功能&#10;密码重置功能"
              />
            </el-form-item>

            <el-form-item label="所属模块">
              <el-tree-select
                v-model="batchForm.module_id"
                :data="moduleTree"
                :props="treeProps"
                placeholder="请选择所属模块（可选）"
                clearable
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="batchGenerate" :loading="batchGenerating">
                <el-icon><MagicStick /></el-icon>
                批量生成
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧结果展示 -->
      <el-col :span="12">
        <!-- 生成结果 -->
        <el-card v-if="generatedTestCases.length > 0" class="result-card">
          <template #header>
            <div class="card-header">
              <el-icon><Select /></el-icon>
              <span>生成结果 ({{ generatedTestCases.length }})</span>
              <el-button type="primary" size="small" @click="saveAllTestCases" :loading="saving">
                保存全部
              </el-button>
            </div>
          </template>

          <div class="testcase-list">
            <div
              v-for="(testcase, index) in generatedTestCases"
              :key="index"
              class="testcase-item"
            >
              <div class="testcase-header">
                <h4>{{ testcase.name }}</h4>
                <div class="testcase-actions">
                  <el-tag :type="getLevelType(testcase.level)">{{ testcase.level }}</el-tag>
                  <el-button size="small" @click="editGeneratedTestCase(testcase, index)">编辑</el-button>
                  <el-button size="small" type="success" @click="saveTestCase(testcase, index)" :loading="savingIndex === index">保存</el-button>
                </div>
              </div>

              <el-collapse class="testcase-collapse">
                <el-collapse-item title="查看详情" name="1">
                  <div class="testcase-content">
                    <p><strong>前置条件：</strong>{{ testcase.precondition }}</p>
                    
                    <div class="testcase-steps">
                      <h5>测试步骤：</h5>
                      <ol>
                        <li v-for="step in testcase.steps" :key="step.step_number">
                          <div class="step-content">
                            <div><strong>操作：</strong>{{ step.description }}</div>
                            <div><strong>预期结果：</strong>{{ step.expected_result }}</div>
                          </div>
                        </li>
                      </ol>
                    </div>

                    <p v-if="testcase.notes"><strong>备注：</strong>{{ testcase.notes }}</p>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </el-card>

        <!-- 建议结果 -->
        <el-card v-if="suggestions.length > 0" class="suggestion-card">
          <template #header>
            <div class="card-header">
              <el-icon><Star /></el-icon>
              <span>测试建议</span>
            </div>
          </template>

          <div class="suggestion-list">
            <div
              v-for="(suggestion, index) in suggestions"
              :key="index"
              class="suggestion-item"
            >
              <h4>{{ suggestion.name }}</h4>
              <p>{{ suggestion.precondition }}</p>
              <el-button type="primary" size="small" @click="useSuggestion(suggestion)">
                使用此建议
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 覆盖度分析 -->
        <el-card v-if="coverageAnalysis" class="coverage-card">
          <template #header>
            <div class="card-header">
              <el-icon><PieChart /></el-icon>
              <span>覆盖度分析</span>
            </div>
          </template>

          <div class="coverage-content">
            <div class="coverage-stats">
              <el-statistic title="覆盖率" :value="coverageAnalysis.coverage_percentage" suffix="%" />
              <el-statistic title="现有用例数" :value="coverageAnalysis.total_testcases" />
            </div>

            <div class="missing-scenarios" v-if="coverageAnalysis.missing_scenarios.length > 0">
              <h5>缺失场景：</h5>
              <el-tag v-for="scenario in coverageAnalysis.missing_scenarios" :key="scenario" type="warning">
                {{ scenario }}
              </el-tag>
            </div>

            <div class="recommendations" v-if="coverageAnalysis.recommendations.length > 0">
              <h5>改进建议：</h5>
              <ul>
                <li v-for="recommendation in coverageAnalysis.recommendations" :key="recommendation">
                  {{ recommendation }}
                </li>
              </ul>
            </div>
          </div>
        </el-card>

        <!-- 空状态 -->
        <el-card v-if="!generatedTestCases.length && !suggestions.length && !coverageAnalysis" class="empty-card">
          <el-empty description="暂无生成结果">
            <p>请在左侧输入需求描述，然后点击生成按钮</p>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑生成的测试用例对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑生成的测试用例"
      width="800px"
      @closed="resetEditForm"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        label-width="100px"
      >
        <el-form-item label="用例名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="用例等级">
          <el-select v-model="editForm.level">
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
            <el-option label="P3" value="P3" />
          </el-select>
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input v-model="editForm.precondition" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmEdit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Document,
  Setting,
  Link,
  MagicStick,
  Star,
  Folder,
  Select,
  PieChart,
  ArrowLeft
} from '@element-plus/icons-vue'
import { aiGeneratorApi, type AIGenerateRequest, type TestCaseSuggestion, type CoverageAnalysis, type RequirementSource } from '@/api/aitestrebort/ai-generator'
import { testcaseApi, type TestCaseModule, type CreateTestCaseData } from '@/api/aitestrebort/testcase'
import { projectApi } from '@/api/aitestrebort/project'

// 路由
const route = useRoute()
const router = useRouter()

// 计算属性
const projectId = computed(() => Number(route.params.projectId))
const projectName = ref('加载中...')

// 检查projectId是否有效
if (!route.params.projectId || isNaN(Number(route.params.projectId))) {
  ElMessage.warning('请先选择一个项目')
  router.replace('/aitestrebort/project')
}

// 加载项目详情
const loadProjectDetail = async () => {
  try {
    const response = await projectApi.getProject(projectId.value)
    if (response.status === 200) {
      projectName.value = response.data.name
    } else {
      ElMessage.error('加载项目详情失败')
      projectName.value = '未知项目'
    }
  } catch (error) {
    console.error('加载项目详情失败:', error)
    ElMessage.error('加载项目详情失败')
    projectName.value = '未知项目'
  }
}

// 响应式数据
const testing = ref(false)
const generating = ref(false)
const suggesting = ref(false)
const batchGenerating = ref(false)
const saving = ref(false)
const savingIndex = ref(-1)
const showEditDialog = ref(false)
const loadingSources = ref(false)
const moduleTree = ref<TestCaseModule[]>([])
const requirementSources = ref<RequirementSource[]>([])
const llmConfigs = ref<any[]>([])
const generatedTestCases = ref<any[]>([])
const suggestions = ref<TestCaseSuggestion[]>([])
const coverageAnalysis = ref<CoverageAnalysis | null>(null)
const editingIndex = ref(-1)
const selectedSourceContent = ref('')

// 生成表单
const generateForm = reactive<AIGenerateRequest>({
  requirement: '',
  module_id: undefined,
  count: 3,
  context: '',
  source_type: 'manual',
  source_id: undefined,
  llm_config_id: undefined
})

// 批量生成表单
const batchForm = reactive({
  requirementsText: '',
  module_id: undefined
})

// 编辑表单
const editForm = reactive({
  name: '',
  level: 'P2',
  precondition: '',
  notes: ''
})

// 表单验证规则
const formRules = {
  requirement: [
    { required: true, message: '请输入需求描述', trigger: 'blur' },
    { min: 10, message: '需求描述至少10个字符', trigger: 'blur' }
  ],
  count: [
    { required: true, message: '请输入生成数量', trigger: 'blur' }
  ]
}

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

// 表单引用
const formRef = ref()
const editFormRef = ref()

// 计算属性
const filteredSources = computed(() => {
  if (generateForm.source_type === 'manual') return []
  return requirementSources.value.filter(source => source.type === generateForm.source_type)
})

// 方法
const getRequirementPlaceholder = () => {
  const placeholders = {
    manual: '请详细描述测试需求，例如：用户登录功能，包括用户名密码验证、记住密码、忘记密码等场景',
    document: '基于选择的需求文档，请描述具体要测试的功能点',
    requirement: '基于选择的需求条目，请描述具体的测试场景',
    module: '基于选择的需求模块，请描述具体的测试重点'
  }
  return placeholders[generateForm.source_type as keyof typeof placeholders] || placeholders.manual
}
const loadModuleTree = async () => {
  try {
    const response = await testcaseApi.getModuleTree(projectId.value)
    if (response.status === 200) {
      moduleTree.value = response.data || []
    }
  } catch (error) {
    console.error('获取模块树失败:', error)
  }
}

const loadRequirementSources = async () => {
  loadingSources.value = true
  try {
    console.log('开始加载需求来源，项目ID:', projectId.value)
    const response = await aiGeneratorApi.getRequirementSources(projectId.value)
    console.log('需求来源API响应:', response)
    
    if (response.data?.status === 200 || response.status === 200) {
      const sources = response.data?.data?.sources || response.data?.sources || []
      requirementSources.value = sources
      console.log('成功加载需求来源:', sources.length, '个')
      
      // 如果有预设的source_id，尝试预览内容
      if (generateForm.source_id) {
        setTimeout(() => {
          previewContent()
        }, 100)
      }
    } else {
      console.warn('获取需求来源失败:', response.data?.message || response.message)
      ElMessage.warning(response.data?.message || response.message || '获取需求来源失败')
    }
  } catch (error) {
    console.error('获取需求来源失败:', error)
    ElMessage.warning('获取需求来源失败，请检查网络连接')
  } finally {
    loadingSources.value = false
  }
}

const onSourceTypeChange = () => {
  generateForm.source_id = undefined
  selectedSourceContent.value = ''
  if (generateForm.source_type !== 'manual') {
    loadRequirementSources()
  }
}

const onSourceChange = () => {
  selectedSourceContent.value = ''
  if (generateForm.source_id) {
    previewContent()
  }
}

const previewContent = async () => {
  if (!generateForm.source_id) return
  
  try {
    console.log('开始预览内容，source_id:', generateForm.source_id)
    const response = await aiGeneratorApi.getRequirementSourceContent(projectId.value, generateForm.source_id)
    console.log('内容预览API响应:', response)
    
    if (response.data?.status === 200 || response.status === 200) {
      const content = response.data?.data?.content || response.data?.content || ''
      selectedSourceContent.value = content.length > 300 ? content.substring(0, 300) + '...' : content
      console.log('成功获取内容预览，长度:', content.length)
    } else {
      console.warn('获取内容预览失败:', response.data?.message || response.message)
    }
  } catch (error) {
    console.error('获取内容预览失败:', error)
    ElMessage.warning('获取内容预览失败')
  }
}

const loadLLMConfigs = async () => {
  try {
    console.log('开始加载LLM配置，项目ID:', projectId.value)
    const response = await projectApi.getLLMConfigs(projectId.value)
    console.log('LLM配置API响应:', response)
    
    if (response.data?.status === 200 || response.status === 200) {
      const configs = response.data?.data?.items || response.data?.items || response.data?.data || []
      llmConfigs.value = configs
      console.log('成功加载LLM配置:', configs.length, '个')
    } else {
      console.warn('获取LLM配置失败:', response.data?.message || response.message || '未知错误')
    }
  } catch (error) {
    console.error('获取LLM配置失败:', error)
  }
}

const testConnection = async () => {
  testing.value = true
  try {
    const response = await aiGeneratorApi.testConnection()
    if (response.data.status === 200) {
      ElMessage.success('AI 服务连接正常')
    } else {
      ElMessage.error(response.data.message || 'AI 服务连接失败')
    }
  } catch (error) {
    console.error('测试连接失败:', error)
    ElMessage.error('AI 服务连接失败')
  } finally {
    testing.value = false
  }
}

const generateTestCases = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    generating.value = true
    
    console.log('开始生成测试用例，请求参数:', generateForm)
    const response = await aiGeneratorApi.generateTestCases(projectId.value, generateForm)
    console.log('生成测试用例API响应:', response)
    
    // 统一处理响应格式
    if (response.data?.status === 200 || response.status === 200) {
      const testcases = response.data?.data?.testcases || response.data?.testcases || []
      generatedTestCases.value = testcases
      suggestions.value = []
      coverageAnalysis.value = null
      
      console.log('成功生成测试用例:', testcases.length, '个')
      ElMessage.success(`成功生成 ${testcases.length} 个测试用例`)
    } else {
      const errorMsg = response.data?.message || response.message || '生成测试用例失败'
      console.error('生成测试用例失败:', errorMsg)
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('生成测试用例失败:', error)
    ElMessage.error('生成测试用例失败')
  } finally {
    generating.value = false
  }
}

const generateSuggestions = async () => {
  if (!generateForm.requirement) {
    ElMessage.warning('请先输入需求描述')
    return
  }
  
  suggesting.value = true
  try {
    console.log('开始生成建议，需求描述:', generateForm.requirement)
    
    // 创建一个专门用于生成建议的请求
    const suggestionRequest = {
      ...generateForm,
      count: 1, // 建议只生成1个作为示例
      requirement: `请为以下需求提供测试建议和思路：${generateForm.requirement}`
    }
    
    const response = await aiGeneratorApi.generateTestCases(projectId.value, suggestionRequest)
    console.log('生成建议API响应:', response)
    
    if (response.data?.status === 200 || response.status === 200) {
      const testcases = response.data?.data?.testcases || response.data?.testcases || []
      
      // 将生成的测试用例转换为建议格式
      const suggestionList = testcases.map((testcase, index) => ({
        name: `建议 ${index + 1}: ${testcase.name}`,
        precondition: testcase.precondition || '无特殊前置条件',
        level: testcase.level || 'P2',
        steps: testcase.steps || [],
        notes: testcase.notes || '基于需求分析生成的测试建议'
      }))
      
      suggestions.value = suggestionList
      generatedTestCases.value = []
      coverageAnalysis.value = null
      
      console.log('成功生成建议:', suggestionList.length, '个')
      ElMessage.success(`生成了 ${suggestionList.length} 个测试建议`)
    } else {
      const errorMsg = response.data?.message || response.message || '生成建议失败'
      console.error('生成建议失败:', errorMsg)
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('生成建议失败:', error)
    ElMessage.error('生成建议失败')
  } finally {
    suggesting.value = false
  }
}

const batchGenerate = async () => {
  if (!batchForm.requirementsText.trim()) {
    ElMessage.warning('请输入需求列表')
    return
  }
  
  const requirements = batchForm.requirementsText
    .split('\n')
    .map(req => req.trim())
    .filter(req => req.length > 0)
  
  if (requirements.length === 0) {
    ElMessage.warning('请输入有效的需求列表')
    return
  }
  
  batchGenerating.value = true
  try {
    console.log('开始批量生成，需求列表:', requirements)
    const response = await aiGeneratorApi.batchGenerate(projectId.value, {
      requirements: requirements,
      module_id: batchForm.module_id || generateForm.module_id,
      llm_config_id: generateForm.llm_config_id
    })
    console.log('批量生成API响应:', response)
    
    if (response.data?.status === 200 || response.status === 200) {
      const testcases = response.data?.data?.created_testcases || response.data?.created_testcases || []
      generatedTestCases.value = testcases
      suggestions.value = []
      coverageAnalysis.value = null
      
      console.log('批量生成成功:', testcases.length, '个测试用例')
      ElMessage.success(`批量生成了 ${testcases.length} 个测试用例`)
    } else {
      const errorMsg = response.data?.message || response.message || '批量生成失败'
      console.error('批量生成失败:', errorMsg)
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('批量生成失败:', error)
    ElMessage.error('批量生成失败')
  } finally {
    batchGenerating.value = false
  }
}

const useSuggestion = (suggestion: TestCaseSuggestion) => {
  // 将建议转换为测试用例
  const testcase = {
    name: suggestion.name.replace(/^建议 \d+: /, ''), // 移除建议前缀
    level: suggestion.level,
    precondition: suggestion.precondition,
    steps: suggestion.steps,
    notes: suggestion.notes,
    description: suggestion.notes || ''
  }
  
  // 添加到生成的测试用例列表
  generatedTestCases.value = [testcase]
  suggestions.value = []
  
  ElMessage.success('已将建议转换为测试用例，您可以进一步编辑或保存')
}

const editGeneratedTestCase = (testcase: any, index: number) => {
  editingIndex.value = index
  editForm.name = testcase.name
  editForm.level = testcase.level
  editForm.precondition = testcase.precondition
  editForm.notes = testcase.notes
  showEditDialog.value = true
}

const confirmEdit = () => {
  if (editingIndex.value >= 0) {
    const testcase = generatedTestCases.value[editingIndex.value]
    testcase.name = editForm.name
    testcase.level = editForm.level
    testcase.precondition = editForm.precondition
    testcase.notes = editForm.notes
    showEditDialog.value = false
    ElMessage.success('编辑成功')
  }
}

const saveTestCase = async (testcase: any, index: number) => {
  savingIndex.value = index
  try {
    console.log('开始保存测试用例:', testcase)
    
    const testcaseData: CreateTestCaseData = {
      name: testcase.name,
      description: testcase.description || testcase.notes || '',
      precondition: testcase.precondition,
      level: testcase.level,
      notes: testcase.notes,
      module_id: generateForm.module_id
    }
    
    const response = await testcaseApi.createTestCase(projectId.value, testcaseData)
    console.log('创建测试用例API响应:', response)
    
    if (response.data?.status === 200 || response.status === 200) {
      // 保存测试步骤
      const testcaseId = response.data?.data?.id || response.data?.id
      if (testcase.steps && testcase.steps.length > 0) {
        for (const step of testcase.steps) {
          await testcaseApi.createTestCaseStep(projectId.value, testcaseId, {
            step_number: step.step_number,
            description: step.description,
            expected_result: step.expected_result
          })
        }
      }
      
      ElMessage.success('测试用例保存成功')
      generatedTestCases.value.splice(index, 1)
    } else {
      const errorMsg = response.data?.message || response.message || '保存失败'
      console.error('保存测试用例失败:', errorMsg)
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('保存测试用例失败:', error)
    ElMessage.error('保存测试用例失败')
  } finally {
    savingIndex.value = -1
  }
}

const saveAllTestCases = async () => {
  saving.value = true
  try {
    for (let i = generatedTestCases.value.length - 1; i >= 0; i--) {
      await saveTestCase(generatedTestCases.value[i], i)
    }
    ElMessage.success('所有测试用例保存成功')
  } catch (error) {
    ElMessage.error('保存过程中出现错误')
  } finally {
    saving.value = false
  }
}

const resetEditForm = () => {
  editingIndex.value = -1
  editForm.name = ''
  editForm.level = 'P2'
  editForm.precondition = ''
  editForm.notes = ''
}

const getLevelType = (level: string) => {
  const types: Record<string, string> = {
    P0: 'danger',
    P1: 'warning',
    P2: 'primary',
    P3: 'info'
  }
  return types[level] || 'info'
}

// 生命周期
onMounted(() => {
  loadProjectDetail()
  loadModuleTree()
  loadLLMConfigs()
  
  // 检查URL参数，如果有requirementId，则预填充表单
  const requirementId = route.query.requirementId as string
  if (requirementId) {
    generateForm.source_type = 'requirement'
    generateForm.source_id = requirementId
    // 延迟加载需求来源，确保在设置source_id后加载
    setTimeout(() => {
      loadRequirementSources()
    }, 100)
  }
})
</script>

<style scoped>
.aitestrebort-ai-generator {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  display: flex;
  align-items: center;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.generator-card,
.batch-generator-card {
  height: fit-content;
}

.result-card,
.suggestion-card,
.coverage-card,
.empty-card {
  margin-bottom: 20px;
}

.testcase-list {
  max-height: 600px;
  overflow-y: auto;
}

.testcase-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 15px;
  padding: 15px;
}

.testcase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.testcase-header h4 {
  margin: 0;
  color: #303133;
  flex: 1;
}

.testcase-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.testcase-actions .el-button {
  margin: 0;
  padding: 5px 12px;
  font-size: 12px;
}

.testcase-collapse {
  border: none;
  margin-top: 8px;
}

.testcase-collapse :deep(.el-collapse-item__header) {
  background-color: #f5f7fa;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  height: auto;
  line-height: 1.5;
}

.testcase-collapse :deep(.el-collapse-item__wrap) {
  border: none;
  background-color: transparent;
}

.testcase-collapse :deep(.el-collapse-item__content) {
  padding: 12px 0 0 0;
}

.testcase-content p {
  margin: 8px 0;
  color: #606266;
}

.testcase-steps {
  margin: 15px 0;
}

.testcase-steps h5 {
  margin: 0 0 10px 0;
  color: #303133;
}

.testcase-steps ol {
  margin: 0;
  padding-left: 20px;
}

.testcase-steps li {
  margin-bottom: 10px;
}

.step-content {
  background-color: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  margin-top: 5px;
}

.step-content div {
  margin-bottom: 5px;
}

.step-content div:last-child {
  margin-bottom: 0;
}

.suggestion-list {
  max-height: 400px;
  overflow-y: auto;
}

.suggestion-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
}

.suggestion-item h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.suggestion-item p {
  margin: 0 0 10px 0;
  color: #606266;
}

.coverage-content {
  padding: 10px 0;
}

.coverage-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 20px;
}

.missing-scenarios,
.recommendations {
  margin-bottom: 15px;
}

.missing-scenarios h5,
.recommendations h5 {
  margin: 0 0 10px 0;
  color: #303133;
}

.missing-scenarios .el-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.recommendations li {
  margin-bottom: 5px;
  color: #606266;
}

.el-breadcrumb {
  cursor: pointer;
}

.source-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.source-name {
  font-weight: 500;
  color: #303133;
}

.source-desc {
  font-size: 12px;
  color: #909399;
}
</style>