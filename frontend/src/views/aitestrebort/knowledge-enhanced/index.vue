<template>
  <div class="knowledge-enhanced-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>知识库管理</h2>
        <p class="header-desc">管理项目知识库，支持文档上传、向量化和RAG查询</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建知识库
        </el-button>
        <el-button @click="showConfigDialog = true">
          <el-icon><Setting /></el-icon>
          全局配置
        </el-button>
      </div>
    </div>

    <!-- 搜索和过滤 -->
    <div class="search-bar">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-input
            v-model="searchForm.search"
            placeholder="搜索知识库名称或描述"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.is_active" placeholder="状态" clearable @change="handleSearch">
            <el-option label="全部" :value="undefined" />
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadKnowledgeBases">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 知识库列表 -->
    <div class="knowledge-list">
      <el-row :gutter="16">
        <el-col :span="8" v-for="kb in knowledgeBases" :key="kb.id">
          <el-card class="knowledge-card" shadow="hover" @click="selectKnowledgeBase(kb)">
            <template #header>
              <div class="card-header">
                <span class="kb-name">{{ kb.name }}</span>
                <el-dropdown @command="handleKbAction">
                  <el-button type="text" size="small">
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{action: 'edit', kb}">编辑</el-dropdown-item>
                      <el-dropdown-item :command="{action: 'query', kb}">RAG查询</el-dropdown-item>
                      <el-dropdown-item :command="{action: 'delete', kb}" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            
            <div class="kb-info">
              <p class="kb-desc">{{ kb.description || '暂无描述' }}</p>
              
              <div class="kb-stats">
                <div class="stat-item">
                  <span class="stat-label">文档数量:</span>
                  <span class="stat-value">{{ kb.document_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">已处理:</span>
                  <span class="stat-value">{{ kb.processed_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">分块大小:</span>
                  <span class="stat-value">{{ kb.chunk_size }}</span>
                </div>
              </div>
              
              <div class="kb-status">
                <el-tag :type="kb.is_active ? 'success' : 'danger'" size="small">
                  {{ kb.is_active ? '启用' : '禁用' }}
                </el-tag>
                <span class="create-time">{{ formatTime(kb.created_at) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 知识库详情抽屉 -->
    <el-drawer
      v-model="showDetailDrawer"
      :title="selectedKb?.name"
      size="60%"
      direction="rtl"
    >
      <KnowledgeBaseDetail
        v-if="selectedKb"
        :knowledge-base="selectedKb"
        :project-id="projectId"
        @refresh="loadKnowledgeBases"
      />
    </el-drawer>

    <!-- 创建知识库对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建知识库"
      width="500px"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="知识库名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入知识库描述"
          />
        </el-form-item>
        <el-form-item label="分块大小" prop="chunk_size">
          <el-input-number v-model="createForm.chunk_size" :min="100" :max="4000" />
        </el-form-item>
        <el-form-item label="分块重叠" prop="chunk_overlap">
          <el-input-number v-model="createForm.chunk_overlap" :min="0" :max="500" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>

    <!-- 全局配置对话框 -->
    <el-dialog
      v-model="showConfigDialog"
      title="知识库全局配置"
      width="600px"
    >
      <GlobalConfigForm @close="showConfigDialog = false" />
    </el-dialog>

    <!-- RAG查询对话框 -->
    <el-dialog
      v-model="showQueryDialog"
      title="RAG查询测试"
      width="800px"
    >
      <RAGQueryForm
        v-if="queryKb"
        :knowledge-base="queryKb"
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
import { Plus, Setting, Search, Refresh, MoreFilled } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type KnowledgeBase } from '@/api/aitestrebort/knowledge-enhanced'
import KnowledgeBaseDetail from './components/KnowledgeBaseDetail.vue'
import GlobalConfigForm from './components/GlobalConfigForm.vue'
import RAGQueryForm from './components/RAGQueryForm.vue'

const route = useRoute()
const projectId = computed(() => parseInt(route.params.projectId as string))

// 响应式数据
const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const creating = ref(false)

// 搜索表单
const searchForm = reactive({
  search: '',
  is_active: undefined as boolean | undefined
})

// 创建表单
const createForm = reactive({
  name: '',
  description: '',
  chunk_size: 1000,
  chunk_overlap: 200
})

const createRules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 对话框状态
const showCreateDialog = ref(false)
const showConfigDialog = ref(false)
const showDetailDrawer = ref(false)
const showQueryDialog = ref(false)

// 选中的知识库
const selectedKb = ref<KnowledgeBase | null>(null)
const queryKb = ref<KnowledgeBase | null>(null)

// 表单引用
const createFormRef = ref()

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    loading.value = true
    const response = await knowledgeEnhancedApi.knowledgeBase.getKnowledgeBases(
      projectId.value,
      searchForm
    )
    
    if (response.data) {
      knowledgeBases.value = response.data
    }
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
    ElMessage.error('加载知识库列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  loadKnowledgeBases()
}

// 选择知识库
const selectKnowledgeBase = (kb: KnowledgeBase) => {
  selectedKb.value = kb
  showDetailDrawer.value = true
}

// 知识库操作
const handleKbAction = async (command: { action: string; kb: KnowledgeBase }) => {
  const { action, kb } = command
  
  switch (action) {
    case 'edit':
      // 编辑知识库
      Object.assign(createForm, {
        name: kb.name,
        description: kb.description,
        chunk_size: kb.chunk_size,
        chunk_overlap: kb.chunk_overlap
      })
      showCreateDialog.value = true
      break
      
    case 'query':
      // RAG查询
      queryKb.value = kb
      showQueryDialog.value = true
      break
      
    case 'delete':
      // 删除知识库
      await handleDelete(kb)
      break
  }
}

// 创建知识库
const handleCreate = async () => {
  try {
    await createFormRef.value?.validate()
    
    creating.value = true
    await knowledgeEnhancedApi.knowledgeBase.createKnowledgeBase(
      projectId.value,
      createForm
    )
    
    ElMessage.success('知识库创建成功')
    showCreateDialog.value = false
    
    // 重置表单
    Object.assign(createForm, {
      name: '',
      description: '',
      chunk_size: 1000,
      chunk_overlap: 200
    })
    
    // 刷新列表
    await loadKnowledgeBases()
    
  } catch (error) {
    console.error('Failed to create knowledge base:', error)
    ElMessage.error('创建知识库失败')
  } finally {
    creating.value = false
  }
}

// 删除知识库
const handleDelete = async (kb: KnowledgeBase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识库 "${kb.name}" 吗？此操作将同时删除所有相关文档和数据。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await knowledgeEnhancedApi.knowledgeBase.deleteKnowledgeBase(
      projectId.value,
      kb.id
    )
    
    ElMessage.success('知识库删除成功')
    await loadKnowledgeBases()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete knowledge base:', error)
      ElMessage.error('删除知识库失败')
    }
  }
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleDateString()
}

// 初始化
onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped>
.knowledge-enhanced-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0 0 5px 0;
  color: #303133;
}

.header-desc {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.search-bar {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.knowledge-list {
  margin-bottom: 20px;
}

.knowledge-card {
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.knowledge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kb-name {
  font-weight: 600;
  color: #303133;
}

.kb-info {
  padding: 10px 0;
}

.kb-desc {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.kb-stats {
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 13px;
}

.stat-label {
  color: #909399;
}

.stat-value {
  color: #303133;
  font-weight: 500;
}

.kb-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.create-time {
  font-size: 12px;
  color: #c0c4cc;
}
</style>