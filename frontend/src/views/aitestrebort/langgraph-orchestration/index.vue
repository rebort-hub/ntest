<template>
  <div class="langgraph-orchestration">
    <el-card class="page-header">
      <div class="header-content">
        <el-button @click="goBack" style="margin-right: 16px;">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div>
          <h2>LangGraph智能编排</h2>
          <p>基于LangGraph的智能对话和RAG查询系统</p>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- RAG查询区域 -->
      <el-col :span="12">
        <el-card class="rag-query-card">
          <template #header>
            <div class="card-header">
              <span>RAG智能查询</span>
              <el-button 
                type="primary" 
                size="small" 
                @click="executeRAGQuery"
                :loading="ragLoading"
              >
                执行查询
              </el-button>
            </div>
          </template>

          <div class="rag-query-content">
            <el-form :model="ragForm" label-width="120px" class="query-form">
              <el-form-item label="查询问题">
                <el-input
                  v-model="ragForm.question"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入您的问题..."
                />
              </el-form-item>

              <el-form-item label="知识库">
                <el-select 
                  v-model="ragForm.knowledge_base_id" 
                  placeholder="选择知识库"
                  style="width: 100%"
                  size="small"
                >
                  <el-option
                    v-for="kb in knowledgeBases"
                    :key="kb.id"
                    :label="kb.name"
                    :value="kb.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="回答模式">
                <el-select 
                  v-model="ragForm.prompt_template" 
                  placeholder="选择回答模式"
                  style="width: 100%"
                  size="small"
                >
                  <el-option label="通用模式（推荐）" value="default">
                    <span>通用模式</span>
                    <span style="color: #909399; font-size: 12px; margin-left: 8px;">结构化回答，适合大多数场景</span>
                  </el-option>
                  <el-option label="技术模式" value="technical">
                    <span>技术模式</span>
                    <span style="color: #909399; font-size: 12px; margin-left: 8px;">包含代码示例和最佳实践</span>
                  </el-option>
                  <el-option label="测试模式" value="testing">
                    <span>测试模式</span>
                    <span style="color: #909399; font-size: 12px; margin-left: 8px;">测试用例设计和测试策略</span>
                  </el-option>
                  <el-option label="简洁模式" value="concise">
                    <span>简洁模式</span>
                    <span style="color: #909399; font-size: 12px; margin-left: 8px;">快速简洁的回答</span>
                  </el-option>
                </el-select>
              </el-form-item>

              <el-form-item label="高级设置">
                <el-row :gutter="10">
                  <el-col :span="8">
                    <el-input-number
                      v-model="ragForm.top_k"
                      :min="1"
                      :max="20"
                      size="small"
                      placeholder="返回数量"
                    />
                  </el-col>
                  <el-col :span="8">
                    <el-input-number
                      v-model="ragForm.similarity_threshold"
                      :min="0"
                      :max="1"
                      :step="0.1"
                      size="small"
                      placeholder="相似度阈值"
                    />
                  </el-col>
                  <el-col :span="8">
                    <el-switch
                      v-model="ragForm.use_knowledge_base"
                      active-text="使用知识库"
                      size="small"
                    />
                  </el-col>
                </el-row>
              </el-form-item>
            </el-form>

            <!-- RAG查询结果 - 可滚动区域 -->
            <div v-if="ragResult" class="rag-result-scroll">
              <el-divider content-position="left">查询结果</el-divider>
              
              <div class="answer-section">
                <h4>回答</h4>
                <div class="answer-content" v-html="formatMarkdown(ragResult.answer)"></div>
              </div>

              <div class="context-section">
                <h4>相关上下文 ({{ ragResult.context.length }}条)</h4>
                <el-collapse>
                  <el-collapse-item
                    v-for="(ctx, index) in ragResult.context"
                    :key="index"
                    :title="`上下文 ${index + 1} (相似度: ${((ctx.score || ctx.similarity_score || 0) * 100).toFixed(1)}%)`"
                  >
                    <div class="context-content" v-html="formatMarkdown(ctx.content)"></div>
                    <div class="context-metadata">
                      <el-tag size="small">{{ ctx.metadata.source || ctx.metadata.document_title || '未知来源' }}</el-tag>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>

              <div class="timing-info">
                <el-tag type="info" size="small">检索时间: {{ (ragResult.retrieval_time * 1000).toFixed(0) }}ms</el-tag>
                <el-tag type="success" size="small">生成时间: {{ (ragResult.generation_time * 1000).toFixed(0) }}ms</el-tag>
                <el-tag type="warning" size="small">总时间: {{ (ragResult.total_time * 1000).toFixed(0) }}ms</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 对话历史区域 -->
      <el-col :span="12">
        <el-card class="conversation-card">
          <template #header>
            <div class="card-header">
              <span>对话历史</span>
              <el-button 
                type="danger" 
                size="small" 
                @click="clearConversation"
              >
                清空历史
              </el-button>
            </div>
          </template>

          <div class="conversation-history">
            <div
              v-for="(msg, index) in conversationHistory"
              :key="index"
              :class="['message', msg.type]"
            >
              <div class="message-header">
                <span class="message-type">{{ msg.type === 'user' ? '用户' : 'AI' }}</span>
                <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
              </div>
              <div class="message-content" v-html="formatMarkdown(msg.content)"></div>
            </div>
          </div>

          <div class="conversation-input">
            <el-input
              v-model="conversationInput"
              placeholder="继续对话..."
              @keyup.enter="sendMessage"
            >
              <template #append>
                <el-button @click="sendMessage" :loading="conversationLoading">
                  发送
                </el-button>
              </template>
            </el-input>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统状态区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>系统状态</span>
          </template>

          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="知识库数量" :value="knowledgeBases.length" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="今日查询" :value="todayQueries" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="平均响应时间" :value="avgResponseTime" suffix="ms" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功率" :value="successRate" suffix="%" />
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { advancedFeaturesApi } from '@/api/aitestrebort/advanced-features'
import { marked } from 'marked'
import type { 
  RAGQueryRequest, 
  RAGQueryResponse 
} from '@/api/aitestrebort/advanced-features'

