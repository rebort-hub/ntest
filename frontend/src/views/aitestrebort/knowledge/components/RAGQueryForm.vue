<template>
  <div class="rag-query-form">
    <div class="query-header">
      <h4>{{ knowledgeBase.name }} - RAG查询测试</h4>
      <p class="query-description">
        基于知识库内容进行智能问答，系统会检索相关文档片段并生成回答。
      </p>
    </div>
    
    <!-- 查询输入 -->
    <div class="query-input-section">
      <el-form label-width="80px">
        <el-form-item label="查询内容">
          <el-input
            v-model="queryForm.query"
            type="textarea"
            :rows="4"
            placeholder="请输入您要查询的问题..."
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="返回数量">
              <el-input-number
                v-model="queryForm.top_k"
                :min="1"
                :max="20"
                :step="1"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="相似度阈值">
              <el-slider
                v-model="queryForm.similarity_threshold"
                :min="0.1"
                :max="1.0"
                :step="0.1"
                :show-tooltip="true"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="executeQuery" 
            :loading="querying"
            :disabled="!queryForm.query.trim()"
          >
            <el-icon><Search /></el-icon>
            执行查询
          </el-button>
          <el-button @click="clearQuery">清空</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 查询结果 -->
    <div v-if="queryResult" class="query-result-section">
      <el-divider content-position="left">查询结果</el-divider>
      
      <div class="result-content">
        <div class="query-info">
          <h5>查询内容</h5>
          <p class="query-text">{{ queryResult.query }}</p>
        </div>
        
        <div v-if="queryResult.answer" class="answer-section">
          <h5>智能回答</h5>
          <div class="answer-content">
            {{ queryResult.answer }}
          </div>
        </div>
        
        <div class="sources-section">
          <h5>相关内容 ({{ queryResult.results?.length || 0 }} 条结果)</h5>
          
          <div v-if="queryResult.results?.length" class="sources-list">
            <div
              v-for="(source, index) in queryResult.results"
              :key="index"
              class="source-item"
            >
              <div class="source-header">
                <span class="source-index">#{{ index + 1 }}</span>
                <span class="source-title">{{ source.metadata?.document_title || source.metadata?.title || '未知文档' }}</span>
                <el-tag size="small" type="success">
                  相似度: {{ (source.metadata?.score * 100 || 0).toFixed(1) }}%
                </el-tag>
              </div>
              <div class="source-content">
                {{ source.content }}
              </div>
              <div class="source-meta">
                <span v-if="source.metadata?.chunk_index !== undefined">
                  分块: {{ source.metadata.chunk_index }}
                </span>
                <span v-if="source.metadata?.page_number">
                  | 页码: {{ source.metadata.page_number }}
                </span>
              </div>
            </div>
          </div>
          
          <div v-else class="no-results">
            <el-empty description="未找到相关内容" />
          </div>
        </div>
        
        <div class="timing-info">
          <el-descriptions :column="3" size="small" border>
            <el-descriptions-item label="检索时间">
              {{ queryResult.retrieval_time?.toFixed(3) || 0 }}s
            </el-descriptions-item>
            <el-descriptions-item label="总时间">
              {{ queryResult.total_time?.toFixed(3) || 0 }}s
            </el-descriptions-item>
            <el-descriptions-item label="结果数量">
              {{ queryResult.total_results || 0 }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </div>

    <!-- 查询历史 -->
    <div v-if="queryHistory.length" class="query-history-section">
      <el-divider content-position="left">查询历史</el-divider>
      
      <div class="history-list">
        <div
          v-for="(history, index) in queryHistory"
          :key="index"
          class="history-item"
          @click="loadHistoryQuery(history)"
        >
          <div class="history-query">{{ history.query }}</div>
          <div class="history-meta">
            <span>{{ history.results?.length || 0 }} 条结果</span>
            <span>{{ history.total_time?.toFixed(2) || 0 }}s</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="form-actions">
      <el-button @click="$emit('close')">关闭</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type KnowledgeBase } from '@/api/aitestrebort/knowledge-enhanced'

interface Props {
  knowledgeBase: KnowledgeBase
  projectId: number
}

interface QueryResult {
  query: string
  results?: Array<{
    content: string
    metadata: any
  }>
  answer?: string
  retrieval_time?: number
  total_time?: number
  total_results?: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

// 响应式数据
const querying = ref(false)
const queryResult = ref<QueryResult | null>(null)
const queryHistory = ref<QueryResult[]>([])

// 查询表单
const queryForm = reactive({
  query: '',
  top_k: 5,
  similarity_threshold: 0.3
})

// 方法
const executeQuery = async () => {
  if (!queryForm.query.trim()) {
    ElMessage.warning('请输入查询内容')
    return
  }

  querying.value = true
  try {
    const response = await knowledgeEnhancedApi.rag.queryKnowledgeBase(
      props.projectId,
      props.knowledgeBase.id,
      {
        query: queryForm.query,
        top_k: queryForm.top_k,
        include_metadata: true
      }
    )
    
    if (response.data) {
      queryResult.value = response.data
      
      // 添加到历史记录
      queryHistory.value.unshift({
        ...response.data,
        query: queryForm.query
      })
      
      // 限制历史记录数量
      if (queryHistory.value.length > 10) {
        queryHistory.value = queryHistory.value.slice(0, 10)
      }
      
      ElMessage.success('查询完成')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败，请检查知识库状态')
  } finally {
    querying.value = false
  }
}

const clearQuery = () => {
  queryForm.query = ''
  queryResult.value = null
}

const loadHistoryQuery = (history: QueryResult) => {
  queryForm.query = history.query
  queryResult.value = history
}
</script>

<style scoped>
.rag-query-form {
  padding: 20px;
}

.query-header {
  margin-bottom: 24px;
}

.query-header h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.query-description {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.query-input-section {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.query-result-section {
  margin-bottom: 20px;
}

.result-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.query-info {
  margin-bottom: 20px;
}

.query-info h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.query-text {
  margin: 0;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #409eff;
  font-size: 13px;
  line-height: 1.5;
}

.answer-section {
  margin-bottom: 20px;
}

.answer-section h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.answer-content {
  padding: 12px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #67c23a;
  font-size: 13px;
  line-height: 1.6;
}

.sources-section {
  margin-bottom: 20px;
}

.sources-section h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.sources-list {
  space-y: 12px;
}

.source-item {
  margin-bottom: 12px;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.source-index {
  font-weight: 600;
  color: #409eff;
  font-size: 12px;
}

.source-title {
  flex: 1;
  margin: 0 12px;
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.source-content {
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
  margin-bottom: 8px;
}

.source-meta {
  font-size: 11px;
  color: #909399;
}

.no-results {
  text-align: center;
  padding: 40px;
}

.timing-info {
  margin-top: 16px;
}

.query-history-section {
  margin-bottom: 20px;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  margin-bottom: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background: #e6f7ff;
}

.history-query {
  font-size: 13px;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1.4;
}

.history-meta {
  font-size: 11px;
  color: #909399;
  display: flex;
  gap: 12px;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}
</style>