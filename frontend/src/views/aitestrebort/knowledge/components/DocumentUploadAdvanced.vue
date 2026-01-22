<template>
  <el-dialog
    :model-value="modelValue"
    title="上传文档"
    width="700px"
    @update:model-value="$emit('update:modelValue', $event)"
    @closed="resetUploader"
  >
    <section class="document-upload-advanced">
      <!-- 上传方式选择 -->
      <el-tabs v-model="uploadMode" class="upload-tabs">
        <!-- 文件上传 -->
        <el-tab-pane label="文件上传" name="file">
          <uploader
            ref="uploaderRef"
            :options="uploaderOptions"
            :file-status-text="statusText"
            @file-progress="onFileProgress"
            @file-success="onFileSuccess"
            @file-error="onFileError"
            @file-removed="onFileRemoved"
            @complete="onComplete"
            class="uploader-container"
          >
            <!-- 不支持 HTML5 File API 的时候会显示 -->
            <uploader-unsupport></uploader-unsupport>
            
            <!-- 拖拽上传区域 -->
            <uploader-drop>
              <div class="upload-drag-area">
                <div class="upload-options">
                  <!-- 上传"文件" -->
                  <uploader-btn class="upload-btn">
                    <div class="upload-item upload-file">
                      <el-icon class="upload-icon"><Document /></el-icon>
                      <div class="upload-text">上传文件</div>
                      <div class="upload-hint">支持 PDF、Word、PPT 等</div>
                    </div>
                  </uploader-btn>
                  
                  <!-- 上传"文件夹" -->
                  <uploader-btn :directory="true" class="upload-btn">
                    <div class="upload-item upload-folder">
                      <el-icon class="upload-icon"><Folder /></el-icon>
                      <div class="upload-text">上传文件夹</div>
                      <div class="upload-hint">批量上传整个文件夹</div>
                    </div>
                  </uploader-btn>
                </div>
                
                <div class="upload-tips">
                  <p>支持的文件类型：PDF、Word、Excel、PowerPoint、Markdown、HTML、纯文本、图片（JPG、PNG、GIF）</p>
                  <p>支持文件夹批量上传，单个文件最大 50MB</p>
                  <p>新增支持：Excel表格(.xlsx, .xls)、Markdown文档(.md)、HTML文档(.html)</p>
                </div>
              </div>
            </uploader-drop>
            
            <!-- 文件列表 -->
            <uploader-list></uploader-list>
          </uploader>
        </el-tab-pane>
        
        <!-- URL上传 -->
        <el-tab-pane label="网页链接" name="url">
          <div class="url-upload-container">
            <el-form :model="urlForm" :rules="urlRules" ref="urlFormRef" label-width="100px">
              <el-form-item label="文档标题" prop="title">
                <el-input 
                  v-model="urlForm.title" 
                  placeholder="请输入文档标题"
                  clearable
                />
              </el-form-item>
              
              <el-form-item label="网页链接" prop="url">
                <el-input 
                  v-model="urlForm.url" 
                  placeholder="请输入网页链接，例如：https://example.com"
                  clearable
                >
                  <template #prepend>
                    <el-icon><Link /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="handleUrlUpload" :loading="urlUploading">
                  <el-icon><Upload /></el-icon>
                  上传链接
                </el-button>
                <el-button @click="resetUrlForm">重置</el-button>
              </el-form-item>
            </el-form>
            
            <el-alert
              title="提示"
              type="info"
              :closable="false"
              show-icon
            >
              <p>支持上传网页链接，系统会自动抓取网页内容并进行处理</p>
              <p>请确保链接可以正常访问</p>
            </el-alert>
          </div>
        </el-tab-pane>
      </el-tabs>
    </section>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
      <el-button type="danger" @click="cancelAll" v-if="hasUploading && uploadMode === 'file'">取消全部</el-button>
      <el-button type="primary" @click="retryAll" v-if="hasError && uploadMode === 'file'">重试失败</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Folder, Link, Upload } from '@element-plus/icons-vue'
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

// 组件引用
const uploaderRef = ref()
const urlFormRef = ref()

// 上传模式
const uploadMode = ref<'file' | 'url'>('file')

// 上传状态
const hasUploading = ref(false)
const hasError = ref(false)
const urlUploading = ref(false)

// URL表单
const urlForm = reactive({
  title: '',
  url: ''
})

// URL表单验证规则
const urlRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入网页链接', trigger: 'blur' },
    { 
      pattern: /^https?:\/\/.+/, 
      message: '请输入有效的网页链接（以http://或https://开头）', 
      trigger: 'blur' 
    }
  ]
}

