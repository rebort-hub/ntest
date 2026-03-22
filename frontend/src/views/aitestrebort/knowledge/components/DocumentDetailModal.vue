<template>
  <el-dialog
    :model-value="modelValue"
    :title="document?.title || '文档详情'"
    width="80%"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>
    
    <div v-else-if="document" class="document-detail">
      <!-- 文档基本信息 -->
      <div class="document-info">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="文档名称">{{ document.title }}</el-descriptions-item>
          <el-descriptions-item label="文档类型">{{ getTypeLabel(document.document_type) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(document.status)" size="small">
              {{ getStatusText(document.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatFileSize(document.file_size) }}</el-descriptions-item>
          <el-descriptions-item label="页数">{{ document.page_count || '-' }}</el-descriptions-item>
          <el-descriptions-item label="字数">{{ document.word_count || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分块数">{{ document.chunk_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="上传者">{{ document.uploader_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="上传时间">{{ formatDate(document.uploaded_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 错误信息 -->
        <div v-if="document.status === 'failed' && document.error_message" class="error-info">
          <el-alert
            title="处理失败"
            type="error"
            :description="document.error_message"
            show-icon
            :closable="false"
          />
        </div>
      </div>
      
      <!-- 文档内容 -->
      <div v-if="document.status === 'completed'" class="document-content">
        <div class="content-header">
          <h4>文档内容</h4>
        </div>
        
        <!-- 原文内容 -->
        <div class="original-content">
          <el-input
            v-model="documentContent"
            type="textarea"
            :rows="15"
            readonly
            placeholder="正在加载文档内容..."
          />
        </div>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { knowledgeEnhancedApi } from '@/api/aitestrebort/knowledge-enhanced'

interface Props {
  modelValue: boolean
  documentId: string | null
  projectId: number
  knowledgeBaseId: string
}

interface Document {
  id: string
  title: string
  document_type: string
  status: string
  error_message?: string
  file_size?: number
  page_count?: number
  word_count?: number
  chunk_count?: number
  uploader_name?: string
  uploaded_at: string
  processed_at?: string
  content?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// 响应式数据
const loading = ref(false)
const document = ref<Document | null>(null)
const documentContent = ref('')

// 计算属性已移除

// 方法
const getTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    pdf: 'PDF文档',
    docx: 'Word文档',
    pptx: 'PowerPoint',
    txt: '文本文件',
    md: 'Markdown',
    html: 'HTML文件',
    url: '网页链接'
  }
  return typeMap[type] || type
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

const formatFileSize = (size?: number) => {
  if (!size) return '-'
  
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const fetchDocumentDetail = async () => {
  if (!props.documentId) return
  
  loading.value = true
  try {
    const response = await knowledgeEnhancedApi.document.getDocumentContent(
      props.projectId,
      props.knowledgeBaseId,
      props.documentId
    )
    
    if (response.data) {
      document.value = response.data
      documentContent.value = response.data.content || ''
    }
  } catch (error) {
    console.error('获取文档详情失败:', error)
    ElMessage.error('获取文档详情失败')
  } finally {
    loading.value = false
  }
}

// 监听文档ID变化
watch(() => props.documentId, (newId) => {
  if (newId && props.modelValue) {
    fetchDocumentDetail()
  }
}, { immediate: true })

// 监听对话框显示状态
watch(() => props.modelValue, (visible) => {
  if (visible && props.documentId) {
    fetchDocumentDetail()
  } else {
    // 重置数据
    document.value = null
    documentContent.value = ''
  }
})
</script>

<style scoped>
.loading-container {
  padding: 20px;
}

.document-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.document-info {
  margin-bottom: 20px;
}

.error-info {
  margin-top: 16px;
}

.document-content {
  margin-top: 20px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.content-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
}

.original-content {
  margin-bottom: 20px;
}
</style>