<template>
  <div style="margin-left: 5px; margin-right: 5px">
    <el-row>
      <el-col :xs="9" :sm="8" :md="9" :lg="10" :xl="10"
              style="border:3px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
        <el-tabs v-model="caseListTab">
          <el-tab-pane :label="caseListTab" :name="caseListTab">
            <span>
              <el-select v-model="responseTimeLevelFilter" placeholder="根据响应时间筛选" size="small" style="width: 20%;margin-right: 5px" @change="selectByResponseTime">
                <el-option
                    v-for="item in responseTimeLevelFilterOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                />
              </el-select>
              <el-input v-model="filterText" placeholder="输入关键字过滤" style="width: 55%;margin-right: 5px"/>
              <el-button type="primary" @click="treeIsShowAll('expand')" style="margin: 0 3px 0 0; padding: 4px; float: right">展开全部</el-button>
              <el-button type="primary" @click="treeIsShowAll('collapse')" style="margin: 0 3px 0 0; padding: 4px; float: right">收起全部</el-button>
            </span>
            <el-scrollbar class="aside_scroll" :style="{height: `${treeScrollHeight}`}">
              <el-tree
                  v-loading="treeIsLoading"
                  ref="treeRef"
                  class="filter-tree"
                  node-key="id"
                  :data="treeShowList"
                  :props="defaultProps"
                  highlight-current
                  :default-expanded-keys="suiteIdList"
                  :expand-on-click-node="false"
                  :filter-node-method="filterNode"
                  @node-click="clickTree"
              >
                <template #default="{ node, data }">
                  <div class="custom-tree-node" @mouseenter="mouseenter(data)" @mouseleave="mouseleave(data)">
                    <span :style="{
                      'color': getColor(data),
                      'textDecoration': data.result === 'skip' ? 'line-through' : ''
                    }"
                    >
                      <span style="font-size: 12px">【{{ getTage(data) }}】<span :style="{color: getSpanColor(data)}">{{ getDuration(data) }}</span></span>
                      <span>{{ node.label }}</span>
                    </span>
                      <span v-show="data.id === currentNode.id && data.suite_id && data.result !== 'waite'">
                        <el-button type="primary" @click.stop="showCaseEditor(data)" style="margin: 0; padding: 4px">编辑</el-button>
                    </span>
                  </div>
                </template>
              </el-tree>
            </el-scrollbar>
          </el-tab-pane>
        </el-tabs>
      </el-col>

      <el-col :xs="15" :sm="16" :md="15" :lg="14" :xl="14">
        <div style="margin-left: 5px">
          <!-- 测试步骤详情 -->
          <el-tabs v-show="reportStepDetailIsShow" v-model="stepDataTab">
            <el-tab-pane :label="stepDataTab" :name="stepDataTab">
              <el-scrollbar class="aside_scroll" :style="{height: `${scrollHeight}`}">
                <showReportStepDetailView
                    :test-type="testType"
                    :report-step-data="reportStep"
                    :before-img-is-loading="beforeImgIsLoading"
                    :after-img-is-loading="afterImgIsLoading"
                />
              </el-scrollbar>
            </el-tab-pane>
          </el-tabs>

          <!-- 测试用例详情 -->
          <el-tabs v-show="reportCaseDetailIsShow" v-model="caseDataTab">
            <el-tab-pane :label="caseDataTab" :name="caseDataTab">
              <el-scrollbar class="aside_scroll" :style="{height: `${scrollHeight}`}">
                <showReportCaseDetailView :test-type="testType" :report-case-data="reportCase"/>
<!--                <showReportCaseDetailView :test-type="testType"/>-->
              </el-scrollbar>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-col>
    </el-row>
  </div>

</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, watch, nextTick, computed} from "vue";
import {ElMessage, ElTree} from 'element-plus'
import {
  GetReportStepDetail,
  GetReportStepImg,
  GetReportSuiteList
} from "@/api/autotest/report";
import {bus, busEvent} from "@/utils/bus-events";
import showReportCaseDetailView from './case-detail.vue'
import showReportStepDetailView from './step-detail.vue'
import {ellipsis} from "@/utils/parse-data";
import {GetConfigByCode} from "@/api/config/config-value";

const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})


interface Tree {
  [key: string]: any
}

const filterText = ref('')
const treeRef = ref<InstanceType<typeof ElTree>>()
const tempLabel = ref()
const defaultProps = {
  children: 'children',
  label: 'name',
}
const responseTimeLevel = ref({"slow": 300, "very_slow": 1000})
const responseTimeLevelFilterOptions = ref({})
const responseTimeLevelFilter = ref(0)