// 上传配置
const uploaderOptions = reactive({
  // 上传服务端接口地址
  target: `/api/aitestrebort/knowledge/projects/${props.projectId}/knowledge-bases/${props.knowledgeBaseId}/documents`,
  
  // 请求方式
  method: 'POST',
  
  // 上传接口headers配置
  headers: {
    'access-token': localStorage.getItem('accessToken') || ''
  },
  
  // 文件参数名
  fileParameterName: 'file',
  
  // 发起请求时携带的其他参数
  query: (file: any) => {
    // 从文件名提取标题
    const title = file.name.replace(/\.[^/.]+$/, '')
    // 从文件扩展名提取类型
    const ext = file.name.split('.').pop()?.toLowerCase() || 'txt'
    
    return {
      title: title,
      document_type: ext
    }
  },
  
  // 格式化剩余时间
  parseTimeRemaining: (timeRemaining: number, parsedTimeRemaining: string) => {
    return parsedTimeRemaining
      .replace(/\syears?/, '年')
      .replace(/\days?/, '天')
      .replace(/\shours?/, '小时')
      .replace(/\sminutes?/, '分钟')
      .replace(/\sseconds?/, '秒')
  },
  
  // 是否单文件上传
  singleFile: false,
  
  // 禁用分块上传（后端不支持）
  testChunks: false,
  forceChunkSize: false,
  
  // 最大自动失败重试上传次数
  maxChunkRetries: 3,
  
  // 并发上传数
  simultaneousUploads: 3
})

// 状态文字
const statusText = reactive({
  success: '上传成功',
  error: '上传失败',
  uploading: '上传中',
  paused: '已暂停',
  waiting: '等待上传'
})

// 事件处理
const onFileProgress = (rootFile: any, file: any, chunk: any) => {
  hasUploading.value = true
  
  // 动态设置进度条样式
  setTimeout(() => {
    const progressBars = document.querySelectorAll('.uploader-file-progress-bar')
    progressBars.forEach((bar: any) => {
      const progress = parseFloat(bar.getAttribute('aria-valuenow') || '0')
      bar.style.setProperty('--progress', `${progress}%`)
      bar.style.background = `conic-gradient(#67c23a ${progress}%, #e4e7ed 0)`
    })
  }, 0)
}

const onFileSuccess = (rootFile: any, file: any, response: any) => {
  console.log('文件上传成功:', file.name)
  // 不显示单个文件的成功提示，等所有文件完成后统一提示
}

const onFileError = (rootFile: any, file: any, response: any) => {
  console.error('文件上传失败:', file.name, response)
  hasError.value = true
  
  let errorMessage = '上传失败'
  try {
    const res = JSON.parse(response)
    errorMessage = res.message || errorMessage
  } catch {
    // 忽略解析错误
  }
  
  ElMessage.error(`${file.name} 上传失败: ${errorMessage}`)
}

const onFileRemoved = (file: any) => {
  console.log('文件已移除:', file.name)
}

const onComplete = () => {
  console.log('所有文件上传完成')
  hasUploading.value = false
  // 显示成功提示
  if (!hasError.value) {
    ElMessage.success('文档上传成功')
  }
  emit('success')
  
  // 清空文件列表
  setTimeout(() => {
    if (uploaderRef.value) {
      uploaderRef.value.uploader.cancel()
      // 清空所有文件
      const files = uploaderRef.value.uploader.files
      files.forEach((file: any) => {
        file.cancel()
      })
    }
  }, 1000) // 延迟1秒清空，让用户看到成功状态
}

// 操作方法
const cancelAll = () => {
  if (uploaderRef.value) {
    uploaderRef.value.cancel()
    hasUploading.value = false
    ElMessage.info('已取消所有上传')
  }
}

const clearAll = () => {
  if (uploaderRef.value && uploaderRef.value.uploader) {
    // 取消所有上传
    uploaderRef.value.uploader.cancel()
    // 清空文件列表
    const files = uploaderRef.value.uploader.files
    files.forEach((file: any) => {
      file.cancel()
    })
    hasUploading.value = false
    hasError.value = false
  }
}

const retryAll = () => {
  if (uploaderRef.value) {
    uploaderRef.value.retry()
    hasError.value = false
    ElMessage.info('正在重试失败的文件')
  }
}

const resetUploader = () => {
  hasUploading.value = false
  hasError.value = false
  uploadMode.value = 'file'
  resetUrlForm()
}

// URL上传方法
const handleUrlUpload = async () => {
  if (!urlFormRef.value) return
  
  try {
    await urlFormRef.value.validate()
    urlUploading.value = true
    
    // 创建FormData
    const formData = new FormData()
    formData.append('title', urlForm.title)
    formData.append('document_type', 'url')
    formData.append('url', urlForm.url)
    
    const response = await knowledgeEnhancedApi.document.uploadDocument(
      props.projectId,
      props.knowledgeBaseId,
      formData
    )
    
    if (response.status === 200) {
      ElMessage.success('网页链接上传成功，正在后台处理...')
      emit('success')
      resetUrlForm()
    } else {
      ElMessage.error(response.message || '上传失败')
    }
    
  } catch (error: any) {
    console.error('URL上传失败:', error)
    if (error !== 'cancel') {
      ElMessage.error('网页链接上传失败')
    }
  } finally {
    urlUploading.value = false
  }
}

