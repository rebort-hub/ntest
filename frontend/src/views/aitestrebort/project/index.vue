<template>
  <div class="aitestrebort-project">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>aitestrebort 项目管理</h2>
        <p>智能测试用例管理平台</p>
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
      <el-row :gutter="20" v-loading="loading">
        <el-col :span="8" v-for="project in projects" :key="project.id">
          <el-card class="project-card" shadow="hover" @click="enterProject(project)">
            <template #header>
              <div class="card-header">
                <span class="project-name">{{ project.name }}</span>
                <el-dropdown @command="handleProjectAction">
                  <el-button type="text" @click.stop>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{action: 'edit', project}">编辑</el-dropdown-item>
                      <el-dropdown-item :command="{action: 'delete', project}" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            
            <div class="project-content">
              <p class="project-description">{{ project.description || '暂无描述' }}</p>
              
              <div class="project-stats">
                <div class="stat-item">
                  <el-icon><Document /></el-icon>
                  <span>测试用例: {{ project.testcase_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <el-icon><User /></el-icon>
                  <span>成员: {{ project.member_count || 0 }}</span>
                </div>
              </div>

              <!-- 高级功能快速入口 -->
              <div class="advanced-features">
                <div class="feature-title">高级功能</div>
                <div class="feature-buttons">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click.stop="goToAdvancedFeature(project, 'langgraph-orchestration')"
                  >
                    <el-icon><Link /></el-icon>
                    LangGraph编排
                  </el-button>
                  <el-button 
                    size="small" 
                    type="success" 
                    @click.stop="goToAdvancedFeature(project, 'agent-execution')"
                  >
                    <el-icon><Setting /></el-icon>
                    Agent执行
                  </el-button>
                  <el-button 
                    size="small" 
                    type="warning" 
                    @click.stop="goToAdvancedFeature(project, 'script-generation')"
                  >
                    <el-icon><EditPen /></el-icon>
                    脚本生成
                  </el-button>
                  <el-button 
                    size="small" 
                    type="info" 
                    @click.stop="goToAdvancedFeature(project, 'requirement-retrieval')"
                  >
                    <el-icon><Search /></el-icon>
                    需求检索
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger" 
                    @click.stop="goToAdvancedFeature(project, 'quality-assessment')"
                  >
                    <el-icon><Star /></el-icon>
                    质量评估
                  </el-button>
                </div>
              </div>

              <!-- 新增功能模块 -->
              <div class="new-features">
                <div class="feature-title">高级功能</div>
                <div class="feature-buttons">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click.stop="goToAdvancedFeature(project, 'requirements')"
                  >
                    <el-icon><Document /></el-icon>
                    需求管理
                  </el-button>
                  <el-button 
                    size="small" 
                    type="success" 
                    @click.stop="goToAdvancedFeature(project, 'ai-diagram')"
                  >
                    <el-icon><PieChart /></el-icon>
                    AI图表生成
                  </el-button>
                  <el-button 
                    size="small" 
                    type="warning" 
                    @click.stop="goToAdvancedFeature(project, 'test-suite')"
                  >
                    <el-icon><Collection /></el-icon>
                    测试套件
                  </el-button>
                  <el-button 
                    size="small" 
                    type="info" 
                    @click.stop="goToAdvancedFeature(project, 'test-execution')"
                  >
                    <el-icon><Timer /></el-icon>
                    执行历史
                  </el-button>
                </div>
              </div>
              
              <div class="project-meta">
                <span class="create-time">创建时间: {{ formatDate(project.create_time) }}</span>
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
  Timer
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
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
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
}

.project-list {
  min-height: 400px;
}

.project-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-name {
  font-weight: 600;
  color: #303133;
}

.project-content {
  padding: 10px 0;
}

.project-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
  min-height: 20px;
}

.project-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #909399;
  font-size: 13px;
}

.project-meta {
  color: #c0c4cc;
  font-size: 12px;
}

.advanced-features {
  margin: 15px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.new-features {
  margin: 15px 0;
  padding: 15px;
  background-color: #e8f5e8;
  border-radius: 6px;
  border: 1px solid #c3e6c3;
}

.feature-title {
  font-size: 13px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 10px;
}

.feature-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-buttons .el-button {
  font-size: 12px;
  padding: 4px 8px;
  height: auto;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>