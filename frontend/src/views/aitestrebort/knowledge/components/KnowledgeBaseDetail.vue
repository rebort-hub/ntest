<template>
  <div class="knowledge-base-detail">
    <div class="detail-header">
      <div class="header-left">
        <el-button @click="$emit('close')" style="margin-right: 12px;">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <h3>{{ knowledgeBase.name }}</h3>
      </div>
      <el-button type="text" @click="$emit('close')">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>

    <div class="detail-content">
      <!-- 功能标签页 -->
      <el-tabs v-model="activeTab" class="detail-tabs">
        <!-- 基本信息标签页 -->
        <el-tab-pane label="知识库基本信息" name="info">
          <!-- 基本信息和配置信息 - 两列布局 -->
          <div class="info-grid">
            <!-- 基本信息 -->
            <div class="info-section">
              <h4>基本信息</h4>
              <div class="info-item">
                <span class="label">描述:</span>
                <span class="value">{{ knowledgeBase.description || '暂无描述' }}</span>
              </div>
              <div class="info-item">
                <span class="label">状态:</span>
                <el-tag :type="knowledgeBase.is_active ? 'success' : 'danger'" size="small">
                  {{ knowledgeBase.is_active ? '启用' : '禁用' }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="label">创建时间:</span>
                <span class="value">{{ formatDate(knowledgeBase.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="label">更新时间:</span>
                <span class="value">{{ formatDate(knowledgeBase.updated_at) }}</span>
              </div>
            </div>

            <!-- 配置信息 -->
            <div class="info-section">
              <h4>配置信息</h4>
              <div class="info-item">
                <span class="label">分块大小:</span>
                <span class="value">{{ knowledgeBase.chunk_size }}</span>
              </div>
              <div class="info-item">
                <span class="label">分块重叠:</span>
                <span class="value">{{ knowledgeBase.chunk_overlap }}</span>
              </div>
            </div>
          </div>

          <!-- 统计信息 -->
          <div class="info-section">
            <h4>统计信息</h4>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value">{{ knowledgeBase.document_count || 0 }}</div>
                <div class="stat-label">文档数量</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ knowledgeBase.processed_count || 0 }}</div>
                <div class="stat-label">已处理</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ knowledgeBase.chunk_count || 0 }}</div>
                <div class="stat-label">分块总数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ processingProgress }}%</div>
                <div class="stat-label">处理进度</div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 文档管理标签页 -->
        <el-tab-pane label="知识库文档管理" name="documents">
          <div class="section-header">
            <h4>文档管理</h4>
            <div class="header-actions">
              <el-button type="default" size="small" @click="fetchDocuments" :loading="documentsLoading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
              <el-button type="primary" size="small" @click="showUploadModal">
                <el-icon><Upload /></el-icon>
                上传文档
              </el-button>
            </div>
          </div>

          <div class="documents-list">
            <el-table
              :data="documents"
              :loading="documentsLoading"
              size="small"
              max-height="200"
            >
              <el-table-column prop="title" label="文档名称" min-width="120">
                <template #default="{ row }">
                  <el-link @click="viewDocument(row.id)" :underline="false" class="document-title-link">
                    {{ row.title }}
                  </el-link>
                </template>
              </el-table-column>
              <el-table-column prop="document_type" label="类型" width="60" />
              <el-table-column prop="status" label="状态" width="80" align="center">
                <template #default="{ row }">
                  <div class="status-cell">
                    <el-tag :type="getStatusType(row.status)" size="small">
                      {{ getStatusText(row.status) }}
                    </el-tag>
                    <el-tooltip v-if="row.status === 'failed' && row.error_message" :content="row.error_message">
                      <el-icon style="color: #f56c6c; margin-left: 4px; cursor: help;"><Warning /></el-icon>
                    </el-tooltip>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="chunk_count" label="分块数" width="70" align="center">
                <template #default="{ row }">
                  {{ row.chunk_count || 0 }}
                </template>
              </el-table-column>
              <el-table-column prop="uploader_name" label="上传者" width="80" />
              <el-table-column prop="uploaded_at" label="上传时间" width="100">
                <template #default="{ row }">
                  {{ formatDate(row.uploaded_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right" align="center">
                <template #default="{ row }">
                  <el-button type="text" size="small" @click="viewDocument(row.id)">查看</el-button>
                  <el-button v-if="row.status === 'failed'" type="text" size="small" @click="reprocessDocument(row.id)">重试</el-button>
                  <el-button type="text" size="small" @click="deleteDocument(row.id)" style="color: #f56c6c;">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 查询测试标签页 -->
        <el-tab-pane label="知识库RAG查询测试" name="query">
          <div class="query-section">
            <h4>查询测试</h4>
            <div class="query-form">
              <el-input
                v-model="queryText"
                type="textarea"
                :rows="3"
                placeholder="输入查询内容..."
                style="margin-bottom: 12px"
              />

          <!-- 查询参数设置 -->
          <div class="query-settings">
            <div class="setting-item">
              <label>相似度阈值:</label>
              <el-slider
                v-model="similarityThreshold"
                :min="0.1"
                :max="1.0"
                :step="0.1"
                :show-tooltip="true"
                style="width: 120px;"
              />
              <span class="value-display">{{ similarityThreshold }}</span>
            </div>

            <div class="setting-item">
              <label>检索数量:</label>
              <el-input-number
                v-model="topK"
                :min="1"
                :max="20"
                :step="1"
                size="small"
                style="width: 80px;"
              />
            </div>
          </div>

          <el-button
            type="primary"
            :loading="queryLoading"
            @click="testQuery"
            style="width: 100%"
          >
            测试查询
          </el-button>
        </div>

        <div v-if="queryResult" class="query-result">
          <h5>查询结果</h5>
          <div class="result-content">
            <div class="query-info">
              <strong>查询内容:</strong>
              <p>{{ queryResult.query }}</p>
            </div>
            <div class="answer" v-if="queryResult.answer">
              <strong>回答:</strong>
              <p>{{ queryResult.answer }}</p>
            </div>
            <div class="sources">
              <strong>相关内容 ({{ queryResult.sources.length }} 条结果):</strong>
              <div
                v-for="(source, index) in queryResult.sources"
                :key="index"
                class="source-item"
              >
                <div class="source-content">{{ source.content }}</div>
                <div class="source-meta">
                  <span>文档: {{ source.metadata.document_title || source.metadata.title || source.metadata.source }}</span> |
                  <span>相似度: {{ ((source.score || source.similarity_score || 0) * 100).toFixed(1) }}%</span>
                  <span v-if="source.metadata.page_number"> | 页码: {{ source.metadata.page_number }}</span>
                </div>
              </div>
            </div>
            <div class="timing">
              <small>
                检索时间: {{ queryResult.retrieval_time?.toFixed(2) || 0 }}s |
                生成时间: {{ queryResult.generation_time?.toFixed(2) || 0 }}s |
                总时间: {{ queryResult.total_time?.toFixed(2) || 0 }}s
              </small>
            </div>
          </div>
        </div>
          </div>
        </el-tab-pane>

        <!-- 测试用例生成标签页 -->
        <el-tab-pane label="基于知识库测试用例生成" name="testcase">
          <TestCaseGenerator
            :knowledge-base="knowledgeBase"
            :project-id="projectId"
          />
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 上传文档对话框 -->
    <DocumentUploadAdvanced
      v-model="isUploadModalVisible"
      :knowledge-base-id="knowledgeBase.id"
      :project-id="projectId"
      @success="handleDocumentUploaded"
    />

    <!-- 文档详情对话框 -->
    <DocumentDetailModal
      v-model="isDocumentDetailVisible"
      :document-id="selectedDocumentId"
      :project-id="projectId"
      :knowledge-base-id="knowledgeBase.id"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close, Refresh, Upload, Warning, ArrowLeft } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type KnowledgeBase } from '@/api/aitestrebort/knowledge-enhanced'
import DocumentUploadAdvanced from './DocumentUploadAdvanced.vue'
import DocumentDetailModal from './DocumentDetailModal.vue'
import TestCaseGenerator from './TestCaseGenerator.vue'

interface Props {
  knowledgeBase: KnowledgeBase
  projectId: number
}

interface Document {
  id: string
  title: string
  document_type: string
  status: string
  error_message?: string
  chunk_count?: number
  uploader_name?: string
  uploaded_at: string
}

interface QueryResponse {
  query: string
  answer?: string
  sources: Array<{
    content: string
    metadata: any
    similarity_score: number
  }>
  retrieval_time?: number
  generation_time?: number
  total_time?: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  refresh: []
  close: []
}>()

// 响应式数据
const activeTab = ref('info')
const documents = ref<Document[]>([])
const documentsLoading = ref(false)
const queryText = ref('')
const queryLoading = ref(false)
const queryResult = ref<QueryResponse | null>(null)
const similarityThreshold = ref(0.3)
const topK = ref(3)
const isUploadModalVisible = ref(false)
const isDocumentDetailVisible = ref(false)
const selectedDocumentId = ref<string | null>(null)

// 计算处理进度
const processingProgress = computed(() => {
  const total = props.knowledgeBase.document_count || 0
  const processed = props.knowledgeBase.processed_count || 0
  if (total === 0) return 0
  return Math.round((processed / total) * 100)
})

// 方法
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    processing: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

const fetchDocuments = async () => {
  documentsLoading.value = true
  try {
    const response = await knowledgeEnhancedApi.document.getDocuments(
      props.projectId,
      props.knowledgeBase.id
    )
    
    if (response.data) {
      documents.value = response.data.documents || response.data || []
    }
  } catch (error) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败')
  } finally {
    documentsLoading.value = false
  }
}

