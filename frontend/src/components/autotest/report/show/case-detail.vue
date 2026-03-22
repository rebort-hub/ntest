<template>
  <div>
    <el-collapse v-model="defaultShowDetailInfo">
      <el-collapse-item name="error_msg">
        <template #title>
          <div class="el-collapse-item-title"> {{ '错误信息：' }}</div>
        </template>
        <pre class="el-collapse-item-content" style="overflow: auto; color: #FA6E86">{{ reportCaseData.error_msg }}</pre>
      </el-collapse-item>

      <el-collapse-item name="caseInfo">
        <template #title>
          <div class="el-collapse-item-title"> {{ '用例信息：' }}</div>
        </template>
        <el-descriptions class="margin-top" :column="2" border>
          <el-descriptions-item>
            <template #label> 用例名 </template>
            {{ reportCaseData.name }}
          </el-descriptions-item>

          <el-descriptions-item>
            <template #label> 执行结果 </template>
            <el-tag
                size="small"
                :type="resultTagMapping[reportCaseData.result]"
            >{{ resultMapping[reportCaseData.result] }}</el-tag>
          </el-descriptions-item>

          <el-descriptions-item>
            <template #label> 开始时间 </template>
            {{ reportCaseData.summary.time.start_at }}
          </el-descriptions-item>

          <el-descriptions-item>
            <template #label> 结束时间 </template>
            {{ reportCaseData.summary.time.end_at }}
          </el-descriptions-item>

          <el-descriptions-item>
            <template #label>
              <span> 执行用例耗时 </span>
              <el-tooltip class="item" effect="dark" placement="top-start" content="执行此用例耗费的时间，不包含数据解析、数据写库时间">
                <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
              </el-tooltip>
            </template>
            {{ reportCaseData.summary.time.case_duration }} 秒
          </el-descriptions-item>

          <el-descriptions-item>
            <template #label>
              <span> 执行步骤总耗时 </span>
              <el-tooltip class="item" effect="dark" placement="top-start" content="执行此用例下的所有步骤的总耗时">
                <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
              </el-tooltip>
            </template>
            {{ reportCaseData.summary.time.step_duration }} 毫秒
          </el-descriptions-item>

          <el-descriptions-item>
            <template #label>
              <span> 执行测试总共耗时 </span>
              <el-tooltip class="item" effect="dark" placement="top-start" content="包含数据解析、数据写库时间">
                <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
              </el-tooltip>
            </template>
            {{ reportCaseData.summary.time.all_duration }} 秒
          </el-descriptions-item>

        </el-descriptions>
      </el-collapse-item>

      <el-collapse-item name="stepInfo">
        <template #title>
          <div class="el-collapse-item-title"> {{ '步骤统计：' }}</div>
        </template>
        <el-descriptions class="margin-top" :column="3" border>

          <el-descriptions-item>
            <template #label> 通过数量 </template>
            <el-tag
                size="small"
                :type="resultTagMapping['success']"
            >{{ reportCaseData.summary.stat.success }}</el-tag>
          </el-descriptions-item>

          <el-descriptions-item>
            <template #label> 不通过数量 </template>
            <el-tag
                size="small"
                :type="resultTagMapping['fail']"
            >{{ reportCaseData.summary.stat.fail }}</el-tag>
          </el-descriptions-item>

          <el-descriptions-item>
            <template #label> 错误数量 </template>
            <el-tag
                size="small"
                :type="resultTagMapping['error']"
            >{{ reportCaseData.summary.stat.error }}</el-tag>
          </el-descriptions-item>

          <el-descriptions-item>
            <template #label> 跳过数量 </template>
            <el-tag
                size="small"
                :type="resultTagMapping['skip']"
            >{{ reportCaseData.summary.stat.skip }}</el-tag>
          </el-descriptions-item>

          <el-descriptions-item>
            <template #label> 总数 </template>
            <el-tag
                size="small"
            >{{ reportCaseData.summary.stat.total }}</el-tag>
          </el-descriptions-item>

        </el-descriptions>
      </el-collapse-item>

      <el-collapse-item name="variables">
        <template #title>
          <div class="el-collapse-item-title"> {{ '变量信息：' }}</div>
        </template>

        <el-table
            :data="objectToList(reportCaseData.case_data.variables)"
            size="small"
            stripe
        >
          <el-table-column prop="num" label="序号" align="center" min-width="10%">
            <template #default="scope">
              <span> {{ scope.$index + 1 }} </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip prop="key" label="变量名称" align="center" min-width="45%">
            <template #default="scope">
              <span>
                {{ scope.row.key }}
              </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip prop="value" label="变量值" align="center" min-width="45%">
            <template #default="scope">
              <span>
                {{ scope.row.value }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-collapse-item>

      <el-collapse-item name="headers">
        <template #title>
          <div class="el-collapse-item-title"> {{ '头部信息：' }}</div>
        </template>

        <el-table :data="objectToList(reportCaseData.case_data.headers)" size="small" stripe>
          <el-table-column prop="num" label="序号" align="center" min-width="10%">
            <template #default="scope">
              <span> {{ scope.$index + 1 }} </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip prop="key" label="key" align="center" min-width="45%">
            <template #default="scope">
              <span>
                {{ scope.row.key }}
              </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip prop="value" label="value" align="center" min-width="45%">
            <template #default="scope">
              <span>
                {{ scope.row.value }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-collapse-item>

      <el-collapse-item name="skipIf">
        <template #title>
          <div class="el-collapse-item-title"> {{ '跳过条件：' }}</div>
        </template>

        <skipIfView
            ref="skipIfView"
            :test-type="testType"
            :current-data="reportCaseData.case_data.skip_if"
            :env-list="[]"
            :use-type="'case'"
        />
      </el-collapse-item>

    </el-collapse>
  </div>
</template>

<script setup lang="ts">
import {Help} from "@icon-park/vue-next";
import skipIfView from '@/components/input/skip-if.vue'
import {GetReportCaseDetail} from "@/api/autotest/report";
import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";

const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})