watch(filterText, (val) => {
  treeRef.value!.filter(val)
})

const filterNode = (value: string, data: Tree) => {
  if (!value) return true
  return data.name.includes(value)
}

// 鼠标滑入
const mouseenter = (data: { name: string; showDropdownMenu: boolean; }) => {
  data.realName = data.name
  currentNode.value = data
  tempLabel.value = JSON.parse(JSON.stringify(data.name))
  data.name = ellipsis(data.name, 8)
}

// 鼠标滑出
const mouseleave = (data: { name: any; showDropdownMenu: boolean; }) => {
  currentNode.value = {}
  data.name = tempLabel.value
}

const getColor = (data) => {
  return data.result === 'error' ? 'rgb(232, 124, 37)'
      : data.result === 'fail' ? 'rgb(250, 110, 134)'
          : data.result === 'success' ? 'rgb(25, 212, 174)'
          : data.result === 'running' ? '#3A8EE6'
          : '#909399'
}

const getTage = (data) => {
  return data.report_case_id ? '步骤' : data.suite_id ? '用例' : '用例集'
}

const getDuration = (data) => {
  if (!data.summary) return ''
  return data.summary.time ? `【${data.summary.time.all_duration}秒】` : `【${data.summary.elapsed_ms || 0}毫秒】`
}

// 如果是接口自动化测试，把响应时间长的耗时标注出来
const getSpanColor = (data) => {
  if (props.testType !== 'api' || !data.summary || !data.summary.elapsed_ms){
    return ''
  }
  else if (data.summary.elapsed_ms > responseTimeLevel.value.very_slow) {
    return 'rgb(250, 110, 134)'
  }
  else if (data.summary.elapsed_ms > responseTimeLevel.value.slow) {
    return 'rgb(232, 124, 37)'
  }
  return 'rgb(25, 212, 174)'
}

const clickTree = (data: any) => {
  console.log(data)
  if (data.report_case_id) { // 点步骤
    getStepData(data.id)
    reportCaseDetailIsShow.value = false
  } else if (data.suite_id) { // 点用例
    reportCase.value = JSON.parse(JSON.stringify(data))
    bus.emit(busEvent.drawerIsShow, {
      eventType: 'show-report-case-detail',
      reportCaseId: data.id
    })
    reportStepDetailIsShow.value = false
    reportCaseDetailIsShow.value = true
  }
}

const reportId = ref()
const treeIsLoading = ref(false)
const suiteList = ref([])
const slowList = ref([])
const verySlowList = ref([])
const treeShowList = ref([])
const suiteIdList = ref([])
const currentNode = ref({id: undefined})
const treeScrollHeight = computed(() => {
  if (innerHeight < 800) {  // 小屏
    return `${innerHeight * 0.70}px`
  } else {  // 大屏
    return `${innerHeight * 0.80}px`
  }
})
const scrollHeight = computed(() => {
  if (innerHeight < 800) {  // 小屏
    return `${innerHeight * 0.70}px`
  } else {  // 大屏
    return `${innerHeight * 0.83}px`
  }
})

const caseListTab = '用例列表'
const caseDataTab = '用例明细'
const stepDataTab = '步骤明细'
const reportCaseDetailIsShow = ref(false)
const reportStepDetailIsShow = ref(false)
const reportCase = ref({
  name: '测试用例',
  result: 'success',
  summary: {
    stat: {fail: 0, skip: 0, error: 0, total: 0, success: 0},
    time: {end_at: '', start_at: '', case_duration: 0, step_duration: 0, all_duration: 0},
    result: 'success'
  },
  case_data: {
    id: 18,
    env: null,
    num: 0,
    desc: '测试用例',
    name: '测试用例',
    status: 1,
    headers: [],
    skip_if: [],
    suite_id: 20,
    module_id: null,
    run_times: 1,
    variables: [],
    create_user: 1
  },
  error_msg: ''
})
const reportStep = ref({
  result: '',
  case_id: undefined,
  name: undefined,
  stat: {elapsed_ms: undefined, content_size: undefined, request_at: undefined, response_at: undefined},
  redirect_print: undefined,
  variables_mapping: {},
  extract_msgs: {},
  validation_results: [],
  before: null,
  after: null,
  request: {
    url: undefined,
    method: undefined,
    headers: {},
    body: {},
    timeout: 60,
    params: {},
    json: {},
    data: {},
    files: {},
    verify: false,
    allow_redirects: false
  },
  response: {
    ok: true,
    url: undefined,
    status_code: 200,
    reason: 'OK',
    cookies: {},
    encoding: 'utf-8',
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Content-Length': '84',
      Server: 'Werkzeug/2.0.1 Python/3.9.6',
      Date: 'Tue, 20 Jun 2023 05:56:20 GMT'
    },
    content_type: 'text/html; charset=utf-8',
    json: {}
  },
  test_action: {
    execute_name: '',
    action: '',
    by_type: '',
    screen: '',
    element: '',
    text: '',
    wait_time_out: ''
  }
})
const beforeImgIsLoading = ref(false)
const afterImgIsLoading = ref(false)

