<template>
  <div class="dashboard-container">
    <!-- 统计卡片区域 -->
    <div class="stats-grid">
      <div 
        v-for="item in title_list" 
        :key="item.id" 
        class="stat-card"
        :class="{ active: activeCard === item.name }"
        :style="{ '--active-color': item.color }"
        @click="sendEvent(item)"
      >
        <div class="stat-card-header">
          <div class="stat-icon" :style="{ background: gradient_dict[item.name], color: 'white' }">
            <component :is="getIcon(item.icon)"></component>
          </div>
          <div class="stat-trend">
            <span class="trend-icon positive">↗</span>
            <span class="trend-text" :style="{ color: item.color }">+12.5%</span>
          </div>
        </div>
        
        <div class="stat-content">
          <h3 class="stat-number">{{ formatNumber(item.total) }}</h3>
          <p class="stat-label">{{ item.title }}</p>
        </div>
        
        <div class="stat-footer">
          <div class="mini-chart">
            <svg width="100%" height="30" viewBox="0 0 100 30">
              <path 
                :d="generateMiniChart()" 
                fill="none" 
                :stroke="item.color" 
                stroke-width="2"
                opacity="0.6"
              />
              <path 
                :d="generateMiniChart()" 
                fill="none" 
                :stroke="item.color" 
                stroke-width="2"
                stroke-dasharray="3,3"
                opacity="0.3"
              />
            </svg>
          </div>
          <span class="stat-subtitle">较上周</span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="chart-section">
      <div class="chart-header">
        <div class="chart-title">
          <h2>数据趋势分析</h2>
          <p class="chart-subtitle">实时监控各项指标变化趋势</p>
        </div>
        <div class="chart-controls">
          <el-radio-group v-model="timeRange" size="small" @change="handleTimeRangeChange">
            <el-radio-button label="7d">近7天</el-radio-button>
            <el-radio-button label="30d">近30天</el-radio-button>
            <el-radio-button label="90d">近3个月</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      
      <div class="chart-container">
        <Charts />
      </div>
    </div>

    <!-- 快速操作区域 -->
    <div class="quick-actions">
      <div class="action-card" @click="navigateToPage('create')">
        <div class="action-icon">
          <el-icon><Plus /></el-icon>
        </div>
        <div class="action-content">
          <h4>创建测试</h4>
          <p>快速创建新的测试用例</p>
        </div>
      </div>
      
      <div class="action-card" @click="navigateToPage('report')">
        <div class="action-icon">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <div class="action-content">
          <h4>查看报告</h4>
          <p>查看最新的测试报告</p>
        </div>
      </div>
      
      <div class="action-card" @click="navigateToPage('system')">
        <div class="action-icon">
          <el-icon><Setting /></el-icon>
        </div>
        <div class="action-content">
          <h4>系统配置</h4>
          <p>管理系统设置和配置</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Charts from './chart.vue'
import * as iconPark from "@icon-park/vue-next";
import { Plus, DataAnalysis, Setting } from '@element-plus/icons-vue'
import {onMounted, ref} from 'vue'
import {getTitleCount} from "@/api/autotest/dashboard";
import {bus, busEvent} from "@/utils/bus-events";
import { useRouter } from 'vue-router'

const router = useRouter()

const title_list = ref([])
const activeCard = ref('')
const timeRange = ref('7d')

const icon_dict = {
  api: 'api', case: 'cubeFive', step: 'listNumbers', report: 'chartHistogram'
}
const color_dict = {
  api: '#3b82f6',      // 蓝色 - API接口
  case: '#10b981',     // 绿色 - 测试用例  
  step: '#f59e0b',     // 橙色 - 测试步骤
  report: '#ef4444'    // 红色 - 测试报告
}

// 渐变配色方案
const gradient_dict = {
  api: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
  case: 'linear-gradient(135deg, #10b981 0%, #047857 100%)', 
  step: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
  report: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
}

const getIcon = (iconName: string) => {
  const normalizedIconName = iconName.charAt(0).toUpperCase() + iconName.slice(1);
  return iconPark[normalizedIconName] || null;
}

const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const generateMiniChart = () => {
  // 生成简单的趋势线路径
  const points = []
  for (let i = 0; i <= 10; i++) {
    const x = i * 10
    const y = 15 + Math.sin(i * 0.5) * 10 + Math.random() * 5
    points.push(`${x},${y}`)
  }
  return `M ${points.join(' L ')}`
}

