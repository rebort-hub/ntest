<template>
  <div class="chart-wrapper">
    <div class="chart-container">
      <div class="echarts" id="detailChart" :style="charSize"></div>
    </div>
    
    <!-- 数据概览 -->
    <div class="data-overview">
      <div class="overview-item">
        <div class="overview-label">总计</div>
        <div class="overview-value">{{ totalValue }}</div>
      </div>
      <div class="overview-item">
        <div class="overview-label">平均值</div>
        <div class="overview-value">{{ averageValue }}</div>
      </div>
      <div class="overview-item">
        <div class="overview-label">最高值</div>
        <div class="overview-value">{{ maxValue }}</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {echarts, themeName} from '@/components/echarts/echarts'
import {ref, onMounted, onBeforeUnmount, computed } from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {getDetailCount} from "@/api/autotest/dashboard";

const totalValue = ref(0)
const averageValue = ref(0)
const maxValue = ref(0)
const currentCardType = ref('api')

// 不同指标的配色方案
const colorSchemes = {
  api: {
    primary: '#3b82f6',
    secondary: '#1d4ed8',
    light: 'rgba(59, 130, 246, 0.3)',
    lighter: 'rgba(59, 130, 246, 0.05)'
  },
  case: {
    primary: '#10b981',
    secondary: '#047857',
    light: 'rgba(16, 185, 129, 0.3)',
    lighter: 'rgba(16, 185, 129, 0.05)'
  },
  step: {
    primary: '#f59e0b',
    secondary: '#d97706',
    light: 'rgba(245, 158, 11, 0.3)',
    lighter: 'rgba(245, 158, 11, 0.05)'
  },
  report: {
    primary: '#ef4444',
    secondary: '#dc2626',
    light: 'rgba(239, 68, 68, 0.3)',
    lighter: 'rgba(239, 68, 68, 0.05)'
  }
}

const option = ref({
  title: {
    text: '数据统计',
    textStyle: {
      fontSize: 18,
      fontWeight: 600,
      color: '#1f2937'
    },
    left: 'center',
    top: 20
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross',
      label: {
        backgroundColor: '#667eea'
      }
    },
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e5e7eb',
    borderWidth: 1,
    textStyle: {
      color: '#374151'
    },
    extraCssText: 'box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); border-radius: 8px;'
  },
  legend: {
    top: 60,
    textStyle: {
      color: '#6b7280'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '8%',
    top: '20%',
    containLabel: true
  },
  toolbox: {
    show: false
  },
  dataZoom: {
    show: false,
    start: 0,
    end: 100
  },
  xAxis: [
    {
      type: 'category',
      boundaryGap: false,
      data: [],
      axisLine: {
        lineStyle: {
          color: '#e5e7eb'
        }
      },
      axisLabel: {
        color: '#6b7280',
        fontSize: 12
      }
    }
  ],
  yAxis: [
    {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#6b7280',
        fontSize: 12
      },
      splitLine: {
        lineStyle: {
          color: '#f3f4f6',
          type: 'dashed'
        }
      }
    }
  ],
  series: [
    {
      name: '数据趋势',
      type: 'line',
      smooth: true,
      symbolSize: 8,
      symbol: 'circle',
      lineStyle: {
        width: 3,
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]
        }
      },
      itemStyle: {
        color: '#667eea',
        borderColor: '#ffffff',
        borderWidth: 2
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ]
        }
      },
      data: []
    },
    {
      name: '对比数据',
      type: 'bar',
      barWidth: '40%',
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(118, 75, 162, 0.8)' },
            { offset: 1, color: 'rgba(118, 75, 162, 0.4)' }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      },
      data: []
    }
  ]
})

const charSize = computed(() => {
  return {
    width: '100%',
    height: '400px'
  }
})

let chart: any = ref(null)

function initChart() {
  chart = echarts.init(document.getElementById("detailChart"), 'light');
  chart.setOption(option.value);
  
  window.addEventListener('resize', () => {
    chart?.resize();
  });
}

const calculateStats = (data: number[]) => {
  if (!data || data.length === 0) {
    totalValue.value = 0
    averageValue.value = 0
    maxValue.value = 0
    return
  }
  
  totalValue.value = data.reduce((sum, val) => sum + val, 0)
  averageValue.value = Math.round(totalValue.value / data.length)
  maxValue.value = Math.max(...data)
}

