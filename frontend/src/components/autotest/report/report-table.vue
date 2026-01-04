<template>
  <div>
    <el-input
        v-model="queryItems.name"
        placeholder="报告名，支持模糊查询"
        size="small"
        clearable
        style="width: 200px; margin-right: 10px"
    />

    <el-select
        v-model="queryItems.create_user"
        placeholder="创建人"
        filterable
        default-first-option
        clearable
        size="small"
        style="width: 150px; margin-right: 10px"
    >
      <el-option v-for="item in userList" :key="item.id" :label="item.name" :value="item.id"/>
    </el-select>

    <el-select
        v-model="queryItems.run_env"
        style="width: 150px; margin-right: 10px"
        placeholder="运行环境"
        size="small"
        clearable
        default-first-option
    >
      <el-option v-for="item in eventList" :key="item.code" :label="item.name" :value="item.code"/>
    </el-select>

    <el-select
        v-model="queryItems.run_type"
        placeholder="运行维度"
        size="small"
        filterable
        clearable
        style="width: 100px;margin-right: 10px"
        default-first-option
    >
      <el-option v-for="(value, key) in runTypeDict" :key="key" :label="value" :value="key"/>
    </el-select>

    <el-select
        v-model="queryItems.trigger_type"
        placeholder="触发类型"
        size="small"
        filterable
        clearable
        style="width: 100px;margin-right: 10px"
        default-first-option
    >
      <el-option v-for="(value, key) in reportTriggerTypeMappingContent" :key="key" :label="value" :value="key"/>
    </el-select>

    <el-popover :visible="checkDeleteIsShow" placement="top" popper-class="down-popover" width="450px">
      确定删除所选中的测试报告?
      <div style="color: red">
        1、关联了问题记录的测试报告不会被删除 <br>
        2、触发方式为【定时任务】或者【流水线】的，只有管理员能删除
      </div>
      <div style="text-align: right; margin-top: 10px">
        <el-button size="small" type="text" @click="checkDeleteIsShow = false">取消</el-button>
        <el-button type="primary" size="small" @click="deleteData(null)">确定</el-button>
      </div>
      <template #reference>
        <el-button
            :disabled="selectedList.length === 0"
            type="danger"
            size="small"
            style="margin-left: 5px"
            @click="checkDeleteIsShow = true"
        >批量删除
        </el-button>
      </template>
    </el-popover>

    <el-button type="primary" @click="getTableDataList">查询</el-button>

    <el-table
        v-loading="tableIsLoading"
        element-loading-text="正在获取数据"
        element-loading-spinner="el-icon-loading"
        :data="tableDataList"
        stripe
        @selection-change="clickSelectAll"
        :height="tableHeight"
        @row-dblclick="rowDblclick">

      <el-table-column type="selection" min-width="2%"/>

      <el-table-column prop="id" label="序号" align="center" min-width="5%">
        <template #default="scope">
          <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
        </template>
      </el-table-column>

      <el-table-column show-overflow-tooltip prop="id" align="center" label="报告id" min-width="5%"/>

      <el-table-column show-overflow-tooltip prop="name" align="center" label="报告名称" min-width="22%"/>

      <el-table-column show-overflow-tooltip prop="create_time" align="center" label="生成时间"
                       min-width="13%">
        <template #default="scope">
          <span> {{ paramsISOTime(scope.row.create_time) }} </span>
        </template>
      </el-table-column>

      <el-table-column show-overflow-tooltip prop="env" label="维度" align="center"
                       min-width="4%">
        <template #default="scope">
                      <span> {{
                          scope.row.run_type === 'api' ? '接口' :
                              scope.row.run_type === 'case' ? '用例' :
                                  scope.row.run_type === 'suite' ? '用例集' : '任务'
                        }} </span>
        </template>
      </el-table-column>

      <el-table-column show-overflow-tooltip prop="trigger_type" label="触发" align="center"
                       min-width="6%">
        <template #default="scope">
          <span> {{ reportTriggerTypeMappingContent[scope.row.trigger_type] }} </span>
        </template>
      </el-table-column>

      <el-table-column v-if="testType !== 'app'" show-overflow-tooltip prop="env" label="运行环境"
                       align="center" min-width="7%">
        <template #default="scope">
          <span> {{ eventDict[scope.row.env] }} </span>
        </template>
      </el-table-column>

      <el-table-column show-overflow-tooltip prop="is_passed" label="是否通过" align="center"
                       min-width="8%">
        <template #default="scope">
          <el-tag size="small" :type="reportStatusMappingTagType[scope.row.is_passed]">
            {{ reportStatusMappingContent[scope.row.is_passed] }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column show-overflow-tooltip prop="process" label="是否完成" align="center" min-width="7%">
        <template #default="scope">
          <el-tag
              size="small"
              :type="scope.row.process === 3 && scope.row.status === 2 ? 'success' : 'warning'"
          >
            {{ scope.row.process === 3 && scope.row.status === 2 ? '已完成' : '执行中' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column show-overflow-tooltip prop="process" label="是否通知" align="center" min-width="7%">
        <template #header>
          <span>是否通知</span>
          <el-tooltip class="item" effect="dark" placement="top-start">
            <template #content>
              <div>只有执行任务产生的报告才能触发通知</div>
            </template>
            <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </template>
        <template #default="scope">
          <el-tag size="small" :type="scope.row.notified === true ? 'success' : 'info'" >
            {{ scope.row.notified === true ? '已通知' : '未通知' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column show-overflow-tooltip prop="create_user" label="创建人" align="center" min-width="7%">
        <template #default="scope">
          <span> {{ userDict[scope.row.create_user] }} </span>
        </template>
      </el-table-column>

      <el-table-column
          fixed="right"
          show-overflow-tooltip
          prop="desc"
          align="center"
          label="操作"
          width="150">
        <template #default="scope">
<!--          <el-popconfirm title="确定把此报告的运行结果通知到对应任务的报告接收人吗？" @confirm="notifyReport(scope.row)">-->
<!--            <template #reference>-->
<!--              <el-button-->
<!--                  v-show="scope.row.process === 3 && scope.row.status === 2 && scope.row.run_type === 'task' && scope.row.notified === false"-->
<!--                  type="text"-->
<!--                  size="small"-->
<!--                  style="margin: 0; padding: 2px"-->
<!--              >通知-->
<!--              </el-button>-->
<!--            </template>-->
<!--          </el-popconfirm>-->

          <el-button
              v-show="scope.row.process === 3 && scope.row.status === 2 && scope.row.run_type === 'task' && scope.row.notified === false"
              type="text"
              size="small"
              style="margin: 0; padding: 2px"
              @click.native="showNotifyDialog(scope.row)"
          >通知
          </el-button>

          <el-button
              v-show="scope.row.run_type !== 'api' || isAdmin"
              type="text"
              size="small"
              style="margin: 0; padding: 2px"
              @click.native="showReRunDialog(scope.row)"
          >重跑
          </el-button>

          <!--查看报告-->
          <el-button
              type="text"
              size="small"
              style="margin: 0; padding: 2px"
              @click.native="openReportById(scope.row.id)"
          >查看
          </el-button>
          <el-popconfirm :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row)">
            <template #reference>
              <el-button
                  v-show="scope.row.status !== 1"
                  style="margin: 0; padding: 2px;color: red"
                  type="text"
                  size="small"
              >删除
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <pagination
        v-show="tableDataTotal > 0"
        :pageNum="queryItems.page_no"
        :pageSize="queryItems.page_size"
        :total="tableDataTotal"
        @pageFunc="changePagination"
    />

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

    <el-dialog
        v-model="notifyDialogIsShow"
        title="选择通知渠道"
        width="500"
    >
      <div style="margin-bottom: 20px;font-size: 20px;text-align: center">{{ report.name }}</div>

      <div style="margin-bottom: 20px;">
        <div style="margin-bottom: 5px;">
          <span style="color: red">1、若选择的通知渠道不是“按任务设置”，则默认为“始终发送”</span>
        </div>
        <div style="margin-bottom: 5px;">
          <span style="color: red">2、必须在对应任务的通知渠道设置了通知对象才能成功发送</span>
        </div>
      </div>

      <div style="margin: 10px">
        <el-radio v-model="notifyTo" label="default">按任务设置</el-radio>
        <el-radio v-model="notifyTo" label="ding_ding">钉钉</el-radio>
        <el-radio v-model="notifyTo" label="we_chat">企业微信</el-radio>
        <el-radio v-model="notifyTo" label="fei_shu" disabled>飞书</el-radio>
        <el-radio v-model="notifyTo" label="email">邮件</el-radio>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" :loading="notifyIsLoading" size="small" @click="notifyReport()">确定通知</el-button>
          <el-button size="small" @click="notifyDialogIsShow = false">取消</el-button>
        </div>
      </template>
    </el-dialog>

    <SelectRunEnv :test-type="testType"></SelectRunEnv>
    <ShowRunProcess :test-type="testType"></ShowRunProcess>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, watch, nextTick, computed} from "vue";
import Pagination from '@/components/pagination.vue'

import {GetProject, GetProjectList} from "@/api/autotest/project";
import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {
  DeleteReport,
  GetReport,
  GetReportRerunCaseList,
  GetReportList, NotifyReport
} from "@/api/autotest/report";
import {reportStatusMappingContent, reportStatusMappingTagType, reportTriggerTypeMappingContent} from "../mapping";
import {GetRunEnvList} from "@/api/config/run-env";
import {GetConfigByCode} from "@/api/config/config-value";
import SelectRunEnv from "@/components/select-run-env.vue";
import ShowRunProcess from "@/components/show-run-process.vue";
import {GetCase, RunCase} from "@/api/autotest/case";
import {GetServerList} from "@/api/autotest/device-server";
import {GetPhoneList} from "@/api/autotest/device-phone";
import {RunTask} from "@/api/autotest/task";
import {RunCaseSuite} from "@/api/autotest/case-suite";
import {RunApi} from "@/api/autotest/api";
import {paramsISOTime} from "@/utils/parse-data";
import {Help} from "@icon-park/vue-next";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  userList: {
    default: [],
    type: Array
  },
  userDict: {
    default: {},
    type: Object
  }
})

const tableIsLoading = ref(false)
const checkDeleteIsShow = ref(false)
const projectBusinessId = ref()
const report = ref({})
const eventList = ref([])
const eventDict = ref({})
const runTypeDict = ref({})
const tableDataList = ref([])
const selectedList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  project_id: undefined,
  name: undefined,
  create_user: undefined,
  run_env: undefined,
  run_type: undefined,
  trigger_type: undefined,
  trigger_id: undefined
})

