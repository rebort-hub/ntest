<template>
  <div>
    <el-dialog
        width="85%"
        title="测试执行进度"
        v-model="processIsShow"
        :close-on-click-modal="false"
        append-to-body
    >
      <div style="margin-left: 20px; margin-right: 20px">
        <div style="text-align: center; margin-bottom: 5px">
          <el-button type="danger" @click="changeReportStepStatus(reportId, null,null,'stop')">中断所有用例的测试执行</el-button>
        </div>
        <el-steps
            :active="activeProcess"
            align-center
            finish-status="success"
            :process-status="statusMapping[activeStatus]"
        >
          <el-step title="触发执行"/>
          <el-step title="解析数据"/>
          <el-step title="执行测试"/>
          <el-step title="写入报告"/>
        </el-steps>

        <div>
          <div v-show="activeProcess === 0" style="margin-top: 20px; text-align: center">
            <div>正在触发执行测试...</div>
          </div>

          <div v-show="activeProcess === 1" style="margin-top: 20px; text-align: center">
            <div>正在解析数据...</div>
            <div>若一直卡在此节点</div>
            <div>1、可能是数据较多，解析确实需要花一些时间</div>
            <div>2、可能是解析的时候报错了，此情况请查看日志</div>
          </div>

          <div v-show="activeProcess === 2">
            <div v-show="reportId">
              <el-row>
                <el-col :xs="10" :sm="9" :md="10" :lg="11" :xl="11" style="border:3px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
                  <el-tabs v-model="caseTab">
                    <el-tab-pane :label="caseTab" :name="caseTab">
                      <el-table
                          :data="reportCaseDataList"
                          :row-class-name="tableRowClassName"
                          :height="tableHeight"
                          size="small"
                          @row-click="clickCase"
                      >
                        <el-table-column prop="num" label="序号" align="center" min-width="15%">
                          <template #default="scope">
                            <span> {{ scope.$index + 1 }} </span>
                          </template>
                        </el-table-column>

                        <el-table-column prop="result" label="状态" align="center" min-width="20%">
                          <template #default="scope">
                            <el-tag
                                size="small"
                                :type="resultTagMapping[scope.row.result]"
                            >{{ resultMapping[scope.row.result] }}
                            </el-tag>
                          </template>
                        </el-table-column>

                        <el-table-column show-overflow-tooltip prop="name" label="用例名" align="left" min-width="55%">
                          <template #default="scope">
                            <span
                                :style="{'textDecoration': scope.row.result === 'skip' ? 'line-through' : ''}"
                            > {{ scope.row.name }} </span>
                          </template>
                        </el-table-column>

                        <el-table-column prop="result" align="center" label="操作" min-width="12%">
                          <template #default="scope">
                            <el-button
                                v-show="scope.row.result === 'waite'"
                                type="danger"
                                size="small"
                                @click="changeReportStepStatus(null, scope.row.id,null,'stop')"
                            >中断</el-button>
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-tab-pane>
                  </el-tabs>

                </el-col>

                <el-col :xs="14" :sm="15" :md="14" :lg="13" :xl="13">
                  <div style="margin-left: 5px">
                    <el-tabs v-model="stepTab">
                      <el-tab-pane :label="stepTab" :name="stepTab">
                        <el-table
                            :data="reportStepDataList"
                            :row-class-name="tableRowClassName"
                            :height="tableHeight"
                            size="small"
                        >
                          <el-table-column prop="num" label="序号" align="center" min-width="8%">
                            <template #default="scope">
                              <span> {{ scope.$index + 1 }} </span>
                            </template>
                          </el-table-column>

                          <el-table-column prop="result" label="状态" align="center" min-width="12%">
                            <template #default="scope">
                              <el-tag
                                  size="small"
                                  :type="resultTagMapping[scope.row.result]"
                              >{{ resultMapping[scope.row.result] }}
                              </el-tag>
                            </template>
                          </el-table-column>

                          <el-table-column show-overflow-tooltip prop="name" align="left" label="步骤名" min-width="50%">
                            <template #default="scope">
                            <span
                                :style="{'textDecoration': scope.row.result === 'skip' ? 'line-through' : ''}"
                            > {{ scope.row.name }} </span>
                            </template>
                          </el-table-column>

                          <el-table-column prop="process" align="center" label="节点" min-width="15%">
                            <template #default="scope">
                              <el-tag size="small" type="info">{{ processMapping[scope.row.process] }}</el-tag>
                            </template>
                          </el-table-column>

                          <el-table-column prop="result" align="center" label="操作" min-width="15%">
                            <template #default="scope">
                              <el-button
                                  v-show="scope.row.result !== 'waite'"
                                  type="primary"
                                  size="small"
                                  style="margin: 2px;padding: 2px"
                                  @click="showStepData(scope.row.id)"
                              >查看
                              </el-button>
                              <el-button
                                  v-show="scope.row.result === 'waite' && scope.row.status == 'pause'"
                                  type="success"
                                  size="small"
                                  style="margin: 2px;padding: 2px"
                                  @click="changeReportStepStatus(null, null, scope.row.id, 'resume')"
                              >放行
                              </el-button>
                              <el-button
                                  v-show="scope.row.result === 'waite' && scope.row.status == 'resume'"
                                  type="warning"
                                  size="small"
                                  style="margin: 2px;padding: 2px"
                                  @click="changeReportStepStatus(null, null, scope.row.id, 'pause')"
                              >打断点
                              </el-button>
                            </template>
                          </el-table-column>
                        </el-table>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </el-col>
              </el-row>
            </div>

            <div v-show="!reportId" style="margin-top: 50px; text-align: center">
              执行耗时多久取决于用例设计，请耐心等待
            </div>

          </div>

          <div v-show="activeProcess === 3" style="margin-top: 50px; text-align: center">
            <div>正在分析和保存测试报告...</div>
            <div>1、用例执行完毕，正在保存测试报告</div>
            <div>2、保存完毕后会自动打开测试报告页面</div>
          </div>
        </div>

      </div>
    </el-dialog>

    <div>
      <el-drawer
          title="步骤数据"
          v-model="reportStepDetailIsShow"
          :append-to-body="true"
          size="60%"
      >
        <div style="margin-left: 20px; margin-right: 20px">
          <showStepView :test-type="testType" :report-step-data="reportStepData" />
        </div>

      </el-drawer>
    </div>

    <div>
      <el-dialog v-model="showTimeOutMessage" title="等待测试执行超时" width="800">
        <div style="color: red;margin-bottom: 30px">
          注：等待测试执行的超时时间，可在配置管理更改，code 为 run_time_out
        </div>

        <div style="margin-bottom: 10px">
          测试【<span style="color: red">{{busEvent.data.runTimeout}}</span>】秒内未运行结束，
          有以下【<span style="color: red">2</span>】种情况，请确认
        </div>

        <div style="margin-bottom: 10px">
          1、用例【<span style="color: red">解析</span>】过程中，
          执行【<span style="color: red">自定义函数报错</span>】，
          此情况请到【<span style="color: red">执行错误记录</span>】查看详细信息，并修改自定义函数
        </div>

        <div style="margin-bottom: 10px">
          2、设计的测试的执行时间就是【<span style="color: red">应该超过{{busEvent.data.runTimeout}}</span>】秒，
          此情况请等待测试执行结束并到【<span style="color: red">测试报告</span>】页查看测试报告
        </div>

        <template #footer>
          <div class="dialog-footer">
            <el-button type="primary" @click="showTimeOutMessage = false">关闭</el-button>
          </div>
        </template>
      </el-dialog>
    </div>

  </div>