// 配置 marked
marked.setOptions({
  breaks: true,  // 支持 GitHub 风格的换行
  gfm: true,     // 启用 GitHub Flavored Markdown
  headerIds: false,  // 不生成标题 ID
  mangle: false  // 不混淆邮箱地址
})

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.projectId)

// 计算返回路径
const backPath = computed(() => {
  const from = route.query.from as string
  if (from === 'testcase') {
    return `/aitestrebort/project/${projectId}/testcase`
  }
  return '/aitestrebort/project'
})

// 返回方法
const goBack = () => {
  router.push(backPath.value)
}

// 响应式数据
const ragLoading = ref(false)
const conversationLoading = ref(false)
const knowledgeBases = ref<Array<{
  id: string
  name: string
  description: string
  document_count: number
  created_at: string
}>>([])

const ragForm = reactive<RAGQueryRequest>({
  question: '',
  knowledge_base_id: '',
  use_knowledge_base: true,
  similarity_threshold: 0.7,
  top_k: 5,
  prompt_template: 'default',  // 默认使用通用模式
  thread_id: undefined
})

const ragResult = ref<RAGQueryResponse | null>(null)
const conversationHistory = ref<Array<{
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
}>>([])

const conversationInput = ref('')

// 统计数据
const todayQueries = ref(0)
const avgResponseTime = ref(0)
const successRate = ref(0)

// 方法
const loadKnowledgeBases = async () => {
  try {
    const response = await advancedFeaturesApi.langGraph.getProjectKnowledgeBases(projectId)
    if (response.data) {
      knowledgeBases.value = response.data
      if (knowledgeBases.value.length > 0) {
        ragForm.knowledge_base_id = knowledgeBases.value[0].id
      }
    }
  } catch (error) {
    console.error('加载知识库失败:', error)
    ElMessage.error('加载知识库失败')
  }
}

