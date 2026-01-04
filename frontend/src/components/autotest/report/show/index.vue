<template>
  <div class="layout-container">
    <!-- 无测试报告数据，或者测试报告中没有运行数据 -->
    <!--    <div v-show="!reportSummary || reportSummary.stat.test_case.total === 0" class="str">-->
    <!--      无运行数据或所有运行数据均已跳过-->
    <!--    </div>-->

    <!-- 有数据 -->
    <div v-show="reportSummary && reportSummary.stat.count.step > 0">
      <!-- 第一行，头部信息 -->
      <div class="report-header">
        <span style="float: left;font-size: 13px;color: #3a8ee6;margin-left: 10px">
          <span v-if="testType !== 'app'" style="margin-right: 20px"
          >运行环境: {{runEnvDict[reportSummary.env.code] }}</span>
          <span style="margin-right: 20px">执行模式: {{ report.is_async === 1 ? '并行运行' : '串行运行' }}</span>
          <span style="margin-right: 20px">开始时间: {{ paramsISOTime(report.create_time) }}</span>
          <!-- 执行耗时保留3为小数 -->
          <span style="margin-right: 20px">总共耗时: {{
              reportSummary.time.all_duration ? reportSummary.time.all_duration.toString().slice(0, 5) : '-'
            }} 秒</span>

        </span>
        <span style="float: right;font-size: 13px;color: #3a8ee6">
              <span v-if="report.run_type == 'api'">
                <el-button type="primary" size="small" @click.native="saveAsCase">存为用例</el-button>
                <el-tooltip class="item" effect="dark" placement="top-start">
                  <template #content>
                    <div>1、把当前报告对应的接口转为用例</div>
                    <div>2、保存成功后，新增后的用例归属在当前报告所属服务的【接口用例集】类型的用例集下</div>
                  </template>
                  <span style="margin-right: 20px;color: #409EFF"><Help></Help></span>
                </el-tooltip>
              </span>

              <el-button v-show="report.status === 1" type="danger" size="small" @click="changeReportStepStatus()">中断测试执行</el-button>

              <el-button
                  v-if="reportSummary.result !== 'success'"
                  type="primary"
                  size="small"
                  @click.native="showHitDrawer"
              >记录问题</el-button>

              <el-button type="primary" size="small" @click="showPythonScript = true">Python脚本</el-button>

              <el-button type="primary" size="small" @click="showReRunDialog">重跑</el-button>

          <!-- 删除报告 -->
            <el-popover :visible="checkDeleteIsShow" placement="top" popper-class="down-popover" width="450px">
              确定删除所选中的测试报告?
              <div style="color: red">
                1、关联了问题记录的测试报告不会被删除 <br>
                2、触发方式为【定时任务】或者【流水线】的，只有管理员能删除
              </div>
              <div style="text-align: right; margin-right: 10px">
                <el-button size="small" type="text" @click="checkDeleteIsShow = false">取消</el-button>
                <el-button type="primary" size="small" @click="deleteReport">确定</el-button>
              </div>
              <template #reference>
                <el-button
                    type="danger"
                    size="small"
                    style="margin-right: 5px"
                    @click="checkDeleteIsShow = true"
                >删除
                </el-button>
              </template>
            </el-popover>

          <el-button style="text-align: right; margin-right: 10px" type="primary" size="small" @click="showReportStat = true">查看统计</el-button>
          </span>
      </div>

    </div>

    <!-- 用例/步骤列表查看 -->
    <showCaseAndStepListView :test-type="testType"/>

    <!-- 记录问题 -->
    <addHitDrawer/>

    <!-- 打开用例 -->
    <editCaseDrawer :test-type="testType" :project-id="report.project_id"/>

    <selectRunEnv :test-type="testType" :business-id="project.business_id"></selectRunEnv>
    <showRunProcess :test-type="testType"></showRunProcess>

    <el-drawer
        title="脚本管理"
        size="85%"
        :append-to-body="true"
        v-model="showPythonScript"
    >
      <pythonScriptIndex/>
    </el-drawer>

    <el-drawer
        title="报告统计"
        size="85%"
        :append-to-body="true"
        v-model="showReportStat"
    >
      <div>
        <el-collapse v-model="defaultShowDetailInfo">
        <el-collapse-item name="reportInfo">
          <template #title>
            <div class="el-collapse-item-title"> {{ '报告统计：' }}</div>
          </template>
          <el-descriptions class="margin-top" :column="2" border>
            <el-descriptions-item>
              <template #label> 用例名 </template>
              {{ report.name }}
            </el-descriptions-item>
          </el-descriptions>
        </el-collapse-item>

        <el-collapse-item name="caseInfo">
          <template #title>
            <div class="el-collapse-item-title"> {{ '用例统计：' }}</div>
          </template>
          <el-descriptions class="margin-top" :column="2" border>
            <el-descriptions-item>
              <template #label> 执行用例 </template>
              {{ reportSummary.stat.test_case.total }}条
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 通过用例 </template>
              {{reportSummary.stat.test_case.success}} 条
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 不通过用例 </template>
              {{reportSummary.stat.test_case.fail}} 条
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 报错用例 </template>
              {{reportSummary.stat.test_case.error}} 条
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 通过率 </template>
              {{(reportSummary.stat.test_case.success / reportSummary.stat.test_case.total).toFixed(6) * 100}} %
            </el-descriptions-item>

          </el-descriptions>
        </el-collapse-item>

        <el-collapse-item name="stepInfo">
          <template #title>
            <div class="el-collapse-item-title"> {{ '步骤统计：' }}</div>
          </template>
          <el-descriptions class="margin-top" :column="3" border>
            <el-descriptions-item>
              <template #label> 执行步骤 </template>
              {{reportSummary.stat.test_step.total}} 个
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 通过步骤 </template>
              {{reportSummary.stat.test_step.success}} 个
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> {{ testType=='api' ? '涉及接口' : '涉及元素'}} </template>
              {{testType=='api' ? reportSummary.stat.count.api : reportSummary.stat.count.element}} 个
            </el-descriptions-item>

          </el-descriptions>
        </el-collapse-item>
        </el-collapse>
      </div>
    </el-drawer>

    <el-dialog
        v-model="reRunDialogIsShow"
        title="选择重跑维度"
        width="500"
    >

      <div style="margin-bottom: 20px;">
        <div style="margin-bottom: 5px;">
          <span style="color: red">1、重跑所有：重跑当前选择的报告下的所有用例</span>
        </div>
        <div style="margin-bottom: 5px;">
          <span style="color: red">2、重跑不通过的：重跑当前选择的报告下结果为不通过的用例</span>
        </div>
        <div style="margin-bottom: 5px;">
          <span style="color: red">3、不管选择的是什么维度的重跑，都会生成一份新的测试报告</span>
        </div>
      </div>

      <div style="margin: 10px">
        <el-radio v-model="reRunOption" label="all">重跑所有</el-radio>
        <br>
        <el-radio :disabled="report.is_passed" v-model="reRunOption" label="passed">重跑通过的, 并且<span style="color:red;">【不保存】</span>到当前测试报告下</el-radio>
        <br>
        <el-radio :disabled="report.is_passed" v-model="reRunOption" label="failed-not-cover">重跑不通过的, 并且<span style="color:red;">【不保存】</span>到当前测试报告下</el-radio>
        <br>
        <el-radio :disabled="report.is_passed" v-model="reRunOption" label="failed-and-cover">重跑不通过的, 并把测试结果<span style="color:red;">【保存】</span>到当前测试报告下</el-radio>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" size="small" @click="clickReRun()">确定重跑</el-button>
          <el-button size="small" @click="reRunDialogIsShow = false">取消</el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount} from "vue";
