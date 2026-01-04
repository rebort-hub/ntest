<template>
  <div class="document-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item @click="$router.push('/aitestrebort/project')">项目管理</el-breadcrumb-item>
          <el-breadcrumb-item @click="$router.push(`/aitestrebort/project/${projectId}/requirements`)">需求管理</el-breadcrumb-item>
          <el-breadcrumb-item>{{ document?.title || '文档详情' }}</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">{{ document?.title }}</h1>
      </div>
      <div class="header-right">
        <el-button @click="downloadDocument" v-if="document">
          <el-icon><Download /></el-icon>
          下载文档
        </el-button>
        <el-button @click="showSplitDialog = true" type="primary" v-if="document">
          <el-icon><Operation /></el-icon>
          拆分模块
        </el-button>
      </div>
    </div>

    <!-- 文档信息 -->
    <div v-if="document" class="document-info">
      <el-card>
        <template #header>
          <h3>文档信息</h3>
        </template>
        
        <el-descriptions :column="3" border>
          <el-descriptions-item label="文档标题">{{ document.title }}</el-descriptions-item>
          <el-descriptions-item label="文档类型">
            <el-tag size="small">{{ getDocumentTypeText(document.document_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(document.status)" size="small">
              {{ getStatusText(document.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="字数">{{ document.word_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="页数">{{ document.page_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="版本">{{ document.version }}</el-descriptions-item>
          <el-descriptions-item label="上传时间">{{ formatDate(document.uploaded_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(document.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="是否最新">
            <el-tag :type="document.is_latest ? 'success' : 'warning'" size="small">
              {{ document.is_latest ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="document.description" class="document-description">
          <h4>文档描述</h4>
          <p>{{ document.description }}</p>
        </div>
      </el-card>
    </div>

    <!-- 文档内容 -->
    <div class="document-content">
      <el-card>
        <template #header>
          <div class="content-header">
            <h3>文档内容</h3>
            <div class="content-actions">
              <el-button-group>
                <el-button
                  :type="viewMode === 'original' ? 'primary' : 'default'"
                  @click="viewMode = 'original'"
                >
                  原始内容
                </el-button>
                <el-button
                  :type="viewMode === 'modules' ? 'primary' : 'default'"
                  @click="viewMode = 'modules'"
                >
                  模块视图
                </el-button>
              </el-button-group>
            </div>
          </div>
        </template>

        <!-- 原始内容视图 -->
        <div v-if="viewMode === 'original'" class="original-content">
          <div v-if="documentContent" class="content-text" v-html="documentContent"></div>
          <div v-else class="content-placeholder">
            <el-empty description="暂无内容" />
          </div>
        </div>

        <!-- 模块视图 -->
        <div v-if="viewMode === 'modules'" class="modules-content">
          <div v-if="modules.length > 0" class="modules-list">
            <div
              v-for="(module, index) in modules"
              :key="module.id"
              class="module-item"
            >
              <div class="module-header">
                <h4>模块 {{ index + 1 }}: {{ module.title }}</h4>
                <div class="module-actions">
                  <el-button type="text" @click="editModule(module)">编辑</el-button>
                  <el-button type="text" @click="generateTestCasesFromModule(module)">生成用例</el-button>
                </div>
              </div>
              <div class="module-content">
                {{ module.content }}
              </div>
              <div class="module-meta">
                <span>字符数: {{ module.content.length }}</span>
                <span>创建时间: {{ formatDate(module.created_at) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="modules-placeholder">
            <el-empty description="暂无模块，请先拆分文档">
              <el-button type="primary" @click="showSplitDialog = true">
                拆分模块
              </el-button>
            </el-empty>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 相关操作 -->
    <div class="related-actions">
      <el-card>
        <template #header>
          <h3>相关操作</h3>
        </template>
        
        <div class="actions-grid">
          <el-button @click="startReview" type="primary">
            <el-icon><Document /></el-icon>
            开始评审
          </el-button>
          <el-button @click="viewReviewHistory">
            <el-icon><View /></el-icon>
            评审历史
          </el-button>
          <el-button @click="generateReport">
            <el-icon><Printer /></el-icon>
            生成报告
          </el-button>
          <el-button @click="exportModules">
            <el-icon><Download /></el-icon>
            导出模块
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 模块拆分对话框 -->
    <ModuleSplitDialog
      v-model="showSplitDialog"
      :document="document"
      :project-id="projectId"
      @success="handleSplitSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Download, Operation, Document, View, Printer
} from '@element-plus/icons-vue'
import { requirementDocumentApi, type RequirementDocument } from '@/api/aitestrebort/requirements'
import ModuleSplitDialog from './components/ModuleSplitDialog.vue'

interface Module {
  id: string
  title: string
  content: string
  created_at: string
}

// 获取路由参数
const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.projectId))
const documentId = computed(() => String(route.params.documentId))

// 响应式数据
const loading = ref(false)
const document = ref<RequirementDocument | null>(null)
const documentContent = ref('')
const modules = ref<Module[]>([])
const viewMode = ref<'original' | 'modules'>('original')
const showSplitDialog = ref(false)

// 方法
const loadDocument = async () => {
  loading.value = true
  try {
    const response = await requirementDocumentApi.getDocument(
      projectId.value,
      documentId.value
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

const loadModules = async () => {
  // 模拟加载模块数据
  modules.value = [
    {
      id: '1',
      title: '系统概述',
      content: '本系统是一个基于Web的AI驱动平台，主要用于管理测试用例、AI生成用例，执行自动化测试、生成测试报告等功能。系统采用前后端分离的架构设计，前端使用Vue3+TypeScript开发，后端使用FastAPI+Python开发。',
      created_at: new Date().toISOString()
    },
    {
      id: '2',
      title: '功能需求',
      content: '系统需要支持用户管理、项目管理、测试用例管理、自动化脚本管理、测试执行、报告生成等核心功能。每个功能模块都需要提供完整的CRUD操作，并支持权限控制和数据导出。',
      created_at: new Date().toISOString()
    }
  ]
}

const downloadDocument = () => {
  ElMessage.info('下载功能开发中...')
}

const startReview = () => {
  router.push(`/aitestrebort/project/${projectId.value}/requirement-review?documentId=${documentId.value}`)
}

const viewReviewHistory = () => {
  router.push(`/aitestrebort/project/${projectId.value}/requirement-review`)
}

const generateReport = () => {
  ElMessage.info('报告生成功能开发中...')
}

const exportModules = () => {
  ElMessage.info('模块导出功能开发中...')
}

const editModule = (module: Module) => {
  ElMessage.info(`编辑模块: ${module.title}`)
}

const generateTestCasesFromModule = (module: Module) => {
  router.push(`/aitestrebort/project/${projectId.value}/ai-generator?moduleId=${module.id}`)
}

const handleSplitSuccess = () => {
  ElMessage.success('模块拆分成功')
  loadModules()
}

// 辅助方法
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const getDocumentTypeText = (type: string) => {
  const types: Record<string, string> = {
    pdf: 'PDF',
    doc: 'Word',
    docx: 'Word',
    txt: 'TXT',
    md: 'Markdown'
  }
  return types[type] || type.toUpperCase()
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

// 生命周期
onMounted(() => {
  loadDocument()
  loadModules()
})
</script>

<style scoped>
.document-detail {
  padding: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 8px 0 0 0;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 12px;
}

.document-info {
  margin-bottom: 24px;
}

.document-description {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.document-description h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.document-description p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.document-content {
  margin-bottom: 24px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-header h3 {
  margin: 0;
}

.original-content {
  min-height: 400px;
}

.content-text {
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
}

.content-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.modules-content {
  min-height: 400px;
}

.modules-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.module-item {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #fafafa;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.module-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.module-actions {
  display: flex;
  gap: 8px;
}

.module-content {
  margin-bottom: 12px;
  line-height: 1.6;
  color: #606266;
}

.module-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.modules-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.related-actions {
  margin-bottom: 24px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}
</style>