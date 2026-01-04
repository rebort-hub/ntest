<template>
  <div class="global-config-form">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>
    
    <div v-else>
      <el-form
        ref="formRef"
        :model="configForm"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="嵌入服务" prop="embedding_service">
          <el-select v-model="configForm.embedding_service" placeholder="选择嵌入服务" @change="handleServiceChange">
            <el-option
              v-for="service in embeddingServices"
              :key="service.value"
              :label="service.label"
              :value="service.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="API基础URL" prop="api_base_url">
          <el-input
            v-model="configForm.api_base_url"
            placeholder="如: http://localhost:11434"
          />
          <div class="form-tip">
            API服务的基础URL地址
          </div>
        </el-form-item>

        <el-form-item 
          v-if="needsApiKey" 
          label="API密钥" 
          prop="api_key"
        >
          <el-input
            v-model="configForm.api_key"
            type="password"
            placeholder="请输入API密钥"
            show-password
          />
          <div class="form-tip">
            API服务的访问密钥
          </div>
        </el-form-item>

        <el-form-item label="模型名称" prop="model_name">
          <el-input
            v-model="configForm.model_name"
            placeholder="如: text-embedding-ada-002"
          />
          <div class="form-tip">
            具体的嵌入模型名称
          </div>
        </el-form-item>

        <el-form-item label="默认分块大小" prop="chunk_size">
          <el-input-number
            v-model="configForm.chunk_size"
            :min="100"
            :max="4000"
            :step="100"
          />
          <div class="form-tip">
            文档分块的默认大小（字符数）
          </div>
        </el-form-item>

        <el-form-item label="默认分块重叠" prop="chunk_overlap">
          <el-input-number
            v-model="configForm.chunk_overlap"
            :min="0"
            :max="500"
            :step="50"
          />
          <div class="form-tip">
            相邻分块之间的重叠字符数
          </div>
        </el-form-item>
      </el-form>

      <!-- 连接测试 -->
      <div class="test-section">
        <el-divider content-position="left">连接测试</el-divider>
        <el-button 
          type="primary" 
          @click="testConnection" 
          :loading="testing"
          :disabled="!canTest"
        >
          测试连接
        </el-button>
        
        <div v-if="testResult" class="test-result">
          <el-alert
            :title="testResult.success ? '连接成功' : '连接失败'"
            :type="testResult.success ? 'success' : 'error'"
            :description="testResult.message"
            show-icon
            :closable="false"
          />
          
          <div v-if="testResult.success && testResult.embedding_dimension" class="test-details">
            <p><strong>嵌入维度:</strong> {{ testResult.embedding_dimension }}</p>
            <p><strong>响应时间:</strong> {{ testResult.response_time }}s</p>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <el-button @click="$emit('close')">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存配置
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { knowledgeEnhancedApi } from '@/api/aitestrebort/knowledge-enhanced'

const emit = defineEmits<{
  close: []
}>()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const testing = ref(false)
const testResult = ref<any>(null)
const formRef = ref()

const embeddingServices = ref([
  { value: 'openai', label: 'OpenAI' },
  { value: 'azure_openai', label: 'Azure OpenAI' },
  { value: 'ollama', label: 'Ollama' },
  { value: 'custom', label: '自定义API' }
])

// 配置表单
const configForm = reactive({
  embedding_service: 'custom',
  api_base_url: 'http://localhost:11434',
  api_key: '',
  model_name: 'text-embedding-ada-002',
  chunk_size: 1000,
  chunk_overlap: 200
})

// 表单验证规则
const formRules = {
  embedding_service: [
    { required: true, message: '请选择嵌入服务', trigger: 'change' }
  ],
  api_base_url: [
    { required: true, message: '请输入API基础URL', trigger: 'blur' }
  ],
  model_name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  api_key: [
    { 
      validator: (rule: any, value: any, callback: any) => {
        if (needsApiKey.value && !value) {
          callback(new Error('请输入API密钥'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 计算属性
const needsApiKey = computed(() => {
  return ['openai', 'azure_openai'].includes(configForm.embedding_service)
})

const canTest = computed(() => {
  return configForm.api_base_url && configForm.model_name && 
         (!needsApiKey.value || configForm.api_key)
})

// 方法
const loadConfig = async () => {
  loading.value = true
  try {
    const response = await knowledgeEnhancedApi.config.getGlobalConfig()
    if (response.data) {
      Object.assign(configForm, response.data)
    }
  } catch (error) {
    console.error('获取配置失败:', error)
    ElMessage.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

const handleServiceChange = () => {
  // 清空API密钥和测试结果
  configForm.api_key = ''
  testResult.value = null
  
  // 根据服务类型设置默认值
  switch (configForm.embedding_service) {
    case 'openai':
      configForm.api_base_url = 'https://api.openai.com/v1'
      configForm.model_name = 'text-embedding-ada-002'
      break
    case 'azure_openai':
      configForm.api_base_url = ''
      configForm.model_name = 'text-embedding-ada-002'
      break
    case 'ollama':
      configForm.api_base_url = 'http://localhost:11434'
      configForm.model_name = 'nomic-embed-text'
      break
    case 'custom':
      configForm.api_base_url = 'http://localhost:11434'
      configForm.model_name = 'text-embedding-ada-002'
      break
  }
}

const testConnection = async () => {
  testing.value = true
  testResult.value = null
  
  try {
    const response = await knowledgeEnhancedApi.config.testEmbeddingConnection({
      embedding_service: configForm.embedding_service,
      api_base_url: configForm.api_base_url,
      api_key: configForm.api_key,
      model_name: configForm.model_name
    })
    
    testResult.value = response.data
  } catch (error) {
    console.error('连接测试失败:', error)
    testResult.value = {
      success: false,
      message: '连接测试失败，请检查配置'
    }
  } finally {
    testing.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    await knowledgeEnhancedApi.config.updateGlobalConfig(configForm)
    
    ElMessage.success('配置保存成功')
    emit('close')
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  } finally {
    submitting.value = false
  }
}

// 生命周期
onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.global-config-form {
  padding: 20px;
}

.loading-container {
  padding: 40px;
  text-align: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.test-section {
  margin: 30px 0;
}

.test-result {
  margin-top: 16px;
}

.test-details {
  margin-top: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 13px;
}

.test-details p {
  margin: 4px 0;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}

.form-actions .el-button {
  margin-left: 10px;
}
</style>