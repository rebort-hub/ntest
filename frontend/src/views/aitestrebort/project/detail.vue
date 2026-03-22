<template>
  <div class="project-detail">
    <!-- 项目头部信息 -->
    <div class="project-header">
      <div class="header-left">
        <el-button @click="goBack" style="margin-right: 16px;">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <div class="project-info">
          <h1 class="project-title">{{ projectInfo.name || '加载中...' }}</h1>
          <p class="project-description">{{ projectInfo.description || '暂无描述' }}</p>
        </div>
      </div>
      <div class="header-right">
        <el-tag type="success" v-if="projectInfo.status === 'active'">活跃</el-tag>
        <el-tag type="info" v-else>非活跃</el-tag>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="project-content">
      <!-- 左侧功能菜单 -->
      <div class="sidebar">
        <el-menu
          :default-active="activeMenu"
          class="project-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="overview">
            <el-icon><DataBoard /></el-icon>
            <span>项目概览</span>
          </el-menu-item>
          
          <el-menu-item index="testcase">
            <el-icon><Document /></el-icon>
            <span>AI测试用例</span>
          </el-menu-item>
          
          <el-menu-item index="automation">
            <el-icon><DocumentAdd /></el-icon>
            <span>AI自动化脚本</span>
          </el-menu-item>
          
          <el-menu-item index="test-suite">
            <el-icon><Collection /></el-icon>
            <span>AI测试套件</span>
          </el-menu-item>
          
          <el-menu-item index="test-execution">
            <el-icon><Timer /></el-icon>
            <span>AI执行历史</span>
          </el-menu-item>
          
          <el-menu-item index="ai-generator">
            <el-icon><MagicStick /></el-icon>
            <span>AI 离线生成</span>
          </el-menu-item>
          
          <el-menu-item index="knowledge">
            <el-icon><Reading /></el-icon>
            <span>知识库</span>
          </el-menu-item>
          
          <el-menu-item index="requirements">
            <el-icon><Memo /></el-icon>
            <span>Ai需求管理</span>
          </el-menu-item>
          
          <el-menu-item index="conversations">
            <el-icon><ChatDotRound /></el-icon>
            <span>LLM 对话</span>
          </el-menu-item>
          
          <el-menu-item index="prompts">
            <el-icon><Document /></el-icon>
            <span>提示词</span>
          </el-menu-item>
          
          <el-submenu index="advanced">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>高级功能</span>
            </template>
            <el-menu-item index="langgraph-orchestration">
              <el-icon><Link /></el-icon>
              RAG检索
            </el-menu-item>
            <el-menu-item index="agent-execution">
              <el-icon><Cpu /></el-icon>
              Agent智能执行
            </el-menu-item>
            <el-menu-item index="script-generation">
              <el-icon><EditPen /></el-icon>
              AI脚本生成
            </el-menu-item>
            <el-menu-item index="requirement-retrieval">
              <el-icon><Search /></el-icon>
              AI需求检索
            </el-menu-item>
            <el-menu-item index="quality-assessment">
              <el-icon><Star /></el-icon>
              AI质量评估
            </el-menu-item>
            <el-menu-item index="requirement-review">
              <el-icon><View /></el-icon>
              AI需求评审
            </el-menu-item>
            <el-menu-item index="ai-diagram">
              <el-icon><PieChart /></el-icon>
              AI图表生成
            </el-menu-item>
          </el-submenu>
        </el-menu>
      </div>

      <!-- 右侧内容区域 -->
      <div class="content-area">
        <router-view :key="$route.fullPath" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, DataBoard, Document, DocumentAdd, Collection, Timer,
  MagicStick, Reading, Memo, Setting, ChatDotRound, Link, Cpu,
  EditPen, Search, Star, View, PieChart
} from '@element-plus/icons-vue'
import { projectApi } from '@/api/aitestrebort/project'

const route = useRoute()
const router = useRouter()

// 获取项目ID
const projectId = computed(() => Number(route.params.projectId))

// 项目信息
const projectInfo = ref({
  id: 0,
  name: '',
  description: '',
  status: 'active'
})

// 当前激活的菜单
const activeMenu = ref('overview')

// 返回项目列表
const goBack = () => {
  router.push('/aitestrebort/project')
}

