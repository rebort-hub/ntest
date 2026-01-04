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
    default: '100%'
  }
})
const chart = ref()

const  initChart = () => {
  const newChart = getNewChart(chart.value)
  let option = {
    title: {
      text: props.chartData.title,
      left: 'center',
      top: 15,
      textStyle: {
        fontSize: 14,
        fontWeight: 500,
        color: '#303133'
      }
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      borderColor: '#409eff',
      borderWidth: 1,
      textStyle: {
        color: '#fff',
        fontSize: 12
      },
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      textStyle: {
        fontSize: 11,
        color: '#606266'
      }
    },
    series: [
      {
        name: props.chartData.title,
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: false
        },
        data: props.chartData.stat_list,
        color: ['#67c23a', '#f56c6c', '#e6a23c', '#409eff', '#909399']
      }
    ]
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
  width: 100%;
  height: 100%;
  border-radius: 4px;
}
</style>
