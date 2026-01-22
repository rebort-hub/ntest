<template>
  <div class="rag-query-form">
    <el-card class="query-card">
      <template #header>
        <div class="card-header">
          <span>RAG 智能问答</span>
          <el-switch
            v-model="useRAG"
            active-text="RAG模式"
            inactive-text="检索模式"
            @change="handleModeChange"
          />
        </div>
      </template>
      
      <!-- 查询表单 -->
      <el-form :model="queryForm" label-width="100px" class="query-form">
        <el-form-item label="问题">
          <el-input
            v-model="queryForm.query"
            type="textarea"
            :rows="3"
            placeholder="请输入您的问题..."
            @keydown.ctrl.enter="handleQuery"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="检索数量">
              <el-input-number
                v-model="queryForm.top_k"
                :min="1"
                :max="20"
                size="small"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="相似度阈值">
              <el-input-number
                v-model="queryForm.score_threshold"
                :min="0"
                :max="1"
                :step="0.1"
                size="small"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="响应模式">
              <el-switch
                v-model="useStream"
                active-text="流式"
                inactive-text="普通"
                :disabled="!useRAG"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- RAG 配置 -->
        <div v-if="useRAG" class="rag-config">
          <el-divider content-position="left">LLM 配置</el-divider>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="服务商">
                <el-select v-model="queryForm.llm_provider" size="small">
                  <el-option label="OpenAI" value="openai" />
                  <el-option label="Azure OpenAI" value="azure" />
                  <el-option label="其他" value="other" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="模型">
                <el-input v-model="queryForm.llm_model" size="small" placeholder="gpt-3.5-turbo" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="温度">
                <el-input-number
                  v-model="queryForm.temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  size="small"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="API Key">
                <el-input
                  v-model="queryForm.llm_api_key"
                  type="password"
                  size="small"
                  placeholder="请输入 API Key"
                  show-password
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Base URL">
                <el-input
                  v-model="queryForm.llm_base_url"
                  size="small"
                  placeholder="https://api.openai.com/v1"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="系统提示词">
            <el-input
              v-model="queryForm.system_prompt"
              type="textarea"
              :rows="2"
              placeholder="可选：自定义系统提示词"
            />
          </el-form-item>
        </div>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="handleQuery"
            :loading="querying"
            :disabled="!queryForm.query.trim()"
          >
            <el-icon><Search /></el-icon>
            {{ useRAG ? '智能问答' : '检索文档' }}
          </el-button>
          <el-button @click="clearResults">清空结果</el-button>
          <el-button @click="$emit('close')">关闭</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 查询结果 -->
    <div v-if="queryResults.length > 0 || currentAnswer" class="results-section">
      <!-- RAG 回答 -->
      <el-card v-if="useRAG && currentAnswer" class="answer-card">
        <template #header>
          <div class="answer-header">
            <span>AI 回答</span>
            <div class="answer-stats">
              <el-tag size="small">检索: {{ lastQueryStats.retrieval_time?.toFixed(2) }}s</el-tag>
              <el-tag size="small" type="success">生成: {{ lastQueryStats.generation_time?.toFixed(2) }}s</el-tag>
            </div>
          </div>
        </template>
        
        <div class="answer-content">
          <div v-if="useStream && streaming" class="streaming-indicator">
            <el-icon class="rotating"><Loading /></el-icon>
            正在生成回答...
          </div>
          <div class="answer-text" v-html="formatAnswer(currentAnswer)"></div>
        </div>
      </el-card>
      
      <!-- 检索结果 -->
      <el-card class="sources-card">
        <template #header>
          <span>参考文档 ({{ queryResults.length }})</span>
        </template>
        
        <div class="sources-list">
          <div
            v-for="(result, index) in queryResults"
            :key="index"
            class="source-item"
          >
            <div class="source-header">
              <span class="source-title">{{ result.metadata?.document_title || '未知文档' }}</span>
              <el-tag size="small" :type="getScoreType(result.score)">
                相似度: {{ (result.score * 100).toFixed(1) }}%
              </el-tag>
            </div>
            <div class="source-content">{{ result.content }}</div>
            <div class="source-meta">
              分块: {{ result.metadata?.chunk_index }} | ID: {{ result.id }}
            </div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 空状态 -->
    <el-empty
      v-if="!querying && queryResults.length === 0 && !currentAnswer"
      description="请输入问题开始查询"
      :image-size="100"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Loading } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type KnowledgeBase } from '@/api/aitestrebort/knowledge-enhanced'

