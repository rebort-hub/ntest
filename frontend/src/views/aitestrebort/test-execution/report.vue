<template>
  <div class="execution-report-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item @click="$router.push('/aitestrebort/project')">项目管理</el-breadcrumb-item>
          <el-breadcrumb-item @click="$router.push(`/aitestrebort/project/${projectId}/test-execution`)">测试执行历史</el-breadcrumb-item>
          <el-breadcrumb-item>执行报告</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button @click="exportPDF">
          <el-icon><Document /></el-icon>
          导出PDF
        </el-button>
        <el-button @click="exportExcel">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
        <el-button @click="$router.go(-1)">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
    </div>

    <!-- 报告内容 -->
    <div class="report-container" v-if="execution">
      <!-- 报告头部 -->
      <div class="report-header">
        <div class="report-title">
          <h1>{{ execution.suite_name }} - 执行报告</h1>
          <div class="report-meta">
            <span>执行时间: {{ formatDateTime(execution.start_time) }}</span>
            <span>总耗时: {{ formatDuration(execution.duration) }}</span>
            <span>执行者: {{ execution.executor_name }}</span>
            <span>执行环境: {{ execution.environment || '默认环境' }}</span>
          </div>
        </div>
        <div class="report-status">
          <el-tag :type="getStatusColor(execution.status)" size="large">
            {{ getStatusText(execution.status) }}
          </el-tag>
        </div>
      </div>

      <!-- 执行概览 -->
      <div class="report-section">
        <h2>执行概览</h2>
        <el-row :gutter="24">
          <el-col :span="12">
            <div class="overview-chart" ref="overviewChartRef"></div>
          </el-col>
          <el-col :span="12">
            <div class="summary-stats">
              <div class="stat-item">
                <div class="stat-label">总执行项</div>
                <div class="stat-value">{{ execution.total_count }}</div>
              </div>
              <div class="stat-item success">
                <div class="stat-label">成功</div>
                <div class="stat-value">{{ execution.success_count }}</div>
              </div>
              <div class="stat-item danger">
                <div class="stat-label">失败</div>
                <div class="stat-value">{{ execution.failed_count }}</div>
              </div>
              <div class="stat-item warning">
                <div class="stat-label">跳过</div>
                <div class="stat-value">{{ execution.skipped_count || 0 }}</div>
              </div>
              <div class="stat-item primary">
                <div class="stat-label">成功率</div>
                <div class="stat-value">{{ successRate }}%</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 执行时间线 -->
      <div class="report-section">
        <h2>执行时间线</h2>
        <div class="timeline-chart" ref="timelineChartRef"></div>
      </div>

      <!-- 详细结果 -->
      <div class="report-section">
        <h2>详细结果</h2>
        <el-table :data="reportItems" stripe>
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="name" label="执行项名称" min-width="250" />
          <el-table-column prop="type" label="类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="row.type === 'testcase' ? 'primary' : 'success'" size="small">
                {{ row.type === 'testcase' ? '测试用例' : '自动化脚本' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusColor(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="耗时" width="100" align="center">
            <template #default="{ row }">
              {{ formatDuration(row.duration) }}
            </template>
          </el-table-column>
          <el-table-column prop="start_time" label="开始时间" width="150" align="center">
            <template #default="{ row }">
              {{ formatTime(row.start_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="error_message" label="错误信息" min-width="300">
            <template #default="{ row }">
              <div v-if="row.error_message" class="error-message">
                <el-tooltip :content="row.error_message" placement="top">
                  <span>{{ row.error_message.length > 50 ? row.error_message.substring(0, 50) + '...' : row.error_message }}</span>
                </el-tooltip>
              </div>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 失败分析 -->
      <div class="report-section" v-if="failedItems.length > 0">
        <h2>失败分析</h2>
        <div class="failure-analysis">
          <div class="failure-summary">
            <el-alert
              :title="`本次执行共有 ${failedItems.length} 个项目失败`"
              type="error"
              :closable="false"
              show-icon
            />
          </div>
          <div class="failure-items">
            <el-card
              v-for="(item, index) in failedItems"
              :key="index"
              class="failure-item"
              shadow="hover"
            >
              <template #header>
                <div class="failure-header">
                  <span class="failure-name">{{ item.name }}</span>
                  <el-tag type="danger" size="small">{{ item.type === 'testcase' ? '测试用例' : '自动化脚本' }}</el-tag>
                </div>
              </template>
              <div class="failure-content">
                <p><strong>错误信息：</strong></p>
                <div class="error-detail">{{ item.error_message }}</div>
                <el-row :gutter="16" style="margin-top: 12px;">
                  <el-col :span="8">
                    <strong>执行时间：</strong>{{ formatTime(item.start_time) }}
                  </el-col>
                  <el-col :span="8">
                    <strong>耗时：</strong>{{ formatDuration(item.duration) }}
                  </el-col>
                  <el-col :span="8">
                    <strong>重试次数：</strong>{{ item.retry_count || 0 }}
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </div>
        </div>
      </div>

      <!-- 性能分析 -->
      <div class="report-section">
        <h2>性能分析</h2>
        <div class="performance-analysis">
          <el-row :gutter="24">
            <el-col :span="16">
              <div class="performance-chart" ref="performanceChartRef"></div>
            </el-col>
            <el-col :span="8">
              <div class="performance-stats">
                <el-card class="stat-card">
                  <el-statistic title="平均执行时间" :value="averageDuration" suffix="秒" />
                </el-card>
                <el-card class="stat-card">
                  <el-statistic title="最长执行时间" :value="maxDuration" suffix="秒" />
                </el-card>
                <el-card class="stat-card">
                  <el-statistic title="最短执行时间" :value="minDuration" suffix="秒" />
                </el-card>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 建议和总结 -->
      <div class="report-section">
        <h2>建议和总结</h2>
        <el-row :gutter="24">
          <el-col :span="8" v-if="execution.failed_count > 0">
            <el-card class="recommendation-card" header="失败项目处理建议">
              <ul class="recommendation-list">
                <li>检查失败的测试用例和脚本，分析失败原因</li>
                <li>确认测试环境配置是否正确</li>
                <li>验证测试数据的有效性</li>
                <li>考虑增加重试机制或优化测试逻辑</li>
              </ul>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="recommendation-card" header="性能优化建议">
              <ul class="recommendation-list">
                <li>考虑增加并发执行数量以提高执行效率</li>
                <li>优化执行时间较长的测试项</li>
                <li>合理安排测试执行顺序</li>
                <li>定期清理测试环境和数据</li>
              </ul>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="recommendation-card" header="质量改进建议">
              <ul class="recommendation-list">
                <li>定期维护和更新测试用例</li>
                <li>建立测试数据管理机制</li>
                <li>完善测试环境监控</li>
                <li>增强测试覆盖率分析</li>
              </ul>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-else class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Download, ArrowLeft } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 获取路由参数
const route = useRoute()
const projectId = computed(() => Number(route.params.projectId))
const executionId = computed(() => route.params.executionId as string)

// 图表引用
const overviewChartRef = ref()
const timelineChartRef = ref()
const performanceChartRef = ref()

// 图表实例
let overviewChart: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null
let performanceChart: echarts.ECharts | null = null

// 响应式数据
const execution = ref(null)
const reportItems = ref([])

// 计算属性
const successRate = computed(() => {
  if (!execution.value || execution.value.total_count === 0) return 0
  return Math.round((execution.value.success_count / execution.value.total_count) * 100)
})

const failedItems = computed(() => {
  return reportItems.value.filter(item => item.status === 'failed')
})

const averageDuration = computed(() => {
  if (reportItems.value.length === 0) return 0
  const total = reportItems.value.reduce((sum, item) => sum + item.duration, 0)
  return Math.round(total / reportItems.value.length / 1000)
})

const maxDuration = computed(() => {
  if (reportItems.value.length === 0) return 0
  return Math.round(Math.max(...reportItems.value.map(item => item.duration)) / 1000)
})

const minDuration = computed(() => {
  if (reportItems.value.length === 0) return 0
  return Math.round(Math.min(...reportItems.value.map(item => item.duration)) / 1000)
})

// 方法
const loadExecutionData = async () => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    execution.value = {
      id: executionId.value,
      suite_name: '用户管理功能测试套件',
      status: 'success',
      progress: 100,
      success_count: 12,
      failed_count: 2,
      skipped_count: 1,
      total_count: 15,
      duration: 180000, // 3分钟
      executor_name: '张三',
      start_time: '2024-01-15T10:30:00Z',
      end_time: '2024-01-15T10:33:00Z',
      environment: '测试环境'
    }
    
    reportItems.value = [
      {
        name: '用户注册功能测试',
        type: 'testcase',
        status: 'success',
        duration: 15000,
        start_time: '2024-01-15T10:30:00Z',
        error_message: null,
        retry_count: 0
      },
      {
        name: '用户登录功能测试',
        type: 'testcase',
        status: 'success',
        duration: 12000,
        start_time: '2024-01-15T10:30:15Z',
        error_message: null,
        retry_count: 0
      },
      {
        name: '用户注册UI自动化测试',
        type: 'script',
        status: 'failed',
        duration: 8000,
        start_time: '2024-01-15T10:30:30Z',
        error_message: 'Element not found: #register-button. The element selector "#register-button" could not be located on the page. This might be due to timing issues, incorrect selector, or the element not being rendered yet.',
        retry_count: 2
      },
      {
        name: '密码重置功能测试',
        type: 'testcase',
        status: 'success',
        duration: 10000,
        start_time: '2024-01-15T10:30:45Z',
        error_message: null,
        retry_count: 0
      },
      {
        name: '用户权限验证测试',
        type: 'testcase',
        status: 'failed',
        duration: 18000,
        start_time: '2024-01-15T10:31:00Z',
        error_message: 'Assertion failed: Expected status code 403, but got 200. The permission check did not work as expected.',
        retry_count: 1
      }
    ]
    
    // 初始化图表
    await nextTick()
    initCharts()
  } catch (error) {
    console.error('加载执行数据失败:', error)
    ElMessage.error('加载执行数据失败')
  }
}

const initCharts = () => {
  initOverviewChart()
  initTimelineChart()
  initPerformanceChart()
}

const initOverviewChart = () => {
  if (!overviewChartRef.value || !execution.value) return
  
  overviewChart = echarts.init(overviewChartRef.value)
  
  const data = [
    { name: '成功', value: execution.value.success_count, itemStyle: { color: '#67C23A' } },
    { name: '失败', value: execution.value.failed_count, itemStyle: { color: '#F56C6C' } },
    { name: '跳过', value: execution.value.skipped_count || 0, itemStyle: { color: '#E6A23C' } }
  ]
  
  const option = {
    title: {
      text: '执行结果分布',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        name: '执行结果',
        type: 'pie',
        radius: '60%',
        center: ['60%', '50%'],
        data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  overviewChart.setOption(option)
}

const initTimelineChart = () => {
  if (!timelineChartRef.value) return
  
  timelineChart = echarts.init(timelineChartRef.value)
  
  const data = reportItems.value.map((item, index) => ({
    name: item.name,
    value: [
      index,
      new Date(item.start_time).getTime(),
      new Date(item.start_time).getTime() + item.duration,
      item.duration
    ],
    itemStyle: {
      color: item.status === 'success' ? '#67C23A' : item.status === 'failed' ? '#F56C6C' : '#E6A23C'
    }
  }))
  
  const option = {
    title: {
      text: '执行时间线',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      formatter: (params: any) => {
        const item = reportItems.value[params.value[0]]
        return `${item.name}<br/>开始时间: ${formatTime(item.start_time)}<br/>耗时: ${formatDuration(item.duration)}<br/>状态: ${getStatusText(item.status)}`
      }
    },
    grid: {
      left: '15%',
      right: '10%',
      top: '15%',
      bottom: '10%'
    },
    xAxis: {
      type: 'time',
      axisLabel: {
        formatter: (value: number) => new Date(value).toLocaleTimeString('zh-CN')
      }
    },
    yAxis: {
      type: 'category',
      data: reportItems.value.map(item => item.name),
      axisLabel: {
        width: 150,
        overflow: 'truncate'
      }
    },
    series: [
      {
        type: 'custom',
        renderItem: (params: any, api: any) => {
          const categoryIndex = api.value(0)
          const start = api.coord([api.value(1), categoryIndex])
          const end = api.coord([api.value(2), categoryIndex])
          const height = api.size([0, 1])[1] * 0.6
          
          return {
            type: 'rect',
            shape: {
              x: start[0],
              y: start[1] - height / 2,
              width: end[0] - start[0],
              height: height
            },
            style: api.style()
          }
        },
        data
      }
    ]
  }
  
  timelineChart.setOption(option)
}

const initPerformanceChart = () => {
  if (!performanceChartRef.value) return
  
  performanceChart = echarts.init(performanceChartRef.value)
  
  const categories = reportItems.value.map(item => item.name)
  const durations = reportItems.value.map(item => Math.round(item.duration / 1000))
  
  const option = {
    title: {
      text: '执行耗时分析',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        const param = params[0]
        return `${param.name}<br/>耗时: ${param.value}秒`
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '15%',
      bottom: '25%'
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        rotate: 45,
        interval: 0,
        width: 100,
        overflow: 'truncate'
      }
    },
    yAxis: {
      type: 'value',
      name: '耗时(秒)'
    },
    series: [
      {
        name: '执行耗时',
        type: 'bar',
        data: durations,
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
  
  performanceChart.setOption(option)
}

const exportPDF = () => {
  ElMessage.info('PDF导出功能开发中...')
}

const exportExcel = () => {
  ElMessage.info('Excel导出功能开发中...')
}

// 辅助方法
const getStatusColor = (status: string) => {
  const colors = {
    success: 'success',
    failed: 'danger',
    skipped: 'warning',
    running: 'primary',
    cancelled: 'info'
  }
  return colors[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts = {
    success: '成功',
    failed: '失败',
    skipped: '跳过',
    running: '执行中',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const formatDuration = (ms: number) => {
  if (!ms) return '-'
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes > 0) {
    return `${minutes}分${remainingSeconds}秒`
  }
  return `${remainingSeconds}秒`
}

const formatDateTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN')
}

// 清理图表实例
const cleanup = () => {
  if (overviewChart) {
    overviewChart.dispose()
    overviewChart = null
  }
  if (timelineChart) {
    timelineChart.dispose()
    timelineChart = null
  }
  if (performanceChart) {
    performanceChart.dispose()
    performanceChart = null
  }
}

// 生命周期
onMounted(() => {
  loadExecutionData()
})

// 组件卸载时清理
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(cleanup)
</script>

<style scoped>
.execution-report-page {
  padding: 16px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-right {
  display: flex;
  gap: 12px;
}

.report-container {
  background: white;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid #ebeef5;
}

.report-title h1 {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.report-meta {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: #606266;
}

.report-section {
  margin-bottom: 40px;
}

.report-section h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  border-left: 4px solid #409EFF;
  padding-left: 16px;
}

.overview-chart {
  height: 400px;
}

.summary-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.stat-item.success {
  border-left-color: #67C23A;
}

.stat-item.danger {
  border-left-color: #F56C6C;
}

.stat-item.warning {
  border-left-color: #E6A23C;
}

.stat-item.primary {
  border-left-color: #409EFF;
}

.stat-label {
  font-size: 16px;
  color: #606266;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.timeline-chart {
  height: 400px;
}

.performance-analysis {
  margin-top: 16px;
}

.performance-chart {
  height: 400px;
}

.performance-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-card {
  text-align: center;
}

.error-message {
  color: #F56C6C;
  font-size: 13px;
  cursor: pointer;
}

.failure-analysis {
  margin-top: 16px;
}

.failure-summary {
  margin-bottom: 24px;
}

.failure-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 16px;
}

.failure-item {
  border-left: 4px solid #F56C6C;
}

.failure-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.failure-name {
  font-weight: bold;
  color: #303133;
}

.failure-content p {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}

.error-detail {
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #721c24;
  line-height: 1.5;
  margin-top: 8px;
}

.recommendation-card {
  height: 100%;
}

.recommendation-list {
  margin: 0;
  padding-left: 20px;
}

.recommendation-list li {
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.loading-container {
  background: white;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.el-breadcrumb {
  cursor: pointer;
}
</style>