<template>
  <div class="test-suite-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <div>
          <h1 class="page-title">测试套件管理</h1>
          <p class="page-description">创建和管理测试套件，支持批量执行自动化脚本</p>
        </div>
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
            <el-tag size="small" type="info">{{ row.test_case_count || 0 }}</el-tag>
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
              <el-form-item label="并发数" prop="max_concurrent_tasks">
                <el-input-number
                  v-model="suiteForm.max_concurrent_tasks"
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
            <el-descriptions-item label="并发数">{{ selectedSuite.max_concurrent_tasks }}</el-descriptions-item>
            <el-descriptions-item label="超时时间">{{ selectedSuite.timeout }}秒</el-descriptions-item>
            <el-descriptions-item label="创建者">{{ selectedSuite.creator_name }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(selectedSuite.created_at) }}</el-descriptions-item>
          </el-descriptions>
          <div class="description-content">
            <strong>描述：</strong>{{ selectedSuite.description }}
          </div>
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

    <!-- 选择脚本对话框 -->
    <ScriptSelector
      v-model="showSelectScriptsDialog"
      :project-id="projectId"
      :selected-scripts="scripts"
      @confirm="handleScriptsSelected"
    />

    <!-- 执行配置对话框 -->
    <ExecutionConfigDialog
      v-model="showExecutionConfigDialog"
      :suite="selectedSuite"
      @confirm="handleExecutionConfig"
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
  Plus, Search, VideoPlay, Clock, ArrowLeft
} from '@element-plus/icons-vue'
import ScriptSelector from './components/ScriptSelector.vue'
import ExecutionProgressDialog from './components/ExecutionProgressDialog.vue'
import ExecutionConfigDialog from './components/ExecutionConfigDialog.vue'
import {
  getTestSuites,
  createTestSuite,
  updateTestSuite,
  deleteTestSuite,
  getTestSuiteDetail,
  addScriptsToSuite,
  removeScriptFromSuite,
  getSuiteScripts,
  executeTestSuite
} from '@/api/aitestrebort/testsuite'

// 获取项目ID
const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.projectId))

// 响应式数据
const loading = ref(false)
const submitting = ref(false)

// 返回方法
const goBack = () => {
  const from = route.query.from as string
  if (from === 'testcase') {
    router.push(`/aitestrebort/project/${projectId.value}/testcase`)
  } else {
    router.push('/aitestrebort/project')
  }
}
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showSelectScriptsDialog = ref(false)
const showExecutionConfigDialog = ref(false)
const showExecutionDialog = ref(false)

const testSuites = ref([])
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
  max_concurrent_tasks: 1,
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
    const response = await getTestSuites({
      project_id: projectId.value,
      search: searchForm.search || undefined,
      status: searchForm.status || undefined,
      page: searchForm.page,
      page_size: searchForm.page_size
    })
    
    if (response.status === 200) {
      testSuites.value = response.data.items
      total.value = response.data.total
    } else {
      ElMessage.error(response.message || '获取测试套件失败')
    }
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

const viewSuite = async (suite) => {
  try {
    const response = await getTestSuiteDetail(suite.id, projectId.value)
    if (response.status === 200) {
      selectedSuite.value = response.data
      scripts.value = response.data.scripts || []
      showDetailDialog.value = true
    } else {
      ElMessage.error(response.message || '获取套件详情失败')
    }
  } catch (error) {
    console.error('获取套件详情失败:', error)
    ElMessage.error('获取套件详情失败')
  }
}

const editSuite = (suite) => {
  editingSuite.value = suite
  Object.assign(suiteForm, {
    name: suite.name,
    description: suite.description,
    max_concurrent_tasks: suite.max_concurrent_tasks,
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
    
    const response = await deleteTestSuite(suite.id, projectId.value)
    if (response.status === 200) {
      // 后端已经通过request拦截器显示了成功消息，这里不再重复显示
      await loadTestSuites()
    } else {
      // 错误消息也已经通过request拦截器显示了，这里只处理业务逻辑
      console.error('删除失败:', response.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除测试套件失败:', error)
      // 网络错误等异常情况才显示错误消息
      ElMessage.error('删除测试套件失败')
    }
  }
}

const executeSuite = async (suite) => {
  selectedSuite.value = suite
  showExecutionConfigDialog.value = true
}

const handleExecutionConfig = async (config) => {
  if (!selectedSuite.value) return
  
  try {
    const response = await executeTestSuite(selectedSuite.value.id, projectId.value, {
      ...config,
      max_concurrent_tasks: config.max_concurrent_tasks,
      timeout: config.timeout,
      environment: config.environment,
      mcp_config_id: config.mcp_config_id,
      browser: config.browser,
      headless: config.headless
    })
    
    if (response.status === 200) {
      currentExecutionId.value = response.data.execution_id || `exec_${Date.now()}`
      showExecutionDialog.value = true
      ElMessage.success('测试套件开始执行')
    } else {
      ElMessage.error(response.message || '执行失败')
    }
  } catch (error) {
    console.error('执行测试套件失败:', error)
    ElMessage.error('执行测试套件失败')
  }
}

const viewExecutionHistory = (suite) => {
  router.push({
    path: `/aitestrebort/project/${projectId.value}/test-execution`,
    query: { 
      suiteId: suite.id,
      from: 'test-suite'
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const formData = {
      project_id: projectId.value,
      name: suiteForm.name,
      description: suiteForm.description,
      max_concurrent_tasks: suiteForm.max_concurrent_tasks,
      timeout: suiteForm.timeout,
      status: suiteForm.status
    }
    
    let response
    if (editingSuite.value) {
      response = await updateTestSuite(editingSuite.value.id, projectId.value, formData)
    } else {
      response = await createTestSuite(formData)
    }
    
    if (response.status === 200) {
      // 后端已经通过request拦截器显示了成功消息，这里不再重复显示
      showCreateDialog.value = false
      await loadTestSuites()
    } else {
      // 错误消息也已经通过request拦截器显示了，这里只处理业务逻辑
      console.error('操作失败:', response.message)
    }
  } catch (error) {
    console.error('操作失败:', error)
    // 网络错误等异常情况才显示错误消息
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
    max_concurrent_tasks: 1,
    timeout: 300,
    status: 'active'
  })
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleScriptsSelected = async (selectedScripts) => {
  if (!selectedSuite.value) return
  
  try {
    const scriptIds = selectedScripts.map(script => script.id)
    const response = await addScriptsToSuite(selectedSuite.value.id, projectId.value, scriptIds)
    
    if (response.status === 200) {
      // 后端已经通过request拦截器显示了成功消息，这里不再重复显示
      // 重新加载套件详情
      await viewSuite(selectedSuite.value)
    } else {
      // 错误消息也已经通过request拦截器显示了，这里只处理业务逻辑
      console.error('添加失败:', response.message)
    }
  } catch (error) {
    console.error('添加脚本失败:', error)
    ElMessage.error('添加脚本失败')
  }
}

const removeScript = async (script) => {
  if (!selectedSuite.value) return
  
  try {
    const response = await removeScriptFromSuite(selectedSuite.value.id, projectId.value, script.id)
    if (response.status === 200) {
      // 后端已经通过request拦截器显示了成功消息，这里不再重复显示
      // 重新加载套件详情
      await viewSuite(selectedSuite.value)
    } else {
      // 错误消息也已经通过request拦截器显示了，这里只处理业务逻辑
      console.error('移除失败:', response.message)
    }
  } catch (error) {
    console.error('移除脚本失败:', error)
    ElMessage.error('移除脚本失败')
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
  display: flex;
  align-items: center;
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