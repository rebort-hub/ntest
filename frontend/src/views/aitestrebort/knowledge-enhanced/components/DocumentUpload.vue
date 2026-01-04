<template>
  <div class="document-upload">
    <el-upload
      ref="uploadRef"
      class="upload-demo"
      drag
      :action="uploadUrl"
      :headers="uploadHeaders"
      :data="uploadData"
      :before-upload="beforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-progress="handleProgress"
      :file-list="fileList"
      multiple
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 PDF、Word、PowerPoint、文本、Markdown、HTML 文件，单个文件不超过 50MB
        </div>
      </template>
    </el-upload>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-progress">
      <el-progress :percentage="uploadProgress" :status="uploadStatus" />
      <p class="progress-text">{{ progressText }}</p>
    </div>

    <!-- 上传结果 -->
    <div v-if="uploadResults.length > 0" class="upload-results">
      <h4>上传结果</h4>
      <el-table :data="uploadResults" size="small">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'" size="small">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="说明" />
      </el-table>
    </div>

    <!-- 操作按钮 -->
    <div class="form-actions">
      <el-button @click="$emit('close')">关闭</el-button>
      <el-button type="primary" @click="clearResults" v-if="uploadResults.length > 0">
        清空结果
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadProps, UploadUserFile } from 'element-plus'

interface Props {
  projectId: number
  knowledgeBaseId: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  success: []
  close: []
}>()

// 响应式数据
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref<'success' | 'exception' | undefined>()
const progressText = ref('')
const fileList = ref<UploadUserFile[]>([])
const uploadResults = ref<Array<{
  filename: string
  success: boolean
  message: string
}>>([])

// 上传配置
const uploadUrl = computed(() => {
  return `/api/aitestrebort/knowledge/projects/${props.projectId}/knowledge-bases/${props.knowledgeBaseId}/documents`
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('access-token')
  return {
    'Authorization': `Bearer ${token}`
  }
})

const uploadData = computed(() => {
  return {
    project_id: props.projectId,
    knowledge_base_id: props.knowledgeBaseId
  }
})

// 上传前检查
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  // 检查文件类型
  const allowedTypes = ['pdf', 'docx', 'pptx', 'txt', 'md', 'html']
  const fileExtension = file.name.split('.').pop()?.toLowerCase()
  
  if (!fileExtension || !allowedTypes.includes(fileExtension)) {
    ElMessage.error(`不支持的文件类型: ${fileExtension}`)
    return false
  }
  
  // 检查文件大小 (50MB)
  const maxSize = 50 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  
  uploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = undefined
  progressText.value = `正在上传 ${file.name}...`
  
  return true
}

// 上传进度
const handleProgress: UploadProps['onProgress'] = (event) => {
  uploadProgress.value = Math.round(event.percent || 0)
  
  if (uploadProgress.value < 100) {
    progressText.value = `上传中... ${uploadProgress.value}%`
  } else {
    progressText.value = '处理中，请稍候...'
  }
}

// 上传成功
const handleSuccess: UploadProps['onSuccess'] = (response, file) => {
  uploading.value = false
  uploadStatus.value = 'success'
  progressText.value = '上传完成'
  
  uploadResults.value.push({
    filename: file.name,
    success: true,
    message: response.message || '上传成功'
  })
  
  ElMessage.success(`${file.name} 上传成功`)
  emit('success')
}

// 上传失败
const handleError: UploadProps['onError'] = (error, file) => {
  uploading.value = false
  uploadStatus.value = 'exception'
  progressText.value = '上传失败'
  
  let errorMessage = '上传失败'
  try {
    const errorData = JSON.parse(error.message)
    errorMessage = errorData.message || errorMessage
  } catch {
    // 忽略解析错误
  }
  
  uploadResults.value.push({
    filename: file.name,
    success: false,
    message: errorMessage
  })
  
  ElMessage.error(`${file.name} 上传失败: ${errorMessage}`)
}

// 清空结果
const clearResults = () => {
  uploadResults.value = []
  fileList.value = []
}
</script>

<style scoped>
.document-upload {
  padding: 20px;
}

.upload-demo {
  margin-bottom: 20px;
}

.upload-progress {
  margin: 20px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.progress-text {
  margin: 10px 0 0 0;
  text-align: center;
  color: #606266;
  font-size: 14px;
}

.upload-results {
  margin: 20px 0;
}

.upload-results h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}

.form-actions .el-button {
  margin-left: 10px;
}
</style>