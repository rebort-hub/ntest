<template>
  <div class="layout-container" v-loading="isLoading">
    <div style="margin-top: 10px; margin-left: 5px; margin-right: 5px;">
      <div>
        <span style="color: red">*</span>
        数据来源：
        【<span style="color: red">接口自动化</span>】
        下用例集类型为
        【<span style="color: red">造数据用例集</span>】
        下状态为
        【<span style="color: red">已通过-要执行</span>】
        的
        【<span style="color: red">用例</span>】
      </div>

      <el-row>
        <el-col :span="4" style="border:1px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
          <el-tabs v-model="businessListTab">
            <el-tab-pane :label="businessListTab" :name="businessListTab">
                <el-input v-model="businessTreeFilterText" placeholder="输入关键字进行过滤" />
                <el-scrollbar :style="{height: treeHeight}">
                  <el-tree
                      ref="businessTreeRef"
                      class="filter-tree"
                      :data="businessList"
                      :props="defaultProps"
                      :filter-node-method="filterNode"
                      node-key="id"
                      @node-click="getProjectList"
                      highlight-current
                  >
                    <template #default="{ node, data }">
                      <div class="custom-tree-node">
                        <span>{{ node.label }}</span>
                      </div>
                    </template>
                  </el-tree>
                </el-scrollbar>
            </el-tab-pane>
          </el-tabs>
        </el-col>

        <el-col :span="4" style="border:1px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
          <el-tabs v-model="projectListTab">
            <el-tab-pane :label="projectListTab" :name="projectListTab">
<!--              <el-scrollbar class="aside_scroll" :style="{height: `${scrollHeight}`}">-->
<!--                <el-tabs v-model="projectActiveId" tab-position="left" :before-leave="getCaseList">-->
<!--                  <el-tab-pane-->
<!--                      v-for="(project) in projectList"-->
<!--                      :key="project.id"-->
<!--                      :name="project.id.toString()"-->
<!--                      :label="project.name"-->
<!--                  />-->
<!--                </el-tabs>-->
<!--              </el-scrollbar>-->
              <el-input v-model="projectTreeFilterText" placeholder="输入关键字进行过滤" />
              <el-scrollbar :style="{height: treeHeight}">
                <el-tree
                    ref="projectTreeRef"
                    class="filter-tree"
                    :data="projectList"
                    :props="defaultProps"
                    :filter-node-method="filterNode"
                    node-key="id"
                    @node-click="getCaseList"
                    highlight-current
                >
                  <template #default="{ node, data }">
                    <div class="custom-tree-node">
                      <span>{{ node.label }}</span>
                    </div>
                  </template>
                </el-tree>
              </el-scrollbar>
            </el-tab-pane>
          </el-tabs>
        </el-col>

        <el-col :span="16">
          <el-tabs v-model="caseListTab">
            <el-tab-pane :label="caseListTab" :name="caseListTab">
              <div style="margin-left: 10px">
                <el-table
                    ref="caseTable"
                    element-loading-text="正在获取数据..."
                    size="small"
                    :height="scrollHeight"
                    element-loading-spinner="el-icon-loading"
                    :data="caseList"
                    stripe
                >
                  <el-table-column prop="num" label="序号" align="left" min-width="8%">
                    <template #default="scope">
                      <span> {{ scope.$index + 1 }} </span>
                    </template>
                  </el-table-column>

                  <el-table-column show-overflow-tooltip align="left" label="用例名称" min-width="55%">
                    <template #default="scope">
                      <span> {{ scope.row.name }} </span>
                    </template>
                  </el-table-column>

                  <el-table-column show-overflow-tooltip align="left" label="用例描述" min-width="20%">
                    <template #default="scope">
                      <el-popover
                          trigger="hover"
                          placement="bottom-start"
                          style="margin-right: 10px"
                          popper-class="down-popover"
                          width="1300px"
                      >
                        <showCaseDesc
                            :case-desc="scope.row.desc"
                            :case-skip-if="scope.row.skip_if"
                            :case-variables="scope.row.variables"
                            :case-extracts="scope.row.output"
                            :project-id="selectProjectId"
                        />
                        <template #reference>
                          <span> {{ scope.row.desc || '-' }} </span>
                        </template>
                      </el-popover>
                    </template>
                  </el-table-column>

                  <el-table-column label="操作" align="left" width="130">
                    <template #default="scope">

                      <!-- 运行用例 -->
                      <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="clickRunCase(scope.row)">运行 </el-button>

                      <!--修改用例-->
                      <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="editCase(scope.row)">修改 </el-button>

                      <!--查看报告-->
                      <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showReport(scope.row)">查看报告</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-col>
      </el-row>