import {Help} from "@icon-park/vue-next";
import {useRoute} from "vue-router"
import {
  GetReport,
  DeleteReport,
  ReportAsCase,
  ChangeReportStepStatus,
  GetReportRerunCaseList
} from "@/api/autotest/report";import {GetProject} from "@/api/autotest/project";
import {GetRunEnvList} from "@/api/config/run-env";
import {bus, busEvent} from "@/utils/bus-events";

import addHitDrawer from '@/views/assist/hits/drawer.vue'
import editCaseDrawer from '@/components/autotest/case/edit-drawer.vue'
import showCaseAndStepListView from './case-and-step-list.vue'
import selectRunEnv from "@/components/select-run-env.vue";
import showRunProcess from "@/components/show-run-process.vue";
import pythonScriptIndex from '@/views/assist/script/index.vue'
import {GetServerList} from "@/api/autotest/device-server";
import {GetPhoneList} from "@/api/autotest/device-phone";
import {GetCase, GetCaseFromProject, RunCase} from "@/api/autotest/case";
import {RunTask} from "@/api/autotest/task";
import {RunCaseSuite} from "@/api/autotest/case-suite";
import {RunApi} from "@/api/autotest/api";
import {paramsISOTime} from "@/utils/parse-data";
import {ElMessage} from "element-plus";

