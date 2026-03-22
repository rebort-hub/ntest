<template>
  <div class="aitestrebort-automation">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item @click="$router.push('/aitestrebort/project')">项目管理</el-breadcrumb-item>
          <el-breadcrumb-item @click="$router.push(`/aitestrebort/project/${projectId}/testcase`)">{{ projectName }}</el-breadcrumb-item>
          <el-breadcrumb-item>Playwright 脚本</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button @click="$router.push(`/aitestrebort/project/${projectId}/testcase`)">
            <el-icon><Document /></el-icon>
            测试用例
          </el-button>
          <!-- 暂时屏蔽创建脚本按钮，因为编辑器初始化问题 -->
          <!-- <el-button @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建脚本
          </el-button> -->
          <el-button type="primary" @click="showGenerateDialog = true">
            <el-icon><MagicStick /></el-icon>
            生成脚本
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.search"
            placeholder="搜索脚本名称"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.module_id" placeholder="选择模块" clearable @change="handleSearch">
            <el-option 
              v-for="module in modules" 
              :key="module.id" 
              :label="module.name" 
              :value="module.id" 
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.status" placeholder="脚本状态" clearable @change="handleSearch">
            <el-option label="草稿" value="draft" />
            <el-option label="激活" value="active" />
            <el-option label="已废弃" value="deprecated" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button @click="loadScripts">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 脚本列表 -->
    <el-table :data="scripts" v-loading="loading">
      <el-table-column label="脚本名称" min-width="300">
        <template #default="{ row }">
          <div class="script-name" :title="row.name">
            <div class="markdown-content" v-html="renderMarkdown(row.name)"></div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="关联用例" width="200">
        <template #default="{ row }">
          <el-tag size="small" type="info" v-if="row.test_case_name">
            <div class="markdown-content" v-html="renderMarkdown(row.test_case_name)"></div>
          </el-tag>
          <el-tag size="small" type="info" v-else>未关联</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="module_name" label="所属模块" width="120">
        <template #default="{ row }">
          <el-tag size="small">{{ row.module_name || '未分类' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="script_type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getTypeColor(row.script_type)">{{ getTypeLabel(row.script_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="来源" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="getSourceColor(row.source)">{{ getSourceLabel(row.source) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusColor(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="150">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="text" @click="viewScript(row)">查看</el-button>
          <el-button 
            type="text" 
            @click="executeScript(row)"
            :disabled="row.status !== 'active'"
          >
            执行
          </el-button>
          <el-button type="text" @click="deleteScript(row)" style="color: #f56c6c;">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:current-page="searchForm.page"
        v-model:page-size="searchForm.page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadScripts"
        @current-change="loadScripts"
      />
    </div>

    <!-- 生成脚本对话框 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="生成 Playwright 脚本"
      width="700px"
      @closed="resetGenerateForm"
    >
      <el-form
        ref="generateFormRef"
        :model="generateForm"
        :rules="generateRules"
        label-width="120px"
      >
        <el-form-item label="生成方式" prop="generate_type">
          <el-radio-group v-model="generateForm.generate_type">
            <el-radio label="single">单个用例</el-radio>
            <el-radio label="module">整个模块</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item 
          v-if="generateForm.generate_type === 'module'" 
          label="选择模块" 
          prop="module_id"
        >
          <el-select v-model="generateForm.module_id" placeholder="请选择模块" style="width: 100%">
            <el-option 
              v-for="module in modules" 
              :key="module.id" 
              :label="module.name" 
              :value="module.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item 
          v-if="generateForm.generate_type === 'single'" 
          label="选择用例" 
          prop="testcase_id"
        >
          <el-select 
            v-model="generateForm.testcase_id" 
            placeholder="请选择测试用例" 
            style="width: 100%"
            filterable
          >
            <el-option 
              v-for="testcase in testcases" 
              :key="testcase.id" 
              :label="stripMarkdown(testcase.name)"
              :value="testcase.id" 
            >
              <div v-html="renderMarkdown(testcase.name)"></div>
            </el-option>
          </el-select>
          <div class="selected-testcase-preview" v-if="selectedTestcaseName">
            <span class="preview-label">已选择：</span>
            <span class="preview-content" v-html="renderMarkdown(selectedTestcaseName)"></span>
          </div>
        </el-form-item>

        <el-form-item label="脚本语言" prop="language">
          <el-select v-model="generateForm.language" placeholder="请选择语言">
            <el-option label="Python" value="python" />
            <el-option label="JavaScript" value="javascript" />
          </el-select>
        </el-form-item>

        <el-form-item label="LLM配置">
          <el-select v-model="generateForm.llm_config_id" placeholder="使用默认配置（推荐）" clearable>
            <el-option 
              v-for="config in llmConfigs" 
              :key="config.id" 
              :label="config.name" 
              :value="config.id" 
            />
          </el-select>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            选择LLM配置用于AI智能生成，留空使用默认配置
          </div>
        </el-form-item>

        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          使用AI智能分析测试用例并生成高质量的Playwright自动化脚本
        </div>
      </el-form>
      
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleGenerate" :loading="generating">
          生成脚本
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建/编辑脚本对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingScript ? '编辑脚本' : '创建脚本'"
      width="80%"
      @closed="resetForm"
      @opened="handleCreateDialogOpened"
    >
      <el-form
        ref="formRef"
        :model="scriptForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="脚本名称" prop="name">
              <el-input v-model="scriptForm.name" placeholder="请输入脚本名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="脚本类型" prop="script_type">
              <el-select v-model="scriptForm.script_type" placeholder="请选择脚本类型">
                <el-option label="UI自动化" value="ui" />
                <el-option label="接口自动化" value="api" />
                <el-option label="单元测试" value="unit" />
                <el-option label="性能测试" value="performance" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="测试框架" prop="framework">
              <el-select v-model="scriptForm.framework" placeholder="请选择测试框架">
                <el-option label="Selenium" value="selenium" />
                <el-option label="Playwright" value="playwright" />
                <el-option label="Requests" value="requests" />
                <el-option label="Pytest" value="pytest" />
                <el-option label="Unittest" value="unittest" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="编程语言" prop="language">
              <el-select v-model="scriptForm.language" placeholder="请选择编程语言">
                <el-option label="Python" value="python" />
                <el-option label="JavaScript" value="javascript" />
                <el-option label="Java" value="java" />
                <el-option label="C#" value="csharp" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="脚本描述" prop="description">
          <el-input
            v-model="scriptForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入脚本描述"
          />
        </el-form-item>

        <el-form-item label="脚本内容" prop="script_content">
          <div class="code-editor-container">
            <pythonEditor 
              ref="createScriptEditorRef"
              :python-code="scriptForm.script_content"
            />
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button @click="validateScript" :loading="validating">验证语法</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingScript ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 脚本详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="脚本详情"
      width="90%"
      :close-on-click-modal="false"
    >
      <div v-if="currentScript">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="脚本名称">{{ currentScript.name }}</el-descriptions-item>
          <el-descriptions-item label="脚本类型">
            <el-tag :type="getTypeColor(currentScript.script_type)">
              {{ getTypeLabel(currentScript.script_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="测试框架">{{ currentScript.framework }}</el-descriptions-item>
          <el-descriptions-item label="编程语言">{{ currentScript.language }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusColor(currentScript.status)">
              {{ getStatusLabel(currentScript.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentScript.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="script-description" v-if="currentScript.description">
          <h4>脚本描述</h4>
          <p>{{ currentScript.description }}</p>
        </div>

        <div class="script-content">
          <div class="content-header">
            <h4>脚本内容</h4>
            <div class="content-actions">
              <el-button 
                v-if="!isEditing" 
                type="primary" 
                size="small" 
                @click="startEditing"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button-group v-else>
                <el-button 
                  type="success" 
                  size="small" 
                  @click="saveScript"
                  :loading="saving"
                >
                  <el-icon><Check /></el-icon>
                  保存
                </el-button>
                <el-button 
                  size="small" 
                  @click="cancelEditing"
                >
                  <el-icon><Close /></el-icon>
                  取消
                </el-button>
              </el-button-group>
            </div>
          </div>
          
          <div class="code-editor-container">
            <VAceEditor
              v-model:value="editableScriptContent"
              :lang="getEditorLanguage(currentScript.language)"
              theme="monokai"
              :options="{
                fontSize: 14,
                showPrintMargin: false,
                wrap: true,
                readOnly: !isEditing
              }"
              style="height: 500px; width: 100%;"
            />
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 执行脚本对话框 -->
    <el-dialog
      v-model="showExecuteDialog"
      title="执行脚本"
      width="600px"
    >
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="执行环境">
          <el-input v-model="executeForm.environment" placeholder="请输入执行环境（可选）" />
        </el-form-item>
        <el-form-item label="执行参数">
          <el-input
            v-model="executeForm.parametersText"
            type="textarea"
            :rows="4"
            placeholder="请输入执行参数（JSON格式，可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showExecuteDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmExecute" :loading="executing">
          执行
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VAceEditor } from 'vue3-ace-editor'
import {
  Plus,
  Search,
  Refresh,
  Document,
  MagicStick,
  ArrowLeft,
  InfoFilled,
  Edit,
  Check,
  Close
} from '@element-plus/icons-vue'
import { automationApi, type AutomationScript, type CreateScriptData, type ExecuteScriptData } from '@/api/aitestrebort/automation'
import { projectApi } from '@/api/aitestrebort/project'
import { testcaseApi } from '@/api/aitestrebort/testcase'
import pythonEditor from '@/components/editor/python-editor.vue'
import { marked } from 'marked'

// 路由
const route = useRoute()
const router = useRouter()

// 计算属性
const projectId = computed(() => Number(route.params.projectId))
const projectName = ref('加载中...')

// 计算选中的测试用例名称
const selectedTestcaseName = computed(() => {
  if (!generateForm.testcase_id) return ''
  const selectedTestcase = testcases.value.find(tc => tc.id === generateForm.testcase_id)
  return selectedTestcase ? selectedTestcase.name : ''
})

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
const loading = ref(false)
const submitting = ref(false)
const validating = ref(false)
const executing = ref(false)
const generating = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showExecuteDialog = ref(false)
const showGenerateDialog = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const editableScriptContent = ref('')
const scripts = ref<AutomationScript[]>([])
const modules = ref<any[]>([])
const testcases = ref<any[]>([])
const llmConfigs = ref<any[]>([])
const total = ref(0)
const editingScript = ref<AutomationScript | null>(null)
const currentScript = ref<AutomationScript | null>(null)

// 搜索表单
const searchForm = reactive({
  search: '',
  module_id: '',
  status: '',
  page: 1,
  page_size: 20
})

// 生成表单
const generateForm = reactive({
  generate_type: 'single',
  module_id: '',
  testcase_id: '',
  language: 'python',
  llm_config_id: '' // 可选，为空时使用全局配置
})

// 脚本表单
const scriptForm = reactive<CreateScriptData>({
  name: '',
  description: '',
  script_type: 'ui',
  script_content: '',
  framework: 'selenium',
  language: 'python'
})

// 执行表单
const executeForm = reactive({
  environment: '',
  parametersText: ''
})

// 生成表单验证规则
const generateRules = computed(() => {
  const rules: any = {
    generate_type: [
      { required: true, message: '请选择生成方式', trigger: 'change' }
    ],
    language: [
      { required: true, message: '请选择脚本语言', trigger: 'change' }
    ]
  }
  
  if (generateForm.generate_type === 'module') {
    rules.module_id = [
      { required: true, message: '请选择模块', trigger: 'change' }
    ]
  } else {
    rules.testcase_id = [
      { required: true, message: '请选择测试用例', trigger: 'change' }
    ]
  }
  
  return rules
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入脚本名称', trigger: 'blur' },
    { min: 2, max: 100, message: '脚本名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  script_type: [
    { required: true, message: '请选择脚本类型', trigger: 'change' }
  ],
  framework: [
    { required: true, message: '请选择测试框架', trigger: 'change' }
  ],
  language: [
    { required: true, message: '请选择编程语言', trigger: 'change' }
  ],
  script_content: [
    { required: true, message: '请输入脚本内容', trigger: 'blur' }
  ]
}

// 表单引用
const formRef = ref()
const generateFormRef = ref()
const createScriptEditorRef = ref()

// 方法
const loadModules = async () => {
  try {
    const response = await testcaseApi.getModules(projectId.value)
    if (response.status === 200) {
      modules.value = response.data.items || response.data || []
      console.log('模块列表加载成功:', modules.value)
    }
  } catch (error) {
    console.error('加载模块失败:', error)
    ElMessage.error('加载模块失败')
  }
}

const loadTestCases = async () => {
  try {
    const response = await testcaseApi.getTestCases(projectId.value)
    console.log('测试用例API响应:', response)
    if (response.status === 200) {
      testcases.value = response.data.items || response.data || []
      console.log('测试用例列表加载成功:', testcases.value)
      console.log('第一个测试用例:', testcases.value[0])
    }
  } catch (error) {
    console.error('加载测试用例失败:', error)
    ElMessage.error('加载测试用例失败')
  }
}

const loadLLMConfigs = async () => {
  try {
    const response = await projectApi.getLLMConfigs(projectId.value)
    if (response.status === 200) {
      llmConfigs.value = response.data.items || response.data || []
      console.log('LLM配置列表加载成功:', llmConfigs.value)
    }
  } catch (error) {
    console.error('加载LLM配置失败:', error)
    ElMessage.error('加载LLM配置失败')
  }
}

const handleGenerate = async () => {
  if (!generateFormRef.value) return
  
  try {
    await generateFormRef.value.validate()
    generating.value = true
    
    if (generateForm.generate_type === 'module') {
      // 批量生成模块下所有测试用例的脚本
      await generateScriptsFromModule()
    } else {
      // 生成单个测试用例的脚本
      await generateScriptFromTestCase()
    }
    
  } catch (error) {
    console.error('生成脚本失败:', error)
    ElMessage.error('生成脚本失败')
  } finally {
    generating.value = false
  }
}

const generateScriptFromTestCase = async () => {
  try {
    // 使用新的脚本生成API
    const response = await automationApi.generateScriptFromTestCase(
      projectId.value, 
      generateForm.testcase_id,
      {
        language: generateForm.language,
        llm_config_id: generateForm.llm_config_id || undefined
      }
    )
    
    if (response.status === 200) {
      // 后端已经有成功提示，前端不再重复显示
      showGenerateDialog.value = false
      resetGenerateForm()
      loadScripts()
    } else {
      throw new Error(response.message || '脚本生成失败')
    }
  } catch (error) {
    console.error('AI生成单个脚本失败:', error)
    throw error
  }
}

const generateScriptsFromModule = async () => {
  try {
    // 使用新的批量脚本生成API
    const response = await automationApi.generateScriptsFromModule(
      projectId.value, 
      generateForm.module_id,
      {
        language: generateForm.language,
        llm_config_id: generateForm.llm_config_id || undefined
      }
    )
    
    if (response.status === 200) {
      const { success_count, fail_count } = response.data
      if (success_count > 0) {
        // 后端已经有成功提示，前端不再重复显示
        showGenerateDialog.value = false
        resetGenerateForm()
        loadScripts()
      } else {
        throw new Error('所有脚本生成失败')
      }
    } else {
      throw new Error(response.message || '批量脚本生成失败')
    }
  } catch (error) {
    console.error('AI批量生成脚本失败:', error)
    throw error
  }
}

const resetGenerateForm = () => {
  generateForm.generate_type = 'single'
  generateForm.module_id = ''
  generateForm.testcase_id = ''
  generateForm.language = 'python'
  generateForm.llm_config_id = ''
  if (generateFormRef.value) {
    generateFormRef.value.resetFields()
  }
}

const loadScripts = async () => {
  loading.value = true
  try {
    const response = await automationApi.getScripts(projectId.value, searchForm)
    console.log('获取脚本列表响应:', response)
    
    // 检查不同的响应格式
    let responseData
    if (response.data && response.data.status === 200) {
      // 标准格式: {status: 200, message: "获取成功", data: {items: [], total: 0}}
      responseData = response.data.data || {}
    } else if (response.data && response.data.items) {
      // 直接格式: {items: [], total: 0, page: 1, page_size: 20}
      responseData = response.data
    } else {
      // 其他格式，尝试直接使用response.data
      responseData = response.data || {}
    }
    
    scripts.value = responseData.items || []
    total.value = responseData.total || 0
    console.log('脚本列表加载成功:', scripts.value.length, '个脚本')
    
    // 如果有数据或者total为0（空列表），都认为是成功的
    if (scripts.value.length > 0 || responseData.total === 0) {
      // 成功加载，不显示错误消息
    } else {
      console.error('获取脚本列表失败: 数据格式异常', response.data)
      ElMessage.error('获取脚本列表失败: 数据格式异常')
    }
  } catch (error) {
    console.error('获取脚本列表失败:', error)
    ElMessage.error('获取脚本列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchForm.page = 1
  loadScripts()
}

const viewScript = (script: AutomationScript) => {
  currentScript.value = script
  editableScriptContent.value = script.script_content
  isEditing.value = false
  showDetailDialog.value = true
}

const startEditing = () => {
  isEditing.value = true
}

const cancelEditing = () => {
  if (currentScript.value) {
    editableScriptContent.value = currentScript.value.script_content
  }
  isEditing.value = false
}

const saveScript = async () => {
  if (!currentScript.value) return
  
  try {
    saving.value = true
    
    const response = await automationApi.updateScript(projectId.value, currentScript.value.id, {
      script_content: editableScriptContent.value
    })
    
    if (response.status === 200) {
      // 后端已经有成功提示，前端不再重复显示
      currentScript.value.script_content = editableScriptContent.value
      isEditing.value = false
      // 刷新脚本列表
      loadScripts()
    } else {
      throw new Error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存脚本失败:', error)
    ElMessage.error('保存脚本失败')
  } finally {
    saving.value = false
  }
}

const getEditorLanguage = (language: string) => {
  switch (language?.toLowerCase()) {
    case 'python':
      return 'python'
    case 'javascript':
    case 'js':
    case 'typescript':
    case 'ts':
      return 'javascript'
    default:
      return 'python'
  }
}

const editScript = (script: AutomationScript) => {
  editingScript.value = script
  scriptForm.name = script.name
  scriptForm.description = script.description || ''
  scriptForm.script_type = script.script_type
  scriptForm.script_content = script.script_content
  scriptForm.framework = script.framework
  scriptForm.language = script.language
  showCreateDialog.value = true
}

const executeScript = (script: AutomationScript) => {
  currentScript.value = script
  executeForm.environment = ''
  executeForm.parametersText = ''
  showExecuteDialog.value = true
}

const deleteScript = async (script: AutomationScript) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除脚本 "${script.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    const response = await automationApi.deleteScript(projectId.value, script.id)
    if (response && response.status === 200) {
      // 框架已经处理了成功提示，这里只处理业务逻辑
      loadScripts()
    } else {
      ElMessage.error(response?.message || '删除脚本失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除脚本失败:', error)
      ElMessage.error('删除脚本失败')
    }
  }
}

const validateScript = async () => {
  if (!currentScript.value && !editingScript.value) return
  
  validating.value = true
  try {
    const scriptId = editingScript.value?.id || currentScript.value?.id
    if (scriptId) {
      const response = await automationApi.validateScript(projectId.value, scriptId)
      if (response.data.status === 200) {
        const result = response.data.data
        if (result.is_valid) {
          ElMessage.success('脚本语法验证通过')
        } else {
          ElMessage.warning(`脚本语法有问题: ${result.errors.join(', ')}`)
        }
      }
    }
  } catch (error) {
    console.error('验证脚本失败:', error)
    ElMessage.error('验证脚本失败')
  } finally {
    validating.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 从pythonEditor中获取代码内容
    if (createScriptEditorRef.value) {
      scriptForm.script_content = createScriptEditorRef.value.tempData
    }
    
    let response
    if (editingScript.value) {
      response = await automationApi.updateScript(projectId.value, editingScript.value.id, scriptForm)
    } else {
      response = await automationApi.createScript(projectId.value, scriptForm)
    }
    
    console.log('脚本操作响应:', response)
    console.log('response.data:', response.data)
    console.log('response.status:', response.status)
    console.log('response.status === 200:', response.status === 200)
    // 检查业务状态码，后端返回格式：{status: 200, message: "新增成功", data: {...}}
    if (response && response.status === 200) {
      // 框架已经处理了成功提示，这里只处理业务逻辑
      showCreateDialog.value = false
      resetForm()
      loadScripts()
    } else {
      console.error('脚本操作失败:', response)
      ElMessage.error(response?.message || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const confirmExecute = async () => {
  if (!currentScript.value) return
  
  executing.value = true
  try {
    const executeData: ExecuteScriptData = {
      environment: executeForm.environment || undefined
    }
    
    if (executeForm.parametersText) {
      try {
        executeData.parameters = JSON.parse(executeForm.parametersText)
      } catch (error) {
        ElMessage.error('执行参数格式错误，请输入有效的JSON')
        return
      }
    }
    
    const response = await automationApi.executeScript(projectId.value, currentScript.value.id, executeData)
    if (response && response.status === 200) {
      // 框架已经处理了成功提示，这里只处理业务逻辑
      showExecuteDialog.value = false
    } else {
      ElMessage.error(response?.message || '执行脚本失败')
    }
  } catch (error) {
    console.error('执行脚本失败:', error)
    ElMessage.error('执行脚本失败')
  } finally {
    executing.value = false
  }
}

const resetForm = () => {
  editingScript.value = null
  scriptForm.name = ''
  scriptForm.description = ''
  scriptForm.script_type = 'ui'
  scriptForm.script_content = ''
  scriptForm.framework = 'selenium'
  scriptForm.language = 'python'
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleCreateDialogOpened = () => {
  // 对话框打开后，延迟一下确保DOM完全渲染，然后刷新Ace Editor
  setTimeout(() => {
    // 触发窗口resize事件，让Ace Editor重新计算尺寸
    window.dispatchEvent(new Event('resize'))
  }, 100)
}

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    playwright_python: 'Playwright Python',
    playwright_javascript: 'Playwright JavaScript'
  }
  return labels[type] || type
}

const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    playwright_python: 'primary',
    playwright_javascript: 'success'
  }
  return colors[type] || 'info'
}

const getSourceLabel = (source: string) => {
  const labels: Record<string, string> = {
    ai_generated: 'AI生成',
    manual: '手动编写',
    recorded: '录制生成'
  }
  return labels[source] || source
}

const getSourceColor = (source: string) => {
  const colors: Record<string, string> = {
    ai_generated: 'success',
    manual: 'primary',
    recorded: 'warning'
  }
  return colors[source] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: '草稿',
    active: '激活',
    deprecated: '已废弃'
  }
  return labels[status] || status
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    draft: 'info',
    active: 'success',
    deprecated: 'danger'
  }
  return colors[status] || 'info'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// Markdown渲染方法
const renderMarkdown = (text: string): string => {
  if (!text) return ''
  
  // 配置marked选项
  marked.setOptions({
    breaks: true, // 支持换行
    gfm: true,    // 支持GitHub风格的Markdown
    sanitize: false // 允许HTML标签
  })
  
  try {
    return marked(text)
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return text
  }
}

// 去除Markdown格式的方法
const stripMarkdown = (text: string): string => {
  if (!text) return ''
  
  // 简单的去除常见Markdown格式
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1') // 去除粗体 **text**
    .replace(/\*(.*?)\*/g, '$1')     // 去除斜体 *text*
    .replace(/`(.*?)`/g, '$1')       // 去除代码 `text`
    .replace(/#{1,6}\s*(.*)/g, '$1') // 去除标题 # text
    .replace(/\[(.*?)\]\(.*?\)/g, '$1') // 去除链接 [text](url)
    .replace(/!\[(.*?)\]\(.*?\)/g, '$1') // 去除图片 ![alt](url)
    .trim()
}

// 生命周期
onMounted(() => {
  loadProjectDetail()
  loadModules()
  loadTestCases()
  loadLLMConfigs()
  loadScripts()
})
</script>

<style scoped>
.aitestrebort-automation {
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

.search-bar {
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.code-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.form-tip {
  display: flex;
  align-items: center;
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  margin-right: 4px;
}

.script-description {
  margin: 20px 0;
}

.script-description h4 {
  margin-bottom: 10px;
  color: #303133;
}

.script-content {
  margin: 20px 0;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.content-header h4 {
  margin: 0;
  color: #303133;
}

.content-actions {
  display: flex;
  gap: 8px;
}

.code-editor-container {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.code-editor-container .ace_editor {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace !important;
}

.code-editor-container .ace_content {
  background-color: #272822 !important;
}

.script-content h4 {
  margin-bottom: 10px;
  color: #303133;
}

.code-block {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.el-breadcrumb {
  cursor: pointer;
}

.script-name {
  max-width: 100%;
  overflow: hidden;
}

.markdown-content {
  display: inline;
  word-break: break-word;
}

.markdown-content p {
  margin: 0;
  display: inline;
}

.markdown-content * {
  display: inline;
  margin: 0;
  padding: 0;
}

.el-tag .markdown-content {
  color: inherit;
}

/* 修复下拉选项中markdown内容的显示问题 */
.el-select-dropdown .el-select-dropdown__item {
  height: auto !important;
  min-height: 34px !important;
  line-height: 1.4 !important;
  padding: 8px 20px !important;
  white-space: normal !important;
}

.el-select-dropdown .el-select-dropdown__item .markdown-content {
  display: block;
  line-height: 1.4;
  word-break: break-word;
}

.el-select-dropdown .el-select-dropdown__item .markdown-content p {
  margin: 0;
  line-height: 1.4;
}

.el-select-dropdown .el-select-dropdown__item .markdown-content * {
  line-height: 1.4;
}

/* 选中用例预览样式 */
.selected-testcase-preview {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border: 1px solid #e1f5fe;
  border-radius: 4px;
  font-size: 13px;
}

.selected-testcase-preview .preview-label {
  color: #666;
  margin-right: 8px;
}

.selected-testcase-preview .preview-content {
  color: #20a162;
}

.selected-testcase-preview .preview-content p {
  margin: 0;
  display: inline;
}

.selected-testcase-preview .preview-content * {
  display: inline;
  margin: 0;
  padding: 0;
}
</style>