</template>

<script setup lang="ts">


import {computed, onBeforeUnmount, onMounted, ref, watch} from "vue";
import {useRouter} from "vue-router";
import {
  ChangeReportStepStatus,
  GetReportCaseList,
  GetReportShowId,
  GetReportStatus,
  GetReportStepDetail,
  GetReportStepList
} from "@/api/autotest/report";
import {bus, busEvent} from "@/utils/bus-events";
import {ElNotification} from "element-plus";
import showStepView from '@/components/autotest/report/show/step-detail.vue'

const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})

const router = useRouter()

const showTimeOutMessage = ref(false)
const processIsShow = ref(false)
const statusMapping = ref({
  1: 'finish',
  2: 'success',
  3: 'error',
  4: 'finish'
})
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.68}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.7}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const activeProcess = ref(2)
const activeStatus = ref(1)
const reportId = ref(1)
const reportCaseId = ref(undefined)
const processMapping = ref({
  'waite': '等待解析',
  'parse': '解析数据',
  'before': '前置条件',
  'after': '后置条件',
  'run': '测试',
  'extract': '数据提取',
  'validate': '断言'
})
const resultMapping = ref({
  'waite': '等待',
  'running': '执行中',
  'fail': '不通过',
  'success': '通过',
  'skip': '跳过',
  'error': '报错'
})
const resultTagMapping = ref({
  'waite': 'info',
  'running': '',
  'fail': 'danger',
  'success': 'success',
  'skip': 'info',
  'error': 'warning'
})