<!--      <selectRunEnv :test-type="'api'" :project-business-id="selectBusinessId"></selectRunEnv>-->
      <showRunProcess :test-type="'api'"></showRunProcess>

      <editCaseDrawer :test-type="'api'" :project-id="selectProjectId"/>

      <el-dialog 
          v-model="reportTableIsShow" 
          title="报告列表" 
          width="85%"
          :close-on-click-modal="false"
          :close-on-press-escape="false"
          top="3vh"
          class="report-table-dialog">
        <ReportTable :test-type="testType" :user-dict="userDict" :user-list="userList"></ReportTable>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed, nextTick, onBeforeUnmount, onMounted, ref, watch} from "vue";
// import SelectRunEnv from "@/components/select-run-env.vue";
import ShowRunProcess from "@/components/show-run-process.vue";
import showCaseDesc from '@/components/autotest/case/show-desc.vue'
import editCaseDrawer from '@/components/autotest/case/edit-drawer.vue'
import {bus, busEvent} from "@/utils/bus-events";
import {GetBusinessList} from "@/api/config/business";
import {GetProjectList} from "@/api/autotest/project";
import {GetMakeDataCaseList, RunCase} from "@/api/autotest/case";
import {ElTree} from "element-plus";
import ReportTable from "@/components/autotest/report/report-table.vue";
import {GetUserList} from "@/api/system/user";

const isLoading = ref(false)
const businessListTab = ref('业务线列表')
const projectListTab = ref('服务列表')
const caseListTab = ref('用例列表')

interface Tree {[key: string]: any}
let treeHeight = computed(() => {
  if (innerHeight < 800) {  // 小屏
    return `${innerHeight * 0.67}px`
  } else {  // 大屏
    return `${innerHeight * 0.80}px`
  }
})
const businessTreeRef = ref<InstanceType<typeof ElTree>>()
const businessTreeFilterText = ref('')
watch(businessTreeFilterText, (val) => {businessTreeRef.value!.filter(val)})
const filterNode = (value: string, data: Tree) => {
  if (!value) return true
  return data.name.includes(value)
}
const projectTreeRef = ref<InstanceType<typeof ElTree>>()
const projectTreeFilterText = ref('')
watch(projectTreeFilterText, (val) => {projectTreeRef.value!.filter(val)})
const defaultProps = {children: 'children', label: 'name'}

const businessList = ref([])
const selectBusinessId = ref()
const selectProjectId = ref()
const projectList = ref([])
const caseList = ref([])
const runCaseId = ref([])
const testType = 'api'
const triggerFrom = 'make-autotest-data'
const reportTableIsShow = ref(false)
const userList = ref([])
const userDict = ref({})
const scrollHeight = computed(() =>{
  if (innerHeight < 800){  // 小屏
    return `${innerHeight * 0.73}px`
  }else {  // 大屏
    return `${innerHeight * 0.82}px`
  }
})

const getUserList = () => {
  GetUserList({}).then((response: object) => {
    userList.value = response.data.data
    response.data.data.forEach(item => {
      userDict.value[item.id] = item.name
    })
  })
}

