<template>
  <div class="document-detail">
    <!-- 文档基本信息 -->
    <div class="document-info">
      <el-descriptions title="文档信息" :column="2" border>
        <el-descriptions-item label="文档名称">{{ document.title }}</el-descriptions-item>
        <el-descriptions-item label="文档类型">
          <el-tag size="small">{{ document.document_type.toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处理状态">
          <el-tag :type="getStatusType(document.status)" size="small">
            {{ getStatusText(document.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="文件大小">{{ formatFileSize(document.file_size) }}</el-descriptions-item>
        <el-descriptions-item label="页数">{{ document.page_count || '-' }}</el-descriptions-item>
        <el-descriptions-item label="字数">{{ document.word_count || '-' }}</el-descriptions-item>
        <el-descriptions-item label="分块数">{{ document.chunk_count || '-' }}</el-descriptions-item>
        <el-descriptions-item label="上传时间">{{ formatTime(document.uploaded_at) }}</el-descriptions-item>
        <el-descriptions-item label="处理时间">{{ document.processed_at ? formatTime(document.processed_at) : '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <!-- 错误信息 -->
      <div v-if="document.error_message" class="error-message">
        <el-alert
          title="处理错误"
          type="error"
          :description="document.error_message"
          :closable="false"
        />
      </div>
    </div>

    <!-- 文档内容 -->
    <div class="document-content">
      <div class="content-header">
        <h4>文档内容</h4>
        <div class="content-actions">
          <el-button size="small" @click="loadContent" :loading="contentLoading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button size="small" @click="reprocessDocument" :loading="reprocessing">
            <el-icon><Refresh /></el-icon>
            重新处理
          </el-button>
        </div>
      </div>

      <div v-if="contentLoading" class="content-loading">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="documentContent" class="content-display">
        <el-input
          v-model="documentContent.content"
          type="textarea"
          :rows="15"
          readonly
          placeholder="文档内容将在这里显示..."
        />
        
        <!-- 分块信息 -->
        <div v-if="documentContent.chunks && documentContent.chunks.length > 0" class="chunks-info">
          <h5>文档分块 ({{ documentContent.chunks.length }} 个)</h5>
          <div class="chunks-list">
            <div
              v-for="(chunk, index) in documentContent.chunks"
              :key="chunk.id"
              class="chunk-item"
            >
              <div class="chunk-header">
                <span class="chunk-index">分块 #{{ chunk.chunk_index + 1 }}</span>
                <span class="chunk-info">
                  {{ chunk.content.length }} 字符
                  <span v-if="chunk.page_number">| 第 {{ chunk.page_number }} 页</span>
                </span>
              </div>
              <div class="chunk-content">
                {{ chunk.content.substring(0, 200) }}
                <span v-if="chunk.content.length > 200">...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="no-content">
        <el-empty description="暂无内容" />
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="form-actions">
      <el-button @click="$emit('close')">关闭</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type Document } from '@/api/aitestrebort/knowledge-enhanced'

interface Props {
  projectId: number
  knowledgeBaseId: string
  document: Document
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

// 响应式数据
const contentLoading = ref(false)
const reprocessing = ref(false)
const documentContent = ref<any>(null)

// 加载文档内容
const loadContent = async () => {
  try {
    contentLoading.value = true
    
    const response = await knowledgeEnhancedApi.document.getDocumentContent(
      props.projectId,
      props.knowledgeBaseId,
      props.document.id,
      {
        include_chunks: true,
        chunk_page: 1,
        chunk_page_size: 50
      }
    )
    
    if (response.data) {
      documentContent.value = response.data
    }
    
  } catch (error) {
    console.error('Failed to load document content:', error)
    ElMessage.error('加载文档内容失败')
  } finally {
    contentLoading.value = false
  }
}

// 重新处理文档
const reprocessDocument = async () => {
  try {
    reprocessing.value = true
    
    await knowledgeEnhancedApi.document.reprocessDocument(
      props.projectId,
      props.knowledgeBaseId,
      props.document.id
    )
    
    ElMessage.success('文档重新处理已开始')
    
  } catch (error) {
    console.error('Failed to reprocess document:', error)
    ElMessage.error('重新处理文档失败')
  } finally {
    reprocessing.value = false
  }
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
  loadContent()
})
</script>

<style scoped>
.document-detail {
  padding: 20px;
}

.document-info {
  margin-bottom: 30px;
}

.error-message {
  margin-top: 15px;
}

.document-content {
  margin-bottom: 30px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.content-header h4 {
  margin: 0;
  color: #303133;
}

.content-actions {
  display: flex;
  gap: 10px;
}

.content-loading {
  padding: 20px;
}

.content-display {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.chunks-info {
  padding: 20px;
  background: #f8f9fa;
  border-top: 1px solid #e4e7ed;
}

.chunks-info h5 {
  margin: 0 0 15px 0;
  color: #303133;
}

.chunks-list {
  max-height: 300px;
  overflow-y: auto;
}

.chunk-item {
  margin-bottom: 15px;
  padding: 10px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.chunk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.chunk-index {
  font-weight: 600;
  color: #409eff;
}

.chunk-info {
  font-size: 12px;
  color: #909399;
}

.chunk-content {
  font-size: 14px;
  line-height: 1.5;
  color: #606266;
}

.no-content {
  padding: 40px;
  text-align: center;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}
</style>