const resetUrlForm = () => {
  urlForm.title = ''
  urlForm.url = ''
  if (urlFormRef.value) {
    urlFormRef.value.resetFields()
  }
}
</script>

<style scoped>
.document-upload-advanced {
  padding: 15px;
}

.upload-tabs {
  margin-bottom: 15px;
}

.uploader-container {
  min-height: 350px;
}

/* URL上传容器 */
.url-upload-container {
  padding: 15px;
  min-height: 250px;
}

.url-upload-container .el-form {
  max-width: 600px;
  margin: 0 auto 15px;
}

.url-upload-container .el-alert {
  max-width: 600px;
  margin: 0 auto;
}

/* 清除插件默认按钮样式 */
:deep(.uploader-btn) {
  border: none;
  padding: 0;
  background: none;
  margin: 0;
}

:deep(.uploader-btn:hover) {
  background: none;
}

/* 拖拽区域样式 - 缩小 */
.upload-drag-area {
  padding: 20px 15px;
  text-align: center;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  background: #fafafa;
  transition: all 0.3s;
}

.upload-drag-area:hover {
  border-color: #409eff;
  background: #f0f7ff;
}

.upload-options {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 15px;
}

.upload-btn {
  cursor: pointer;
}

/* 缩小上传按钮 - 统一高度 */
.upload-item {
  width: 120px;
  height: 120px;
  padding: 15px 10px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fff;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
  transform: translateY(-1px);
}

.upload-file {
  border-color: #409eff;
}

.upload-folder {
  border-color: #67c23a;
}

/* 缩小图标 */
.upload-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.upload-file .upload-icon {
  color: #409eff;
}

.upload-folder .upload-icon {
  color: #67c23a;
}

.upload-text {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 11px;
  color: #909399;
}

.upload-tips {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.upload-tips p {
  margin: 3px 0;
  font-size: 12px;
  color: #606266;
}

/* 文件列表样式优化 - 固定高度，添加滚动条 */
:deep(.uploader-list) {
  margin-top: 15px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 5px;
}

/* 滚动条样式 */
:deep(.uploader-list)::-webkit-scrollbar {
  width: 6px;
}

:deep(.uploader-list)::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

:deep(.uploader-list)::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

:deep(.uploader-list)::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

:deep(.uploader-file) {
  margin-bottom: 8px;
  padding: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
}

:deep(.uploader-file-name) {
  font-weight: 500;
  font-size: 13px;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.uploader-file-size) {
  font-size: 12px;
  color: #909399;
}

:deep(.uploader-file-status) {
  font-size: 12px !important;
  color: #67c23a !important;
  margin-right: 10px !important;
  min-width: 60px !important;
}

/* 圆形进度条样式 - 绿色 */
:deep(.uploader-file-progress) {
  width: 50px !important;
  height: 50px !important;
  position: relative !important;
  flex-shrink: 0 !important;
  margin: 0 10px !important;
}

/* 隐藏原始进度条 */
:deep(.uploader-file-progress .uploader-file-progress-bar) {
  width: 50px !important;
  height: 50px !important;
  border-radius: 50% !important;
  background: #e4e7ed !important;
  position: relative !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  overflow: visible !important;
}

/* 进度条背景圆环 - 使用伪元素创建圆形进度 */
:deep(.uploader-file-progress .uploader-file-progress-bar)::before {
  content: '' !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  border-radius: 50% !important;
  background: inherit !important;
  z-index: 1 !important;
}

/* 内圆白色背景显示百分比 */
:deep(.uploader-file-progress .uploader-file-progress-bar)::after {
  content: attr(aria-valuenow) '%' !important;
  position: absolute !important;
  width: 38px !important;
  height: 38px !important;
  border-radius: 50% !important;
  background: #fff !important;
  z-index: 2 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 11px !important;
  color: #67c23a !important;
  font-weight: 600 !important;
}

/* 操作按钮样式 - 确保可见 */
:deep(.uploader-file-actions) {
  display: flex !important;
  gap: 8px !important;
  flex-shrink: 0 !important;
  z-index: 10 !important;
  margin-left: auto !important;
  align-items: center !important;
}

:deep(.uploader-file-actions > *),
:deep(.uploader-file-actions button),
:deep(.uploader-file-actions .uploader-file-pause),
:deep(.uploader-file-actions .uploader-file-resume),
:deep(.uploader-file-actions .uploader-file-retry),
:deep(.uploader-file-actions .uploader-file-remove) {
  padding: 6px 12px !important;
  font-size: 13px !important;
  background: #fff !important;
  border: 1px solid #dcdfe6 !important;
  border-radius: 4px !important;
  cursor: pointer !important;
  transition: all 0.3s !important;
  color: #606266 !important;
  opacity: 1 !important;
  visibility: visible !important;
  display: inline-block !important;
  min-width: 60px !important;
  text-align: center !important;
}

:deep(.uploader-file-actions > *:hover),
:deep(.uploader-file-actions button:hover) {
  color: #409eff !important;
  border-color: #c6e2ff !important;
  background-color: #ecf5ff !important;
}
</style>
