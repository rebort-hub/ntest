<template>
  <div class="global-config-form">
    <el-form :model="configForm" :rules="configRules" ref="configFormRef" label-width="120px">
      <el-form-item label="嵌入服务" prop="embedding_service">
        <el-select v-model="configForm.embedding_service" placeholder="选择嵌入服务">
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
          placeholder="如: http://localhost:11434 或 https://api.openai.com/v1"
        />
      </el-form-item>

      <el-form-item label="API密钥" prop="api_key">
        <el-input
          v-model="configForm.api_key"
          type="password"
          placeholder="请输入API密钥"
          show-password
        />
      </el-form-item>

      <el-form-item label="模型名称" prop="model_name">
        <el-input
          v-model="configForm.model_name"
          placeholder="如: text-embedding-ada-002"
        />
      </el-form-item>

      <el-form-item label="默认分块大小" prop="chunk_size">
        <el-input-number
          v-model="configForm.chunk_size"
          :min="100"
          :max="4000"
          :step="100"
        />
        <span class="form-tip">建议值: 1000-2000</span>
      </el-form-item>

      <el-form-item label="默认分块重叠" prop="chunk_overlap">
        <el-input-number
          v-model="configForm.chunk_overlap"
          :min="0"
          :max="500"
          :step="50"
        />
        <span class="form-tip">建议值: 100-300</span>
      </el-form-item>
    </el-form>

    <!-- 连接测试 -->
    <div class="test-section">
      <el-button @click="testConnection" :loading="testing">
        <el-icon><Connection /></el-icon>
        测试连接
      </el-button>
      
      <div v-if="testResult" class="test-result">
        <el-alert
          :type="testResult.success ? 'success' : 'error'"
          :title="testResult.message"
          :closable="false"
        >
          <template v-if="testResult.success" #default>
            <p>嵌入维度: {{ testResult.embedding_dimension }}</p>
            <p>响应时间: {{ testResult.response_time }}s</p>
          </template>
        </el-alert>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="form-actions">
      <el-button @click="$emit('close')">取消</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">保存配置</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type KnowledgeGlobalConfig } from '@/api/aitestrebort/knowledge-enhanced'

const emit = defineEmits<{
  close: []
}>()

// 响应式数据
const embeddingServices = ref<Array<{ value: string; label: string }>>([])
const saving = ref(false)
const testing = ref(false)
const testResult = ref<any>(null)

// 配置表单
const configForm = reactive<Partial<KnowledgeGlobalConfig>>({
  embedding_service: 'custom',
  api_base_url: '',
  api_key: '',
  model_name: 'text-embedding-ada-002',
  chunk_size: 1000,
  chunk_overlap: 200
})

// 表单验证规则
const configRules = {
  embedding_service: [
    { required: true, message: '请选择嵌入服务', trigger: 'change' }
  ],
  api_base_url: [
    { required: true, message: '请输入API基础URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  model_name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  chunk_size: [
    { required: true, message: '请输入分块大小', trigger: 'blur' },
    { type: 'number', min: 100, max: 4000, message: '分块大小应在100-4000之间', trigger: 'blur' }
  ],
  chunk_overlap: [
    { required: true, message: '请输入分块重叠', trigger: 'blur' },
    { type: 'number', min: 0, max: 500, message: '分块重叠应在0-500之间', trigger: 'blur' }
  ]
}

// 表单引用
const configFormRef = ref()

// 加载嵌入服务列表
const loadEmbeddingServices = async () => {
  try {
    const response = await knowledgeEnhancedApi.config.getEmbeddingServices()
    if (response.data?.services) {
      embeddingServices.value = response.data.services
    }
  } catch (error) {
    console.error('Failed to load embedding services:', error)
  }
}

// 加载当前配置
const loadCurrentConfig = async () => {
  try {
    const response = await knowledgeEnhancedApi.config.getGlobalConfig()
    if (response.data) {
      Object.assign(configForm, response.data)
    }
  } catch (error) {
    console.error('Failed to load current config:', error)
  }
}

// 测试连接
const testConnection = async () => {
  try {
    await configFormRef.value?.validate(['embedding_service', 'api_base_url', 'model_name'])
    
    testing.value = true
    testResult.value = null
    
    const testConfig = {
      embedding_service: configForm.embedding_service!,
      api_base_url: configForm.api_base_url!,
      api_key: configForm.api_key || '',
      model_name: configForm.model_name!
    }
    
    const response = await knowledgeEnhancedApi.config.testEmbeddingConnection(testConfig)
    testResult.value = response.data
    
    if (response.data?.success) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error('连接测试失败')
    }
    
  } catch (error) {
    console.error('Connection test failed:', error)
    testResult.value = {
      success: false,
      message: '连接测试失败: ' + (error as Error).message
    }
    ElMessage.error('连接测试失败')
  } finally {
    testing.value = false
  }
}

// 保存配置
const handleSave = async () => {
  try {
    await configFormRef.value?.validate()
    
    saving.value = true
    
    await knowledgeEnhancedApi.config.updateGlobalConfig(configForm)
    
    ElMessage.success('配置保存成功')
    emit('close')
    
  } catch (error) {
    console.error('Failed to save config:', error)
    ElMessage.error('保存配置失败')
  } finally {
    saving.value = false
  }
}

// 初始化
onMounted(() => {
  loadEmbeddingServices()
  loadCurrentConfig()
})
</script>

<style scoped>
.global-config-form {
  padding: 20px;
}

.form-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.test-section {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.test-result {
  margin-top: 15px;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}

.form-actions .el-button {
  margin-left: 10px;
}
</style>