const reportCaseData = ref({
  name: '',
  result: '',
  error_msg: '',
  summary: {
    "stat": {
      "fail": 0,
      "skip": 0,
      "error": 0,
      "total": 0,
      "success": 0,
      "response_time": {
        "slow": [],
        "very_slow": []
      }
    },
    "time": {
      "end_at": "",
      "start_at": "",
      "all_duration": 0,
      "case_duration": 0,
      "step_duration": 0
    },
    "result": ""
  },
  case_data: {
    "id": 15,
    "name": "",
    "headers": {},
    "run_env": "",
    "skip_if": [],
    "run_type": "",
    "suite_id": 0,
    "run_times": 1,
    "variables": {}
  }
})
const defaultShowDetailInfo =  ['error_msg', 'caseInfo', 'stepInfo', reportCaseData.value.error_msg ? 'error_msg' : '']
const resultMapping = {waite: '等待', running: '执行中', fail: '不通过', success: '通过', skip: '跳过', error: '报错'}
const resultTagMapping = {waite: 'info', running: '', fail: 'danger', success: 'success', skip: 'info', error: 'warning'}

const objectToList = (variables) => {
  let newVariables = []
  Object.keys(variables).forEach(key => {
    newVariables.push({key: key, value: variables[key]})
  })
  return newVariables
}

const getReportCaseDetail = (dataId) => {
  GetReportCaseDetail(props.testType, {id: dataId}).then(response => {
    reportCaseData.value = response.data
  })
}

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'show-report-case-detail') {
    getReportCaseDetail(message.reportCaseId)
  }
}

</script>

<style scoped lang="scss">
.el-collapse-item-title {
  font-weight: 600;
  font-size: 15px;
  margin-left: 10px;
  color: #409eff
}

</style>