// 菜单选择处理
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  
  // 根据菜单项跳转到对应页面
  const routeMap: Record<string, string> = {
    'overview': `/aitestrebort/project/${projectId.value}/overview`,
    'testcase': `/aitestrebort/project/${projectId.value}/testcase`,
    'automation': `/aitestrebort/project/${projectId.value}/automation`,
    'test-suite': `/aitestrebort/project/${projectId.value}/test-suite`,
    'test-execution': `/aitestrebort/project/${projectId.value}/test-execution`,
    'ai-generator': `/aitestrebort/project/${projectId.value}/ai-generator`,
    'knowledge': `/aitestrebort/project/${projectId.value}/knowledge`,
    'requirements': `/aitestrebort/project/${projectId.value}/requirements`,
    'conversations': `/aitestrebort/conversations`,
    'prompts': `/aitestrebort/prompts`,
    'langgraph-orchestration': `/aitestrebort/project/${projectId.value}/langgraph-orchestration`,
    'agent-execution': `/aitestrebort/project/${projectId.value}/agent-execution`,
    'script-generation': `/aitestrebort/project/${projectId.value}/script-generation`,
    'requirement-retrieval': `/aitestrebort/project/${projectId.value}/requirement-retrieval`,
    'quality-assessment': `/aitestrebort/project/${projectId.value}/quality-assessment`,
    'requirement-review': `/aitestrebort/project/${projectId.value}/requirement-review`,
    'ai-diagram': `/aitestrebort/project/${projectId.value}/ai-diagram`
  }
  
  const targetRoute = routeMap[index]
  if (targetRoute) {
    router.push(targetRoute)
  }
}

// 根据当前路由设置激活菜单
const updateActiveMenu = () => {
  const path = route.path
  const pathSegments = path.split('/')
  const lastSegment = pathSegments[pathSegments.length - 1]
  
  // 根据路径设置激活菜单
  if (path.includes('/testcase')) {
    activeMenu.value = 'testcase'
  } else if (path.includes('/automation')) {
    activeMenu.value = 'automation'
  } else if (path.includes('/test-suite')) {
    activeMenu.value = 'test-suite'
  } else if (path.includes('/test-execution')) {
    activeMenu.value = 'test-execution'
  } else if (path.includes('/ai-generator')) {
    activeMenu.value = 'ai-generator'
  } else if (path.includes('/knowledge')) {
    activeMenu.value = 'knowledge'
  } else if (path.includes('/requirements')) {
    activeMenu.value = 'requirements'
  } else if (path.includes('/conversations')) {
    activeMenu.value = 'conversations'
  } else if (path.includes('/prompts')) {
    activeMenu.value = 'prompts'
  } else if (path.includes('/langgraph-orchestration')) {
    activeMenu.value = 'langgraph-orchestration'
  } else if (path.includes('/agent-execution')) {
    activeMenu.value = 'agent-execution'
  } else if (path.includes('/script-generation')) {
    activeMenu.value = 'script-generation'
  } else if (path.includes('/requirement-retrieval')) {
    activeMenu.value = 'requirement-retrieval'
  } else if (path.includes('/quality-assessment')) {
    activeMenu.value = 'quality-assessment'
  } else if (path.includes('/requirement-review')) {
    activeMenu.value = 'requirement-review'
  } else if (path.includes('/ai-diagram')) {
    activeMenu.value = 'ai-diagram'
  } else {
    activeMenu.value = 'overview'
  }
}

// 加载项目信息
const loadProjectInfo = async () => {
  try {
    const response = await projectApi.getProject(projectId.value)
    if (response.status === 200) {
      projectInfo.value = response.data
    } else {
      ElMessage.error('加载项目信息失败')
    }
  } catch (error) {
    console.error('加载项目信息失败:', error)
    ElMessage.error('加载项目信息失败')
  }
}

// 监听路由变化
watch(() => route.path, () => {
  updateActiveMenu()
}, { immediate: true })

// 组件挂载时加载数据
onMounted(() => {
  loadProjectInfo()
  updateActiveMenu()
})
</script>

<style scoped>
.project-detail {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.project-info {
  margin-left: 16px;
}

.project-title {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.project-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.project-menu {
  border-right: none;
  height: 100%;
}

.project-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
  padding-left: 20px !important;
}

.project-menu .el-submenu .el-menu-item {
  height: 40px;
  line-height: 40px;
  padding-left: 40px !important;
}

.content-area {
  flex: 1;
  overflow: hidden;
  background: white;
}

/* 菜单样式优化 */
.el-menu-item:hover {
  background-color: #f5f7fa !important;
}

.el-menu-item.is-active {
  background-color: #ecf5ff !important;
  color: #409eff !important;
}

.el-submenu__title:hover {
  background-color: #f5f7fa !important;
}
</style>