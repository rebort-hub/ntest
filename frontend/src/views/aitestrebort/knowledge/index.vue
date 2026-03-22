<template>
  <div class="knowledge-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title">知识库管理</h1>
          <p class="page-description">管理项目相关的知识文档和资料</p>
        </div>
        <div class="header-actions">
          <el-button @click="showSystemStatus">
            <el-icon><Document /></el-icon>
            系统状态
          </el-button>
          <el-button @click="showGlobalConfigDialog = true">
            <el-icon><Setting /></el-icon>
            全局配置
          </el-button>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建知识库
          </el-button>
        </div>
      </div>
    </div>

    <div class="content-container">
      <!-- 知识库列表 -->
      <div v-if="!selectedKnowledgeBase" class="knowledge-base-list">
        <!-- 内容标签页 -->
        <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="main-tabs">
          <el-tab-pane label="知识库列表" name="knowledge-bases">
            <!-- 搜索栏 -->
            <div class="list-header">
              <div class="search-bar">
                <el-input
                  v-model="searchForm.search"
                  placeholder="搜索知识库..."
                  style="width: 300px"
                  clearable
                  @input="handleSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              <div class="filter-bar">
                <el-select v-model="searchForm.is_active" placeholder="状态筛选" style="width: 120px" clearable @change="handleSearch">
                  <el-option label="启用" :value="true" />
                  <el-option label="禁用" :value="false" />
                </el-select>
              </div>
            </div>

            <!-- 知识库表格 -->
            <el-card class="table-card">
              <el-table :data="knowledgeBases" v-loading="loading" @row-click="selectKnowledgeBase">
                <el-table-column prop="name" label="知识库名称" min-width="200">
                  <template #default="{ row }">
                    <el-link @click="selectKnowledgeBase(row)" :underline="false">{{ row.name }}</el-link>
                  </template>
                </el-table-column>
                <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
                  <template #default="{ row }">
                    {{ row.description || '暂无描述' }}
                  </template>
                </el-table-column>
                <el-table-column prop="is_active" label="状态" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                      {{ row.is_active ? '启用' : '禁用' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="统计" width="120" align="center">
                  <template #default="{ row }">
                    <div class="stats-cell">
                      <div>文档: {{ row.document_count || 0 }}</div>
                      <div>分块: {{ row.chunk_count || 0 }}</div>
                    </div>
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
                    <el-button type="text" @click.stop="editKnowledgeBase(row)">编辑</el-button>
                    <el-button type="text" @click.stop="viewStatistics(row)">统计</el-button>
                    <el-button type="text" @click.stop="deleteKnowledgeBase(row)" style="color: #f56c6c;">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 分页 -->
              <div class="pagination-container" v-if="total > 0">
                <el-pagination
                  v-model:current-page="searchForm.page"
                  v-model:page-size="searchForm.page_size"
                  :total="total"
                  :page-sizes="[10, 20, 50, 100]"
                  layout="total, sizes, prev, pager, next, jumper"
                  @size-change="loadKnowledgeBases"
                  @current-change="loadKnowledgeBases"
                />
              </div>
            </el-card>
          </el-tab-pane>
          
          <el-tab-pane label="系统统计" name="statistics">
            <SystemStatistics :project-id="projectId" />
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 右侧详情面板 - 占据整个内容区域 -->
      <div v-if="selectedKnowledgeBase" class="detail-panel-full">
        <KnowledgeBaseDetail
          :knowledge-base="selectedKnowledgeBase"
          :project-id="projectId"
          @refresh="loadKnowledgeBases"
          @close="selectedKnowledgeBase = null"
        />
      </div>
    </div>

    <!-- 创建/编辑知识库对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingKnowledgeBase ? '编辑知识库' : '创建知识库'"
      width="600px"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="knowledgeBaseForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="知识库名称" prop="name">
          <el-input v-model="knowledgeBaseForm.name" placeholder="请输入知识库名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="knowledgeBaseForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入知识库描述"
          />
        </el-form-item>
        
        <el-form-item label="分块大小" prop="chunk_size">
          <el-input-number v-model="knowledgeBaseForm.chunk_size" :min="100" :max="2000" :step="100" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">字符数</span>
        </el-form-item>
        
        <el-form-item label="分块重叠" prop="chunk_overlap">
          <el-input-number v-model="knowledgeBaseForm.chunk_overlap" :min="0" :max="500" :step="50" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">字符数</span>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="knowledgeBaseForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingKnowledgeBase ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 知识库详情抽屉 -->
    <div v-if="false" style="display: none;">
      <!-- 保留原有的抽屉代码以备后用 -->
    </div>

    <!-- 全局配置对话框 -->
    <el-dialog
      v-model="showGlobalConfigDialog"
      title="知识库全局配置"
      width="700px"
    >
      <GlobalConfigForm @close="showGlobalConfigDialog = false" />
    </el-dialog>

    <!-- RAG查询对话框 -->
    <el-dialog
      v-model="showQueryDialog"
      title="RAG查询测试"
      width="900px"
    >
      <RAGQueryForm
        v-if="queryKnowledgeBase"
        :knowledge-base="queryKnowledgeBase"
        :project-id="projectId"
        @close="showQueryDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, Setting, Document, MoreFilled, ArrowLeft
} from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type KnowledgeBase } from '@/api/aitestrebort/knowledge-enhanced'
import { knowledgeApi } from '@/api/aitestrebort/knowledge'
import KnowledgeBaseDetail from './components/KnowledgeBaseDetail.vue'
import GlobalConfigForm from './components/GlobalConfigForm.vue'
import RAGQueryForm from './components/RAGQueryForm.vue'
import SystemStatistics from './components/SystemStatistics.vue'