const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})

const route = useRoute()
const reportId = route.query.id
const report = ref({
  name: '',
  create_time: '',
  project_id: undefined,
  is_async: 0,
  run_type: '',
  trigger_id: [],
  temp_variables: []
})
const reportSummary = ref({
  result: 'success',
  stat: {
    test_case: {fail: 0, skip: 0, error: 0, total: 1, success: 0},
    test_step: {fail: 0, skip: 0, error: 0, total: 0, success: 0},
    count: {api: 0, step: 0, element: 0}
  },
  time: {end_at: '', start_at: '', case_duration: 0, step_duration: 0, all_duration: 0},
  env: {code: '', name: ''}
})

const runEnvList = ref([])
const runEnvDict = ref({})
const checkDeleteIsShow = ref(false)
const showPythonScript = ref(false)
const caseChartData = ref({
  columns: ['caseName', 'num'],
  rows: [
    {'caseName': '成功步骤', num: 0},
    {'caseName': '失败步骤', num: 0},
    {'caseName': '错误步骤', num: 0},
    {'caseName': '跳过步骤', num: 0}
  ]
})
const suiteChartData = ref({
  columns: ['name', 'num'],
  rows: [
    {'name': '成功case', 'num': 0}, {'name': '失败case', 'num': 0}
  ]
})

const project = ref({
  business_id: undefined
})

const triggerFrom = 'show-report'
const reRunDialogIsShow = ref(false)
const reRunIdList = ref([])
const reRunOption = ref('failed-and-cover')
const insert_to = ref()
const showReportStat = ref(false)
const defaultShowDetailInfo = ['reportInfo', 'caseInfo', 'stepInfo']

const getReport = (reportId: any) => {
  GetReport(props.testType, {id: reportId}).then(response => {
    report.value = response.data
    reportSummary.value = response.data.summary

    bus.emit(busEvent.drawerIsShow, {
      eventType: 'show-report-case-list',
      content: {id: reportId, runType: response.data.run_type}
    })

    // 渲染饼图需要的数据, 如果是没完成的报告，则饼图统计为0
    if (reportSummary.value.stat) {
      caseChartData.value['rows'][0]['num'] = reportSummary.value.stat.test_step.success
      caseChartData.value['rows'][1]['num'] = reportSummary.value.stat.test_step.fail
      caseChartData.value['rows'][2]['num'] = reportSummary.value.stat.test_step.error
      caseChartData.value['rows'][3]['num'] = reportSummary.value.stat.test_step.skip
      suiteChartData.value['rows'][0]['num'] = reportSummary.value.stat.test_case.success
      suiteChartData.value['rows'][1]['num'] = reportSummary.value.stat.test_case.fail
    }
  })
}

const deleteReport = () => {
  DeleteReport(props.testType, {id_list: [reportId]}).then(response => {
    if (response) {
      // window.opener = null;
      // window.open('about:blank', '_self')
      window.close();
    }
  })
}

const changeReportStepStatus = () => {
  ChangeReportStepStatus(props.testType, {report_id: report.value.id, status: 'stop'}).then(response => {
    // location.reload(); // 刷新当前页面
  })
}

const getRunEnvList = () => {
  GetRunEnvList({page_no: 1, page_size: 99999}).then(response => {
    runEnvList.value = response.data.data
    runEnvList.value.forEach((env: { code: string | number; name: any; }) => {
      runEnvDict.value[env.code] = env.name
    })
  })
}

const showHitDrawer = () => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'hit',
    content: {
      date: reportSummary.value.time.start_at,
      test_type: reportSummary.value.run_type,
      run_env: reportSummary.value.env.code,
      report_id: reportId,
      project_id: report.value.project_id
    }
  })
}

const saveAsCase = () => {
  ReportAsCase(props.testType, {id: reportId}).then(response => {
  })
}

