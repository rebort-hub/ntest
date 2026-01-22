<template>
  <div v-loading="loading" class="global-config-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
    >
      <el-form-item label="嵌入服务" prop="embedding_service">
        <el-select v-model="formData.embedding_service" placeholder="请选择嵌入服务">
          <el-option
            v-for="service in embeddingServices"
            :key="service.value"
            :label="service.label"
            :value="service.value"
          />
        </el-select>
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          选择嵌入服务类型。注意：某些API服务可能不支持嵌入功能。
        </div>
      </el-form-item>

      <el-form-item label="API基础URL" prop="api_base_url">
        <el-input
          v-model="formData.api_base_url"
          placeholder="如：https://api.openai.com/v1"
        />
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>
            输入API基础URL（不包含 /embeddings）。
            <el-link type="primary" @click="showUrlExamples = !showUrlExamples" :underline="false">
              {{ showUrlExamples ? '隐藏' : '查看' }}示例
            </el-link>
          </span>
        </div>
        <el-collapse-transition>
          <div v-show="showUrlExamples" class="url-examples">
            <div class="example-item">
              <strong>OpenAI:</strong> https://api.openai.com/v1
            </div>
            <div class="example-item">
              <strong>DeepSeek:</strong> https://api.deepseek.com/v1
            </div>
            <div class="example-item">
              <strong>Ollama (本地BGE-M3):</strong> http://localhost:11434
            </div>
            <div class="example-tip">
              💡 推荐使用 Ollama + BGE-M3：免费、中文优化、本地运行
            </div>
          </div>
        </el-collapse-transition>
      </el-form-item>

      <el-form-item label="模型名称" prop="model_name">
        <el-input
          v-model="formData.model_name"
          placeholder="如：text-embedding-ada-002 或 bge-m3"
        />
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>
            Ollama使用 <code>bge-m3</code>，OpenAI使用 <code>text-embedding-3-small</code>
          </span>
        </div>
      </el-form-item>

      <el-form-item label="API密钥" prop="api_key">
        <el-input
          v-model="formData.api_key"
          type="password"
          placeholder="请输入API密钥（可选）"
          show-password
        />
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>
            如显示为星号，测试时会自动使用已保存的密钥。如需更换，请输入新密钥。
          </span>
        </div>
      </el-form-item>

      <el-form-item label="模型名称" prop="model_name">
        <el-input
          v-model="formData.model_name"
          placeholder="如：text-embedding-ada-002"
        />
      </el-form-item>

      <el-form-item label="分块大小" prop="chunk_size">
        <el-input-number
          v-model="formData.chunk_size"
          :min="100"
          :max="2000"
          :step="100"
        />
        <span style="margin-left: 10px; color: #909399; font-size: 12px;">字符数</span>
      </el-form-item>

      <el-form-item label="分块重叠" prop="chunk_overlap">
        <el-input-number
          v-model="formData.chunk_overlap"
          :min="0"
          :max="500"
          :step="50"
        />
        <span style="margin-left: 10px; color: #909399; font-size: 12px;">字符数</span>
      </el-form-item>

      <el-form-item>
        <el-button @click="testConnection" :loading="testing">
          <el-icon><Connection /></el-icon>
          测试连接
        </el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存配置
        </el-button>
        <el-button @click="$emit('close')">取消</el-button>
      </el-form-item>
    </el-form>

    <el-alert
      v-if="testResult"
      :title="testResult.success ? '连接成功' : '连接失败'"
      :type="testResult.success ? 'success' : 'error'"
      :description="testResult.message"
      :closable="false"
      style="margin-top: 16px"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection, InfoFilled } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi } from '@/api/aitestrebort/knowledge-enhanced'

const emit = defineEmits<{
  close: []
  saved: []
}>()

const formRef = ref()
const loading = ref(false)
const testing = ref(false)
const submitting = ref(false)
const embeddingServices = ref<Array<{ value: string; label: string }>>([])
const testResult = ref<{ success: boolean; message: string } | null>(null)
const showUrlExamples = ref(false)

const formData = reactive({
  embedding_service: 'custom',
  api_base_url: '',
  api_key: '',
  model_name: 'text-embedding-ada-002',
  chunk_size: 1000,
  chunk_overlap: 200
})

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
  chunk_size: [
    { required: true, message: '请输入分块大小', trigger: 'blur' }
  ],
  chunk_overlap: [
    { required: true, message: '请输入分块重叠', trigger: 'blur' }
  ]
}

const loadConfig = async () => {
  loading.value = true
  try {
    const response = await knowledgeEnhancedApi.config.getGlobalConfig()
    if (response.data) {
      Object.assign(formData, response.data)
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

const loadEmbeddingServices = async () => {
  try {
    const response = await knowledgeEnhancedApi.config.getEmbeddingServices()
    if (response.data && response.data.services) {
      embeddingServices.value = response.data.services
    }
  } catch (error) {
    console.error('加载嵌入服务列表失败:', error)
  }
}

const testConnection = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    testing.value = true
    testResult.value = null

    const response = await knowledgeEnhancedApi.config.testEmbeddingConnection({
      embedding_service: formData.embedding_service,
      api_base_url: formData.api_base_url,
      api_key: formData.api_key,
      model_name: formData.model_name
    })

    if (response.data) {
      testResult.value = response.data
      if (response.data.success) {
        ElMessage.success('连接测试成功')
      } else {
        ElMessage.error('连接测试失败')
      }
    }
  } catch (error: any) {
    console.error('测试连接失败:', error)
    testResult.value = {
      success: false,
      message: error?.message || '连接测试失败'
    }
    ElMessage.error('连接测试失败')
  } finally {
    testing.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    await knowledgeEnhancedApi.config.updateGlobalConfig(formData)

    ElMessage.success('配置保存成功')
    emit('saved')
    emit('close')
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadConfig()
  loadEmbeddingServices()
})
</script>

<style scoped>
.global-config-form {
  padding: 20px;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  font-size: 14px;
}

.url-examples {
  margin-top: 8px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.example-item {
  margin-bottom: 8px;
  font-size: 12px;
  line-height: 1.5;
}

.example-item:last-child {
  margin-bottom: 0;
}

.example-item strong {
  color: #303133;
  margin-right: 8px;
}

.example-tip {
  margin-top: 12px;
  padding: 8px 12px;
  background-color: #e6f7ff;
  border-left: 3px solid #1890ff;
  border-radius: 4px;
  font-size: 12px;
  color: #0050b3;
}

code {
  padding: 2px 6px;
  background-color: #f5f5f5;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #d63200;
}
</style>
