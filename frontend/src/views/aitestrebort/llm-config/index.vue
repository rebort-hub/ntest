<template>
  <div class="llm-config-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>LLM 配置管理</h2>
        <p>管理大语言模型配置，支持多种 LLM 提供商</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建配置
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.search"
            placeholder="搜索配置名称"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.provider" placeholder="提供商" clearable @change="handleSearch">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Claude" value="claude" />
            <el-option label="Gemini" value="gemini" />
            <el-option label="通义千问" value="qwen" />
            <el-option label="文心一言" value="ernie" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button @click="loadConfigs">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 配置列表 -->
    <el-table :data="configs" v-loading="loading">
      <el-table-column prop="name" label="模型名称" min-width="150" />
      <el-table-column prop="config_name" label="配置标识" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.config_name || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="provider" label="提供商" width="120">
        <template #default="{ row }">
          <el-tag :type="getProviderType(row.provider)">{{ getProviderLabel(row.provider) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="model_name" label="模型" min-width="150" />
      <el-table-column prop="context_limit" label="上下文限制" width="120">
        <template #default="{ row }">
          <el-text size="small">{{ formatContextLimit(row.context_limit) }}</el-text>
        </template>
      </el-table-column>
      <el-table-column prop="supports_vision" label="多模态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.supports_vision ? 'success' : 'info'" size="small">
            {{ row.supports_vision ? '支持' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="temperature" label="温度" width="80" />
      <el-table-column prop="is_default" label="默认" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_default ? 'success' : 'info'" size="small">
            {{ row.is_default ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="150">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="text" @click="testConfig(row)" :loading="testingId === row.id">测试</el-button>
          <el-button type="text" @click="editConfig(row)">编辑</el-button>
          <el-button 
            type="text" 
            @click="setDefault(row)" 
            :disabled="row.is_default"
          >
            设为默认
          </el-button>
          <el-button type="text" @click="deleteConfig(row)" style="color: #f56c6c;">删除</el-button>
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
        @size-change="loadConfigs"
        @current-change="loadConfigs"
      />
    </div>

    <!-- 创建/编辑配置对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingConfig ? '编辑 LLM 配置' : '创建 LLM 配置'"
      width="600px"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="configForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="configForm.name" placeholder="请输入模型名称，如 gpt-4" />
          <el-text size="small" type="info">模型的具体名称</el-text>
        </el-form-item>
        
        <el-form-item label="配置标识" prop="config_name">
          <el-input v-model="configForm.config_name" placeholder="如：生产环境OpenAI、测试Claude配置（可选）" />
          <el-text size="small" type="info">用于区分不同环境的配置</el-text>
        </el-form-item>
        
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="configForm.provider" placeholder="选择提供商" @change="handleProviderChange">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Claude" value="claude" />
            <el-option label="Gemini" value="gemini" />
            <el-option label="通义千问" value="qwen" />
            <el-option label="文心一言" value="ernie" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="模型名称" prop="model_name">
          <el-select 
            v-model="configForm.model_name" 
            placeholder="选择或输入模型名称"
            filterable
            allow-create
          >
            <el-option 
              v-for="model in availableModels" 
              :key="model" 
              :label="model" 
              :value="model" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="API 密钥" prop="api_key">
          <el-input 
            v-model="configForm.api_key" 
            type="password" 
            placeholder="请输入 API 密钥"
            show-password
          />
        </el-form-item>

        <el-form-item label="API 地址" prop="base_url">
          <el-input v-model="configForm.base_url" placeholder="API 基础地址（可选）" />
        </el-form-item>

        <el-form-item label="系统提示词" prop="system_prompt">
          <el-input 
            v-model="configForm.system_prompt" 
            type="textarea" 
            :rows="4"
            placeholder="指导LLM行为的系统级提示词（可选）"
          />
          <el-text size="small" type="info">会在每次对话开始时自动添加</el-text>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="温度" prop="temperature">
              <el-input-number 
                v-model="configForm.temperature" 
                :min="0" 
                :max="2" 
                :step="0.1" 
                :precision="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大令牌" prop="max_tokens">
              <el-input-number 
                v-model="configForm.max_tokens" 
                :min="1" 
                :max="32000" 
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="上下文限制" prop="context_limit">
          <el-input-number 
            v-model="configForm.context_limit" 
            :min="1000" 
            :max="2000000" 
            :step="1000"
            style="width: 100%"
          />
          <el-text size="small" type="info">
            模型最大上下文Token数（GPT-4o: 128000, Claude: 200000, Gemini: 1000000）
          </el-text>
        </el-form-item>

        <el-form-item label="多模态支持">
          <el-switch 
            v-model="configForm.supports_vision"
            active-text="支持图片输入"
            inactive-text="仅文本"
          />
          <el-text size="small" type="info" style="display: block; margin-top: 5px;">
            标识模型是否支持图片/多模态输入（如GPT-4V、Qwen-VL等）
          </el-text>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="configForm.is_default">设为默认配置</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button @click="testCurrentConfig" :loading="testing">测试连接</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingConfig ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh
} from '@element-plus/icons-vue'
import { globalApi, type GlobalLLMConfig, type CreateGlobalLLMConfigData } from '@/api/aitestrebort/global'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const testing = ref(false)
const testingId = ref<number | null>(null)
const showCreateDialog = ref(false)
const configs = ref<GlobalLLMConfig[]>([])
const total = ref(0)
const editingConfig = ref<GlobalLLMConfig | null>(null)

// 搜索表单
const searchForm = reactive({
  search: '',
  provider: '',
  page: 1,
  page_size: 20
})

// 配置表单
const configForm = reactive<CreateGlobalLLMConfigData>({
  name: '',
  config_name: '',
  provider: 'openai',
  model_name: '',
  api_key: '',
  base_url: '',
  system_prompt: '',
  temperature: 0.7,
  max_tokens: 2000,
  supports_vision: false,
  context_limit: 128000,
  is_default: false
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '配置名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  provider: [
    { required: true, message: '请选择提供商', trigger: 'change' }
  ],
  model_name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  api_key: [
    { required: true, message: '请输入 API 密钥', trigger: 'blur' }
  ]
}

// 表单引用
const formRef = ref()

// 计算属性
const availableModels = computed(() => {
  const modelMap: Record<string, string[]> = {
    openai: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o', 'gpt-4o-mini'],
    claude: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku', 'claude-2.1'],
    gemini: ['gemini-pro', 'gemini-pro-vision', 'gemini-1.5-pro'],
    qwen: ['qwen-turbo', 'qwen-plus', 'qwen-max'],
    ernie: ['ernie-bot', 'ernie-bot-turbo', 'ernie-bot-4.0'],
    other: []
  }
  return modelMap[configForm.provider] || []
})

// 方法
const loadConfigs = async () => {
  loading.value = true
  try {
    const response = await globalApi.getLLMConfigs(searchForm)
    if (response.status === 200) {
      configs.value = response.data.items || response.data || []
      total.value = response.data.total || configs.value.length
    }
  } catch (error: any) {
    console.error('获取配置列表失败:', error)
    // 只处理业务逻辑错误，HTTP错误由响应拦截器处理
    if (error.response?.status < 500 && error.response?.data?.message) {
      ElMessage.error({
        message: error.response.data.message,
        duration: 5000
      })
    }
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchForm.page = 1
  loadConfigs()
}

const handleProviderChange = () => {
  configForm.model_name = ''
  // 根据提供商设置默认的 base_url
  const defaultUrls: Record<string, string> = {
    openai: 'https://api.openai.com/v1',
    claude: 'https://api.anthropic.com',
    gemini: 'https://generativelanguage.googleapis.com/v1',
    qwen: 'https://dashscope.aliyuncs.com/api/v1',
    ernie: 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1'
  }
  configForm.base_url = defaultUrls[configForm.provider] || ''
}

const testConfig = async (config: GlobalLLMConfig) => {
  testingId.value = config.id
  try {
    const response = await globalApi.testLLMConfig(config.id)
    if (response.status === 200) {
      ElMessage.success({
        message: `配置 "${config.name}" 测试成功`,
        duration: 3000
      })
    }
  } catch (error: any) {
    console.error('测试配置失败:', error)
    
    // 对于LLM配置测试，我们总是显示详细的错误信息
    let errorMessage = '测试配置失败'
    
    if (error.response?.data?.message) {
      // 后端返回的详细错误信息
      errorMessage = error.response.data.message
    } else if (error.message) {
      // 网络或其他错误
      errorMessage = error.message
    }
    
    // 显示详细的错误信息，延迟一点显示以避免与响应拦截器冲突
    setTimeout(() => {
      ElMessage.error({
        message: errorMessage,
        duration: 10000, // 延长显示时间，让用户有时间阅读详细信息
        showClose: true
      })
    }, 100)
  } finally {
    testingId.value = null
  }
}

const testCurrentConfig = async () => {
  if (!configForm.api_key) {
    ElMessage.warning('请先输入 API 密钥')
    return
  }
  
  if (!configForm.model_name) {
    ElMessage.warning('请先输入模型名称')
    return
  }
  
  testing.value = true
  try {
    // 创建临时配置进行测试
    const tempConfig = {
      ...configForm,
      name: configForm.name || '临时测试配置'
    }
    
    // 如果是编辑模式，直接测试现有配置
    if (editingConfig.value) {
      const response = await globalApi.testLLMConfig(editingConfig.value.id)
      if (response.status === 200) {
        ElMessage.success({
          message: '连接测试成功！配置可以正常使用',
          duration: 3000
        })
      }
    } else {
      // 新建模式，先创建临时配置进行测试
      try {
        const createResponse = await globalApi.createLLMConfig(tempConfig)
        if (createResponse.status === 200) {
          const tempConfigId = createResponse.data.id
          
          // 测试临时配置
          try {
            const testResponse = await globalApi.testLLMConfig(tempConfigId)
            if (testResponse.status === 200) {
              ElMessage.success({
                message: '连接测试成功！配置可以正常使用',
                duration: 3000
              })
            }
          } finally {
            // 删除临时配置
            await globalApi.deleteLLMConfig(tempConfigId)
          }
        }
      } catch (createError: any) {
        console.error('创建临时配置失败:', createError)
        throw new Error('无法创建临时配置进行测试')
      }
    }
  } catch (error: any) {
    console.error('连接测试失败:', error)
    
    // 对于LLM配置测试，我们总是显示详细的错误信息
    let errorMessage = '连接测试失败'
    
    if (error.response?.data?.message) {
      // 后端返回的详细错误信息
      errorMessage = error.response.data.message
    } else if (error.message) {
      // 网络或其他错误
      errorMessage = error.message
    }
    
    // 显示详细的错误信息，延迟一点显示以避免与响应拦截器冲突
    setTimeout(() => {
      ElMessage.error({
        message: errorMessage,
        duration: 10000, // 延长显示时间
        showClose: true
      })
    }, 100)
  } finally {
    testing.value = false
  }
}

const editConfig = (config: GlobalLLMConfig) => {
  editingConfig.value = config
  configForm.name = config.name
  configForm.config_name = config.config_name || ''
  configForm.provider = config.provider
  configForm.model_name = config.model_name
  configForm.api_key = config.api_key
  configForm.base_url = config.base_url || ''
  configForm.system_prompt = config.system_prompt || ''
  configForm.temperature = config.temperature || 0.7
  configForm.max_tokens = config.max_tokens || 2000
  configForm.supports_vision = config.supports_vision || false
  configForm.context_limit = config.context_limit || 128000
  configForm.is_default = config.is_default
  showCreateDialog.value = true
}

const setDefault = async (config: GlobalLLMConfig) => {
  try {
    const response = await globalApi.updateLLMConfig(config.id, { is_default: true })
    if (response.status === 200) {
      loadConfigs()
    }
  } catch (error) {
    console.error('设置默认配置失败:', error)
  }
}

const deleteConfig = async (config: GlobalLLMConfig) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置 "${config.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    const response = await globalApi.deleteLLMConfig(config.id)
    if (response.status === 200) {
      loadConfigs()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除配置失败:', error)
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    let response
    if (editingConfig.value) {
      response = await globalApi.updateLLMConfig(editingConfig.value.id, configForm)
    } else {
      response = await globalApi.createLLMConfig(configForm)
    }
    
    if (response.status === 200) {
      ElMessage.success({
        message: editingConfig.value ? '配置更新成功' : '配置创建成功',
        duration: 3000
      })
      showCreateDialog.value = false
      loadConfigs()
    }
  } catch (error: any) {
    console.error('提交失败:', error)
    // 只处理业务逻辑错误，HTTP错误由响应拦截器处理
    if (error.response?.status < 500 && error.response?.data?.message) {
      ElMessage.error({
        message: error.response.data.message,
        duration: 5000
      })
    }
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingConfig.value = null
  configForm.name = ''
  configForm.config_name = ''
  configForm.provider = 'openai'
  configForm.model_name = ''
  configForm.api_key = ''
  configForm.base_url = ''
  configForm.system_prompt = ''
  configForm.temperature = 0.7
  configForm.max_tokens = 2000
  configForm.supports_vision = false
  configForm.context_limit = 128000
  configForm.is_default = false
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const getProviderType = (provider: string) => {
  const types: Record<string, string> = {
    openai: 'primary',
    claude: 'success',
    gemini: 'warning',
    qwen: 'danger',
    ernie: 'info',
    other: 'default'
  }
  return types[provider] || 'default'
}

const getProviderLabel = (provider: string) => {
  const labels: Record<string, string> = {
    openai: 'OpenAI',
    claude: 'Claude',
    gemini: 'Gemini',
    qwen: '通义千问',
    ernie: '文心一言',
    other: '其他'
  }
  return labels[provider] || provider
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatContextLimit = (limit?: number) => {
  if (!limit) return '128K'
  if (limit >= 1000000) {
    return `${(limit / 1000000).toFixed(1)}M`
  }
  if (limit >= 1000) {
    return `${(limit / 1000).toFixed(0)}K`
  }
  return `${limit}`
}

// 生命周期
onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.llm-config-management {
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
</style>