const reprocessDocument = async (documentId: string) => {
  try {
    await knowledgeEnhancedApi.document.reprocessDocument(
      props.projectId,
      props.knowledgeBase.id,
      documentId
    )
    ElMessage.success('文档重新处理已开始')
    await fetchDocuments()
  } catch (error) {
    console.error('重新处理文档失败:', error)
    ElMessage.error('重新处理文档失败')
  }
}

const deleteDocument = async (documentId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？', '确认删除', {
      type: 'warning'
    })
    
    await knowledgeEnhancedApi.document.deleteDocument(
      props.projectId,
      props.knowledgeBase.id,
      documentId
    )
    
    // 响应拦截器会显示成功消息
    await fetchDocuments()
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
      // 响应拦截器会显示错误消息
    }
  }
}

const testQuery = async () => {
  if (!queryText.value.trim()) {
    ElMessage.warning('请输入查询内容')
    return
  }

  queryLoading.value = true
  try {
    const response = await knowledgeEnhancedApi.rag.queryKnowledgeBase(
      props.projectId,
      props.knowledgeBase.id,
      {
        query: queryText.value,
        top_k: topK.value,
        score_threshold: similarityThreshold.value,
        use_rag: false  // 简单检索模式
      }
    )
    
    if (response.data) {
      queryResult.value = response.data
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败')
  } finally {
    queryLoading.value = false
  }
}

const showUploadModal = () => {
  isUploadModalVisible.value = true
}

const handleDocumentUploaded = () => {
  isUploadModalVisible.value = false  // 关闭上传弹窗
  fetchDocuments()
  emit('refresh')
  // 响应拦截器会显示成功消息
}

const viewDocument = (documentId: string) => {
  selectedDocumentId.value = documentId
  isDocumentDetailVisible.value = true
}

// 生命周期
onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.knowledge-base-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.detail-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
}

