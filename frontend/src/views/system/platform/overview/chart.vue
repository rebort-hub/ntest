<template>
  <div ref="chart" class="chart" :style="{height:height,width:width}" />
</template>

<script setup lang="ts">
import {onMounted, ref} from "vue";
import {getNewChart} from '@/components/echarts/echarts'
const props = defineProps({
  chartData: {
    type: Object,
    required: true
  },
  className: {
    type: String,
    default: 'chart'
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: innerHeight > 800 ? `${innerHeight * 0.5}px` : `${innerHeight * 0.45}px`
  }
})
const chart = ref()

const  initChart = () => {
  const newChart = getNewChart(chart.value) // echarts.init(chart.value, themeName)
  let option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      borderColor: '#409eff',
      borderWidth: 1,
      textStyle: {
        color: '#fff',
        fontSize: 12
      }
    },
    legend: {
      top: 8,
      textStyle: {
        fontSize: 11
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '8%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01],
      axisLine: {
        lineStyle: {
          color: '#e4e7ed'
        }
      },
      axisLabel: {
        color: '#606266',
        fontSize: 10
      },
      splitLine: {
        lineStyle: {
          color: '#f5f7fa',
          type: 'dashed'
        }
      }
    },
    yAxis: {
      type: 'category',
      axisLabel: {
        interval: 0,
        color: '#606266',
        fontSize: 10
      },
      axisLine: {
        lineStyle: {
          color: '#e4e7ed'
        }
      },
      data: props.chartData.options_list // ['公共业务线', 'xx业务线']
    },
    series: props.chartData.items.map((item, index) => ({
      ...item,
      barWidth: '60%',
      itemStyle: {
        borderRadius: [0, 2, 2, 0],
        color: ['#409eff', '#67c23a', '#e6a23c', '#f56c6c'][index % 4]
      }
    }))
  }

  newChart.setOption(option)
  
  // 响应式处理
  window.addEventListener('resize', () => {
    newChart.resize()
  })
}


onMounted(() => {
  initChart()
})


</script>

<style scoped lang="scss">
.chart {
  border-radius: 4px;
  background: #fff;
}
</style>