onMounted(() => {
  getTitleCount().then(response => {
    title_list.value = []
    response.data.forEach((item: { name: string; title: string; total: number; color: string; icon: string }) => {
      item.icon = icon_dict[item.name]
      item.color = color_dict[item.name]
    })
    title_list.value = response.data
    if (title_list.value.length > 0) {
      activeCard.value = title_list.value[0].name
      sendEvent(title_list.value[0])
    }
  })
})

const sendEvent = (row: any) => {
  activeCard.value = row.name
  bus.emit(busEvent.changeData, {type: 'dashboardCard', name: row.name});
};

// 快速操作跳转函数
const navigateToPage = (type: string) => {
  switch (type) {
    case 'create':
      // 跳转到API测试用例管理页面
      router.push('/api-test/case')
      break
    case 'report':
      // 跳转到API测试报告页面
      router.push('/api-test/report')
      break
    case 'system':
      // 跳转到系统管理页面
      router.push('/system/user')
      break
    default:
      break
  }
}

// 时间范围切换处理
const handleTimeRangeChange = (value: string) => {
  timeRange.value = value
  // 重新获取当前选中卡片的数据
  if (activeCard.value) {
    const currentCard = title_list.value.find(item => item.name === activeCard.value)
    if (currentCard) {
      // 发送事件更新图表，传递时间范围参数
      bus.emit(busEvent.changeData, {
        type: 'dashboardCard', 
        name: currentCard.name,
        timeRange: value
      });
    }
  }
}

</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  min-height: calc(100vh - 60px);
}

/* 深色模式适配 */
[data-theme="dark"] .dashboard-container {
  background: linear-gradient(135deg, #0a0a0a 0%, #141414 100%) !important;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  }

  &.active {
    border-color: var(--active-color);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }
}

/* 深色模式下的统计卡片 */
[data-theme="dark"] .stat-card {
  background: rgba(29, 30, 31, 0.98) !important;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;

  &:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4) !important;
  }

  &.active {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5) !important;
  }
}

.stat-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  
  .trend-icon {
    font-size: 16px;
    
    &.positive {
      color: #10b981;
    }
    
    &.negative {
      color: #ef4444;
    }
  }
  
  .trend-text {
    font-size: 12px;
    font-weight: 600;
    color: #10b981;
  }
}

.stat-content {
  margin-bottom: 20px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
  line-height: 1;
}

/* 深色模式下的统计数字 */
[data-theme="dark"] .stat-number {
  color: #e5eaf3 !important;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
  font-weight: 500;
}

/* 深色模式下的统计标签 */
[data-theme="dark"] .stat-label {
  color: #cfd3dc !important;
}

.stat-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mini-chart {
  flex: 1;
  height: 30px;
  margin-right: 12px;
}

.stat-subtitle {
  font-size: 12px;
  color: #9ca3af;
}

/* 深色模式下的副标题 */
[data-theme="dark"] .stat-subtitle {
  color: #a3a6ad !important;
}

.chart-section {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 深色模式下的图表区域 */
[data-theme="dark"] .chart-section {
  background: rgba(29, 30, 31, 0.98) !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.chart-title {
  h2 {
    font-size: 24px;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 8px 0;
  }
}

/* 深色模式下的图表标题 */
[data-theme="dark"] .chart-title h2 {
  color: #e5eaf3 !important;
}

.chart-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* 深色模式下的图表副标题 */
[data-theme="dark"] .chart-subtitle {
  color: #cfd3dc !important;
}

.chart-controls {
  .el-radio-group {
    --el-radio-button-checked-bg-color: #3b82f6;
    --el-radio-button-checked-border-color: #3b82f6;
  }
}

.chart-container {
  border-radius: 12px;
  overflow: hidden;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.action-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  }

  &:nth-child(1) .action-icon {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  }

  &:nth-child(2) .action-icon {
    background: linear-gradient(135deg, #10b981, #047857);
  }

  &:nth-child(3) .action-icon {
    background: linear-gradient(135deg, #f59e0b, #d97706);
  }
}

/* 深色模式下的快速操作卡片 */
[data-theme="dark"] .action-card {
  background: rgba(29, 30, 31, 0.98) !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;

  &:hover {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4) !important;
  }
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.action-content {
  h4 {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 4px 0;
  }

  p {
    font-size: 14px;
    color: #6b7280;
    margin: 0;
  }
}

/* 深色模式下的操作内容 */
[data-theme="dark"] .action-content {
  h4 {
    color: #e5eaf3 !important;
  }

  p {
    color: #cfd3dc !important;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .chart-section {
    padding: 20px;
  }

  .chart-header {
    flex-direction: column;
    gap: 16px;
  }

  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>
