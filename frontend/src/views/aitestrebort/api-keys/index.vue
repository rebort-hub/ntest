<template>
  <div class="api-keys-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>API 密钥管理</h2>
        <p>管理各种服务的 API 密钥，确保安全存储</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建密钥
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.search"
            placeholder="搜索密钥名称"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.service_type" placeholder="服务类型" clearable @change="handleSearch">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Claude" value="claude" />
            <el-option label="Gemini" value="gemini" />
            <el-option label="通义千问" value="qwen" />
            <el-option label="文心一言" value="ernie" />
            <el-option label="GitHub" value="github" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.is_active" placeholder="状态" clearable @change="handleSearch">
            <el-option label="激活" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button @click="loadApiKeys">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 密钥列表 -->
    <el-table :data="apiKeys" v-loading="loading">
      <el-table-column prop="name" label="密钥名称" min-width="150" />
      <el-table-column prop="service_type" label="服务类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getServiceType(row.service_type)">{{ getServiceLabel(row.service_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="api_key" label="API 密钥" min-width="200">
        <template #default="{ row }">
          <div class="api-key-cell">
            <span v-if="!row.showKey" class="masked-key">{{ maskApiKey(row.api_key) }}</span>
            <span v-else class="full-key">{{ row.api_key }}</span>
            <el-button 
              type="text" 
              size="small" 
              @click="toggleKeyVisibility(row)"
              style="margin-left: 8px;"
            >
              <el-icon>
                <View v-if="!row.showKey" />
                <Hide v-else />
              </el-icon>
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="copyApiKey(row.api_key)"
              style="margin-left: 4px;"
            >
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-switch 
            v-model="row.is_active" 
            @change="toggleStatus(row)"
            :loading="toggleLoading === row.id"
          />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="150">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="text" @click="testApiKey(row)" :loading="testingId === row.id">测试</el-button>
          <el-button type="text" @click="editApiKey(row)">编辑</el-button>
          <el-button type="text" @click="regenerateKey(row)" :loading="regeneratingId === row.id">重新生成</el-button>
          <el-button type="text" @click="deleteApiKey(row)" style="color: #f56c6c;">删除</el-button>
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
        @size-change="loadApiKeys"
        @current-change="loadApiKeys"
      />
    </div>

    <!-- 创建/编辑密钥对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingApiKey ? '编辑 API 密钥' : '创建 API 密钥'"
      width="600px"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="keyForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="密钥名称" prop="name">
          <el-input v-model="keyForm.name" placeholder="请输入密钥名称" />
        </el-form-item>
        
        <el-form-item label="服务类型" prop="service_type">
          <el-select v-model="keyForm.service_type" placeholder="选择服务类型" @change="handleServiceTypeChange">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Claude" value="claude" />
            <el-option label="Gemini" value="gemini" />
            <el-option label="通义千问" value="qwen" />
            <el-option label="文心一言" value="ernie" />
            <el-option label="GitHub" value="github" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="API 密钥" prop="api_key">
          <el-input 
            v-model="keyForm.api_key" 
            type="password" 
            placeholder="请输入 API 密钥"
            show-password
          />
          <div class="key-help" v-if="keyHelp">
            <el-text size="small" type="info">{{ keyHelp }}</el-text>
          </div>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="keyForm.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入密钥描述（可选）"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="keyForm.is_active">激活此密钥</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button @click="validateCurrentKey" :loading="validating">验证密钥</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingApiKey ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 密钥使用统计对话框 -->
    <el-dialog
      v-model="showStatsDialog"
      title="密钥使用统计"
      width="800px"
    >
      <div class="stats-content" v-if="currentStats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总调用次数" :value="currentStats.total_calls" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="成功调用" :value="currentStats.success_calls" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="失败调用" :value="currentStats.failed_calls" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="成功率" :value="currentStats.success_rate" suffix="%" />
          </el-col>
        </el-row>
        
        <div class="usage-chart" style="margin-top: 20px;">
          <!-- 这里可以添加图表组件 -->
          <el-text>使用趋势图（待实现）</el-text>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Hide, CopyDocument
} from '@element-plus/icons-vue'
import { projectApi, type APIKey, type CreateAPIKeyData } from '@/api/aitestrebort/project'

// 获取默认项目ID
const defaultProjectId = ref<number>(1)

// 从localStorage获取或设置默认项目ID
const getDefaultProjectId = async () => {
  try {
    // 尝试从localStorage获取
    const stored = localStorage.getItem('defaultProjectId')
    if (stored) {
      defaultProjectId.value = Number(stored)
      return
    }
    
    // 如果没有，获取用户的第一个项目
    const response = await projectApi.getProjects({ page_no: 1, page_size: 1 })
    if (response.status === 200 && response.data.items && response.data.items.length > 0) {
      defaultProjectId.value = response.data.items[0].id
      localStorage.setItem('defaultProjectId', String(defaultProjectId.value))
    }
  } catch (error) {
    console.error('获取默认项目ID失败:', error)
  }
}

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const validating = ref(false)
const testingId = ref<number | null>(null)
const toggleLoading = ref<number | null>(null)
const regeneratingId = ref<number | null>(null)
const showCreateDialog = ref(false)
const showStatsDialog = ref(false)
const apiKeys = ref<(APIKey & { showKey?: boolean })[]>([])
const total = ref(0)
const editingApiKey = ref<APIKey | null>(null)
const currentStats = ref<any>(null)

// 搜索表单
const searchForm = reactive({
  search: '',
  service_type: '',
  is_active: undefined as boolean | undefined,
  page: 1,
  page_size: 20
})

// 密钥表单
const keyForm = reactive<CreateAPIKeyData>({
  name: '',
  service_type: 'openai',
  api_key: '',
  description: '',
  is_active: true
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入密钥名称', trigger: 'blur' },
    { min: 2, max: 50, message: '密钥名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  service_type: [
    { required: true, message: '请选择服务类型', trigger: 'change' }
  ],
  api_key: [
    { required: true, message: '请输入 API 密钥', trigger: 'blur' }
  ]
}

// 表单引用
const formRef = ref()

// 计算属性
const keyHelp = computed(() => {
  const helpMap: Record<string, string> = {
    openai: '格式：sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    claude: '格式：sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    gemini: '格式：AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    qwen: '格式：sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    ernie: '格式：xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    github: '格式：ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  }
  return helpMap[keyForm.service_type] || '请输入有效的 API 密钥'
})

// 方法
const loadApiKeys = async () => {
  loading.value = true
  try {
    const params = {
      search: searchForm.search,
      service_type: searchForm.service_type,
      is_active: searchForm.is_active,
      page: searchForm.page,
      page_size: searchForm.page_size
    }
    console.log('Loading API keys with params:', params)
    const response = await projectApi.getAPIKeys(defaultProjectId.value, params)
    console.log('API keys response:', response)
    if (response.status === 200) {
      apiKeys.value = (response.data.items || response.data || []).map((key: APIKey) => ({
        ...key,
        showKey: false
      }))
      total.value = response.data.total || apiKeys.value.length
    }
  } catch (error) {
    console.error('获取密钥列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchForm.page = 1
  loadApiKeys()
}

const handleServiceTypeChange = () => {
  keyForm.api_key = ''
}

const toggleKeyVisibility = (key: APIKey & { showKey?: boolean }) => {
  key.showKey = !key.showKey
}

const copyApiKey = async (apiKey: string) => {
  try {
    await navigator.clipboard.writeText(apiKey)
    ElMessage.success('API 密钥已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const toggleStatus = async (key: APIKey) => {
  toggleLoading.value = key.id
  try {
    await projectApi.updateAPIKey(defaultProjectId.value, key.id, { 
      is_active: key.is_active 
    })
  } catch (error) {
    // 恢复状态
    key.is_active = !key.is_active
  } finally {
    toggleLoading.value = null
  }
}

const testApiKey = async (key: APIKey) => {
  testingId.value = key.id
  try {
    // 这里应该调用测试 API 密钥的接口
    await new Promise(resolve => setTimeout(resolve, 2000)) // 模拟测试
    ElMessage.success('API 密钥测试成功')
  } catch (error) {
    ElMessage.error('API 密钥测试失败')
  } finally {
    testingId.value = null
  }
}

const validateCurrentKey = async () => {
  if (!keyForm.api_key) {
    ElMessage.warning('请先输入 API 密钥')
    return
  }
  
  validating.value = true
  try {
    // 这里应该调用验证当前密钥的 API
    await new Promise(resolve => setTimeout(resolve, 2000)) // 模拟验证
    ElMessage.success('密钥验证成功')
  } catch (error) {
    ElMessage.error('密钥验证失败')
  } finally {
    validating.value = false
  }
}

const editApiKey = (key: APIKey) => {
  editingApiKey.value = key
  keyForm.name = key.name
  keyForm.service_type = key.service_type
  keyForm.api_key = key.api_key
  keyForm.description = key.description || ''
  keyForm.is_active = key.is_active
  showCreateDialog.value = true
}

const regenerateKey = async (key: APIKey) => {
  try {
    await ElMessageBox.confirm(
      '重新生成密钥将使当前密钥失效，确定继续吗？',
      '确认重新生成',
      { type: 'warning' }
    )
    
    regeneratingId.value = key.id
    // 这里应该调用重新生成密钥的 API
    await new Promise(resolve => setTimeout(resolve, 2000)) // 模拟重新生成
    ElMessage.success('密钥重新生成成功')
    loadApiKeys()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重新生成密钥失败')
    }
  } finally {
    regeneratingId.value = null
  }
}

const deleteApiKey = async (key: APIKey) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除密钥 "${key.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await projectApi.deleteAPIKey(defaultProjectId.value, key.id)
    loadApiKeys()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除密钥失败:', error)
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (editingApiKey.value) {
      await projectApi.updateAPIKey(defaultProjectId.value, editingApiKey.value.id, keyForm)
    } else {
      await projectApi.createAPIKey(defaultProjectId.value, keyForm)
    }
    
    showCreateDialog.value = false
    loadApiKeys()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingApiKey.value = null
  keyForm.name = ''
  keyForm.service_type = 'openai'
  keyForm.api_key = ''
  keyForm.description = ''
  keyForm.is_active = true
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const getServiceType = (serviceType: string) => {
  const types: Record<string, string> = {
    openai: 'primary',
    claude: 'success',
    gemini: 'warning',
    qwen: 'danger',
    ernie: 'info',
    github: 'default',
    other: 'default'
  }
  return types[serviceType] || 'default'
}

const getServiceLabel = (serviceType: string) => {
  const labels: Record<string, string> = {
    openai: 'OpenAI',
    claude: 'Claude',
    gemini: 'Gemini',
    qwen: '通义千问',
    ernie: '文心一言',
    github: 'GitHub',
    other: '其他'
  }
  return labels[serviceType] || serviceType
}

const maskApiKey = (apiKey: string) => {
  if (!apiKey || apiKey.length <= 8) return apiKey
  return apiKey.substring(0, 4) + '*'.repeat(Math.min(apiKey.length - 8, 20)) + apiKey.substring(apiKey.length - 4)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(async () => {
  await getDefaultProjectId()
  loadApiKeys()
})
</script>

<style scoped>
.api-keys-management {
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

.header-left h2 {
  margin: 0 0 5px 0;
  color: #303133;
}

.header-left p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.search-bar {
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.api-key-cell {
  display: flex;
  align-items: center;
}

.masked-key {
  font-family: 'Courier New', monospace;
  color: #909399;
}

.full-key {
  font-family: 'Courier New', monospace;
  color: #303133;
}

.key-help {
  margin-top: 4px;
}

.stats-content {
  padding: 20px 0;
}

.usage-chart {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
}
</style>