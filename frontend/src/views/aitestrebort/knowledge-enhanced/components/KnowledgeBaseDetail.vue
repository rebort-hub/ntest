<template>
  <div class="knowledge-detail">
    <!-- 知识库信息 -->
    <div class="kb-info-section">
      <h3>基本信息</h3>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="知识库名称">{{ knowledgeBase.name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="knowledgeBase.is_active ? 'success' : 'danger'">
            {{ knowledgeBase.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ knowledgeBase.description || '暂无描述' }}</el-descriptions-item>
        <el-descriptions-item label="分块大小">{{ knowledgeBase.chunk_size }}</el-descriptions-item>
        <el-descriptions-item label="分块重叠">{{ knowledgeBase.chunk_overlap }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(knowledgeBase.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(knowledgeBase.updated_at) }}</el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 统计信息 -->
    <div class="stats-section">
      <h3>统计信息</h3>
      <el-row :gutter="16">
        <el-col :span="6">
          <el-statistic title="文档总数" :value="statistics.document_count" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="已处理" :value="statistics.processed_count" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="分块总数" :value="statistics.chunk_count" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="处理进度" :value="processingProgress" suffix="%" />
        </el-col>
      </el-row>
    </div>

    <!-- 操作按钮 -->
    <div class="actions-section">
      <el-button type="primary" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon>
        上传文档
      </el-button>
      <el-button @click="showQueryDialog = true">
        <el-icon><Search /></el-icon>
        RAG查询
      </el-button>
      <el-button @click="loadDocuments">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 文档列表 -->
    <div class="documents-section">
      <div class="section-header">
        <h3>文档列表</h3>
        <div class="filters">
          <el-select v-model="documentFilter.status" placeholder="状态" clearable @change="loadDocuments">
            <el-option label="全部" value="" />
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
          <el-select v-model="documentFilter.document_type" placeholder="类型" clearable @change="loadDocuments">
            <el-option label="全部" value="" />
            <el-option label="PDF" value="pdf" />
            <el-option label="Word" value="docx" />
            <el-option label="PowerPoint" value="pptx" />
            <el-option label="文本" value="txt" />
            <el-option label="Markdown" value="md" />
            <el-option label="HTML" value="html" />
          </el-select>
        </div>
      </div>

      <el-table :data="documents" v-loading="documentsLoading">
        <el-table-column prop="title" label="文档名称" min-width="200" />
        <el-table-column prop="document_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ row.document_type.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.status)"
              size="small"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="文件大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="chunk_count" label="分块数" width="80" />
        <el-table-column prop="uploaded_at" label="上传时间" width="150">
          <template #default="{ row }">
            {{ formatTime(row.uploaded_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDocument(row)">查看</el-button>
            <el-button size="small" @click="viewChunks(row)">分块</el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteDocument(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadDocuments"
          @current-change="loadDocuments"
        />
      </div>
    </div>

    <!-- 上传文档对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传文档" width="500px">
      <DocumentUpload
        :project-id="projectId"
        :knowledge-base-id="knowledgeBase.id"
        @success="handleUploadSuccess"
        @close="showUploadDialog = false"
      />
    </el-dialog>

    <!-- RAG查询对话框 -->
    <el-dialog v-model="showQueryDialog" title="RAG查询" width="800px">
      <RAGQuery
        :project-id="projectId"
        :knowledge-base="knowledgeBase"
        @close="showQueryDialog = false"
      />
    </el-dialog>

    <!-- 文档详情对话框 -->
    <el-dialog v-model="showDocumentDialog" title="文档详情" width="800px">
      <DocumentDetail
        v-if="selectedDocument"
        :project-id="projectId"
        :knowledge-base-id="knowledgeBase.id"
        :document="selectedDocument"
        @close="showDocumentDialog = false"
      />
    </el-dialog>

    <!-- 分块查看对话框 -->
    <el-dialog v-model="showChunksDialog" title="文档分块" width="900px">
      <DocumentChunks
        v-if="selectedDocument"
        :project-id="projectId"
        :knowledge-base-id="knowledgeBase.id"
        :document="selectedDocument"
        @close="showChunksDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Search, Refresh } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type KnowledgeBase, type Document } from '@/api/aitestrebort/knowledge-enhanced'
import DocumentUpload from './DocumentUpload.vue'
import RAGQuery from './RAGQuery.vue'
import DocumentDetail from './DocumentDetail.vue'
import DocumentChunks from './DocumentChunks.vue'

interface Props {
  knowledgeBase: KnowledgeBase
  projectId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  refresh: []
}>()

// 响应式数据
const documents = ref<Document[]>([])
const documentsLoading = ref(false)
const statistics = ref({
  document_count: 0,
  processed_count: 0,
  chunk_count: 0
})

// 文档过滤
const documentFilter = reactive({
  status: '',
  document_type: '',
  search: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 对话框状态
const showUploadDialog = ref(false)
const showQueryDialog = ref(false)
const showDocumentDialog = ref(false)
const showChunksDialog = ref(false)

// 选中的文档
const selectedDocument = ref<Document | null>(null)

// 计算处理进度
const processingProgress = computed(() => {
  if (statistics.value.document_count === 0) return 0
  return Math.round((statistics.value.processed_count / statistics.value.document_count) * 100)
})

// 加载统计信息
const loadStatistics = async () => {
  try {
    const response = await knowledgeEnhancedApi.knowledgeBase.getKnowledgeBaseStatistics(
      props.projectId,
      props.knowledgeBase.id
    )
    
    if (response.data) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

// 加载文档列表
const loadDocuments = async () => {
  try {
    documentsLoading.value = true
    
    const params = {
      ...documentFilter,
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    const response = await knowledgeEnhancedApi.document.getDocuments(
      props.projectId,
      props.knowledgeBase.id,
      params
    )
    
    if (response.data) {
      documents.value = response.data.documents
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('Failed to load documents:', error)
    ElMessage.error('加载文档列表失败')
  } finally {
    documentsLoading.value = false
  }
}

// 查看文档
const viewDocument = (document: Document) => {
  selectedDocument.value = document
  showDocumentDialog.value = true
}

// 查看分块
const viewChunks = (document: Document) => {
  selectedDocument.value = document
  showChunksDialog.value = true
}

// 删除文档
const deleteDocument = async (document: Document) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${document.title}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await knowledgeEnhancedApi.document.deleteDocument(
      props.projectId,
      props.knowledgeBase.id,
      document.id
    )
    
    ElMessage.success('文档删除成功')
    await loadDocuments()
    await loadStatistics()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete document:', error)
      ElMessage.error('删除文档失败')
    }
  }
}

// 上传成功处理
const handleUploadSuccess = () => {
  showUploadDialog.value = false
  loadDocuments()
  loadStatistics()
  emit('refresh')
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

// 格式化文件大小
const formatFileSize = (size?: number) => {
  if (!size) return '-'
  
  const units = ['B', 'KB', 'MB', 'GB']
  let index = 0
  let fileSize = size
  
  while (fileSize >= 1024 && index < units.length - 1) {
    fileSize /= 1024
    index++
  }
  
  return `${fileSize.toFixed(1)} ${units[index]}`
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

// 初始化
onMounted(() => {
  loadStatistics()
  loadDocuments()
})
</script>

<style scoped>
.knowledge-detail {
  padding: 20px;
}

.kb-info-section,
.stats-section,
.actions-section,
.documents-section {
  margin-bottom: 30px;
}

.kb-info-section h3,
.stats-section h3,
.documents-section h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.actions-section {
  display: flex;
  gap: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.filters {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}
</style>