// 获取项目ID
const route = useRoute()
const projectId = computed(() => Number(route.params.projectId))

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showGlobalConfigDialog = ref(false)
const showQueryDialog = ref(false)
const knowledgeBases = ref<KnowledgeBase[]>([])
const total = ref(0)
const editingKnowledgeBase = ref<KnowledgeBase | null>(null)
const selectedKnowledgeBase = ref<KnowledgeBase | null>(null)
const queryKnowledgeBase = ref<KnowledgeBase | null>(null)
const activeTab = ref('knowledge-bases')

// 搜索表单
const searchForm = reactive({
  search: '',
  is_active: undefined as boolean | undefined,
  page: 1,
  page_size: 12
})

// 知识库表单
const knowledgeBaseForm = reactive({
  name: '',
  description: '',
  chunk_size: 1000,
  chunk_overlap: 200,
  is_active: true
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在 2 到 100 个字符', trigger: 'blur' }
  ]
}

// 表单引用
const formRef = ref()

// 方法
const handleTabChange = (tabName: string) => {
  activeTab.value = tabName
  // 根据标签页切换加载不同数据
  if (tabName === 'knowledge-bases') {
    loadKnowledgeBases()
  }
}

const loadKnowledgeBases = async () => {
  loading.value = true
  try {
    // 使用增强版API
    const response = await knowledgeEnhancedApi.knowledgeBase.getKnowledgeBases(
      projectId.value,
      {
        search: searchForm.search,
        is_active: searchForm.is_active,
        page: searchForm.page,
        page_size: searchForm.page_size
      }
    )
    
    if (response.data) {
      // 处理分页响应
      if (response.data.items) {
        knowledgeBases.value = response.data.items
        total.value = response.data.total
      } else {
        // 兼容旧格式（没有分页）
        knowledgeBases.value = response.data
        total.value = response.data.length
      }
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
    ElMessage.error('获取知识库列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchForm.page = 1
  loadKnowledgeBases()
}

const selectKnowledgeBase = (knowledgeBase: KnowledgeBase) => {
  selectedKnowledgeBase.value = knowledgeBase
}

const handleKbAction = async (command: { action: string; kb: KnowledgeBase }) => {
  const { action, kb } = command
  
  switch (action) {
    case 'edit':
      editKnowledgeBase(kb)
      break
    case 'query':
      queryKnowledgeBase.value = kb
      showQueryDialog.value = true
      break
    case 'stats':
      await viewStatistics(kb)
      break
    case 'delete':
      await deleteKnowledgeBase(kb)
      break
  }
}

const editKnowledgeBase = (knowledgeBase: KnowledgeBase) => {
  editingKnowledgeBase.value = knowledgeBase
  Object.assign(knowledgeBaseForm, {
    name: knowledgeBase.name,
    description: knowledgeBase.description,
    chunk_size: knowledgeBase.chunk_size,
    chunk_overlap: knowledgeBase.chunk_overlap,
    is_active: knowledgeBase.is_active
  })
  showCreateDialog.value = true
}

const deleteKnowledgeBase = async (knowledgeBase: KnowledgeBase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识库 "${knowledgeBase.name}" 吗？此操作将同时删除所有相关文档和数据。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await knowledgeEnhancedApi.knowledgeBase.deleteKnowledgeBase(
      projectId.value,
      knowledgeBase.id
    )
    
    // 响应拦截器会显示成功消息
    await loadKnowledgeBases()
    
    // 如果删除的是当前选中的知识库，清除选中状态
    if (selectedKnowledgeBase.value?.id === knowledgeBase.id) {
      selectedKnowledgeBase.value = null
    }
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除知识库失败:', error)
      ElMessage.error('删除知识库失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (editingKnowledgeBase.value) {
      const response = await knowledgeEnhancedApi.knowledgeBase.updateKnowledgeBase(
        projectId.value,
        editingKnowledgeBase.value.id,
        knowledgeBaseForm
      )
      // 如果没有抛出异常，说明成功了
      showCreateDialog.value = false
      await loadKnowledgeBases()
    } else {
      const response = await knowledgeEnhancedApi.knowledgeBase.createKnowledgeBase(
        projectId.value,
        knowledgeBaseForm
      )
      // 如果没有抛出异常，说明成功了
      showCreateDialog.value = false
      await loadKnowledgeBases()
    }
  } catch (error) {
    console.error('提交失败:', error)
    // 响应拦截器已经处理了错误提示
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingKnowledgeBase.value = null
  Object.assign(knowledgeBaseForm, {
    name: '',
    description: '',
    chunk_size: 1000,
    chunk_overlap: 200,
    is_active: true
  })
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const viewStatistics = async (knowledgeBase: KnowledgeBase) => {
  try {
    const response = await knowledgeEnhancedApi.knowledgeBase.getKnowledgeBaseStatistics(
      projectId.value,
      knowledgeBase.id
    )
    
    if (response.data) {
      const stats = response.data
      ElMessageBox.alert(
        `
        <div style="text-align: left;">
          <h4>统计信息</h4>
          <p><strong>文档数量：</strong>${stats.document_count || 0}</p>
          <p><strong>已处理：</strong>${stats.processed_count || 0}</p>
          <p><strong>分块数量：</strong>${stats.chunk_count || 0}</p>
          <p><strong>处理进度：</strong>${stats.document_count > 0 ? Math.round((stats.processed_count / stats.document_count) * 100) : 0}%</p>
        </div>
        `,
        `${knowledgeBase.name} - 统计信息`,
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '确定'
        }
      )
    }
  } catch (error) {
    console.error('获取统计信息失败:', error)
    ElMessage.error('获取统计信息失败')
  }
}

const showSystemStatus = async () => {
  try {
    const response = await knowledgeEnhancedApi.system.getSystemStatus()
    if (response.data) {
      const status = response.data
      
      // 根据状态确定颜色和文本
      let statusColor = 'green'
      let statusText = '正常'
      
      if (status.system_status === 'warning') {
        statusColor = 'orange'
        statusText = '警告'
      } else if (status.system_status === 'error') {
        statusColor = 'red'
        statusText = '异常'
      }
      
      // 构建状态消息
      let statusMessage = ''
      if (status.status_message) {
        statusMessage = `<p><strong>状态详情：</strong><span style="color: ${statusColor}">${status.status_message}</span></p>`
      }
      
      ElMessageBox.alert(
        `
        <div style="text-align: left;">
          <h4>系统状态</h4>
          <p><strong>总知识库数：</strong>${status.total_knowledge_bases || 0}</p>
          <p><strong>总文档数：</strong>${status.total_documents || 0}</p>
          <p><strong>处理中文档：</strong>${status.processing_documents || 0}</p>
          <p><strong>总分块数：</strong>${status.total_chunks || 0}</p>
          <p><strong>系统状态：</strong><span style="color: ${statusColor}">${statusText}</span></p>
          ${statusMessage}
        </div>
        `,
        '系统状态',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '确定'
        }
      )
    }
  } catch (error) {
    console.error('获取系统状态失败:', error)
    ElMessage.error('获取系统状态失败')
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped>
.knowledge-management {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.content-container {
  flex: 1;
  display: flex;
  gap: 20px;
  overflow: hidden;
}

.knowledge-base-list {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.detail-panel-full {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.search-bar {
  display: flex;
  gap: 12px;
}

.filter-bar {
  display: flex;
  gap: 12px;
}

.table-card {
  background: white;
  margin-bottom: 16px;
}

.stats-cell {
  font-size: 12px;
  color: #666;
}

.main-tabs {
  height: 100%;
}

.main-tabs .el-tabs__content {
  height: calc(100% - 40px);
  overflow: auto;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>