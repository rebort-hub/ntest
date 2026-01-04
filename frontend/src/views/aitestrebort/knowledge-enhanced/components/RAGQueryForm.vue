<template>
  <div class="rag-query-form">
    <!-- 查询输入 -->
    <div class="query-input-section">
      <el-form :model="queryForm" label-width="80px">
        <el-form-item label="查询内容">
          <el-input
            v-model="queryForm.query"
            type="textarea"
            :rows="4"
            placeholder="请输入您要查询的问题..."
            @keydown.ctrl.enter="handleQuery"
          />
        </el-form-item>
        
        <el-form-item label="返回数量">
          <el-input-number
            v-model="queryForm.top_k"
            :min="1"
            :max="20"
            :step="1"
          />
        </el-form-item>
        
        <el-form-item label="包含元数据">
          <el-switch v-model="queryForm.include_metadata" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleQuery" :loading="querying">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="clearQuery">清空</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 查询结果 -->
    <div v-if="queryResult" class="query-result-section">
      <div class="result-header">
        <h4>查询结果</h4>
        <div class="result-stats">
          <el-tag size="small">找到 {{ queryResult.total_results }} 个相关片段</el-tag>
          <el-tag size="small" type="info">耗时 {{ queryResult.retrieval_time }}s</el-tag>
        </div>
      </div>

      <div class="result-list">
        <div
          v-for="(result, index) in queryResult.results"
          :key="index"
          class="result-item"
        >
          <div class="result-header-item">
            <span class="result-index">#{{ index + 1 }}</span>
            <span class="result-source">{{ result.metadata.document_title }}</span>
            <el-tag size="small" type="success">
              相似度: {{ (result.metadata.score * 100).toFixed(1) }}%
            </el-tag>
          </div>
          
          <div class="result-content">
            <p>{{ result.content }}</p>
          </div>
          
          <div v-if="queryForm.include_metadata" class="result-metadata">
            <el-descriptions :column="3" size="small" border>
              <el-descriptions-item label="文档">{{ result.metadata.document_title }}</el-descriptions-item>
              <el-descriptions-item label="分块索引">{{ result.metadata.chunk_index }}</el-descriptions-item>
              <el-descriptions-item label="相似度分数">{{ result.metadata.score.toFixed(4) }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </div>
    </div>

    <!-- 查询历史 -->
    <div class="query-history-section">
      <div class="history-header">
        <h4>查询历史</h4>
        <el-button size="small" @click="loadQueryLogs">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <el-table :data="queryLogs" size="small" max-height="300">
        <el-table-column prop="query" label="查询内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="total_results" label="结果数" width="80" />
        <el-table-column prop="retrieval_time" label="耗时(s)" width="80">
          <template #default="{ row }">
            {{ row.retrieval_time?.toFixed(3) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="查询时间" width="150">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" @click="replayQuery(row)">重放</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 操作按钮 -->
    <div class="form-actions">
      <el-button @click="$emit('close')">关闭</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type KnowledgeBase, type QueryResponse, type QueryLog } from '@/api/aitestrebort/knowledge-enhanced'

interface Props {
  knowledgeBase: KnowledgeBase
  projectId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

// 响应式数据
const querying = ref(false)
const queryResult = ref<QueryResponse | null>(null)
const queryLogs = ref<QueryLog[]>([])

// 查询表单
const queryForm = reactive({
  query: '',
  top_k: 5,
  include_metadata: true
})

// 执行查询
const handleQuery = async () => {
  if (!queryForm.query.trim()) {
    ElMessage.warning('请输入查询内容')
    return
  }

  try {
    querying.value = true
    
    const response = await knowledgeEnhancedApi.rag.queryKnowledgeBase(
      props.projectId,
      props.knowledgeBase.id,
      {
        query: queryForm.query,
        top_k: queryForm.top_k,
        include_metadata: queryForm.include_metadata
      }
    )
    
    if (response.data) {
      queryResult.value = response.data
      ElMessage.success('查询完成')
      
      // 刷新查询历史
      await loadQueryLogs()
    }
    
  } catch (error) {
    console.error('Query failed:', error)
    ElMessage.error('查询失败')
  } finally {
    querying.value = false
  }
}

// 清空查询
const clearQuery = () => {
  queryForm.query = ''
  queryResult.value = null
}

// 加载查询历史
const loadQueryLogs = async () => {
  try {
    const response = await knowledgeEnhancedApi.rag.getQueryLogs(
      props.projectId,
      props.knowledgeBase.id,
      {
        page: 1,
        page_size: 10
      }
    )
    
    if (response.data?.query_logs) {
      queryLogs.value = response.data.query_logs
    }
  } catch (error) {
    console.error('Failed to load query logs:', error)
  }
}

// 重放查询
const replayQuery = (log: QueryLog) => {
  queryForm.query = log.query
  handleQuery()
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

// 初始化
onMounted(() => {
  loadQueryLogs()
})
</script>

<style scoped>
.rag-query-form {
  padding: 20px;
}

.query-input-section,
.query-result-section,
.query-history-section {
  margin-bottom: 30px;
}

.query-input-section {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.result-header h4 {
  margin: 0;
  color: #303133;
}

.result-stats {
  display: flex;
  gap: 10px;
}

.result-list {
  max-height: 400px;
  overflow-y: auto;
}

.result-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
}

.result-header-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.result-index {
  font-weight: 600;
  color: #409eff;
}

.result-source {
  font-size: 14px;
  color: #606266;
}

.result-content {
  margin-bottom: 10px;
}

.result-content p {
  margin: 0;
  line-height: 1.6;
  color: #303133;
}

.result-metadata {
  margin-top: 10px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.history-header h4 {
  margin: 0;
  color: #303133;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}
</style>