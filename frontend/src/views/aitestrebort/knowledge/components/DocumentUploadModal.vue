<template>
  <el-dialog
    :model-value="modelValue"
    title="上传文档"
    width="600px"
    @update:model-value="$emit('update:modelValue', $event)"
    @closed="resetForm"
  >
    <el-form
      ref="formRef"
      :model="uploadForm"
      :rules="formRules"
      label-width="100px"
    >
      <el-form-item label="文档标题" prop="title">
        <el-input v-model="uploadForm.title" placeholder="请输入文档标题" />
      </el-form-item>
      
      <el-form-item label="文档类型" prop="document_type">
        <el-select v-model="uploadForm.document_type" placeholder="选择文档类型" @change="handleTypeChange">
          <el-option label="PDF文档" value="pdf" />
          <el-option label="Word文档" value="docx" />
          <el-option label="PowerPoint" value="pptx" />
          <el-option label="文本文件" value="txt" />
          <el-option label="Markdown" value="md" />
          <el-option label="HTML文件" value="html" />
          <el-option label="网页链接" value="url" />
        </el-select>
      </el-form-item>
      
      <!-- 文件上传 -->
      <el-form-item v-if="uploadForm.document_type !== 'url'" label="选择文件" prop="file">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          :accept="getAcceptTypes()"
        >
          <el-button type="primary">选择文件</el-button>
          <template #tip>
            <div class="el-upload__tip">
              {{ getUploadTip() }}
            </div>
          </template>
        </el-upload>
      </el-form-item>
      
      <!-- URL输入 -->
      <el-form-item v-if="uploadForm.document_type === 'url'" label="网页链接" prop="url">
        <el-input v-model="uploadForm.url" placeholder="请输入网页链接" />
      </el-form-item>
      
      <!-- 文本内容输入 -->
      <el-form-item v-if="['txt', 'md'].includes(uploadForm.document_type)" label="文本内容" prop="content">
        <el-input
          v-model="uploadForm.content"
          type="textarea"
          :rows="6"
          placeholder="请输入文本内容（可选，如果不填写将从文件中读取）"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="uploading">
        上传
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { knowledgeEnhancedApi } from '@/api/aitestrebort/knowledge-enhanced'

interface Props {
  modelValue: boolean
  knowledgeBaseId: string
  projectId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

// 响应式数据
const uploading = ref(false)
const formRef = ref()
const uploadRef = ref()

const uploadForm = reactive({
  title: '',
  document_type: '',
  file: null as File | null,
  url: '',
  content: ''
})

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' }
  ],
  document_type: [
    { required: true, message: '请选择文档类型', trigger: 'change' }
  ],
  file: [
    { 
      validator: (rule: any, value: any, callback: any) => {
        if (uploadForm.document_type !== 'url' && !uploadForm.file && !uploadForm.content) {
          callback(new Error('请选择文件或输入内容'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ],
  url: [
    { 
      validator: (rule: any, value: any, callback: any) => {
        if (uploadForm.document_type === 'url' && !uploadForm.url) {
          callback(new Error('请输入网页链接'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 方法
const getAcceptTypes = () => {
  const typeMap: Record<string, string> = {
    pdf: '.pdf',
    docx: '.docx,.doc',
    pptx: '.pptx,.ppt',
    txt: '.txt',
    md: '.md',
    html: '.html,.htm'
  }
  return typeMap[uploadForm.document_type] || ''
}

const getUploadTip = () => {
  const tipMap: Record<string, string> = {
    pdf: '支持PDF格式文件',
    docx: '支持Word文档格式',
    pptx: '支持PowerPoint格式',
    txt: '支持纯文本文件',
    md: '支持Markdown格式文件',
    html: '支持HTML格式文件'
  }
  return tipMap[uploadForm.document_type] || '请选择文件'
}

const handleTypeChange = () => {
  // 清空文件和内容
  uploadForm.file = null
  uploadForm.url = ''
  uploadForm.content = ''
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
  // 自动设置标题
  if (!uploadForm.title && file.name) {
    uploadForm.title = file.name.replace(/\.[^/.]+$/, '')
  }
}

const handleFileRemove = () => {
  uploadForm.file = null
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    uploading.value = true
    
    // 创建FormData
    const formData = new FormData()
    formData.append('title', uploadForm.title)
    formData.append('document_type', uploadForm.document_type)
    
    if (uploadForm.document_type === 'url') {
      formData.append('url', uploadForm.url)
    } else {
      if (uploadForm.file) {
        formData.append('file', uploadForm.file)
      }
      if (uploadForm.content) {
        formData.append('content', uploadForm.content)
      }
    }
    
    await knowledgeEnhancedApi.document.uploadDocument(
      props.projectId,
      props.knowledgeBaseId,
      formData
    )
    
    ElMessage.success('文档上传成功，正在后台处理...')
    emit('success')
    emit('update:modelValue', false)
    
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('文档上传失败')
  } finally {
    uploading.value = false
  }
}

const resetForm = () => {
  uploadForm.title = ''
  uploadForm.document_type = ''
  uploadForm.file = null
  uploadForm.url = ''
  uploadForm.content = ''
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}
</script>

<style scoped>
.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 7px;
}
</style>