const executeRAGQuery = async () => {
  if (!ragForm.question.trim()) {
    ElMessage.warning('请输入查询问题')
    return
  }

  if (!ragForm.knowledge_base_id) {
    ElMessage.warning('请选择知识库')
    return
  }

  ragLoading.value = true
  try {
    const response = await advancedFeaturesApi.langGraph.ragQuery(projectId, ragForm)
    if (response.data) {
      ragResult.value = response.data
      
      // 添加到对话历史
      conversationHistory.value.push({
        type: 'user',
        content: ragForm.question,
        timestamp: new Date()
      })
      
      if (response.data.answer) {
        conversationHistory.value.push({
          type: 'assistant',
          content: response.data.answer,
          timestamp: new Date()
        })
      }

      ElMessage.success('查询完成')
    }
  } catch (error) {
    console.error('RAG查询失败:', error)
    ElMessage.error('查询失败，请重试')
  } finally {
    ragLoading.value = false
  }
}

const sendMessage = async () => {
  if (!conversationInput.value.trim()) {
    return
  }

  const message = conversationInput.value
  conversationInput.value = ''

  // 使用当前输入作为新的查询
  ragForm.question = message
  await executeRAGQuery()
}

const clearConversation = () => {
  conversationHistory.value = []
  ragResult.value = null
  ElMessage.success('对话历史已清空')
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString()
}

// Markdown 格式化函数
// Markdown 格式化函数 - 使用 marked 库进行标准 Markdown 渲染
const formatMarkdown = (text: string) => {
  if (!text) return ''
  
  try {
    // 使用 marked 进行标准 Markdown 渲染
    return marked.parse(text) as string
  } catch (error) {
    console.error('Markdown 渲染失败:', error)
    // 降级：返回纯文本（转义 HTML）
    return text.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>')
  }
}

// 生命周期
onMounted(() => {
  loadKnowledgeBases()
  
  // 模拟统计数据
  todayQueries.value = Math.floor(Math.random() * 100) + 50
  avgResponseTime.value = Math.floor(Math.random() * 1000) + 500
  successRate.value = Math.floor(Math.random() * 20) + 80
})
</script>

<style scoped>
.langgraph-orchestration {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  align-items: center;
}

.page-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #606266;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rag-query-card,
.conversation-card {
  height: 700px;
  display: flex;
  flex-direction: column;
}

.rag-query-card :deep(.el-card__body),
.conversation-card :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.rag-query-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.query-form {
  flex-shrink: 0;
}

.rag-result-scroll {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
  margin-top: 10px;
}

.rag-result-scroll::-webkit-scrollbar {
  width: 6px;
}

.rag-result-scroll::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.rag-result-scroll::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}

.answer-section {
  margin-bottom: 20px;
}

.answer-section h4 {
  margin: 0 0 10px 0;
  color: #409EFF;
  font-size: 14px;
}

.answer-content {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  line-height: 1.8;
  word-wrap: break-word;
  max-height: none;
  overflow: visible;
}

/* Markdown 标准样式 */
.answer-content :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  margin: 16px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #eaecef;
  color: #303133;
}

.answer-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 14px 0 10px 0;
  padding-bottom: 6px;
  border-bottom: 1px solid #eaecef;
  color: #303133;
}

.answer-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  margin: 12px 0 8px 0;
  color: #303133;
}

.answer-content :deep(h4) {
  font-size: 16px;
  font-weight: 600;
  margin: 10px 0 6px 0;
  color: #303133;
}

.answer-content :deep(p) {
  margin: 8px 0;
  line-height: 1.8;
}

.answer-content :deep(strong) {
  font-weight: 600;
  color: #409eff;
}

.answer-content :deep(em) {
  font-style: italic;
  color: #606266;
}

.answer-content :deep(code) {
  padding: 2px 6px;
  background: #f0f0f0;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  color: #e83e8c;
}

.answer-content :deep(pre) {
  padding: 12px;
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
}

.answer-content :deep(pre code) {
  padding: 0;
  background: transparent;
  border: none;
  color: #24292e;
  font-size: 13px;
  line-height: 1.5;
}

.answer-content :deep(ul),
.answer-content :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

.answer-content :deep(li) {
  margin: 4px 0;
  line-height: 1.6;
}

.answer-content :deep(blockquote) {
  margin: 12px 0;
  padding: 8px 16px;
  border-left: 4px solid #dfe2e5;
  background: #f9f9f9;
  color: #6a737d;
}