const getProjectAndSendEvent = () => {
  GetProject(props.testType, {id: report.value.project_id}).then(response => {
    project.value = response.data

    if (report.value.run_type === 'case') {
      const tempVariables = report.value.temp_variables
      if (tempVariables) { // 本身就有临时参数
        sendReRun(tempVariables)
      } else { // 没有就获取用例的数据
        if (report.value.trigger_id.length === 1) {
          GetCase(props.testType, {id: report.value.trigger_id[0]}).then(response => {
            const case_data = response.data
            sendReRun({
              skip_if: case_data.skip_if, variables: case_data.variables,
              run_times: case_data.run_times, headers: case_data.headers
            })
          })
        } else {
          sendReRun(null)
        }
      }
    } else {
      sendReRun(null)
    }
  })
}

const sendReRun = (tempRunArgs: any) => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'select-run-env',
    triggerFrom: triggerFrom,
    showSelectRunModel: ['task', 'suite'].indexOf(report.value.run_type) !== -1,
    runName: report.value.name,
    business_id: project.value.business_id,
    runArgs: tempRunArgs,
    runEnv: report.value.summary.env.code
  })
}

const showReRunDialog = () => {
  insert_to.value = undefined
  reRunOption.value = report.value.is_passed ? 'all' : 'failed-and-cover'
  reRunDialogIsShow.value = true
}

const clickReRun = () => {
  if(reRunOption.value === "all") {
    reRunIdList.value = report.value.trigger_id
  }else {
    if(reRunOption.value === "failed-and-cover") {
      insert_to.value = report.value.id
    }else {
      insert_to.value = undefined
    }
    GetReportRerunCaseList(props.testType, {
      id: report.value.id,
      result: reRunOption.value.includes("failed") ? 'failed' : 'passed'
    }).then((response) => {
      if (response.data.length === 0) {
        ElMessage.warning('当前报告没有失败的用例')
      }
      reRunIdList.value = response.data
    })
  }

  if (props.testType === 'app') {
    if (busEvent.data.runServerList.length < 1) {
      GetServerList({page_no: 1, page_size: 99999}).then(response => {
        busEvent.data.runServerList = response.data.data
      })
    }

    if (busEvent.data.runPhoneList.length < 1) {
      GetPhoneList({page_no: 1, page_size: 99999}).then(response => {
        busEvent.data.runPhoneList = response.data.data
      })
    }
  }

  getProjectAndSendEvent()
}

const getRunUrl = () => {
  const run_type = report.value.run_type
  if (reRunOption.value !== 'all'){
    return RunCase
  }
  return run_type === 'task' ? RunTask
      : run_type === 'suite' ? RunCaseSuite
          : run_type === 'case' ? RunCase
              : RunApi
}

const reRun = (runConf) => {
  const runUrl = getRunUrl()
  runUrl(props.testType, {
    id_list: reRunIdList.value, // report.value.trigger_id,
    env_list: runConf.runEnv,
    is_async: runConf.runType,
    browser: runConf.browser,
    server_id: runConf.runServer,
    phone_id: runConf.runPhone,
    no_reset: runConf.noReset,
    temp_variables: runConf.temp_variables,
    insert_to: insert_to.value,
    'trigger_type': 'page'
  }).then(response => {
    if (response) {
      bus.emit(busEvent.drawerIsShow, {
        eventType: 'run-process',
        batch_id: response.data.batch_id,
        report_id: response.data.report_id
      })
    }
  })
  reRunDialogIsShow.value = false
}

onMounted(() => {
  getReport(reportId)
  getRunEnvList()

  bus.on(busEvent.drawerIsShow, showCaseEditor);
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, showCaseEditor);
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'select-run-env' && message.triggerFrom === triggerFrom) {
    reRun(message)
  }
}

const showCaseEditor = (message: any) => {
  if (message.eventType === 'report-show-edit-case') {
    GetCaseFromProject(props.testType, {id: message.content.caseId}).then(response => {
      project.value = response.data.project
      bus.emit(busEvent.drawerIsShow, {
        eventType: 'edit-case',
        content: JSON.parse(JSON.stringify(response.data.case))
      })
    })
  }
}

</script>

<style scoped lang="scss">
.str {
  font-size: 30px;
  text-align: center;
  margin-top: 10%;
}

.report-header {
  margin-top: 10px;
}

.el-collapse-item-title {
  font-weight: 600;
  font-size: 15px;
  margin-left: 10px;
  color: #409eff
}
</style>
