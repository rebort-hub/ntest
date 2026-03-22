<template>
  <div class="dashboard-container">
    <section class="hero-panel" :class="`hero-${dashboardStyle}`">
      <div class="hero-left">
        <p class="hero-kicker">N-Tester Dashboard</p>
        <h1 class="hero-title">{{ greetingText }}</h1>
        <p class="hero-desc">{{ todayLabel }}，聚焦关键测试指标，快速进入核心操作。</p>
        <div class="hero-meta">
          <div class="hero-meta-item">
            <span class="meta-label">总资源数</span>
            <span class="meta-value">{{ totalSummary }}</span>
          </div>
          <div class="hero-meta-item">
            <span class="meta-label">当前视图</span>
            <span class="meta-value">实时趋势</span>
          </div>
        </div>
      </div>
      <div class="hero-right">
        <div class="style-switch">
          <span
            v-for="item in styleOptions"
            :key="item.key"
            class="style-chip"
            :class="{ active: dashboardStyle === item.key }"
            @click="changeDashboardStyle(item.key)"
          >
            {{ item.label }}
          </span>
        </div>
        <div class="hero-action" @click="navigateToPage('create')">
          <el-icon><Plus /></el-icon>
          <span>新建测试</span>
        </div>
        <div class="hero-action" @click="navigateToPage('report')">
          <el-icon><DataAnalysis /></el-icon>
          <span>查看报告</span>
        </div>
        <div class="hero-action" @click="navigateToPage('system')">
          <el-icon><Setting /></el-icon>
          <span>系统配置</span>
        </div>
      </div>
    </section>

    <section class="kpi-strip">
      <div v-for="item in kpiItems" :key="item.key" class="kpi-item">
        <div class="kpi-head">
          <span class="kpi-name">{{ item.name }}</span>
          <span class="kpi-badge">{{ item.badge }}</span>
        </div>
        <div class="kpi-main">
          <span class="kpi-value">{{ item.value }}</span>
          <span class="kpi-trend" :class="item.trendClass">{{ item.trend }}</span>
        </div>
      </div>
    </section>

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
import {computed, onMounted, ref} from 'vue'
import {getTitleCount} from "@/api/autotest/dashboard";
import {bus, busEvent} from "@/utils/bus-events";
import { useRouter } from 'vue-router'

const router = useRouter()

const title_list = ref([])
const activeCard = ref('')
const timeRange = ref('7d')
const dashboardStyle = ref<'simple' | 'business' | 'vibrant'>('business')
const styleOptions = [
  { key: 'simple', label: '简洁' },
  { key: 'business', label: '商务' },
  { key: 'vibrant', label: '炫彩' }
]

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好，开始今天的测试巡检'
  if (hour < 18) return '下午好，关注执行趋势与质量变化'
  return '晚上好，回顾今天的测试结果'
})

const todayLabel = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

const totalSummary = computed(() => {
  return title_list.value.reduce((sum, item) => sum + Number(item.total || 0), 0)
})

const kpiItems = computed(() => {
  const source = title_list.value || []
  const getCount = (key: string) => Number(source.find((i: any) => i.name === key)?.total || 0)
  const apiTotal = getCount('api')
  const caseTotal = getCount('case')
  const stepTotal = getCount('step')
  const reportTotal = getCount('report')
  const casePerApi = apiTotal > 0 ? (caseTotal / apiTotal).toFixed(1) : '0.0'
  const stepPerCase = caseTotal > 0 ? (stepTotal / caseTotal).toFixed(1) : '0.0'
  const reportCoverage = caseTotal > 0 ? `${Math.min(100, Math.round((reportTotal / caseTotal) * 100))}%` : '0%'

  return [
    { key: 'k1', name: 'API / 用例比', value: casePerApi, trend: '↗ +6.2%', trendClass: 'up', badge: '结构健康' },
    { key: 'k2', name: '步骤密度', value: stepPerCase, trend: '↗ +3.8%', trendClass: 'up', badge: '稳定' },
    { key: 'k3', name: '报告覆盖率', value: reportCoverage, trend: '↘ -1.2%', trendClass: 'down', badge: '待优化' },
    { key: 'k4', name: '总资产规模', value: totalSummary.value, trend: '↗ +12.5%', trendClass: 'up', badge: '增长中' }
  ]
})

const changeDashboardStyle = (style: 'simple' | 'business' | 'vibrant') => {
  dashboardStyle.value = style
  localStorage.setItem('dashboardStyle', style)
}

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
  const savedStyle = localStorage.getItem('dashboardStyle')
  if (savedStyle === 'simple' || savedStyle === 'business' || savedStyle === 'vibrant') {
    dashboardStyle.value = savedStyle
  }
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
  padding: 18px;
  background:
    radial-gradient(circle at 8% 4%, rgba(59, 130, 246, 0.08), transparent 24%),
    radial-gradient(circle at 92% 8%, rgba(16, 185, 129, 0.08), transparent 22%),
    var(--system-container-background);
  border-radius: 14px;
  min-height: calc(100vh - 84px);
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  border-radius: 12px;
  margin-bottom: 16px;
  border: 1px solid var(--el-border-color-light, #ebeef5);
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--el-color-primary) 9%, #ffffff), #ffffff 45%),
    var(--el-bg-color, #ffffff);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
}