.answer-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
  display: block;
  overflow-x: auto;
}

.answer-content :deep(table th),
.answer-content :deep(table td) {
  border: 1px solid #dfe2e5;
  padding: 8px 12px;
  text-align: left;
}

.answer-content :deep(table th) {
  background: #f6f8fa;
  font-weight: 600;
}

.answer-content :deep(table tr:nth-child(even)) {
  background: #f9f9f9;
}

.answer-content :deep(hr) {
  border: none;
  border-top: 2px solid #eaecef;
  margin: 16px 0;
}

.answer-content :deep(a) {
  color: #0366d6;
  text-decoration: none;
}

.answer-content :deep(a:hover) {
  text-decoration: underline;
}

.context-section {
  margin-bottom: 20px;
}

.context-section h4 {
  margin: 0 0 10px 0;
  color: #67C23A;
}

.context-content {
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 10px;
  line-height: 1.6;
  word-wrap: break-word;
  max-height: none;
  overflow: visible;
}

/* Context 区域的 Markdown 样式（简化版） */
.context-content :deep(strong) {
  font-weight: 600;
  color: #303133;
}

.context-content :deep(code) {
  padding: 2px 4px;
  background: #f0f0f0;
  border: 1px solid #e0e0e0;
  border-radius: 2px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
}

.context-content :deep(pre) {
  padding: 8px;
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 4px;
  overflow-x: auto;
  margin: 8px 0;
}

.context-content :deep(ul),
.context-content :deep(ol) {
  margin: 6px 0;
  padding-left: 20px;
}

.context-content :deep(li) {
  margin: 2px 0;
}

.context-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 12px;
}

.context-content :deep(table th),
.context-content :deep(table td) {
  border: 1px solid #dfe2e5;
  padding: 6px 8px;
}

.context-content :deep(table th) {
  background: #f6f8fa;
  font-weight: 600;
}

.context-metadata {
  margin-top: 10px;
}

.timing-info {
  display: flex;
  gap: 10px;
}

.conversation-history {
  height: 450px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

.message {
  margin-bottom: 15px;
  padding: 12px;
  border-radius: 8px;
  word-wrap: break-word;
}

.message.user {
  background-color: #e3f2fd;
  margin-left: 20px;
}

.message.assistant {
  background-color: #f3e5f5;
  margin-right: 20px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: #909399;
}

.message-type {
  font-weight: 600;
}

.message-content {
  line-height: 1.6;
  word-wrap: break-word;
}

/* 对话消息的 Markdown 样式 */
.message-content :deep(h1),
.message-content :deep(h2),
.message-content :deep(h3),
.message-content :deep(h4) {
  margin: 8px 0 6px 0;
  font-weight: 600;
}

.message-content :deep(h1) { font-size: 20px; }
.message-content :deep(h2) { font-size: 18px; }
.message-content :deep(h3) { font-size: 16px; }
.message-content :deep(h4) { font-size: 14px; }

.message-content :deep(p) {
  margin: 6px 0;
}

.message-content :deep(strong) {
  font-weight: 600;
  color: #409eff;
}

.message-content :deep(code) {
  padding: 2px 4px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
}

.message-content :deep(pre) {
  padding: 10px;
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 4px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-content :deep(pre code) {
  padding: 0;
  background: transparent;
  border: none;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  margin: 6px 0;
  padding-left: 20px;
}

.message-content :deep(li) {
  margin: 3px 0;
}

.message-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 13px;
}

.message-content :deep(table th),
.message-content :deep(table td) {
  border: 1px solid #dfe2e5;
  padding: 6px 10px;
}

.message-content :deep(table th) {
  background: #f6f8fa;
  font-weight: 600;
}

.message-content :deep(blockquote) {
  margin: 8px 0;
  padding: 6px 12px;
  border-left: 3px solid #dfe2e5;
  background: rgba(0, 0, 0, 0.02);
  color: #6a737d;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 12px;
  color: #909399;
}

.message-type {
  font-weight: bold;
}

.message-content {
  line-height: 1.5;
}

.conversation-input {
  position: sticky;
  bottom: 0;
  background: white;
}
</style>