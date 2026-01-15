<template>
  <div class="prompt-management">
    <div class="page-header">
      <h2>提示词管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建提示词
      </el-button>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-select v-model="filters.prompt_type" placeholder="选择类型" clearable>
            <el-option label="全部类型" value="" />
            <el-option
              v-for="type in promptTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.is_active" placeholder="选择状态" clearable>
            <el-option label="全部状态" value="" />
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input
            v-model="filters.search"
            placeholder="搜索提示词名称或描述"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadPrompts">刷新</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 提示词列表 -->
    <div class="prompt-list" v-loading="loading">
      <el-row :gutter="16">
        <el-col 
          v-for="prompt in filteredPrompts" 
          :key="prompt.id" 
          :span="6" 
          style="margin-bottom: 16px"
        >
          <el-card class="prompt-card" shadow="hover">
            <div class="card-icon">
              <el-icon :size="40" color="#409EFF">
                <Document />
              </el-icon>
            </div>
            
            <div class="card-content">
              <h3 class="prompt-name">{{ prompt.name }}</h3>
              
              <div class="prompt-meta">
                <el-tag :type="getTypeTagType(prompt.prompt_type)" size="small">
                  {{ getTypeLabel(prompt.prompt_type) }}
                </el-tag>
                <el-tag v-if="prompt.is_default" type="success" size="small">
                  默认
                </el-tag>
              </div>
              
              <p v-if="prompt.description" class="prompt-description">
                {{ truncateContent(prompt.description, 50) }}
              </p>
              
              <div class="card-footer">
                <span class="status-tag">
                  <el-tag :type="prompt.is_active ? 'success' : 'info'" size="small">
                    {{ prompt.is_active ? '启用' : '禁用' }}
                  </el-tag>
                </span>
                <el-dropdown @command="(command) => handleCommand(command, prompt)" trigger="click">
                  <el-button type="text" size="small" class="more-btn">
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit">
                        <el-icon><Edit /></el-icon>
                        编辑
                      </el-dropdown-item>
                      <el-dropdown-item command="duplicate">
                        <el-icon><CopyDocument /></el-icon>
                        复制
                      </el-dropdown-item>
                      <el-dropdown-item 
                        v-if="!prompt.is_default && prompt.prompt_type === 'general'"
                        command="setDefault"
                      >
                        <el-icon><Star /></el-icon>
                        设为默认
                      </el-dropdown-item>
                      <el-dropdown-item 
                        v-if="prompt.is_default"
                        command="clearDefault"
                      >
                        <el-icon><CircleClose /></el-icon>
                        取消默认
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <div v-if="filteredPrompts.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无提示词" />
      </div>
    </div>

    <!-- 创建/编辑提示词对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingPrompt ? '编辑提示词' : '创建提示词'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入提示词名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="类型" prop="prompt_type">
          <el-select v-model="formData.prompt_type" placeholder="选择提示词类型">
            <el-option
              v-for="type in promptTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
              :disabled="type.is_program_call && editingPrompt"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入提示词描述（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="10"
            placeholder="请输入提示词内容"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item v-if="formData.prompt_type === 'general'">
          <el-checkbox v-model="formData.is_default">
            设为默认提示词
          </el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="formData.is_active">
            启用此提示词
          </el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingPrompt ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, MoreFilled, Document, Edit, Delete, CopyDocument, Star, CircleClose } from '@element-plus/icons-vue'
import { globalApi, type GlobalPrompt } from '@/api/aitestrebort/global'
import { projectApi } from '@/api/aitestrebort/project'
import { useRoute } from 'vue-router'

// 获取默认项目ID
const defaultProjectId = ref<number>(1)

// 从localStorage获取或设置默认项目ID
const getDefaultProjectId = async () => {
  try {
    // 尝试从localStorage获取
    const stored = localStorage.getItem('defaultProjectId')
    if (stored) {
      defaultProjectId.value = Number(stored)
      return
    }
    
    // 如果没有，获取用户的第一个项目
    const response = await globalApi.getProjects({ page_no: 1, page_size: 1 })
    if (response.status === 200 && response.data.items && response.data.items.length > 0) {
      defaultProjectId.value = response.data.items[0].id
      localStorage.setItem('defaultProjectId', String(defaultProjectId.value))
    }
  } catch (error) {
    console.error('获取默认项目ID失败:', error)
  }
}

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const editingPrompt = ref<GlobalPrompt | null>(null)
const prompts = ref<GlobalPrompt[]>([])
const promptTypes = ref<Array<{ value: string; label: string; is_program_call: boolean }>>([])

// 筛选条件
const filters = reactive({
  prompt_type: '',
  is_active: '',
  search: ''
})

// 表单数据
const formData = reactive({
  name: '',
  content: '',
  description: '',
  prompt_type: 'general',
  is_default: false,
  is_active: true
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入提示词名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入提示词内容', trigger: 'blur' },
    { min: 10, message: '内容至少 10 个字符', trigger: 'blur' }
  ],
  prompt_type: [
    { required: true, message: '请选择提示词类型', trigger: 'change' }
  ]
}

// 表单引用
const formRef = ref()

// 计算属性
const filteredPrompts = computed(() => {
  let result = prompts.value
  
  if (filters.prompt_type) {
    result = result.filter(p => p.prompt_type === filters.prompt_type)
  }
  
  if (filters.is_active !== '') {
    result = result.filter(p => p.is_active === filters.is_active)
  }
  
  if (filters.search) {
    const keyword = filters.search.toLowerCase()
    result = result.filter(p => 
      p.name.toLowerCase().includes(keyword) ||
      (p.description && p.description.toLowerCase().includes(keyword))
    )
  }
  
  return result
})