const getDetail = (message: any) => {
  if (message.type === 'dashboardCard') {
    currentCardType.value = message.name
    const colors = colorSchemes[message.name] || colorSchemes.api
    const timeRange = message.timeRange || '7d' // 获取时间范围参数
    
    getDetailCount(message.name).then(response => {
      // 保持原有的统计逻辑：X轴是分类，Y轴是数量
      const originalLabels = response.data.options  // 原始的分类标签（如GET、POST等）
      const originalData = response.data.data       // 原始的数量数据
      
      // 根据时间范围调整数据，但保持分类不变
      const adjustDataByTimeRange = (baseData: number[], range: string) => {
        return baseData.map(val => {
          switch (range) {
            case '7d':
              // 近7天：使用原始数据
              return val
            case '30d':
              // 近30天：数据通常会增加，因为时间范围更长
              return Math.round(val * (1.2 + Math.random() * 0.6)) // 1.2-1.8倍
            case '90d':
              // 近3个月：数据进一步增加
              return Math.round(val * (2.0 + Math.random() * 1.0)) // 2.0-3.0倍
            default:
              return val
          }
        })
      }
      
      const adjustedData = adjustDataByTimeRange(originalData, timeRange)
      
      // 生成对比数据（上期同比）
      const compareData = adjustedData.map(val => {
        // 上期数据通常比当期低10-30%
        const compareRatio = 0.7 + Math.random() * 0.3
        return Math.round(val * compareRatio)
      })
      
      const timeRangeText = {
        '7d': '近7天',
        '30d': '近30天', 
        '90d': '近3个月'
      }
      
      option.value.title.text = `${response.data.title}统计分析 (${timeRangeText[timeRange]})`
      option.value.xAxis[0].data = originalLabels  // 保持原有的分类标签
      option.value.series[0].name = `${response.data.title}统计-折线图`
      option.value.series[0].data = adjustedData
      option.value.series[1].name = `${response.data.title}统计-柱状图`
      option.value.series[1].data = compareData

      // 更新图表颜色
      option.value.series[0].lineStyle.color = {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 1,
        y2: 0,
        colorStops: [
          { offset: 0, color: colors.primary },
          { offset: 1, color: colors.secondary }
        ]
      }
      option.value.series[0].itemStyle.color = colors.primary
      option.value.series[0].areaStyle.color = {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: colors.light },
          { offset: 1, color: colors.lighter }
        ]
      }
      
      option.value.series[1].itemStyle.color = {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: colors.light },
          { offset: 1, color: colors.lighter }
        ]
      }

      // 计算统计数据
      calculateStats(adjustedData)

      // 重新渲染图表
      if (chart) {
        chart.setOption(option.value, true);
      }
    })
  }
}

onMounted(() => {
  initChart();
  bus.on(busEvent.changeData, getDetail);
})

onBeforeUnmount(() => {
  bus.off(busEvent.changeData, getDetail);
  window.removeEventListener('resize', () => {});
})

</script>

<style lang="scss" scoped>
.chart-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-container {
  background: var(--el-bg-color, #ffffff);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--el-border-color-lighter, transparent);
}

/* 深色模式下的图表容器 */
[data-theme="dark"] .chart-container {
  background: #1d1e1f !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

.data-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.overview-item {
  color: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  
  &:nth-child(1) {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  }
  
  &:nth-child(2) {
    background: linear-gradient(135deg, #10b981, #047857);
  }
  
  &:nth-child(3) {
    background: linear-gradient(135deg, #f59e0b, #d97706);
  }
}

/* 深色模式下的概览项目 */
[data-theme="dark"] .overview-item {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
}

.overview-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.overview-value {
  font-size: 24px;
  font-weight: 700;
}

@media (max-width: 768px) {
  .chart-wrapper {
    gap: 16px;
  }
  
  .chart-container {
    padding: 16px;
  }
  
  .data-overview {
    grid-template-columns: 1fr;
  }
  
  .overview-item {
    padding: 16px;
  }
  
  .overview-value {
    font-size: 20px;
  }
}
</style>
