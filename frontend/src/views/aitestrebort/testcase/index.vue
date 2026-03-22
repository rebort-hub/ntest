<template>
  <div class="aitestrebort-testcase">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-divider direction="vertical" />
        <el-breadcrumb separator="/">
          <el-breadcrumb-item @click="$router.push('/aitestrebort/project')">项目管理</el-breadcrumb-item>
          <el-breadcrumb-item>{{ projectName }}</el-breadcrumb-item>
          <el-breadcrumb-item>测试用例</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建用例
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧模块树 -->
      <el-col :span="6">
        <el-card class="module-tree-card">
          <template #header>
            <div class="card-header">
              <span>用例模块</span>
              <el-button type="text" @click="showModuleDialog = true">
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          
          <el-tree
            ref="moduleTreeRef"
            :data="moduleTree"
            :props="treeProps"
            node-key="id"
            :expand-on-click-node="false"
            :highlight-current="true"
            @node-click="handleModuleClick"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <span class="node-label">{{ node.label }}</span>
                <el-dropdown @command="handleModuleAction" trigger="click">
                  <el-button type="text" size="small" @click.stop>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{action: 'add', module: data}">添加子模块</el-dropdown-item>
                      <el-dropdown-item :command="{action: 'edit', module: data}">编辑</el-dropdown-item>
                      <el-dropdown-item :command="{action: 'delete', module: data}" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <!-- 右侧用例列表 -->
      <el-col :span="18">
        <el-card class="testcase-list-card">
          <!-- 搜索和筛选 -->
          <div class="search-bar">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-input
                  v-model="searchForm.search"
                  placeholder="搜索用例名称"
                  clearable
                  @input="handleSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </el-col>
              <el-col :span="4">
                <el-select v-model="searchForm.level" placeholder="用例等级" clearable @change="handleSearch">
                  <el-option label="P0" value="P0" />
                  <el-option label="P1" value="P1" />
                  <el-option label="P2" value="P2" />
                  <el-option label="P3" value="P3" />
                </el-select>
              </el-col>
              <el-col :span="4">
                <el-button @click="loadTestCases">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </el-col>
            </el-row>
          </div>

          <!-- 操作栏 -->
          <div class="table-actions">
            <el-button type="success" @click="showAIGenerateDialog = true">
              <el-icon><MagicStick /></el-icon>
              AI 用例生成(在线模式)
            </el-button>
            <el-button type="success" @click="exportToExcel" :loading="exporting">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
            <el-button type="primary" @click="exportToXMind" :loading="exportingXMind">
              <el-icon><Download /></el-icon>
              导出XMind
            </el-button>
          </div>

          <!-- 用例表格 -->
          <div class="table-container">
            <el-table
              ref="testcaseTableRef"
              :data="testcases"
              v-loading="loading"
              @row-click="handleRowClick"
              style="cursor: pointer;"
              border
              stripe
              height="100%"
            >
            <el-table-column type="index" label="序号" width="80" align="center" />
            
            <el-table-column prop="name" label="用例名称" min-width="250">
              <template #default="{ row }">
                <div class="markdown-content" v-html="renderMarkdown(row.name)"></div>
              </template>
            </el-table-column>
            
            <el-table-column prop="level" label="等级" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getLevelType(row.level)">{{ row.level }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="precondition" label="前置条件" min-width="200">
              <template #default="{ row }">
                <div class="precondition-content">
                  <div 
                    v-for="(step, index) in parseSteps(row.precondition)" 
                    :key="index" 
                    class="precondition-step"
                  >
                    <span class="step-number">{{ index + 1 }}.</span>
                    <div class="markdown-content" v-html="renderMarkdown(step)"></div>
                  </div>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="操作步骤" min-width="300">
              <template #default="{ row }">
                <div class="steps-content" v-if="row.steps && row.steps.length > 0">
                  <div 
                    v-for="step in row.steps" 
                    :key="step.step_number" 
                    class="test-step"
                  >
                    <span class="step-number">{{ step.step_number }}.</span>
                    <div class="markdown-content" v-html="renderMarkdown(step.description)"></div>
                  </div>
                </div>
                <div v-else class="no-steps">暂无操作步骤</div>
              </template>
            </el-table-column>
            
            <el-table-column label="预期结果" min-width="300">
              <template #default="{ row }">
                <div class="expected-content" v-if="row.steps && row.steps.length > 0">
                  <div 
                    v-for="step in row.steps" 
                    :key="step.step_number" 
                    class="expected-step"
                  >
                    <span class="step-number">{{ step.step_number }}.</span>
                    <div class="markdown-content expected-text" v-html="renderMarkdown(step.expected_result)"></div>
                  </div>
                </div>
                <div v-else class="no-expected">暂无预期结果</div>
              </template>
            </el-table-column>
            
            <el-table-column prop="notes" label="备注" min-width="150">
              <template #default="{ row }">
                <div class="markdown-content" v-html="renderMarkdown(row.notes || '')"></div>
              </template>
            </el-table-column>
            
            <el-table-column prop="create_time" label="创建时间" width="150">
              <template #default="{ row }">
                {{ formatDate(row.create_time) }}
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="text" @click.stop="editTestCase(row)">编辑</el-button>
                <el-button type="text" @click.stop="copyTestCase(row)">复制</el-button>
                <el-button type="text" @click.stop="deleteTestCase(row)" style="color: #f56c6c;">删除</el-button>
              </template>
            </el-table-column>
            </el-table>
          </div>

          <!-- 分页 -->
          <div class="pagination" v-if="total > 0">
            <el-pagination
              v-model:current-page="searchForm.page_no"
              v-model:page-size="searchForm.page_size"
              :total="total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadTestCases"
              @current-change="loadTestCases"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建/编辑用例对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTestCase ? '编辑测试用例' : '创建测试用例'"
      width="800px"
      @closed="resetTestCaseForm"
    >
      <el-form
        ref="testcaseFormRef"
        :model="testcaseForm"
        :rules="testcaseFormRules"
        label-width="100px"
      >
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="testcaseForm.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="所属模块" prop="module_id">
          <el-tree-select
            v-model="testcaseForm.module_id"
            :data="moduleTree"
            :props="treeProps"
            placeholder="请选择所属模块"
            clearable
          />
        </el-form-item>
        <el-form-item label="用例等级" prop="level">
          <el-select v-model="testcaseForm.level" placeholder="请选择用例等级">
            <el-option label="P0 - 核心功能" value="P0" />
            <el-option label="P1 - 重要功能" value="P1" />
            <el-option label="P2 - 一般功能" value="P2" />
            <el-option label="P3 - 边缘功能" value="P3" />
          </el-select>
        </el-form-item>
        <el-form-item label="前置条件" prop="precondition">
          <el-input
            v-model="testcaseForm.precondition"
            type="textarea"
            :rows="3"
            placeholder="请输入前置条件"
          />
        </el-form-item>
        <el-form-item label="用例描述" prop="description">
          <el-input
            v-model="testcaseForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入用例描述"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="testcaseForm.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
        
        <!-- 测试步骤 -->
        <el-form-item label="测试步骤">
          <div class="test-steps-editor">
            <div 
              v-for="(step, index) in testcaseForm.steps" 
              :key="index" 
              class="step-item"
            >
              <div class="step-header">
                <span class="step-number">步骤 {{ index + 1 }}</span>
                <el-button 
                  type="danger" 
                  size="small" 
                  text 
                  @click="removeStep(index)"
                  v-if="testcaseForm.steps.length > 1"
                >
                  删除
                </el-button>
              </div>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item :label="`操作步骤 ${index + 1}`" :prop="`steps.${index}.description`">
                    <el-input
                      v-model="step.description"
                      type="textarea"
                      :rows="1"
                      :placeholder="`请输入第${index + 1}步的操作步骤`"
                      class="step-input"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item :label="`预期结果 ${index + 1}`" :prop="`steps.${index}.expected_result`">
                    <el-input
                      v-model="step.expected_result"
                      type="textarea"
                      :rows="1"
                      :placeholder="`请输入第${index + 1}步的预期结果`"
                      class="step-input"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
            
            <el-button 
              type="primary" 
              size="small" 
              @click="addStep"
              style="margin-top: 10px;"
            >
              <el-icon><Plus /></el-icon>
              添加步骤
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleTestCaseSubmit" :loading="submitting">
          {{ editingTestCase ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建/编辑模块对话框 -->
    <el-dialog
      v-model="showModuleDialog"
      :title="editingModule ? '编辑模块' : '创建模块'"
      width="500px"
      @closed="resetModuleForm"
    >
      <el-form
        ref="moduleFormRef"
        :model="moduleForm"
        :rules="moduleFormRules"
        label-width="80px"
      >
        <el-form-item label="模块名称" prop="name">
          <el-input v-model="moduleForm.name" placeholder="请输入模块名称" />
        </el-form-item>
        <el-form-item label="父模块" prop="parent_id">
          <el-tree-select
            v-model="moduleForm.parent_id"
            :data="moduleTree"
            :props="treeProps"
            placeholder="请选择父模块（可选）"
            clearable
          />
        </el-form-item>
        <el-form-item label="模块描述" prop="description">
          <el-input
            v-model="moduleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模块描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showModuleDialog = false">取消</el-button>
        <el-button type="primary" @click="handleModuleSubmit" :loading="submitting">
          {{ editingModule ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- AI 生成测试用例对话框 -->
    <AIGenerateDialog
      v-model="showAIGenerateDialog"
      :project-id="projectId"
      :default-module-id="selectedModuleId"
      @success="handleAIGenerateSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  MoreFilled,
  MagicStick,
  Setting,
  ChatDotRound,
  Document,
  Collection,
  Star,
  ArrowDown,
  Link,
  EditPen,
  Download,
  PieChart,
  Timer,
  ArrowLeft
} from '@element-plus/icons-vue'
import { testcaseApi, type TestCase, type TestCaseModule, type CreateTestCaseData, type CreateModuleData } from '@/api/aitestrebort/testcase'
import { projectApi } from '@/api/aitestrebort/project'
import AIGenerateDialog from '@/components/aitestrebort/AIGenerateDialog.vue'
import * as XLSX from 'xlsx'
import { marked } from 'marked'

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
const loading = ref(false)
const submitting = ref(false)
const exporting = ref(false)
const exportingXMind = ref(false)
const showCreateDialog = ref(false)
const showModuleDialog = ref(false)
const showAIGenerateDialog = ref(false)
const testcases = ref<TestCase[]>([])
const moduleTree = ref<TestCaseModule[]>([])
const total = ref(0)
const editingTestCase = ref<TestCase | null>(null)
const editingModule = ref<TestCaseModule | null>(null)
const selectedModuleId = ref<number | null>(null)
const testcaseTableRef = ref()

// 搜索表单
const searchForm = reactive({
  search: '',
  level: '',
  module_id: undefined as number | undefined,
  page_no: 1,
  page_size: 20
})

// 测试用例表单
const testcaseForm = reactive<CreateTestCaseData>({
  name: '',
  description: '',
  precondition: '',
  level: 'P2',
  notes: '',
  module_id: undefined,
  steps: [
    {
      step_number: 1,
      description: '',
      expected_result: ''
    }
  ]
})

// 模块表单
const moduleForm = reactive<CreateModuleData>({
  name: '',
  description: '',
  parent_id: undefined
})

// 表单验证规则
const testcaseFormRules = {
  name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' },
    { min: 2, max: 100, message: '用例名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  level: [
    { required: true, message: '请选择用例等级', trigger: 'change' }
  ]
}

const moduleFormRules = {
  name: [
    { required: true, message: '请输入模块名称', trigger: 'blur' },
    { min: 2, max: 50, message: '模块名称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

// 表单引用
const testcaseFormRef = ref()
const moduleFormRef = ref()
const moduleTreeRef = ref()

// 方法
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

const loadTestCases = async () => {
  loading.value = true
  try {
    const params = { ...searchForm }
    if (selectedModuleId.value) {
      params.module_id = selectedModuleId.value
    }
    
    const response = await testcaseApi.getTestCases(projectId.value, params)
    if (response.status === 200) {
      const testcaseList = response.data.items || []
      
      // 为每个测试用例加载步骤
      for (const testcase of testcaseList) {
        try {
          const stepsResponse = await testcaseApi.getTestCaseSteps(projectId.value, testcase.id)
          if (stepsResponse.status === 200) {
            testcase.steps = stepsResponse.data || []
          } else {
            testcase.steps = []
          }
        } catch (error) {
          console.warn(`加载测试用例 ${testcase.id} 的步骤失败:`, error)
          testcase.steps = []
        }
      }
      
      testcases.value = testcaseList
      total.value = response.data.total || 0
    } else {
      ElMessage.error(response.message || '获取测试用例失败')
    }
  } catch (error) {
    console.error('获取测试用例失败:', error)
    ElMessage.error('获取测试用例失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchForm.page = 1
  loadTestCases()
}

const handleAdvancedFeature = (command: string) => {
  // 添加来源参数，标识从测试用例页面跳转
  router.push({
    path: `/aitestrebort/project/${projectId.value}/${command}`,
    query: { from: 'testcase' }
  })
}

const handleModuleClick = (module: TestCaseModule) => {
  selectedModuleId.value = module.id
  searchForm.module_id = module.id
  loadTestCases()
}

const handleModuleAction = async (command: { action: string; module: TestCaseModule }) => {
  const { action, module } = command
  
  if (action === 'add') {
    moduleForm.parent_id = module.id
    showModuleDialog.value = true
  } else if (action === 'edit') {
    editingModule.value = module
    moduleForm.name = module.name
    moduleForm.description = module.description || ''
    moduleForm.parent_id = module.parent_id
    showModuleDialog.value = true
  } else if (action === 'delete') {
    try {
      await ElMessageBox.confirm(
        `确定要删除模块 "${module.name}" 吗？`,
        '确认删除',
        { type: 'warning' }
      )
      
      const response = await testcaseApi.deleteModule(projectId.value, module.id)
      if (response.status === 200) {
        loadModuleTree()
      }
      // 400错误已经由响应拦截器处理，不需要再次显示
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除模块失败:', error)
      }
    }
  }
}

const handleRowClick = (row: TestCase) => {
  // 可以跳转到用例详情页面
  console.log('点击用例:', row)
}

const editTestCase = async (testcase: TestCase) => {
  editingTestCase.value = testcase
  testcaseForm.name = testcase.name
  testcaseForm.description = testcase.description || ''
  testcaseForm.precondition = testcase.precondition || ''
  testcaseForm.level = testcase.level
  testcaseForm.notes = testcase.notes || ''
  testcaseForm.module_id = testcase.module_id
  
  // 加载测试步骤
  try {
    const stepsResponse = await testcaseApi.getTestCaseSteps(projectId.value, testcase.id)
    if (stepsResponse.status === 200 && stepsResponse.data.length > 0) {
      testcaseForm.steps = stepsResponse.data
    } else {
      // 如果没有步骤，创建一个默认步骤
      testcaseForm.steps = [
        {
          step_number: 1,
          description: '',
          expected_result: ''
        }
      ]
    }
  } catch (error) {
    console.warn('加载测试步骤失败:', error)
    testcaseForm.steps = [
      {
        step_number: 1,
        description: '',
        expected_result: ''
      }
    ]
  }
  
  showCreateDialog.value = true
}

const copyTestCase = async (testcase: TestCase) => {
  try {
    const response = await testcaseApi.copyTestCase(projectId.value, testcase.id)
    if (response.status === 200) {
      loadTestCases()
    }
    // 400错误已经由响应拦截器处理
  } catch (error) {
    console.error('复制用例失败:', error)
  }
}

const deleteTestCase = async (testcase: TestCase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用例 "${testcase.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    const response = await testcaseApi.deleteTestCase(projectId.value, testcase.id)
    if (response.status === 200) {
      loadTestCases()
    }
    // 400错误已经由响应拦截器处理
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用例失败:', error)
    }
  }
}

const handleTestCaseSubmit = async () => {
  if (!testcaseFormRef.value) return
  
  try {
    await testcaseFormRef.value.validate()
    submitting.value = true
    
    // 准备提交的数据（不包含steps，因为后端API分开处理）
    const submitData = {
      name: testcaseForm.name,
      description: testcaseForm.description,
      precondition: testcaseForm.precondition,
      level: testcaseForm.level,
      notes: testcaseForm.notes,
      module_id: testcaseForm.module_id
    }
    
    let response
    let testcaseId: number
    
    if (editingTestCase.value) {
      // 更新测试用例
      response = await testcaseApi.updateTestCase(projectId.value, editingTestCase.value.id, submitData)
      testcaseId = editingTestCase.value.id
    } else {
      // 创建测试用例
      response = await testcaseApi.createTestCase(projectId.value, submitData)
      testcaseId = response.data.id
    }
    
    if (response.status === 200) {
      // 处理测试步骤
      if (testcaseForm.steps && testcaseForm.steps.length > 0) {
        try {
          // 如果是编辑模式，先删除现有步骤
          if (editingTestCase.value) {
            // 获取现有步骤
            const existingStepsResponse = await testcaseApi.getTestCaseSteps(projectId.value, testcaseId)
            if (existingStepsResponse.status === 200 && existingStepsResponse.data.length > 0) {
              // 删除现有步骤（静默删除，不显示每个删除的成功消息）
              for (const existingStep of existingStepsResponse.data) {
                try {
                  await testcaseApi.deleteTestCaseStep(projectId.value, testcaseId, existingStep.id)
                } catch (deleteError) {
                  console.warn(`删除步骤 ${existingStep.id} 失败:`, deleteError)
                }
              }
            }
          }
          
          // 创建新步骤（现在不会显示重复的成功消息）
          for (const step of testcaseForm.steps) {
            if (step.description.trim() || step.expected_result.trim()) {
              try {
                await testcaseApi.createTestCaseStep(projectId.value, testcaseId, {
                  step_number: step.step_number,
                  description: step.description,
                  expected_result: step.expected_result
                })
              } catch (createError) {
                console.warn(`创建步骤 ${step.step_number} 失败:`, createError)
              }
            }
          }
        } catch (stepError) {
          console.error('保存测试步骤失败:', stepError)
          ElMessage.warning('测试用例保存成功，但部分步骤保存失败')
        }
      }
      
      showCreateDialog.value = false
      loadTestCases()
    }
    // 400错误已经由响应拦截器处理
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleModuleSubmit = async () => {
  if (!moduleFormRef.value) return
  
  try {
    await moduleFormRef.value.validate()
    submitting.value = true
    
    let response
    if (editingModule.value) {
      response = await testcaseApi.updateModule(projectId.value, editingModule.value.id, moduleForm)
    } else {
      response = await testcaseApi.createModule(projectId.value, moduleForm)
    }
    
    if (response.status === 200) {
      showModuleDialog.value = false
      loadModuleTree()
    }
    // 400错误已经由响应拦截器处理
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

// 步骤管理方法
const addStep = () => {
  const newStepNumber = testcaseForm.steps!.length + 1
  testcaseForm.steps!.push({
    step_number: newStepNumber,
    description: '',
    expected_result: ''
  })
}

const removeStep = (index: number) => {
  if (testcaseForm.steps!.length > 1) {
    testcaseForm.steps!.splice(index, 1)
    // 重新编号
    testcaseForm.steps!.forEach((step, idx) => {
      step.step_number = idx + 1
    })
  }
}

const resetTestCaseForm = () => {
  editingTestCase.value = null
  testcaseForm.name = ''
  testcaseForm.description = ''
  testcaseForm.precondition = ''
  testcaseForm.level = 'P2'
  testcaseForm.notes = ''
  testcaseForm.module_id = undefined
  testcaseForm.steps = [
    {
      step_number: 1,
      description: '',
      expected_result: ''
    }
  ]
  if (testcaseFormRef.value) {
    testcaseFormRef.value.resetFields()
  }
}

const resetModuleForm = () => {
  editingModule.value = null
  moduleForm.name = ''
  moduleForm.description = ''
  moduleForm.parent_id = undefined
  if (moduleFormRef.value) {
    moduleFormRef.value.resetFields()
  }
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

// 解析步骤文本（支持多行步骤）
const parseSteps = (text: string): string[] => {
  if (!text) return []
  
  // 按换行符分割，过滤空行
  const lines = text.split('\n').filter(line => line.trim())
  
  // 如果只有一行，直接返回
  if (lines.length <= 1) {
    return [text.trim()]
  }
  
  // 检查是否有编号格式（1. 2. 3.）
  const numberedSteps = lines.filter(line => /^\d+\.\s/.test(line.trim()))
  if (numberedSteps.length > 0) {
    return numberedSteps.map(step => step.replace(/^\d+\.\s*/, '').trim())
  }
  
  // 检查是否有项目符号格式（- * +）
  const bulletSteps = lines.filter(line => /^[-*+]\s/.test(line.trim()))
  if (bulletSteps.length > 0) {
    return bulletSteps.map(step => step.replace(/^[-*+]\s*/, '').trim())
  }
  
  // 否则按行分割
  return lines.map(line => line.trim())
}

// Excel导出功能
const exportToExcel = async () => {
  if (testcases.value.length === 0) {
    ElMessage.warning('没有数据可以导出')
    return
  }
  
  exporting.value = true
  
  try {
    // 准备导出数据
    const exportData = testcases.value.map((testcase, index) => {
      // 处理操作步骤
      const steps = testcase.steps || []
      const stepsText = steps.map(step => `${step.step_number}. ${step.description}`).join('\n')
      const expectedText = steps.map(step => `${step.step_number}. ${step.expected_result}`).join('\n')
      
      // 处理前置条件
      const preconditionSteps = parseSteps(testcase.precondition || '')
      const preconditionText = preconditionSteps.map((step, idx) => `${idx + 1}. ${step}`).join('\n')
      
      return {
        '序号': index + 1,
        '用例名称': cleanMarkdown(testcase.name),
        '等级': testcase.level,
        '前置条件': preconditionText,
        '操作步骤': stepsText,
        '预期结果': expectedText,
        '备注': cleanMarkdown(testcase.notes || ''),
        '创建时间': formatDate(testcase.create_time)
      }
    })
    
    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(exportData)
    
    // 设置列宽
    const colWidths = [
      { wch: 8 },   // 序号
      { wch: 30 },  // 用例名称
      { wch: 8 },   // 等级
      { wch: 25 },  // 前置条件
      { wch: 35 },  // 操作步骤
      { wch: 35 },  // 预期结果
      { wch: 20 },  // 备注
      { wch: 15 }   // 创建时间
    ]
    ws['!cols'] = colWidths
    
    // 设置行高（自动换行）
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1')
    for (let row = range.s.r; row <= range.e.r; row++) {
      for (let col = range.s.c; col <= range.e.c; col++) {
        const cellAddress = XLSX.utils.encode_cell({ r: row, c: col })
        if (ws[cellAddress]) {
          ws[cellAddress].s = {
            alignment: {
              wrapText: true,
              vertical: 'top'
            }
          }
        }
      }
    }
    
    // 添加工作表
    XLSX.utils.book_append_sheet(wb, ws, '测试用例')
    
    // 生成文件名
    const fileName = `测试用例_${projectName.value}_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.xlsx`
    
    // 导出文件
    XLSX.writeFile(wb, fileName)
    
    ElMessage.success('Excel文件导出成功')
  } catch (error) {
    console.error('导出Excel失败:', error)
    ElMessage.error('导出Excel失败')
  } finally {
    exporting.value = false
  }
}

// XMind导出功能
const exportToXMind = async () => {
  if (testcases.value.length === 0) {
    ElMessage.warning('没有数据可以导出')
    return
  }
  
  exportingXMind.value = true
  
  try {
    // 调用后端API导出XMind，直接获取文件流
    const response = await fetch(`/api/aitestrebort/projects/${projectId.value}/testcases/export/xmind`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      }
    })
    
    if (!response.ok) {
      throw new Error('导出失败')
    }
    
    // 获取文件流并创建Blob
    const blob = await response.blob()
    
    // 从响应头获取文件名，如果没有则使用默认名称
    const contentDisposition = response.headers.get('content-disposition')
    let filename = `${projectName.value}_testcases.xmind`
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
      }
    }
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    ElMessage.success('XMind文件导出成功')
  } catch (error) {
    console.error('导出XMind失败:', error)
    ElMessage.error('导出XMind失败')
  } finally {
    exportingXMind.value = false
  }
}

// 清理Markdown标记的辅助函数
const cleanMarkdown = (text: string): string => {
  if (!text) return ''
  
  return text
    // 清理Markdown格式符号
    .replace(/\*\*(.*?)\*\*/g, '$1')  // 移除粗体标记 **text**
    .replace(/\*(.*?)\*/g, '$1')      // 移除斜体标记 *text*
    .replace(/`(.*?)`/g, '$1')        // 移除代码标记 `text`
    .replace(/#{1,6}\s*/g, '')        // 移除标题标记 # ## ###
    .replace(/\[(.*?)\]\(.*?\)/g, '$1') // 移除链接格式 [text](url)
    .replace(/!\[.*?\]\(.*?\)/g, '')  // 移除图片
    .replace(/^\s*[-*+]\s+/gm, '')    // 移除列表标记
    .replace(/^\s*\d+\.\s+/gm, '')    // 移除数字列表标记
    .replace(/\n+/g, '\n')            // 合并多个换行
    .trim()
}

const handleAIGenerateSuccess = async (testcases: any[]) => {
  try {
    // 保存生成的测试用例到数据库
    for (const testcase of testcases) {
      const testcaseData: CreateTestCaseData = {
        name: testcase.name,
        description: testcase.description || '',
        precondition: testcase.precondition,
        level: testcase.level,
        notes: testcase.notes,
        module_id: testcase.module_id || selectedModuleId.value
      }
      
      const response = await testcaseApi.createTestCase(projectId.value, testcaseData)
      if (response.data.status === 200) {
        // 保存测试步骤
        const testcaseId = response.data.data.id
        for (const step of testcase.steps || []) {
          await testcaseApi.createTestCaseStep(projectId.value, testcaseId, {
            step_number: step.step_number,
            description: step.description,
            expected_result: step.expected_result
          })
        }
      }
    }
    
    ElMessage.success(`成功保存 ${testcases.length} 个AI生成的测试用例`)
    loadTestCases() // 刷新用例列表
  } catch (error) {
    console.error('保存AI生成的测试用例失败:', error)
    ElMessage.error('保存AI生成的测试用例失败')
  }
}

// 生命周期
onMounted(() => {
  loadProjectDetail()
  loadModuleTree()
  loadTestCases()
})
</script>

<style scoped>
.aitestrebort-testcase {
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
  gap: 12px;
}

.back-button {
  font-size: 14px;
  color: #606266;
  padding: 8px 12px;
}

.back-button:hover {
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.back-button .el-icon {
  margin-right: 4px;
}

.module-tree-card {
  height: calc(100vh - 200px);
  overflow-y: auto;
}

.testcase-list-card {
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.testcase-list-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 20px;
}

.table-container {
  flex: 1;
  overflow: hidden;
  margin-bottom: 16px;
}

.table-container .el-table {
  height: 100%;
}

.table-container :deep(.el-table__body-wrapper) {
  overflow-x: auto;
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 8px;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.search-bar {
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.el-breadcrumb {
  cursor: pointer;
}

/* 测试步骤编辑器样式 */
.test-steps-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 16px;
  background-color: #fafafa;
  max-height: 300px; /* 限制最大高度 */
  overflow-y: auto; /* 添加垂直滚动条 */
}

.step-item {
  margin-bottom: 16px;
  padding: 12px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.step-item:last-child {
  margin-bottom: 0;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #ebeef5;
}

.step-number {
  font-weight: 600;
  color: #409eff;
  font-size: 14px;
}

/* 优化滚动条样式 */
.test-steps-editor::-webkit-scrollbar {
  width: 6px;
}

.test-steps-editor::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 3px;
}

.test-steps-editor::-webkit-scrollbar-track {
  background-color: #f1f1f1;
  border-radius: 3px;
}

/* 步骤输入框样式 */
.step-input :deep(.el-textarea__inner) {
  padding: 8px;
  min-height: 20px;
  line-height: 1.4;
}

.table-actions {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}

/* Markdown内容样式 */
.markdown-content {
  line-height: 1.6;
  word-wrap: break-word;
}

.markdown-content :deep(p) {
  margin: 0;
  line-height: 1.5;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #303133;
}

.markdown-content :deep(em) {
  font-style: italic;
  color: #606266;
}

.markdown-content :deep(code) {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  color: #e6a23c;
}

.markdown-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 4px 0;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #dcdfe6;
  padding-left: 8px;
  margin: 4px 0;
  color: #606266;
}

.markdown-content :deep(ul), .markdown-content :deep(ol) {
  margin: 4px 0;
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 2px 0;
}

/* 前置条件样式 */
.precondition-content {
  max-height: 200px;
  overflow-y: auto;
}

.precondition-step {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  line-height: 1.5;
}

.precondition-step .step-number {
  color: #909399;
  font-weight: 600;
  margin-right: 8px;
  flex-shrink: 0;
  min-width: 20px;
}

.precondition-step .markdown-content {
  flex: 1;
  color: #606266;
}

/* 测试步骤样式 */
.steps-content, .expected-content {
  max-height: 250px;
  overflow-y: auto;
}

.test-step, .expected-step {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
  line-height: 1.5;
}

.test-step .step-number, .expected-step .step-number {
  color: #409eff;
  font-weight: 600;
  margin-right: 8px;
  flex-shrink: 0;
  min-width: 20px;
}

.test-step .markdown-content {
  flex: 1;
  color: #606266;
}

.expected-step .markdown-content.expected-text {
  flex: 1;
  color: #67c23a;
}

.no-steps, .no-expected {
  color: #c0c4cc;
  font-style: italic;
  text-align: center;
  padding: 20px 0;
}

/* 表格样式优化 */
.el-table :deep(.el-table__header-wrapper) th {
  background-color: #f8f9fa;
  color: #303133;
  font-weight: 600;
  font-size: 14px;
}

.el-table :deep(.el-table__row) {
  cursor: default;
}

.el-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

.el-table :deep(.el-table__cell) {
  padding: 12px 8px;
  vertical-align: top;
}

/* 滚动条样式 */
.precondition-content::-webkit-scrollbar,
.steps-content::-webkit-scrollbar,
.expected-content::-webkit-scrollbar {
  width: 6px;
}

.precondition-content::-webkit-scrollbar-thumb,
.steps-content::-webkit-scrollbar-thumb,
.expected-content::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 3px;
}

.precondition-content::-webkit-scrollbar-track,
.steps-content::-webkit-scrollbar-track,
.expected-content::-webkit-scrollbar-track {
  background-color: #f1f1f1;
  border-radius: 3px;
}
</style>