interface Props {
  knowledgeBase: KnowledgeBase
  projectId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

// 查询模式
const useRAG = ref(true)
const useStream = ref(false)

// 查询表单
const queryForm = reactive({
  query: '',
  top_k: 5,
  score_threshold: 0.5,
  llm_provider: 'openai',
  llm_model: 'gpt-3.5-turbo',
  llm_api_key: '',
  llm_base_url: '',
  temperature: 0.7,
  system_prompt: ''
})

// 查询状态
const querying = ref(false)
const streaming = ref(false)

// 查询结果
const queryResults = ref<any[]>([])
const currentAnswer = ref('')
const lastQueryStats = reactive({
  retrieval_time: 0,
  generation_time: 0
})

// 处理模式切换
const handleModeChange = () => {
  clearResults()
}

// 处理查询
const handleQuery = async () => {
  if (!queryForm.query.trim()) {
    ElMessage.warning('请输入问题')
    return
  }

  if (useRAG.value) {
    await handleRAGQuery()
  } else {
    await handleRetrievalQuery()
  }
}

// RAG 查询
const handleRAGQuery = async () => {
  querying.value = true
  currentAnswer.value = ''
  queryResults.value = []
  
  try {
    const params: any = {
      query: queryForm.query,
      top_k: queryForm.top_k,
      score_threshold: queryForm.score_threshold,
      llm_config: {
        provider: queryForm.llm_provider,
        model: queryForm.llm_model,
        temperature: queryForm.temperature
      }
    }

    // 添加 API Key 和 Base URL
    if (queryForm.llm_api_key) {
      params.llm_config.api_key = queryForm.llm_api_key
    }
    if (queryForm.llm_base_url) {
      params.llm_config.base_url = queryForm.llm_base_url
    }
    if (queryForm.system_prompt) {
      params.system_prompt = queryForm.system_prompt
    }

    if (useStream.value) {
      // 流式响应
      streaming.value = true
      await handleStreamQuery(params)
    } else {
      // 普通响应
      const response = await knowledgeEnhancedApi.rag.queryKnowledgeBase(
        props.projectId,
        props.knowledgeBase.id,
        {
          ...params,
          use_rag: true,
          llm_provider: params.llm_config.provider,
          llm_model: params.llm_config.model,
          llm_api_key: params.llm_config.api_key,
          llm_base_url: params.llm_config.base_url,
          temperature: params.llm_config.temperature
        }
      )

      if (response.data) {
        currentAnswer.value = response.data.answer
        queryResults.value = response.data.sources || []
        lastQueryStats.retrieval_time = response.data.retrieval_time || 0
        lastQueryStats.generation_time = response.data.generation_time || 0
      }
    }
  } catch (error: any) {
    console.error('RAG 查询失败:', error)
    ElMessage.error(error.response?.data?.detail || 'RAG 查询失败')
  } finally {
    querying.value = false
    streaming.value = false
  }
}

// 流式查询
const handleStreamQuery = async (params: any) => {
  try {
    const basePath = import.meta.env.VITE_BASE_API || '/api'
    const response = await fetch(
      `${basePath}/aitestrebort/knowledge/projects/${props.projectId}/knowledge-bases/${props.knowledgeBase.id}/query-stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: params.query,
          top_k: params.top_k,
          score_threshold: params.score_threshold,
          llm_provider: params.llm_config.provider,
          llm_model: params.llm_config.model,
          llm_api_key: params.llm_config.api_key,
          llm_base_url: params.llm_config.base_url,
          temperature: params.llm_config.temperature,
          system_prompt: params.system_prompt
        })
      }
    )

    if (!response.ok) {
      throw new Error('流式查询失败')
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('无法读取响应流')
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            continue
          }

          try {
            const json = JSON.parse(data)
            if (json.type === 'sources') {
              queryResults.value = json.data
            } else if (json.type === 'answer') {
              currentAnswer.value += json.data
            } else if (json.type === 'stats') {
              lastQueryStats.retrieval_time = json.data.retrieval_time || 0
              lastQueryStats.generation_time = json.data.generation_time || 0
            }
          } catch (e) {
            console.error('解析流数据失败:', e)
          }
        }
      }
    }
  } catch (error) {
    console.error('流式查询失败:', error)
    throw error
  }
}

// 检索查询
const handleRetrievalQuery = async () => {
  querying.value = true
  queryResults.value = []
  currentAnswer.value = ''
  
  try {
    const response = await knowledgeEnhancedApi.rag.queryKnowledgeBase(
      props.projectId,
      props.knowledgeBase.id,
      {
        query: queryForm.query,
        top_k: queryForm.top_k,
        score_threshold: queryForm.score_threshold,
        use_rag: false
      }
    )

    if (response.data) {
      queryResults.value = response.data.results || []
      lastQueryStats.retrieval_time = response.data.retrieval_time || 0
    }
  } catch (error: any) {
    console.error('检索查询失败:', error)
    ElMessage.error(error.response?.data?.detail || '检索查询失败')
  } finally {
    querying.value = false
  }
}

// 清空结果
const clearResults = () => {
  queryResults.value = []
  currentAnswer.value = ''
  lastQueryStats.retrieval_time = 0
  lastQueryStats.generation_time = 0
}

// 格式化答案（支持 Markdown）
const formatAnswer = (text: string) => {
  if (!text) return ''
  
  // 简单的 Markdown 转换
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

// 获取相似度标签类型
const getScoreType = (score: number) => {
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'info'
}
</script>

<style scoped>
.rag-query-form {
  padding: 20px;
}

.query-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.query-form {
  margin-top: 16px;
}

.rag-config {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.results-section {
  margin-top: 20px;
}

.answer-card {
  margin-bottom: 20px;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.answer-stats {
  display: flex;
  gap: 8px;
}

.answer-content {
  min-height: 100px;
}

.streaming-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  margin-bottom: 12px;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.answer-text {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
}

.answer-text :deep(strong) {
  font-weight: 600;
  color: #409eff;
}

.answer-text :deep(code) {
  padding: 2px 6px;
  background: #f5f7fa;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.sources-card {
  margin-bottom: 20px;
}

.sources-list {
  max-height: 500px;
  overflow-y: auto;
}

.source-item {
  margin-bottom: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
  transition: all 0.3s;
}

.source-item:hover {
  background: #ecf5ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.source-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.source-content {
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  margin-bottom: 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

.source-meta {
  font-size: 12px;
  color: #909399;
}
</style>
