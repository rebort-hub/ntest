<template>
  <div class="test-suite-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">测试套件管理</h1>
        <p class="page-description">创建和管理测试套件，支持批量执行测试用例和自动化脚本</p>
      </div>
      <div class="header-right">
        <el-button @click="showCreateDialog = true" type="primary">
          <el-icon><Plus /></el-icon>
          创建套件
        </el-button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-container">
      <!-- 搜索和筛选 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索套件名称..."
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.status"
          placeholder="状态筛选"
          style="width: 120px; margin-left: 12px"
          clearable
          @change="handleSearch"
        >
          <el-option label="启用" value="active" />
          <el-option label="禁用" value="inactive" />
        </el-select>
      </div>

      <!-- 套件列表 -->
      <el-table :data="testSuites" v-loading="loading" @row-click="viewSuite">
        <el-table-column prop="name" label="套件名称" min-width="200">
          <template #default="{ row }">
            <el-link @click="viewSuite(row)" :underline="false">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="test_case_count" label="用例数量" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.test_case_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="script_count" label="脚本数量" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="success" size="small">{{ row.script_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_execution" label="最后执行" width="150" align="center">
          <template #default="{ row }">
            {{ row.last_execution ? formatDate(row.last_execution) : '未执行' }}
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="创建者" width="100" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="150" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="text" @click.stop="viewSuite(row)">查看</el-button>
            <el-button type="text" @click.stop="editSuite(row)">编辑</el-button>
            <el-button type="text" @click.stop="executeSuite(row)" :disabled="row.status !== 'active'">执行</el-button>
            <el-button type="text" @click.stop="viewExecutionHistory(row)">历史</el-button>
            <el-button type="text" @click.stop="deleteSuite(row)" style="color: #f56c6c;">删除</el-button>
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
          @size-change="loadTestSuites"
          @current-change="loadTestSuites"
        />
      </div>
    </div>

    <!-- 创建/编辑套件对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingSuite ? '编辑测试套件' : '创建测试套件'"
      width="800px"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="suiteForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="套件名称" prop="name">
          <el-input v-model="suiteForm.name" placeholder="请输入套件名称" />
        </el-form-item>
        
        <el-form-item label="套件描述" prop="description">
          <el-input
            v-model="suiteForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入套件描述"
          />
        </el-form-item>
        
        <el-form-item label="执行配置">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="并发数" prop="parallel_count">
                <el-input-number
                  v-model="suiteForm.parallel_count"
                  :min="1"
                  :max="10"
                  placeholder="并发执行数量"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="超时时间" prop="timeout">
                <el-input-number
                  v-model="suiteForm.timeout"
                  :min="60"
                  :max="3600"
                  placeholder="超时时间(秒)"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="suiteForm.status"
            active-value="active"
            inactive-value="inactive"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingSuite ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 套件详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="测试套件详情"
      width="1000px"
    >
      <div v-if="selectedSuite" class="suite-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="套件名称">{{ selectedSuite.name }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="selectedSuite.status === 'active' ? 'success' : 'danger'" size="small">
                {{ selectedSuite.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="并发数">{{ selectedSuite.parallel_count }}</el-descriptions-item>
            <el-descriptions-item label="超时时间">{{ selectedSuite.timeout }}秒</el-descriptions-item>
            <el-descriptions-item label="创建者">{{ selectedSuite.creator_name }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(selectedSuite.created_at) }}</el-descriptions-item>
          </el-descriptions>
          <div class="description-content">
            <strong>描述：</strong>{{ selectedSuite.description }}
          </div>
        </div>

        <!-- 测试用例 -->
        <div class="detail-section">
          <div class="section-header">
            <h4>测试用例 ({{ testCases.length }})</h4>
            <el-button @click="showSelectTestCasesDialog = true">
              <el-icon><Plus /></el-icon>
              添加用例
            </el-button>
          </div>
          <el-table :data="testCases" size="small">
            <el-table-column prop="name" label="用例名称" min-width="200" />
            <el-table-column prop="level" label="优先级" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getLevelColor(row.level)" size="small">{{ row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="module_name" label="所属模块" width="150" />
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button type="text" @click="removeTestCase(row)" style="color: #f56c6c;">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 自动化脚本 -->
        <div class="detail-section">
          <div class="section-header">
            <h4>自动化脚本 ({{ scripts.length }})</h4>
            <el-button @click="showSelectScriptsDialog = true">
              <el-icon><Plus /></el-icon>
              添加脚本
            </el-button>
          </div>
          <el-table :data="scripts" size="small">
            <el-table-column prop="name" label="脚本名称" min-width="200" />
            <el-table-column prop="script_type" label="脚本类型" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small">{{ row.script_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
                  {{ row.status === 'active' ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button type="text" @click="removeScript(row)" style="color: #f56c6c;">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 执行按钮 -->
        <div class="execution-actions">
          <el-button type="primary" @click="executeSuite(selectedSuite)" :disabled="selectedSuite.status !== 'active'">
            <el-icon><VideoPlay /></el-icon>
            执行套件
          </el-button>
          <el-button @click="viewExecutionHistory(selectedSuite)">
            <el-icon><Clock /></el-icon>
            执行历史
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 选择测试用例对话框 -->
    <TestCaseSelector
      v-model="showSelectTestCasesDialog"
      :project-id="projectId"
      :selected-cases="testCases"
      @confirm="handleTestCasesSelected"
    />

    <!-- 选择脚本对话框 -->
    <ScriptSelector
      v-model="showSelectScriptsDialog"
      :project-id="projectId"
      :selected-scripts="scripts"
      @confirm="handleScriptsSelected"
    />

    <!-- 执行进度对话框 -->
    <ExecutionProgressDialog
      v-model="showExecutionDialog"
      :execution-id="currentExecutionId"
      :project-id="projectId"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, VideoPlay, Clock
} from '@element-plus/icons-vue'
import TestCaseSelector from './components/TestCaseSelector.vue'
import ScriptSelector from './components/ScriptSelector.vue'
import ExecutionProgressDialog from './components/ExecutionProgressDialog.vue'

// 获取项目ID
const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.projectId))

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showSelectTestCasesDialog = ref(false)
const showSelectScriptsDialog = ref(false)
const showExecutionDialog = ref(false)

const testSuites = ref([])
const testCases = ref([])
const scripts = ref([])
const total = ref(0)
const selectedSuite = ref(null)
const editingSuite = ref(null)
const currentExecutionId = ref('')

// 搜索表单
const searchForm = reactive({
  search: '',
  status: '',
  page: 1,
  page_size: 20
})

// 套件表单
const suiteForm = reactive({
  name: '',
  description: '',
  parallel_count: 1,
  timeout: 300,
  status: 'active'
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入套件名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入套件描述', trigger: 'blur' }
  ]
}

// 表单引用
const formRef = ref()

// 方法
const loadTestSuites = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    testSuites.value = [
      {
        id: '1',
        name: '用户管理功能测试套件',
        description: '包含用户注册、登录、权限管理等功能的测试用例',
        test_case_count: 15,
        script_count: 8,
        status: 'active',
        parallel_count: 2,
        timeout: 300,
        last_execution: '2024-01-15T10:30:00Z',
        creator_name: '张三',
        created_at: '2024-01-10T09:00:00Z'
      },
      {
        id: '2',
        name: '订单流程测试套件',
        description: '涵盖订单创建、支付、发货、退款等完整流程',
        test_case_count: 25,
        script_count: 12,
        status: 'active',
        parallel_count: 3,
        timeout: 600,
        last_execution: '2024-01-14T14:20:00Z',
        creator_name: '李四',
        created_at: '2024-01-08T11:30:00Z'
      }
    ]
    total.value = testSuites.value.length
  } catch (error) {
    console.error('获取测试套件失败:', error)
    ElMessage.error('获取测试套件失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchForm.page = 1
  loadTestSuites()
}

const viewSuite = (suite) => {
  selectedSuite.value = suite
  loadSuiteDetails(suite.id)
  showDetailDialog.value = true
}

const editSuite = (suite) => {
  editingSuite.value = suite
  Object.assign(suiteForm, {
    name: suite.name,
    description: suite.description,
    parallel_count: suite.parallel_count,
    timeout: suite.timeout,
    status: suite.status
  })
  showCreateDialog.value = true
}

const deleteSuite = async (suite) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试套件 "${suite.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.success('测试套件删除成功')
    await loadTestSuites()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除测试套件失败:', error)
      ElMessage.error('删除测试套件失败')
    }
  }
}

