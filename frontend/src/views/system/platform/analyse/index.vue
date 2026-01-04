<template>
  <div class="analyse-container">
    <!-- 查询条件区域 -->
    <div class="query-section">
      <div class="section-title">
        <el-icon><Search /></el-icon>
        <span>查询条件</span>
      </div>
      <div class="query-form">
        <div class="form-row">
          <div class="form-item">
            <label>业务线</label>
            <el-select 
              v-model="queryItems.business_id" 
              filterable 
              placeholder="选择业务线" 
              size="default"
              class="form-control"
            >
              <el-option v-for="item in businessList" :key="item.id" :label="item.name" :value="item.id"/>
            </el-select>
          </div>
          
          <div class="form-item">
            <label>触发方式</label>
            <el-select 
              v-model="queryItems.trigger_type" 
              filterable 
              placeholder="选择触发方式" 
              size="default" 
              clearable
              class="form-control"
            >
              <el-option v-for="item in triggerTypeList" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </div>
          
          <div class="form-item">
            <label>时间范围</label>
            <el-date-picker
              v-model="timeList"
              type="daterange"
              unlink-panels
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              :shortcuts="pickerOptions"
              value-format="YYYY-MM-DD"
              size="default"
              class="form-control"
            />
          </div>
          
          <div class="form-item">
            <el-button type="primary" @click="getAnalyseChart()" size="default" class="query-btn">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分析结果区域 -->
    <div class="results-section">
      <div class="section-title">
        <el-icon><PieChart /></el-icon>
        <span>分析结果</span>
      </div>
      
      <div class="charts-grid">
        <!-- 执行统计卡片 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>执行次数统计</h3>
            <div class="chart-summary">
              <div class="summary-item">
                <span class="label">总计:</span>
                <span class="value total">{{ analyseChartRes.use_count.detail.all_count }}</span>
              </div>
              <div class="summary-item">
                <span class="label">通过:</span>
                <span class="value success">{{ analyseChartRes.use_count.detail.pass_count }}</span>
              </div>
              <div class="summary-item">
                <span class="label">失败:</span>
                <span class="value error">{{ analyseChartRes.use_count.detail.fail_count }}</span>
              </div>
              <div class="summary-item">
                <span class="label">通过率:</span>
                <span class="value rate">{{ getPassRate() }}%</span>
              </div>
            </div>
          </div>
          <div class="chart-content">
            <count-chart :key="analyseChartRes.use_count.stat" :chart-data="analyseChartRes.use_count.stat"/>
          </div>
        </div>

        <!-- 人员统计卡片 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>执行人员统计</h3>
          </div>
          <div class="chart-content">
            <count-chart :key="analyseChartRes.create.stat" :chart-data="analyseChartRes.create.stat"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, computed} from "vue";
import { Search, PieChart } from '@element-plus/icons-vue'
import countChart from './chart.vue'
import {GetAnalyseChart} from "@/api/autotest/stat";
import {GetBusinessList} from "@/api/config/business";

const queryItems = ref({
  business_id: undefined,
  trigger_type: undefined,
  start_time: undefined,
  end_time: undefined
})
const timeList = ref([])
const triggerTypeList = ref([
  {label: '页面', value: 'page'},
  {label: '流水线', value: 'pipeline'},
  {label: '定时任务', value: 'cron'}
])
const pickerOptions = [
  {
    text: '7天内',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: '30天内',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: '90天内',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
]
const analyseChartRes = ref({
  'use_count': {
    'stat': {
      'title': '执行次数统计',
      'stat_list': [
        {'name': '通过数量', 'value': 0},
        {'name': '不通过数量', 'value': 0}
      ]
    },
    'detail': {'all_count': 0, 'pass_count': 0, 'fail_count': 0}
  },
  'create': {
    'stat': {
      'title': '执行人员统计',
      'stat_list': [{'name': '', 'value': 0}]
    }
  }
})
const businessList = ref([])

const getPassRate = () => {
  const { all_count, pass_count } = analyseChartRes.value.use_count.detail
  if (all_count === 0) return '0.000'
  return ((pass_count / all_count) * 100).toFixed(3)
}

const getBusinessList = () => {
  if (businessList.value.length < 1) {
    GetBusinessList({page_no: 1, page_size: 99999}).then(response => {
      businessList.value = response.data.data
      queryItems.value.business_id = businessList.value[0].id
      getAnalyseChart()
    })
  }
}

const getAnalyseChart = () => {
  if (timeList.value && timeList.value.length > 0) {
    queryItems.value.start_time = timeList.value[0]
    queryItems.value.end_time = timeList.value[1]
  } else {
    queryItems.value.start_time = undefined
    queryItems.value.end_time = undefined
  }
  GetAnalyseChart(queryItems.value).then(response => {
    analyseChartRes.value = response.data
  })
}

onMounted(() => {
  getBusinessList()
})

</script>

<style scoped lang="scss">
.analyse-container {
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

.query-section {
  background: white;
  padding: 16px;
  border-radius: 6px;
  box-shadow: 0 1px 6px 0 rgba(0, 0, 0, 0.08);
  margin-bottom: 16px;
  
  .query-form {
    .form-row {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: end;
    }
    
    .form-item {
      display: flex;
      flex-direction: column;
      min-width: 180px;
      
      label {
        font-size: 12px;
        color: #606266;
        margin-bottom: 6px;
        font-weight: 500;
      }
      
      .form-control {
        width: 100%;
      }
      
      .query-btn {
        margin-top: 0;
        height: 28px;
        padding: 0 16px;
        font-size: 12px;
      }
    }
  }
}

.results-section {
  background: white;
  padding: 16px;
  border-radius: 6px;
  box-shadow: 0 1px 6px 0 rgba(0, 0, 0, 0.08);
  
  .charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 6px;
  }
  
  .chart-card {
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    overflow: hidden;
    
    .chart-header {
      background: #f8f9fa;
      padding: 12px 16px;
      border-bottom: 1px solid #e4e7ed;
      
      h3 {
        margin: 0;
        font-size: 14px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 8px;
      }
      
      .chart-summary {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        
        .summary-item {
          display: flex;
          align-items: center;
          gap: 3px;
          
          .label {
            font-size: 12px;
            color: #909399;
          }
          
          .value {
            font-weight: 500;
            font-size: 12px;
            
            &.total {
              color: #409eff;
            }
            
            &.success {
              color: #67c23a;
            }
            
            &.error {
              color: #f56c6c;
            }
            
            &.rate {
              color: #e6a23c;
            }
          }
        }
      }
    }
    
    .chart-content {
      padding: 16px;
      height: 320px;
    }
  }
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr !important;
  }
}

@media (max-width: 768px) {
  .analyse-container {
    padding: 10px;
  }
  
  .query-section,
  .results-section {
    padding: 12px;
  }
  
  .query-form .form-row {
    flex-direction: column;
    gap: 12px;
    
    .form-item {
      min-width: auto;
      width: 100%;
    }
  }
  
  .chart-card .chart-content {
    height: 260px;
  }
}
</style>