// 方法
const loadPrompts = async () => {
  loading.value = true
  try {
    // 使用默认项目ID
    const params = { project_id: defaultProjectId.value }
    const response = await globalApi.getPrompts(params)
    if (response.status === 200) {
      // 显示所有提示词（包括系统提示词和用户创建的提示词）
      // 注意：系统提示词（程序调用类型）也会显示，但用户可以看到它们
      const allPrompts = response.data.prompts || []
      prompts.value = allPrompts
      
      console.log('加载的提示词:', allPrompts.length, '个')
      console.log('提示词类型:', allPrompts.map(p => p.prompt_type))
    } else {
      ElMessage.error(response.message || '获取提示词列表失败')
    }
  } catch (error) {
    console.error('获取提示词列表失败:', error)
    ElMessage.error('获取提示词列表失败')
  } finally {
    loading.value = false
  }
}

const loadPromptTypes = async () => {
  try {
    const response = await globalApi.getPromptTypes()
    if (response.status === 200) {
      // 只显示通用对话类型，过滤掉程序调用类型（系统内部使用）
      const allTypes = response.data || []
      promptTypes.value = allTypes.filter((t: any) => !t.is_program_call)
    }
  } catch (error) {
    console.error('获取提示词类型失败:', error)
  }
}

const handleSearch = () => {
  // 搜索逻辑已在计算属性中实现
}

const handleCommand = async (command: string, prompt: GlobalPrompt) => {
  switch (command) {
    case 'edit':
      editPrompt(prompt)
      break
    case 'duplicate':
      duplicatePrompt(prompt)
      break
    case 'setDefault':
      setDefaultPrompt(prompt)
      break
    case 'clearDefault':
      clearDefaultPrompt()
      break
    case 'delete':
      deletePrompt(prompt)
      break
  }
}

const editPrompt = (prompt: GlobalPrompt) => {
  editingPrompt.value = prompt
  formData.name = prompt.name
  formData.content = prompt.content
  formData.description = prompt.description || ''
  formData.prompt_type = prompt.prompt_type
  formData.is_default = prompt.is_default
  formData.is_active = prompt.is_active
  showCreateDialog.value = true
}

const duplicatePrompt = async (prompt: GlobalPrompt) => {
  try {
    const response = await globalApi.duplicatePrompt(prompt.id)
    if (response.status === 200) {
      // 拦截器已自动显示成功消息，这里只需要刷新列表
      loadPrompts()
    } else {
      // 错误消息由拦截器处理
    }
  } catch (error) {
    // 异常错误由拦截器处理
  }
}

const setDefaultPrompt = async (prompt: GlobalPrompt) => {
  try {
    const response = await globalApi.setDefaultPrompt(prompt.id)
    if (response.status === 200) {
      loadPrompts()
    }
  } catch (error) {
    // 异常错误由拦截器处理
  }
}

const clearDefaultPrompt = async () => {
  try {
    const response = await globalApi.clearDefaultPrompt({})
    if (response.status === 200) {
      loadPrompts()
    }
  } catch (error) {
    // 异常错误由拦截器处理
  }
}

const deletePrompt = async (prompt: GlobalPrompt) => {
  try {
    await ElMessageBox.confirm(`确定要删除提示词 "${prompt.name}" 吗？`, '确认删除', { type: 'warning' })
    
    const response = await globalApi.deletePrompt(prompt.id)
    if (response.status === 200) {
      loadPrompts()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除提示词失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const data = {
        ...formData,
        // 使用默认项目ID
        project_id: defaultProjectId.value
      }
      
      let response
      if (editingPrompt.value) {
        response = await globalApi.updatePrompt(editingPrompt.value.id, data)
      } else {
        response = await globalApi.createPrompt(data)
      }
      
      if (response.status === 200) {
        // 拦截器已自动显示成功消息
        showCreateDialog.value = false
        loadPrompts()
      }
    } catch (error) {
      // 异常错误由拦截器处理
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  editingPrompt.value = null
  formData.name = ''
  formData.content = ''
  formData.description = ''
  formData.prompt_type = 'general'
  formData.is_default = false
  formData.is_active = true
  formRef.value?.clearValidate()
}

const getTypeLabel = (type: string) => {
  const typeObj = promptTypes.value.find(t => t.value === type)
  return typeObj?.label || type
}

const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    general: '',
    test_generation: 'success',
    code_review: 'warning',
    bug_analysis: 'danger'
  }
  return typeMap[type] || ''
}

const truncateContent = (content: string, maxLength = 100) => {
  if (content.length <= maxLength) return content
  return content.substring(0, maxLength) + '...'
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命周期
onMounted(async () => {
  await getDefaultProjectId()
  loadPrompts()
  loadPromptTypes()
})
</script>

<style scoped>
.prompt-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.filter-section {
  margin-bottom: 20px;
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.prompt-list {
  min-height: 400px;
}

.prompt-card {
  height: 220px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
}

.prompt-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-icon {
  text-align: center;
  padding: 20px 0 10px;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 16px 16px;
}

.prompt-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #303133;
}

.prompt-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.prompt-description {
  margin: 0;
  color: #909399;
  font-size: 13px;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  flex: 1;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

.status-tag {
  display: flex;
  align-items: center;
}

.more-btn {
  padding: 4px;
  font-size: 16px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 1600px) {
  .prompt-list :deep(.el-col-6) {
    max-width: 33.333333% !important;
    flex: 0 0 33.333333% !important;
  }
}

@media (max-width: 1200px) {
  .prompt-list :deep(.el-col-6) {
    max-width: 50% !important;
    flex: 0 0 50% !important;
  }
}

@media (max-width: 768px) {
  .prompt-list :deep(.el-col-6) {
    max-width: 100% !important;
    flex: 0 0 100% !important;
  }
}
</style>
