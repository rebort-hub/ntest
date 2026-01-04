<template>
  <el-dialog
    :model-value="modelValue"
    title="执行报告"
    width="1200px"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-if="execution" class="execution-report">
      <!-- 报告头部 -->
      <div class="report-header">
        <div class="report-title">
          <h2>{{ execution.suite_name }} - 执行报告</h2>
          <div class="report-meta">
            <span>执行时间: {{ formatDateTime(execution.start_time) }}</span>
            <span>总耗时: {{ formatDuration(execution.duration) }}</span>
            <span>执行者: {{ execution.executor_name }}</span>
          </div>
        </div>
        <div class="report-actions">
          <el-button @click="exportPDF">
            <el-icon><Document /></el-icon>
            导出PDF
          </el-button>
          <el-button @click="exportExcel">
            <el-icon><Download /></el-icon>
            导出Excel
          </el-button>
        </div>
      </div>

      <!-- 执行概览 -->
      <div class="report-section">
        <h3>执行概览</h3>
        <el-row :gutter="20">
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
              <div class="stat-item">
                <div class="stat-label">成功率</div>
                <div class="stat-value">{{ successRate }}%</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 执行时间线 -->
      <div class="report-section">
        <h3>执行时间线</h3>
        <div class="timeline-chart" ref="timelineChartRef"></div>
      </div>

      <!-- 详细结果 -->
      <div class="report-section">
        <h3>详细结果</h3>
        <el-table :data="reportItems" max-height="400">
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="name" label="执行项名称" min-width="200" />
          <el-table-column prop="type" label="类型" width="100" align="center">
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
          <el-table-column prop="error_message" label="错误信息" min-width="200">
            <template #default="{ row }">
              <span v-if="row.error_message" class="error-message">{{ row.error_message }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 失败分析 -->
      <div class="report-section" v-if="failedItems.length > 0">
        <h3>失败分析</h3>
        <div class="failure-analysis">
          <div class="failure-summary">
            <p>本次执行共有 {{ failedItems.length }} 个项目失败，主要失败原因分析如下：</p>
          </div>
          <div class="failure-items">
            <div
              v-for="(item, index) in failedItems"
              :key="index"
              class="failure-item"
            >
              <div class="failure-header">
                <h4>{{ item.name }}</h4>
                <el-tag type="danger" size="small">{{ item.type === 'testcase' ? '测试用例' : '自动化脚本' }}</el-tag>
              </div>
              <div class="failure-content">
                <p><strong>错误信息：</strong>{{ item.error_message }}</p>
                <p><strong>执行时间：</strong>{{ formatTime(item.start_time) }}</p>
                <p><strong>耗时：</strong>{{ formatDuration(item.duration) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 性能分析 -->
      <div class="report-section">
        <h3>性能分析</h3>
        <div class="performance-chart" ref="performanceChartRef"></div>
      </div>

      <!-- 建议和总结 -->
      <div class="report-section">
        <h3>建议和总结</h3>
        <div class="recommendations">
          <div class="recommendation-item" v-if="execution.failed_count > 0">
            <h4>失败项目处理建议</h4>
            <ul>
              <li>检查失败的测试用例和脚本，分析失败原因</li>
              <li>确认测试环境配置是否正确</li>
              <li>验证测试数据的有效性</li>
              <li>考虑增加重试机制或优化测试逻辑</li>
            </ul>
          </div>
          <div class="recommendation-item">
            <h4>性能优化建议</h4>
            <ul>
              <li>考虑增加并发执行数量以提高执行效率</li>
              <li>优化执行时间较长的测试项</li>
              <li>合理安排测试执行顺序</li>
            </ul>
          </div>
          <div class="recommendation-item">
            <h4>质量改进建议</h4>
            <ul>
              <li>定期维护和更新测试用例</li>
              <li>建立测试数据管理机制</li>
              <li>完善测试环境监控</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface Props {
  modelValue: boolean
  execution: any
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// 图表引用
const overviewChartRef = ref()
const timelineChartRef = ref()
const performanceChartRef = ref()

// 图表实例
let overviewChart: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null
let performanceChart: echarts.ECharts | null = null

// 计算属性
const successRate = computed(() => {
  if (!props.execution || props.execution.total_count === 0) return 0
  return Math.round((props.execution.success_count / props.execution.total_count) * 100)
})

const reportItems = computed(() => {
  // 模拟报告项数据
  return [
    {
      name: '用户注册功能测试',
      type: 'testcase',
      status: 'success',
      duration: 15000,
      start_time: '2024-01-15T10:30:00Z',
      error_message: null
    },
    {
      name: '用户登录功能测试',
      type: 'testcase',
      status: 'success',
      duration: 12000,
      start_time: '2024-01-15T10:30:15Z',
      error_message: null
    },
    {
      name: '用户注册UI自动化测试',
      type: 'script',
      status: 'failed',
      duration: 8000,
      start_time: '2024-01-15T10:30:30Z',
      error_message: 'Element not found: #register-button'
    },
    {
      name: '密码重置功能测试',
      type: 'testcase',
      status: 'success',
      duration: 10000,
      start_time: '2024-01-15T10:30:45Z',
      error_message: null
    }
  ]
})

const failedItems = computed(() => {
  return reportItems.value.filter(item => item.status === 'failed')
})

// 方法
const initCharts = async () => {
  await nextTick()
  initOverviewChart()
  initTimelineChart()
  initPerformanceChart()
}

const initOverviewChart = () => {
  if (!overviewChartRef.value || !props.execution) return
  
  overviewChart = echarts.init(overviewChartRef.value)
  
  const data = [
    { name: '成功', value: props.execution.success_count, itemStyle: { color: '#67C23A' } },
    { name: '失败', value: props.execution.failed_count, itemStyle: { color: '#F56C6C' } },
    { name: '跳过', value: props.execution.skipped_count || 0, itemStyle: { color: '#E6A23C' } }
  ]
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '执行结果',
        type: 'pie',
        radius: '70%',
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
    tooltip: {
      formatter: (params: any) => {
        const item = reportItems.value[params.value[0]]
        return `${item.name}<br/>开始时间: ${formatTime(item.start_time)}<br/>耗时: ${formatDuration(item.duration)}<br/>状态: ${getStatusText(item.status)}`
      }
    },
    xAxis: {
      type: 'time',
      axisLabel: {
        formatter: (value: number) => new Date(value).toLocaleTimeString('zh-CN')
      }
    },
    yAxis: {
      type: 'category',
      data: reportItems.value.map(item => item.name)
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
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        rotate: 45,
        interval: 0
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
    skipped: 'warning'
  }
  return colors[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts = {
    success: '成功',
    failed: '失败',
    skipped: '跳过'
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

// 监听对话框打开
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.execution) {
    initCharts()
  } else {
    cleanup()
  }
})

// 组件卸载时清理
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(cleanup)
</script>

<style scoped>
.execution-report {
  padding: 16px 0;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #ebeef5;
}

.report-title h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.report-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #606266;
}

.report-actions {
  display: flex;
  gap: 8px;
}

.report-section {
  margin-bottom: 32px;
}

.report-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  border-left: 4px solid #409EFF;
  padding-left: 12px;
}

.overview-chart {
  height: 300px;
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
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
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

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.timeline-chart {
  height: 300px;
}

.performance-chart {
  height: 300px;
}

.error-message {
  color: #F56C6C;
  font-size: 12px;
}

.failure-analysis {
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 6px;
  padding: 16px;
}

.failure-summary {
  margin-bottom: 16px;
}

.failure-summary p {
  margin: 0;
  color: #606266;
}

.failure-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.failure-item {
  background-color: white;
  border: 1px solid #f5c6cb;
  border-radius: 6px;
  padding: 12px;
}

.failure-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.failure-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.failure-content p {
  margin: 4px 0;
  font-size: 12px;
  color: #606266;
}

.recommendations {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.recommendation-item {
  background-color: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 6px;
  padding: 16px;
}

.recommendation-item h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.recommendation-item ul {
  margin: 0;
  padding-left: 20px;
}

.recommendation-item li {
  margin-bottom: 4px;
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
}
</style>