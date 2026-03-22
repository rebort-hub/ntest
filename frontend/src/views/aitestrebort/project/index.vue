<template>
  <div class="aitestrebort-project">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>项目管理</h2>
        <p>项目之间独立隔离，用例生成单独归属独立项目</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建项目
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchForm.search"
            placeholder="搜索项目名称或描述"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-button @click="loadProjects">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 项目列表 -->
    <div class="project-list">
      <el-row :gutter="16" v-loading="loading">
        <el-col :span="6" v-for="project in projects" :key="project.id">
          <el-card class="project-card" shadow="hover" @click="enterProject(project)">
            <div class="project-content">
              <!-- 项目头部 -->
              <div class="project-header">
                <div class="project-icon">
                  <el-icon><Folder /></el-icon>
                </div>
                <div class="project-info">
                  <h3 class="project-name">{{ project.name }}</h3>
                  <p class="project-description">{{ project.description || '暂无描述' }}</p>
                </div>
                <el-dropdown @command="handleProjectAction" trigger="click">
                  <el-button type="text" size="small" @click.stop class="more-btn">
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{action: 'edit', project}">
                        <el-icon><Edit /></el-icon>
                        编辑
                      </el-dropdown-item>
                      <el-dropdown-item :command="{action: 'delete', project}" divided>
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              
              <!-- 项目统计 -->
              <div class="project-stats">
                <div class="stat-item">
                  <el-icon><Document /></el-icon>
                  <span>{{ project.testcase_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <el-icon><User /></el-icon>
                  <span>{{ project.member_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatDate(project.create_time) }}</span>
                </div>
              </div>

              <!-- 快速操作 -->
              <div class="quick-actions">
                <div class="action-buttons">
                  <el-tooltip content="需求管理" placement="top">
                    <el-button 
                      size="small" 
                      text
                      @click.stop="goToAdvancedFeature(project, 'requirements')"
                    >
                      <el-icon><Document /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="测试套件" placement="top">
                    <el-button 
                      size="small" 
                      text
                      @click.stop="goToAdvancedFeature(project, 'test-suite')"
                    >
                      <el-icon><Collection /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="AI脚本生成" placement="top">
                    <el-button 
                      size="small" 
                      text
                      @click.stop="goToAdvancedFeature(project, 'script-generation')"
                    >
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="更多功能" placement="top">
                    <el-dropdown @command="(cmd) => goToAdvancedFeature(project, cmd)" trigger="click">
                      <el-button size="small" text @click.stop>
                        <el-icon><More /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="langgraph-orchestration">
                            <el-icon><Link /></el-icon>
                            RAG检索
                          </el-dropdown-item>
                          <el-dropdown-item command="agent-execution">
                            <el-icon><Setting /></el-icon>
                            Agent执行
                          </el-dropdown-item>
                          <el-dropdown-item command="requirement-retrieval">
                            <el-icon><Search /></el-icon>
                            AI需求检索
                          </el-dropdown-item>
                          <el-dropdown-item command="quality-assessment">
                            <el-icon><Star /></el-icon>
                            AI质量评估
                          </el-dropdown-item>
                          <el-dropdown-item command="ai-diagram">
                            <el-icon><PieChart /></el-icon>
                            AI图表生成
                          </el-dropdown-item>
                          <el-dropdown-item command="test-execution">
                            <el-icon><Timer /></el-icon>
                            执行历史
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </el-tooltip>
                </div>
                <span class="detail-link" @click.stop="enterProject(project)">
                  详情
                  <el-icon><ArrowRight /></el-icon>
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 空状态 -->
      <el-empty v-if="!loading && projects.length === 0" description="暂无项目">
        <el-button type="primary" @click="showCreateDialog = true">创建第一个项目</el-button>
      </el-empty>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:current-page="searchForm.page_no"
        v-model:page-size="searchForm.page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadProjects"
        @current-change="loadProjects"
      />
    </div>

    <!-- 创建/编辑项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProject ? '编辑项目' : '创建项目'"
      width="500px"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="projectForm"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingProject ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  MoreFilled,
  Document,
  User,
  Link,
  Setting,
  EditPen,
  Star,
  PieChart,
  Collection,
  Timer,
  Folder,
  Clock,
  More,
  Edit,
  Delete,
  ArrowRight
} from '@element-plus/icons-vue'
import { projectApi, type Project, type CreateProjectData } from '@/api/aitestrebort/project'

// 路由
const router = useRouter()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const projects = ref<Project[]>([])
const total = ref(0)
const editingProject = ref<Project | null>(null)

// 搜索表单
const searchForm = reactive({
  search: '',
  page_no: 1,
  page_size: 20
})

// 项目表单
const projectForm = reactive<CreateProjectData>({
  name: '',
  description: ''
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '项目名称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 表单引用
const formRef = ref()

// 方法
const loadProjects = async () => {
  loading.value = true
  try {
    const response = await projectApi.getProjects(searchForm)
    if (response.status === 200) {
      projects.value = response.data.items || []
      total.value = response.data.total || 0
    } else {
      ElMessage.error(response.message || '获取项目列表失败')
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchForm.page = 1
  loadProjects()
}

const enterProject = (project: Project) => {
  router.push(`/aitestrebort/project/${project.id}/testcase`)
}

const goToAdvancedFeature = (project: Project, feature: string) => {
  console.log('跳转到高级功能:', project.id, feature)
  const targetPath = `/aitestrebort/project/${project.id}/${feature}`
  console.log('目标路径:', targetPath)
  router.push(targetPath)
}

const handleProjectAction = async (command: { action: string; project: Project }) => {
  const { action, project } = command
  
  if (action === 'edit') {
    editingProject.value = project
    projectForm.name = project.name
    projectForm.description = project.description || ''
    showCreateDialog.value = true
  } else if (action === 'delete') {
    try {
      await ElMessageBox.confirm(
        `确定要删除项目 "${project.name}" 吗？此操作不可恢复。`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      const response = await projectApi.deleteProject(project.id)
      if (response.status === 200) {
        loadProjects()
      }
      // 400错误已经由响应拦截器处理
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除项目失败:', error)
      }
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    let response
    if (editingProject.value) {
      response = await projectApi.updateProject(editingProject.value.id, projectForm)
    } else {
      response = await projectApi.createProject(projectForm)
    }
    
    if (response.status === 200) {
      showCreateDialog.value = false
      loadProjects()
    }
    // 400错误已经由响应拦截器处理
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingProject.value = null
  projectForm.name = ''
  projectForm.description = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.aitestrebort-project {
  padding: 20px;
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}

.header-left h2 {
  margin: 0 0 5px 0;
  color: #303133;
}

.header-left p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.search-bar {
  margin-bottom: 20px;
  flex-shrink: 0;
}

.project-list {
  flex: 1;
  min-height: 200px;
}

.project-list .el-col {
  margin-bottom: 16px;
}

.project-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  height: 100%;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.project-card :deep(.el-card__body) {
  padding: 16px;
}

.project-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.project-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  position: relative;
}

.project-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #ffd666 0%, #ffa940 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.project-icon .el-icon {
  font-size: 20px;
  color: white;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-description {
  font-size: 13px;
  color: #909399;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
  max-height: 2.8em;
}

.more-btn {
  position: absolute;
  top: 0;
  right: 0;
  padding: 4px;
}

.project-stats {
  display: flex;
  gap: 16px;
  padding: 8px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
  font-size: 12px;
}

.stat-item .el-icon {
  font-size: 14px;
  color: #909399;
}

.quick-actions {
  display: flex;
  gap: 4px;
  justify-content: space-between;
  align-items: center;
}

.quick-actions .action-buttons {
  display: flex;
  gap: 4px;
}

.quick-actions .el-button {
  padding: 4px;
  font-size: 16px;
}

.quick-actions .el-button:hover {
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.detail-link {
  font-size: 12px;
  color: #909399;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 2px;
  transition: color 0.3s;
}

.detail-link:hover {
  color: var(--el-color-primary);
}

.detail-link .el-icon {
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 16px 0;
  background: white;
  border-radius: 8px;
  flex-shrink: 0;
}
</style>