.detail-tabs {
  height: 100%;
}

.detail-tabs :deep(.el-tabs__content) {
  height: calc(100% - 55px);
  overflow-y: auto;
  padding: 16px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 24px;
}

.info-section {
  margin-bottom: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.info-section h4 {
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: bold;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
  align-items: center;
}

.label {
  width: 90px;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
  flex-shrink: 0;
  text-align: left;
}

.value {
  flex: 1;
  font-size: 13px;
  color: #303133;
  text-align: left;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

.documents-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.documents-list {
  max-height: 200px;
  overflow-y: auto;
}

.status-cell {
  display: flex;
  align-items: center;
}

.query-section {
  margin-bottom: 24px;
}

.query-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.query-settings {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-item label {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  min-width: 80px;
}

.value-display {
  font-size: 12px;
  color: #303133;
  font-weight: 500;
  min-width: 30px;
}

.query-result {
  margin-top: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.query-result h5 {
  margin: 0 0 12px 0;
  font-size: 12px;
  font-weight: bold;
}

.query-info {
  margin-bottom: 12px;
}

.query-info p {
  margin: 4px 0 0 0;
  font-size: 12px;
  line-height: 1.5;
}

.answer {
  margin-bottom: 12px;
}

.answer p {
  margin: 4px 0 0 0;
  font-size: 12px;
  line-height: 1.5;
}

.sources {
  margin-bottom: 12px;
}

.source-item {
  margin: 8px 0;
  padding: 8px;
  background: white;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.source-content {
  font-size: 12px;
  line-height: 1.4;
  margin-bottom: 4px;
}

.source-meta {
  font-size: 10px;
  color: #909399;
}

.timing {
  font-size: 10px;
  color: #c0c4cc;
  margin-top: 8px;
}

.document-title-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s;
}

.document-title-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}
</style>