const reportCaseDataList = ref([]) // [{ 'id': 1, 'name': '用例1', 'result': 'success' }],
const caseTab = ref('用例列表')
const stepTab = ref('步骤列表')
const reportStepDataList = ref([])  // [{ 'id': 1, 'name': '步骤1', 'process': 'before', 'result': 'success' }]
const reportStepData = ref({})
const reportStepDetailIsShow = ref(false)

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
  window.removeEventListener('resize', handleResize);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'run-process') {
    activeProcess.value = 1
    activeStatus.value = 1
    reportId.value = message.report_id
    reportCaseId.value = undefined
    processIsShow.value = true
    getReport(message.batch_id)
  }
}

const showStepData = (stepDataId) => {
  GetReportStepDetail(props.testType, { id: stepDataId }).then(response => {
    reportStepData.value = response.data.step_data
    reportStepData.value.result = response.data.result
    reportStepDetailIsShow.value = true
  })
}

const tableRowClassName = ({ row, rowIndex }) => {
  return `${row.result}-row`
}

const getShowReportId = (batch_id: any) => {
  GetReportShowId(props.testType, { batch_id: batch_id }).then(response => (
      openReportById(response.data)
  ))
}

const changeReportStepStatus = (report_id: number, report_case_id: number, report_step_id: number, status: string) => {
  ChangeReportStepStatus(props.testType, {
    report_id: report_id,
    report_case_id: report_case_id,
    report_step_id: report_step_id,
    status: status,
  }).then(response => {})
}

// 点击用例，查对应用例的步骤执行信息
const clickCase = (row: { id: undefined; }, column: any, event: any) => {
  reportCaseId.value = row.id
}

const openReportById = (reportId: any) => {
  // 使用路由跳转替代新窗口打开
  const router = useRouter()
  router.push(`/${props.testType}-test/report-show?id=${reportId}`)
}

async function getReport (batch_id) {
  // 触发运行成功，每1.5秒查询一次，
  // 最后都没查出结果，则停止查询，提示用户去测试报告页查看
  // 已出结果，则停止查询，展示测试报告
  const runTimeoutCount = Number(busEvent.data.runTimeout) * 1000 / 1500
  let queryCount = 1

  async function waiteTestFinish() {
    if (processIsShow.value == false){
      return
    }
    if (queryCount <= runTimeoutCount) {
      const reportStatus = await GetReportStatus(props.testType, {
        batch_id: batch_id,
        process: activeProcess.value,
        status: activeStatus.value
      });

      if (reportStatus.status === 200) { // 获取成功
        activeProcess.value = reportStatus.data.process
        activeStatus.value = reportStatus.data.status

        if (reportId.value && activeProcess.value === 2) { // 执行中
          const reportCaseList = await GetReportCaseList(props.testType, {report_id: reportId.value}) // 获取执行的用例
          reportCaseDataList.value = reportCaseList.data
          if (!reportCaseId.value) {
            reportCaseId.value = reportCaseList.data[0].id // 最新的在执行的用例
          }

          const reportStepList = await GetReportStepList(props.testType, {report_case_id: reportCaseId.value}) // 获取指定用例的执行步骤
          reportStepDataList.value = reportStepList.data

        } else if (activeProcess.value === 3 && activeStatus.value === 2) {// 执行完毕
          processIsShow.value = false // 关闭进度框
          getShowReportId(batch_id)
          return
        }
      } else { // 获取失败
        processIsShow.value = false // 关闭进度框
      }
      await new Promise(resolve => setTimeout(resolve, 1500));
      queryCount += 1
    } else { // 超时还未出结果
      showTimeOutMessage.value = true
    }
    return waiteTestFinish()
  }
  await waiteTestFinish()
}

</script>

<style scoped lang="scss">
.el-table .error-row {
  color: rgb(232, 124, 37);
}

.el-table .success-row {
  color: rgb(25, 212, 174);
}

.el-table .fail-row {
  color: rgb(250, 110, 134);
}

.el-table .skip-row {
  color: #909399;
}
</style>
