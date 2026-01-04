<template>
  <div class="aitestrebort-automation">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item @click="$router.push('/aitestrebort/project')">项目管理</el-breadcrumb-item>
          <el-breadcrumb-item @click="$router.push(`/aitestrebort/project/${projectId}/testcase`)">{{ projectName }}</el-breadcrumb-item>
          <el-breadcrumb-item>自动化脚本</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button @click="$router.push(`/aitestrebort/project/${projectId}/testcase`)">
            <el-icon><Document /></el-icon>
            测试用例
          </el-button>
          <el-button @click="$router.push(`/aitestrebort/project/${projectId}/ai-generator`)">
            <el-icon><MagicStick /></el-icon>
            AI 生成
          </el-button>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建脚本
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
          <el-select v-model="searchForm.script_type" placeholder="脚本类型" clearable @change="handleSearch">
            <el-option label="UI自动化" value="ui" />
            <el-option label="接口自动化" value="api" />
            <el-option label="单元测试" value="unit" />
            <el-option label="性能测试" value="performance" />
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
      <el-table-column prop="name" label="脚本名称" min-width="200" />
      <el-table-column prop="script_type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="getTypeColor(row.script_type)">{{ getTypeLabel(row.script_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="framework" label="框架" width="120">
        <template #default="{ row }">
          <el-tag size="small">{{ row.framework }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="language" label="语言" width="100">
        <template #default="{ row }">
          <el-tag size="small" type="info">{{ row.language }}</el-tag>
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
          <el-button type="text" @click="editScript(row)">编辑</el-button>
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

    <!-- 创建/编辑脚本对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingScript ? '编辑脚本' : '创建脚本'"
      width="80%"
      @closed="resetForm"
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
          <div class="code-editor">
            <el-input
              v-model="scriptForm.script_content"
              type="textarea"
              :rows="15"
              placeholder="请输入脚本内容"
              style="font-family: 'Courier New', monospace;"
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
      width="80%"
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
          <h4>脚本内容</h4>
          <pre class="code-block">{{ currentScript.script_content }}</pre>
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
import {
  Plus,
  Search,
  Refresh,
  Document,
  MagicStick
} from '@element-plus/icons-vue'
import { automationApi, type AutomationScript, type CreateScriptData, type ExecuteScriptData } from '@/api/aitestrebort/automation'
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
const loading = ref(false)
const submitting = ref(false)
const validating = ref(false)
const executing = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showExecuteDialog = ref(false)
const scripts = ref<AutomationScript[]>([])
const total = ref(0)
const editingScript = ref<AutomationScript | null>(null)
const currentScript = ref<AutomationScript | null>(null)

// 搜索表单
const searchForm = reactive({
  search: '',
  script_type: '',
  status: '',
  page: 1,
  page_size: 20
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

// 方法
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
  showDetailDialog.value = true
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

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    ui: 'UI自动化',
    api: '接口自动化',
    unit: '单元测试',
    performance: '性能测试'
  }
  return labels[type] || type
}

const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    ui: 'primary',
    api: 'success',
    unit: 'warning',
    performance: 'danger'
  }
  return colors[type] || 'info'
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

// 生命周期
onMounted(() => {
  loadProjectDetail()
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
</style>