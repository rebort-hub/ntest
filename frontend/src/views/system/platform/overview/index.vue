<template>
  <div class="overview-container">
    <!-- 时间选择器区域 -->
    <div class="time-selector-section">
      <div class="section-title">
        <el-icon><Calendar /></el-icon>
        <span>时间范围</span>
      </div>
      <el-radio-group v-model="timeSlot" size="default" @change="getOverviewData" class="time-radio-group">
        <el-radio-button v-for="(value, key) in timeSlotMapping" :key="key" :label="key"/>
      </el-radio-group>
    </div>

    <!-- 统计卡片区域 -->
    <div class="cards-section">
      <div class="section-title">
        <el-icon><DataAnalysis /></el-icon>
        <span>核心指标</span>
      </div>
      <div class="cards-grid">
        <Card v-for="row in useCardRes" :key="row.title" :row="row"/>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="chart-section">
      <div class="section-title">
        <el-icon><TrendCharts /></el-icon>
        <span>趋势分析</span>
      </div>
      <div class="chart-container">
        <overviewChart :chart-data="useChartRes" :key="useChartRes.options_list"/>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref} from "vue";
import { Calendar, DataAnalysis, TrendCharts } from '@element-plus/icons-vue'
import Card from '@/components/card/index.vue'
import overviewChart from './chart.vue'
import {GetUseCard, GetUseChart} from "@/api/autotest/stat";

const timeSlot = ref('近7天')
const timeSlotMapping = {'近7天': -7, '近14天': -14, '近30天': -30, '近90天': -90, '近180天': -180, '近360天': -360}
const useCardRes = ref([
    {
      title: '人工触发次数',
      color: '#36b9cc',
      icon: 'everyUser',
      total: 0
    },
    {
      title: '人工通过率',
      color: '#4e73df',
      icon: 'chartLine',
      total: 0
    },
    {
      title: '巡检次数',
      color: '#1cc88a',
      icon: 'calendar',
      total: 0
    },
    {
      title: '巡检通过率',
      color: '#f6c23e',
      icon: 'chartLine',
      total: 0
    }
])
const useChartRes = ref({
  'options_list': [],
  'items': [
    {'name': '人工触发次数', 'type': 'bar', 'data': 0},
    {'name': '人工通过次数', 'type': 'bar', 'data': 0},
    {'name': '巡检次数', 'type': 'bar', 'data': 0},
    {'name': '巡检通过次数', 'type': 'bar', 'data': 0}
  ]
})
const getOverviewData = () => {
  getUseCard()
  getUseChart()
}


const getUseCard = () => {
  GetUseCard({time_slot: timeSlotMapping[timeSlot.value]}).then(response => {
    useCardRes.value[0].total = response.data.page_trigger_count
    useCardRes.value[1].total = response.data.page_trigger_pass_rate
    useCardRes.value[2].total = response.data.patrol_count
    useCardRes.value[3].total = response.data.patrol_pass_rate
  })
}

// 统计图
const getUseChart = () => {
  GetUseChart({time_slot: timeSlotMapping[timeSlot.value]}).then(response => {
    useChartRes.value = response.data
  })
}

onMounted(() => {
  getOverviewData()
})

</script>

<style scoped lang="scss">
.overview-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
  
  .el-icon {
    margin-right: 6px;
    color: #409eff;
    font-size: 14px;
  }
}

.time-selector-section {
  background: white;
  padding: 16px;
  border-radius: 6px;
  box-shadow: 0 1px 6px 0 rgba(0, 0, 0, 0.08);
  margin-bottom: 16px;
  
  .time-radio-group {
    .el-radio-button {
      margin-right: 6px;
      
      &:last-child {
        margin-right: 0;
      }
    }
  }
}

.cards-section {
  background: white;
  padding: 16px;
  border-radius: 6px;
  box-shadow: 0 1px 6px 0 rgba(0, 0, 0, 0.08);
  margin-bottom: 16px;
  
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
    margin-top: 6px;
  }
}

.chart-section {
  background: white;
  padding: 16px;
  border-radius: 6px;
  box-shadow: 0 1px 6px 0 rgba(0, 0, 0, 0.08);
  
  .chart-container {
    margin-top: 6px;
    border-radius: 4px;
    overflow: hidden;
  }
}

@media (max-width: 768px) {
  .overview-container {
    padding: 10px;
  }
  
  .time-selector-section,
  .cards-section,
  .chart-section {
    padding: 12px;
  }
  
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
