<template>
  <div class="requirements-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-actions">
          <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        </div>
        <h1 class="page-title">需求管理</h1>
        <p class="page-description">管理项目需求文档，支持文档上传、模块拆分、评审分析等功能</p>
      </div>
      <div class="header-right">
        <el-button @click="showUploadDialog = true" type="primary">
          <el-icon><Upload /></el-icon>
          上传需求文档
        </el-button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-container">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 需求文档管理 -->
        <el-tab-pane label="需求文档" name="documents">
          <div class="documents-section">
            <!-- 搜索和筛选 -->
            <div class="search-bar">
              <el-input
                v-model="searchForm.search"
                placeholder="搜索文档标题..."
                style="width: 300px"
                clearable
                @input="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              
              <el-select
                v-model="searchForm.status"
                placeholder="状态筛选"
                style="width: 120px; margin-left: 12px"
                clearable
                @change="handleSearch"
              >
                <el-option label="待处理" value="pending" />
                <el-option label="处理中" value="processing" />
                <el-option label="已完成" value="completed" />
                <el-option label="失败" value="failed" />
              </el-select>
            </div>

            <!-- 文档列表 -->
            <el-table :data="documents" v-loading="documentsLoading" @row-click="viewDocument">
              <el-table-column prop="title" label="文档标题" min-width="200">
                <template #default="{ row }">
                  <el-link @click="viewDocument(row)" :underline="false">{{ row.title }}</el-link>
                </template>
              </el-table-column>
              <el-table-column prop="document_type" label="文档类型" width="100" align="center">
                <template #default="{ row }">
                  <el-tag size="small">{{ getDocumentTypeText(row.document_type) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small">
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="word_count" label="字数" width="100" align="center">
                <template #default="{ row }">
                  {{ row.word_count || 0 }}
                </template>
              </el-table-column>
              <el-table-column prop="page_count" label="页数" width="100" align="center">
                <template #default="{ row }">
                  {{ row.page_count || 0 }}
                </template>
              </el-table-column>
              <el-table-column prop="uploaded_at" label="上传时间" width="150" align="center">
                <template #default="{ row }">
                  {{ formatDate(row.uploaded_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" fixed="right" align="center">
                <template #default="{ row }">
                  <el-button type="text" @click.stop="viewDocument(row)">查看</el-button>
                  <el-button type="text" @click.stop="splitModules(row)">拆分模块</el-button>
                  <el-button type="text" @click.stop="startReview(row)">开始评审</el-button>
                  <el-button type="text" @click.stop="deleteDocument(row)" style="color: #f56c6c;">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination" v-if="total > 0">
              <el-pagination
                v-model:current-page="searchForm.page"
                v-model:page-size="searchForm.page_size"
                :total="total"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="loadDocuments"
                @current-change="loadDocuments"
              />
            </div>
          </div>
        </el-tab-pane>

        <!-- 智能生成测试用例 -->
        <el-tab-pane label="智能生成测试用例" name="ai-generator">
          <AITestCaseGenerator :project-id="projectId" :knowledge-base-id="knowledgeBaseId" />
        </el-tab-pane>

        <!-- 手动需求管理 -->
        <el-tab-pane label="手动需求" name="manual-requirements">
          <div class="manual-requirements-section">
            <div class="section-header">
              <h3>手动需求管理</h3>
              <el-button type="primary" @click="showCreateRequirementDialog = true">
                <el-icon><Plus /></el-icon>
                创建需求
              </el-button>
            </div>

            <!-- 需求列表 -->
            <el-table :data="requirements" v-loading="requirementsLoading">
              <el-table-column prop="title" label="需求标题" min-width="200" />
              <el-table-column prop="type" label="需求类型" width="120" align="center">
                <template #default="{ row }">
                  <el-tag :type="getRequirementTypeColor(row.type)" size="small">
                    {{ getRequirementTypeText(row.type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="priority" label="优先级" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="getPriorityColor(row.priority)" size="small">
                    {{ getPriorityText(row.priority) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="getRequirementStatusColor(row.status)" size="small">
                    {{ getRequirementStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="creator_name" label="创建者" width="100" align="center" />
              <el-table-column prop="created_at" label="创建时间" width="150" align="center">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" fixed="right" align="center">
                <template #default="{ row }">
                  <el-button type="text" @click="viewRequirement(row)">查看</el-button>
                  <el-button type="text" @click="editRequirement(row)">编辑</el-button>
                  <el-button type="text" @click="generateTestCases(row)">生成用例</el-button>
                  <el-button type="text" @click="deleteRequirement(row)" style="color: #f56c6c;">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 上传文档对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传需求文档"
      width="600px"
      @closed="resetUploadForm"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="100px"
      >
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="uploadForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        
        <el-form-item label="文档描述" prop="description">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入文档描述（可选）"
          />
        </el-form-item>
        
        <el-form-item label="文档文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".pdf,.doc,.docx,.txt,.md"
          >
            <el-button>选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、Word、TXT、Markdown 格式，文件大小不超过 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建需求对话框 -->
    <el-dialog
      v-model="showCreateRequirementDialog"
      :title="editingRequirement ? '编辑需求' : '创建需求'"
      width="700px"
      @closed="resetRequirementForm"
    >
      <el-form
        ref="requirementFormRef"
        :model="requirementForm"
        :rules="requirementRules"
        label-width="100px"
      >
        <el-form-item label="需求标题" prop="title">
          <el-input v-model="requirementForm.title" placeholder="请输入需求标题" />
        </el-form-item>
        
        <el-form-item label="需求描述" prop="description">
          <el-input
            v-model="requirementForm.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述需求内容"
          />
        </el-form-item>
        
        <el-form-item label="需求类型" prop="type">
          <el-select v-model="requirementForm.type" placeholder="请选择需求类型">
            <el-option label="功能需求" value="functional" />
            <el-option label="非功能需求" value="non-functional" />
            <el-option label="业务需求" value="business" />
            <el-option label="用户需求" value="user" />
            <el-option label="系统需求" value="system" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="requirementForm.priority" placeholder="请选择优先级">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="requirementForm.status" placeholder="请选择状态">
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="开发中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="相关人员" prop="stakeholders">
          <el-select
            v-model="requirementForm.stakeholders"
            multiple
            filterable
            allow-create
            placeholder="请输入或选择相关人员"
            style="width: 100%"
          >
            <el-option
              v-for="person in stakeholderOptions"
              :key="person"
              :label="person"
              :value="person"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateRequirementDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateRequirement" :loading="submitting">
          {{ editingRequirement ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 模块拆分对话框 -->
    <ModuleSplitDialog
      v-model="showModuleSplitDialog"
      :document="selectedDocument"
      :project-id="projectId"
      @success="handleModuleSplitSuccess"
    />

    <!-- 需求详情对话框 -->
    <RequirementDetailDialog
      v-model="showRequirementDetailDialog"
      :requirement="selectedRequirement"
      :project-id="projectId"
      @refresh="loadRequirements"
      @edit="handleEditFromDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload, Search, Plus, Document, Edit, Delete, ArrowLeft
} from '@element-plus/icons-vue'
import { requirementDocumentApi, requirementApi, type RequirementDocument, type Requirement } from '@/api/aitestrebort/requirements'
import ModuleSplitDialog from './components/ModuleSplitDialog.vue'
import RequirementDetailDialog from './components/RequirementDetailDialog.vue'
import AITestCaseGenerator from './components/AITestCaseGenerator.vue'

// 获取项目ID
const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.projectId))

// 响应式数据
const activeTab = ref('documents')
const documentsLoading = ref(false)
const requirementsLoading = ref(false)
const uploading = ref(false)
const submitting = ref(false)
const showUploadDialog = ref(false)
const showCreateRequirementDialog = ref(false)
const showModuleSplitDialog = ref(false)
const showRequirementDetailDialog = ref(false)

const documents = ref<RequirementDocument[]>([])
const requirements = ref<Requirement[]>([])
const total = ref(0)
const selectedDocument = ref<RequirementDocument | null>(null)
const selectedRequirement = ref<Requirement | null>(null)
const editingRequirement = ref<Requirement | null>(null)
const knowledgeBaseId = ref<number | undefined>(undefined)

// 搜索表单
const searchForm = reactive({
  search: '',
  status: '',
  page: 1,
  page_size: 20
})

// 上传表单
const uploadForm = reactive({
  title: '',
  description: '',
  file: null as File | null
})

// 需求表单
const requirementForm = reactive({
  title: '',
  description: '',
  type: '',
  priority: '',
  status: 'draft',
  stakeholders: [] as string[]
})

// 相关人员选项
const stakeholderOptions = ref(['产品经理', '开发工程师', '测试工程师', '项目经理', 'UI设计师'])

// 表单验证规则
const uploadRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' }
  ]
}

const requirementRules = {
  title: [
    { required: true, message: '请输入需求标题', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入需求描述', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择需求类型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

// 表单引用
const uploadFormRef = ref()
const requirementFormRef = ref()
const uploadRef = ref()

// 方法
const handleTabChange = (tabName: string) => {
  activeTab.value = tabName
  if (tabName === 'documents') {
    loadDocuments()
  } else if (tabName === 'manual-requirements') {
    loadRequirements()
  }
}

const loadDocuments = async () => {
  documentsLoading.value = true
  try {
    const response = await requirementDocumentApi.getDocuments(projectId.value, {
      search: searchForm.search,
      status: searchForm.status,
      page: searchForm.page,
      page_size: searchForm.page_size
    })
    
    if (response.data?.status === 200 || response.status === 200) {
      const data = response.data?.data || response.data
      documents.value = data.items || []
      total.value = data.total || 0
    } else {
      ElMessage.error(response.data?.message || response.message || '获取文档列表失败')
    }
  } catch (error) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败')
  } finally {
    documentsLoading.value = false
  }
}

const loadRequirements = async () => {
  requirementsLoading.value = true
  try {
    const response = await requirementApi.getRequirements(projectId.value)
    
    if (response.data?.status === 200 || response.status === 200) {
      const data = response.data?.data || response.data
      requirements.value = data.items || []
    } else {
      ElMessage.error(response.data?.message || response.message || '获取需求列表失败')
    }
  } catch (error) {
    console.error('获取需求列表失败:', error)
    ElMessage.error('获取需求列表失败')
  } finally {
    requirementsLoading.value = false
  }
}

const handleSearch = () => {
  searchForm.page = 1
  loadDocuments()
}

const viewDocument = (document: RequirementDocument) => {
  router.push(`/aitestrebort/project/${projectId.value}/requirements/${document.id}`)
}

const splitModules = (document: RequirementDocument) => {
  selectedDocument.value = document
  showModuleSplitDialog.value = true
}

const startReview = (document: RequirementDocument) => {
  router.push(`/aitestrebort/project/${projectId.value}/requirement-review?documentId=${document.id}`)
}

const deleteDocument = async (document: RequirementDocument) => {
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
    
    const response = await requirementDocumentApi.deleteDocument(projectId.value, document.id)
    if (response.data?.status === 200 || response.status === 200) {
      ElMessage.success(response.data?.message || '文档删除成功')
      await loadDocuments()
    } else {
      ElMessage.error(response.data?.message || response.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
      ElMessage.error('删除文档失败')
    }
  }
}

const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
  if (!uploadForm.title) {
    uploadForm.title = file.name.replace(/\.[^/.]+$/, '')
  }
}

const handleFileRemove = () => {
  uploadForm.file = null
}

const handleUpload = async () => {
  if (!uploadFormRef.value) return
  
  try {
    await uploadFormRef.value.validate()
    
    if (!uploadForm.file) {
      ElMessage.warning('请选择要上传的文件')
      return
    }
    
    uploading.value = true
    
    const formData = new FormData()
    formData.append('file', uploadForm.file)
    formData.append('title', uploadForm.title)
    formData.append('document_type', uploadForm.file.type.includes('pdf') ? 'pdf' : 'docx')
    if (uploadForm.description) {
      formData.append('description', uploadForm.description)
    }
    
    const response = await requirementDocumentApi.createDocument(projectId.value, formData)
    
    if (response.data?.status === 200 || response.status === 200) {
      ElMessage.success(response.data?.message || '文档上传成功')
      showUploadDialog.value = false
      await loadDocuments()
    } else {
      ElMessage.error(response.data?.message || response.message || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const handleCreateRequirement = async () => {
  if (!requirementFormRef.value) return
  
  try {
    await requirementFormRef.value.validate()
    submitting.value = true
    
    if (editingRequirement.value) {
      const response = await requirementApi.updateRequirement(
        projectId.value,
        editingRequirement.value.id,
        requirementForm
      )
      // 检查响应体中的status字段，而不是HTTP状态码
      if (response.data?.status === 200 || response.status === 200) {
        ElMessage.success(response.data?.message || '需求更新成功')
      } else {
        ElMessage.error(response.data?.message || response.message || '更新失败')
      }
    } else {
      const response = await requirementApi.createRequirement(projectId.value, requirementForm)
      if (response.data?.status === 200 || response.status === 200) {
        ElMessage.success(response.data?.message || '需求创建成功')
      } else {
        ElMessage.error(response.data?.message || response.message || '创建失败')
      }
    }
    
    showCreateRequirementDialog.value = false
    await loadRequirements()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const viewRequirement = (requirement: Requirement) => {
  selectedRequirement.value = requirement
  showRequirementDetailDialog.value = true
}

const editRequirement = (requirement: Requirement) => {
  editingRequirement.value = requirement
  Object.assign(requirementForm, {
    title: requirement.title,
    description: requirement.description,
    type: requirement.type,
    priority: requirement.priority,
    status: requirement.status,
    stakeholders: requirement.stakeholders || []
  })
  showCreateRequirementDialog.value = true
}

const handleEditFromDetail = (requirement: Requirement) => {
  editRequirement(requirement)
}

const generateTestCases = (requirement: Requirement) => {
  console.log('生成测试用例，需求:', requirement)
  try {
    router.push(`/aitestrebort/project/${projectId.value}/ai-generator?requirementId=${requirement.id}`)
  } catch (error) {
    console.error('跳转失败:', error)
    ElMessage.error('页面跳转失败，请稍后重试')
  }
}

const deleteRequirement = async (requirement: Requirement) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除需求 "${requirement.title}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await requirementApi.deleteRequirement(projectId.value, requirement.id)
    if (response.data?.status === 200 || response.status === 200) {
      ElMessage.success(response.data?.message || '需求删除成功')
      await loadRequirements()
    } else {
      ElMessage.error(response.data?.message || response.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除需求失败:', error)
      ElMessage.error('删除需求失败')
    }
  }
}

const resetUploadForm = () => {
  uploadForm.title = ''
  uploadForm.description = ''
  uploadForm.file = null
  if (uploadFormRef.value) {
    uploadFormRef.value.resetFields()
  }
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const resetRequirementForm = () => {
  editingRequirement.value = null
  Object.assign(requirementForm, {
    title: '',
    description: '',
    type: '',
    priority: '',
    status: 'draft',
    stakeholders: []
  })
  if (requirementFormRef.value) {
    requirementFormRef.value.resetFields()
  }
}

const handleModuleSplitSuccess = () => {
  ElMessage.success('模块拆分成功')
  loadDocuments()
}

const goBack = () => {
  const from = route.query.from as string
  if (from === 'testcase') {
    router.push(`/aitestrebort/project/${projectId.value}/testcase`)
  } else {
    router.push('/aitestrebort/project')
  }
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
    uploaded: 'info',
    processing: 'primary',
    ready_for_review: 'warning',
    reviewing: 'primary',
    review_completed: 'success',
    failed: 'danger',
    pending: 'warning',
    completed: 'success'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    uploaded: '已上传',
    processing: '处理中',
    ready_for_review: '待评审',
    reviewing: '评审中',
    review_completed: '评审通过',
    failed: '处理失败',
    pending: '待处理',
    completed: '已完成'
  }
  return texts[status] || status
}

const getRequirementTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    functional: 'primary',
    'non-functional': 'success',
    business: 'warning',
    user: 'info',
    system: 'danger'
  }
  return colors[type] || 'info'
}

const getRequirementTypeText = (type: string) => {
  const texts: Record<string, string> = {
    functional: '功能需求',
    'non-functional': '非功能需求',
    business: '业务需求',
    user: '用户需求',
    system: '系统需求'
  }
  return texts[type] || type
}

const getPriorityColor = (priority: string) => {
  const colors: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return colors[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const texts: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[priority] || priority
}

const getRequirementStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    draft: 'info',
    pending: 'warning',
    confirmed: 'success',
    in_progress: 'primary',
    completed: 'success'
  }
  return colors[status] || 'info'
}

const getRequirementStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    pending: '待审核',
    confirmed: '已确认',
    in_progress: '开发中',
    completed: '已完成'
  }
  return texts[status] || status
}

// 生命周期
onMounted(() => {
  loadDocuments()
  loadKnowledgeBase()
})

// 加载知识库信息
const loadKnowledgeBase = async () => {
  try {
    // 尝试获取项目关联的知识库
    // 这里假设有一个API可以获取项目的知识库
    // 如果没有，可以让用户在生成时选择
    knowledgeBaseId.value = undefined
  } catch (error) {
    console.error('获取知识库失败:', error)
  }
}
</script>

<style scoped>
.requirements-management {
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

.header-actions {
  margin-bottom: 16px;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.content-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}
</style>