const getStepData = (reportStepId: any) => {
  treeIsLoading.value = true
  GetReportStepDetail(props.testType, {id: reportStepId}).then(response => {
    treeIsLoading.value = false
    reportStep.value = response.data.step_data
    reportStep.value.result = response.data.result
    reportStepDetailIsShow.value = true

    // 非接口测试，获取对应的步骤截图
    if (props.testType !== 'api') {
      // 获前置取截图
      beforeImgIsLoading.value = true
      GetReportStepImg(props.testType, {
        report_id: reportId.value,
        report_step_id: reportStepId,
        img_type: 'before_page'
      }).then(response => {
        reportStep.value.before = response.data.data
        beforeImgIsLoading.value = false
      })

      // 获后置取截图
      afterImgIsLoading.value = true
      GetReportStepImg(props.testType, {
        report_id: reportId.value,
        report_step_id: reportStepId,
        img_type: 'after_page'
      }).then(response => {
        reportStep.value.after = response.data.data
        afterImgIsLoading.value = false
      })
    }
  })
}

const getResponseTimeLevel = () => {
  GetConfigByCode({ code: 'response_time_level' }).then(response => {
    responseTimeLevel.value = response.data
    responseTimeLevelFilterOptions.value = [
        {label: "展示全部", value: 0},
        {label: `耗时>${responseTimeLevel.value.slow}毫秒`, value: responseTimeLevel.value.slow},
        {label: `耗时>${responseTimeLevel.value.very_slow}毫秒`, value: responseTimeLevel.value.very_slow},
    ]
  })
}

const getReportSuiteList = () => {
  treeIsLoading.value = true
  GetReportSuiteList(props.testType, {report_id: reportId.value}).then(response => {
    treeIsLoading.value = false

    if (response.data.length === 0) {
      ElMessage.warning("明细未生成 或 已过期（超过一个月）")
      return
    }

    suiteList.value = response.data
    treeShowList.value = suiteList.value
    response.data.forEach(suite => {
      suiteIdList.value.push(suite.id)
      groupByElapsedMs(suite)
    })
  })
}

// 根据响应时间分组，方便筛选
const groupByElapsedMs = (suite) => {
  if (suite.children && suite.children.length > 0) {
    suite.children.forEach(testCase => {
      if (testCase.children && testCase.children.length > 0) {
        testCase.children.forEach(testStep => {
          if (testStep.summary.elapsed_ms > responseTimeLevel.value.very_slow){
            verySlowList.value.push(testStep)
          }else if (testStep.summary.elapsed_ms > responseTimeLevel.value.very_slow){
            slowList.value.push(testStep)
          }
        })
      }
    })
  }
}

// 根据响应时间展示结果
const selectByResponseTime = () => {
  if (responseTimeLevelFilter.value === responseTimeLevel.value.very_slow){
    treeShowList.value = verySlowList.value
  }else if (responseTimeLevelFilter.value === responseTimeLevel.value.slow){
    treeShowList.value = slowList.value
  }else {
    treeShowList.value = suiteList.value
  }
}

// 控制展开全部和收起全部
const treeIsShowAll = (option: string) => {
  const isExpand = option === 'expand'
  const nodes = treeRef.value.store.nodesMap
  for (const node in nodes)
    nodes[node].expanded = isExpand
}

const showCaseEditor = (row: { case_id: any; }) => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'report-show-edit-case',
    content: {
      caseId: row.case_id
    },
  })
}

onMounted(() => {
  getResponseTimeLevel()
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'show-report-case-list') {
    reportId.value = message.content.id
    getReportSuiteList()
  }
}

</script>

<style scoped lang="scss">
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

</style>