const executeSuite = async (suite) => {
  try {
    await ElMessageBox.confirm(
      `确定要执行测试套件 "${suite.name}" 吗？`,
      '确认执行',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 模拟开始执行
    currentExecutionId.value = `exec_${Date.now()}`
    showExecutionDialog.value = true
    
    ElMessage.success('测试套件开始执行')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('执行测试套件失败:', error)
      ElMessage.error('执行测试套件失败')
    }
  }
}

const viewExecutionHistory = (suite) => {
  router.push(`/aitestrebort/project/${projectId.value}/test-execution?suiteId=${suite.id}`)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (editingSuite.value) {
      ElMessage.success('测试套件更新成功')
    } else {
      ElMessage.success('测试套件创建成功')
    }
    
    showCreateDialog.value = false
    await loadTestSuites()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingSuite.value = null
  Object.assign(suiteForm, {
    name: '',
    description: '',
    parallel_count: 1,
    timeout: 300,
    status: 'active'
  })
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const loadSuiteDetails = async (suiteId) => {
  // 模拟加载套件详情
  testCases.value = [
    {
      id: '1',
      name: '用户注册功能测试',
      level: 'P1',
      module_name: '用户管理'
    },
    {
      id: '2',
      name: '用户登录功能测试',
      level: 'P0',
      module_name: '用户管理'
    }
  ]
  
  scripts.value = [
    {
      id: '1',
      name: '用户注册自动化脚本',
      script_type: 'UI',
      status: 'active'
    },
    {
      id: '2',
      name: '用户登录API测试',
      script_type: 'API',
      status: 'active'
    }
  ]
}

const handleTestCasesSelected = (selectedCases) => {
  testCases.value = selectedCases
  ElMessage.success('测试用例添加成功')
}

const handleScriptsSelected = (selectedScripts) => {
  scripts.value = selectedScripts
  ElMessage.success('脚本添加成功')
}

const removeTestCase = (testCase) => {
  const index = testCases.value.findIndex(tc => tc.id === testCase.id)
  if (index > -1) {
    testCases.value.splice(index, 1)
    ElMessage.success('测试用例移除成功')
  }
}

const removeScript = (script) => {
  const index = scripts.value.findIndex(s => s.id === script.id)
  if (index > -1) {
    scripts.value.splice(index, 1)
    ElMessage.success('脚本移除成功')
  }
}

// 辅助方法
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const getLevelColor = (level) => {
  const colors = {
    P0: 'danger',
    P1: 'warning',
    P2: 'primary',
    P3: 'info'
  }
  return colors[level] || 'info'
}

// 生命周期
onMounted(() => {
  loadTestSuites()
})
</script>

<style scoped>
.test-suite-management {
  padding: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.content-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.suite-detail {
  padding: 16px 0;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  border-bottom: none;
  padding-bottom: 0;
}

.description-content {
  margin-top: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  color: #606266;
}

.execution-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>