const getProjectList = (row: { id: any; }) => {
  caseList.value = []
  isLoading.value = true
  selectBusinessId.value = row.id
  GetProjectList(testType,{ business_id: row.id }).then(response => {
    isLoading.value = false
    projectList.value = response.data.data
    if (response.data.total > 0){
      selectProjectId.value = response.data.data[0].id
      nextTick(() => {
        projectTreeRef.value.$el.querySelector(".el-tree-node__content").click()
      })
    }
  })
}

const getCaseList = (row: { id: any; } | undefined) => {
    selectProjectId.value = row ? row.id : selectProjectId.value
    isLoading.value = true
    GetMakeDataCaseList(testType,{ project_id: selectProjectId.value }).then(response => {
      isLoading.value = false
      caseList.value = response.data.data
    })
}

// 查看报告
const showReport = (row) => {
  reportTableIsShow.value = true
  // 使用nextTick确保弹窗完全打开后再发送事件
  nextTick(() => {
    bus.emit(busEvent.drawerIsShow, {
      eventType: 'show-report-table',
      projectId: selectProjectId.value,
      businessId: undefined,
      runType: 'case',
      triggerId: row.id
    })
  })
}

// 编辑用例
const editCase = (row) => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'edit-case',
    content: JSON.parse(JSON.stringify(row))
  })
}

const clickRunCase = (row) => {
  runCaseId.value = [row.id]
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'select-run-env',
    triggerFrom: triggerFrom,
    showSelectRunModel: false,
    business_id: selectBusinessId.value,
    runArgs:       {
      variables: JSON.parse(JSON.stringify(row.variables)),
      headers: row.headers ? JSON.parse(JSON.stringify(row.headers)) : undefined,
      skip_if: JSON.parse(JSON.stringify(row.skip_if))
    }
  })
}

// 运行用例
const runCase = (runConf) => {
  RunCase(testType, {
    id_list: runCaseId.value,
    env_list: runConf.runEnv,
    is_async: runConf.runType,
    browser: runConf.browser,
    server_id: runConf.runServer,
    phone_id: runConf.runPhone,
    no_reset: runConf.noReset,
    temp_variables: runConf.temp_variables,
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
}


const getBusinessList = () => {
  GetBusinessList({page_no: 1, page_size: 1000}).then(response => {
    businessList.value = response.data.data
    if (response.data.total > 0){
      selectBusinessId.value = response.data.data[0].id
      nextTick(() => {
        businessTreeRef.value.$el.querySelector(".el-tree-node__content").click()
      })
    }
  })
}

onMounted(() => {
  nextTick(() => {
    reportTableIsShow.value = true
    setTimeout(function() {
      reportTableIsShow.value = false // 确保报告的组件会渲染，先打开一次
    }, 1)
  });
  getBusinessList()
  getUserList()
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'case-editor') {
    getCaseList(undefined)
  } else if (message.eventType === 'select-run-env' && message.triggerFrom === triggerFrom) {
    runCase(message)
  }
}

</script>

<style scoped lang="scss">
// 报告列表弹窗样式
:deep(.report-table-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 94vh;
    margin-top: 3vh !important;
    margin-bottom: 3vh;
    display: flex;
    flex-direction: column;
  }
  
  .el-dialog__header {
    border-bottom: 1px solid #ebeef5;
    padding: 20px 20px 15px;
    flex-shrink: 0;
  }
  
  .el-dialog__body {
    padding: 20px;
    flex: 1;
    overflow: auto;
  }
}

// 响应式适配
@media (max-width: 1200px) {
  :deep(.report-table-dialog) {
    .el-dialog {
      width: 95% !important;
      margin: 2vh auto !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.report-table-dialog) {
    .el-dialog {
      width: 100% !important;
      margin: 0 !important;
      height: 100vh;
      border-radius: 0;
    }
    
    .el-dialog__body {
      padding: 10px;
    }
  }
}
</style>