.hero-simple {
  background: var(--el-bg-color, #ffffff);
}

.hero-business {
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--el-color-primary) 9%, #ffffff), #ffffff 45%),
    var(--el-bg-color, #ffffff);
}

.hero-vibrant {
  background:
    linear-gradient(125deg, rgba(59, 130, 246, 0.22), rgba(16, 185, 129, 0.22) 48%, rgba(245, 158, 11, 0.2)),
    var(--el-bg-color, #ffffff);
}

.hero-left {
  min-width: 0;
}

.hero-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--el-color-primary);
  letter-spacing: 0.4px;
}

.hero-title {
  margin: 0;
  font-size: 24px;
  line-height: 1.25;
  color: var(--el-text-color-primary);
}

.hero-desc {
  margin: 8px 0 0;
  color: var(--el-text-color-regular);
  font-size: 13px;
}

.hero-meta {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.hero-meta-item {
  display: flex;
  flex-direction: column;
  padding: 8px 12px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--el-color-primary) 8%, transparent);
}

.meta-label {
  color: var(--el-text-color-secondary);
  font-size: 11px;
}

.meta-value {
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 700;
}

.hero-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.style-switch {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px;
  border: 1px solid var(--el-border-color-light, #ebeef5);
  border-radius: 10px;
  background: var(--el-bg-color);
}

.style-chip {
  font-size: 12px;
  color: var(--el-text-color-regular);
  padding: 4px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  &:hover {
    color: var(--el-color-primary);
  }
  &.active {
    color: var(--el-color-primary);
    background: color-mix(in srgb, var(--el-color-primary) 14%, transparent);
    font-weight: 600;
  }
}

.hero-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 34px;
  padding: 0 12px;
  border-radius: 10px;
  font-size: 13px;
  color: var(--el-text-color-primary);
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  cursor: pointer;
  transition: all 0.2s ease;
  &:hover {
    color: var(--el-color-primary);
    border-color: var(--el-color-primary-light-5);
    transform: translateY(-1px);
  }
}

/* 深色模式适配 */
[data-theme="dark"] .dashboard-container {
  background:
    radial-gradient(circle at 8% 4%, rgba(59, 130, 246, 0.14), transparent 24%),
    radial-gradient(circle at 92% 8%, rgba(16, 185, 129, 0.12), transparent 22%),
    var(--system-container-background) !important;
}

[data-theme="dark"] .hero-panel {
  border-color: var(--el-border-color, #4c4d4f);
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--el-color-primary) 18%, #141414), #141414 52%),
    var(--el-bg-color-overlay, #1d1e1f);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.34);
}

[data-theme="dark"] .style-switch {
  border-color: var(--el-border-color, #4c4d4f);
  background: var(--el-bg-color-overlay, #1d1e1f);
}

.kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.kpi-item {
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-light, #ebeef5);
  background: var(--el-bg-color, #ffffff);
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
}

.kpi-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.kpi-name {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.kpi-badge {
  font-size: 11px;
  color: var(--el-color-primary);
  background: color-mix(in srgb, var(--el-color-primary) 12%, transparent);
  border-radius: 999px;
  padding: 2px 7px;
}

.kpi-main {
  margin-top: 8px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.kpi-value {
  font-size: 24px;
  line-height: 1;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.kpi-trend {
  font-size: 12px;
  font-weight: 600;
  &.up {
    color: #10b981;
  }
  &.down {
    color: #f59e0b;
  }
}

[data-theme="dark"] .kpi-item {
  background: var(--el-bg-color-overlay, #1d1e1f);
  border-color: var(--el-border-color, #4c4d4f);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.28);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}

.stat-card {
  background: var(--el-bg-color, #ffffff);
  border-radius: 12px;
  padding: 18px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid var(--el-border-color-light, #ebeef5);
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.1);
  }

  &.active {
    border-color: var(--active-color);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--active-color) 16%, transparent), 0 10px 20px rgba(15, 23, 42, 0.1);
  }
}

/* 深色模式下的统计卡片 */
[data-theme="dark"] .stat-card {
  background: var(--el-bg-color-overlay, #1d1e1f) !important;
  border-color: var(--el-border-color, #4c4d4f) !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.34) !important;

  &:hover {
    box-shadow: 0 10px 22px rgba(0, 0, 0, 0.42) !important;
  }

  &.active {
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--active-color) 18%, transparent), 0 10px 22px rgba(0, 0, 0, 0.42) !important;
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
  font-size: 30px;
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
  background: var(--el-bg-color, #ffffff);
  border: 1px solid var(--el-border-color-light, #ebeef5);
  border-radius: 12px;
  padding: 18px;
  margin-bottom: 18px;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
}

/* 深色模式下的图表区域 */
[data-theme="dark"] .chart-section {
  background: var(--el-bg-color-overlay, #1d1e1f) !important;
  border-color: var(--el-border-color, #4c4d4f) !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.34) !important;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.chart-title {
  h2 {
    font-size: 20px;
    font-weight: 600;
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
  gap: 16px;
}

.action-card {
  background: var(--el-bg-color, #ffffff);
  border: 1px solid var(--el-border-color-light, #ebeef5);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.1);
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
  background: var(--el-bg-color-overlay, #1d1e1f) !important;
  border-color: var(--el-border-color, #4c4d4f) !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.34) !important;

  &:hover {
    box-shadow: 0 10px 22px rgba(0, 0, 0, 0.42) !important;
  }
}

.action-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
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
    padding: 12px;
  }

  .hero-panel {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-title {
    font-size: 20px;
  }

  .hero-right {
    width: 100%;
    flex-wrap: wrap;
    justify-content: flex-start;
  }

  .style-switch {
    width: 100%;
    justify-content: space-between;
  }

  .kpi-strip {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .chart-section {
    padding: 14px;
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
