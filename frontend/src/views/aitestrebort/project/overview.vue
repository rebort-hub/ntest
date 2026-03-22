<template>
  <div class="project-overview">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon testcase">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.testcaseCount }}</div>
                <div class="stat-label">测试用例</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon automation">
                <el-icon><DocumentAdd /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.scriptCount }}</div>
                <div class="stat-label">自动化脚本</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon suite">
                <el-icon><Collection /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.suiteCount }}</div>
                <div class="stat-label">测试套件</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon execution">
                <el-icon><Timer /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ stats.executionCount }}</div>
                <div class="stat-label">执行次数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快速操作 -->
    <el-card class="quick-actions" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>快速操作</span>
        </div>
      </template>
      
      <div class="action-buttons">
        <el-button type="primary" @click="goToTestcase">
          <el-icon><Document /></el-icon>
          创建测试用例
        </el-button>
        
        <el-button type="success" @click="goToAutomation">
          <el-icon><DocumentAdd /></el-icon>
          生成自动化脚本
        </el-button>
        
        <el-button type="warning" @click="goToTestSuite">
          <el-icon><Collection /></el-icon>
          创建测试套件
        </el-button>
        
        <el-button type="info" @click="goToAIGenerator">
          <el-icon><MagicStick /></el-icon>
          AI 智能生成
        </el-button>
      </div>
    </el-card>

    <!-- 最近活动 -->
    <el-card class="recent-activity" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>最近活动</span>
          <el-button type="text" @click="loadRecentActivity">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <div class="activity-container">
        <el-timeline v-if="recentActivities.length > 0">
          <el-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :timestamp="formatDate(activity.time)"
            :type="getActivityType(activity.type)"
          >
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-description">{{ activity.description }}</div>
              <div class="activity-user">{{ activity.user }}</div>
            </div>
          </el-timeline-item>
        </el-timeline>
        
        <el-empty v-else description="暂无最近活动" />
      </div>
    </el-card>

    <!-- 项目信息 -->
    <el-card class="project-info" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>项目信息</span>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="项目名称">{{ projectInfo.name }}</el-descriptions-item>
        <el-descriptions-item label="项目状态">
          <el-tag :type="projectInfo.status === 'active' ? 'success' : 'info'">
            {{ projectInfo.status === 'active' ? '活跃' : '非活跃' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(projectInfo.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="最后更新">{{ formatDate(projectInfo.update_time) }}</el-descriptions-item>
        <el-descriptions-item label="项目描述" :span="2">
          {{ projectInfo.description || '暂无描述' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Document, DocumentAdd, Collection, Timer, MagicStick, Refresh
} from '@element-plus/icons-vue'
import { projectApi } from '@/api/aitestrebort/project'

const route = useRoute()
const router = useRouter()

// 获取项目ID
const projectId = computed(() => Number(route.params.projectId))

// 统计数据
const stats = ref({
  testcaseCount: 0,
  scriptCount: 0,
  suiteCount: 0,
  executionCount: 0
})

// 项目信息
const projectInfo = ref({
  id: 0,
  name: '',
  description: '',
  status: 'active',
  create_time: '',
  update_time: ''
})

// 最近活动
const recentActivities = ref([])

// 快速操作方法
const goToTestcase = () => {
  router.push(`/aitestrebort/project/${projectId.value}/testcase`)
}

const goToAutomation = () => {
  router.push(`/aitestrebort/project/${projectId.value}/automation`)
}

const goToTestSuite = () => {
  router.push(`/aitestrebort/project/${projectId.value}/test-suite`)
}

const goToAIGenerator = () => {
  router.push(`/aitestrebort/project/${projectId.value}/ai-generator`)
}

// 加载项目统计数据
const loadProjectStats = async () => {
  try {
    const response = await projectApi.getProjectStats(projectId.value)
    if (response.status === 200 && response.data) {
      // 映射后端返回的数据字段到前端使用的字段
      stats.value = {
        testcaseCount: response.data.testcase_count || 0,
        scriptCount: response.data.automation_script_count || 0,
        suiteCount: response.data.suite_count || 0,
        executionCount: response.data.execution_count || 0
      }
    }
  } catch (error) {
    console.error('加载项目统计失败:', error)
  }
}

// 加载项目信息
const loadProjectInfo = async () => {
  try {
    const response = await projectApi.getProject(projectId.value)
    if (response.status === 200) {
      projectInfo.value = response.data
    }
  } catch (error) {
    console.error('加载项目信息失败:', error)
  }
}

// 加载最近活动
const loadRecentActivity = async () => {
  try {
    const response = await projectApi.getProjectActivity(projectId.value, { limit: 10 })
    if (response.status === 200 && response.data) {
      recentActivities.value = response.data
    }
  } catch (error) {
    console.error('加载最近活动失败:', error)
  }
}

// 获取活动类型
const getActivityType = (type: string) => {
  const typeMap: Record<string, string> = {
    testcase: 'primary',
    automation: 'success',
    suite: 'warning',
    execution: 'info'
  }
  return typeMap[type] || 'primary'
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 组件挂载时加载数据
onMounted(() => {
  loadProjectInfo()
  loadProjectStats()
  loadRecentActivity()
})
</script>

<style scoped>
.project-overview {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100%;
  max-height: 100vh; /* 限制最大高度为视口高度 */
  overflow-y: auto; /* 添加整体滚动条 */
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.stat-icon.testcase {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.automation {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.suite {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.execution {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 160px;
}

.activity-content {
  padding: 4px 0;
}

.activity-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.activity-description {
  font-size: 13px;
  color: #606266;
}

.project-info .el-descriptions {
  margin-top: 16px;
}

.activity-container {
  max-height: 200px; /* 进一步减小最近活动区域的最大高度 */
  overflow-y: auto; /* 添加滚动条 */
  padding-right: 8px; /* 为滚动条留出空间 */
}

.activity-content {
  padding: 6px 0; /* 减小内边距 */
}

.activity-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px; /* 减小间距 */
  font-size: 14px; /* 稍微减小字体 */
}

.activity-description {
  color: #606266;
  font-size: 13px; /* 减小字体 */
  margin-bottom: 2px; /* 减小间距 */
  line-height: 1.4; /* 调整行高 */
}

.activity-user {
  color: #909399;
  font-size: 11px; /* 减小字体 */
}

/* 优化时间轴样式，使其更紧凑 */
.activity-container .el-timeline {
  padding-left: 0;
}

.activity-container .el-timeline-item {
  padding-bottom: 12px; /* 减小时间轴项之间的间距 */
}

.activity-container .el-timeline-item__timestamp {
  font-size: 11px; /* 减小时间戳字体 */
  color: #c0c4cc;
}
</style>