const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.7}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.81}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const isAdmin = localStorage.getItem('permissions').indexOf('admin') !== -1
const triggerFrom = 'report-index'
const reRunDialogIsShow = ref(false)
const reRunIdList = ref([])
const reRunOption = ref('failed-and-cover')
const insert_to = ref()
const notifyTo = ref('default')
const notifyIsLoading = ref(false)
const notifyDialogIsShow = ref(false)


const rowDblclick = async (row: any, column: any, event: any) => {
  try {
    await toClipboard(row[column.property]);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}


const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const getReportAndSendEvent = () => {
  GetReport(props.testType, {id: report.value.id}).then(response => {
    report.value = response.data

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
    business_id: projectBusinessId.value,
    runArgs: tempRunArgs,
    runEnv: report.value.summary.env.code
  })
}

const showReRunDialog = (row: {}) => {
  report.value = row
  insert_to.value = undefined
  reRunOption.value = report.value.is_passed ? 'all' : 'failed-and-cover'
  reRunDialogIsShow.value = true
}

const showNotifyDialog = (row: {}) => {
  report.value = row
  notifyTo.value = 'default'
  notifyDialogIsShow.value = true
  notifyIsLoading.value = false
}

const notifyReport = () => {
  notifyIsLoading.value = true
  NotifyReport(props.testType, {id: report.value.id, notify_to: notifyTo.value}).then(response => {
    notifyIsLoading.value = false
    notifyDialogIsShow.value = false
    getTableDataList()
  })
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

  getReportAndSendEvent()
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


const openReportById = (reportId: any) => {
  window.open(`/${props.testType}-test/report-show?id=${reportId}`, '_blank')
}

const clickSelectAll = (val: never[]) => {
  selectedList.value = val
}

const getSubmitId = (row: any) => {
  let selectedIdList: any[] = []
  if (row) {
    selectedIdList = [row.id]
  } else {
    selectedList.value.forEach(item => {
      selectedIdList.push(item.id)
    })
  }
  return selectedIdList
}

const deleteData = (row: { id: any; }) => {
  tableIsLoading.value = true
  DeleteReport(props.testType, {id_list: getSubmitId(row)}).then(response => {
    checkDeleteIsShow.value = false
    tableIsLoading.value = false
    if (response) {
      getTableDataList()
    }
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetReportList(props.testType, queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

const getRunEnvList = (businessId) => {
  GetRunEnvList({business_id: businessId}).then(response => {
    eventList.value = response.data.data
    eventList.value.forEach(env => {
      eventDict.value[env.code] = env.name
    })
  })
}


const getRunTypeDict = () => {
  GetConfigByCode({code: 'run_type'}).then(response => {
    runTypeDict.value = response.data
  })
}

onMounted(() => {
  getRunTypeDict()
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
  bus.on(busEvent.drawerIsShow, selectProject);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
  bus.off(busEvent.drawerIsShow, selectProject);
  window.removeEventListener('resize', handleResize);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'select-run-env' && message.triggerFrom === triggerFrom) {
    reRun(message)
  }
}

const selectProject = (message: any) => {
  if (message.eventType === 'show-report-table') {
    queryItems.value.project_id = message.projectId
    queryItems.value.run_type = message.runType
    queryItems.value.trigger_id = message.triggerId
    if (message.businessId){
      projectBusinessId.value = message.businessId
      getRunEnvList(projectBusinessId.value)
    }else {
      getProjectAndRunEnvList(message.projectId)
    }
    getTableDataList()
  }
}

const getProjectAndRunEnvList = (projectId: number) => {
  GetProject(props.testType, {id: projectId}).then(response => {
    getRunEnvList(response.data.business_id)
  })
}

</script>

<style scoped lang="scss">

//.first-col {
//  width: 20% !important;
//}
//
//.second-col {
//  width: 79% !important;
//}

</style>
