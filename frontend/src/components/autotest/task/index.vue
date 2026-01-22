<template>
  <div class="layout-container">
    <div>
      <el-row>
        <el-col :xs="3" :sm="2" :md="3" :lg="4" :xl="4" style="border:1px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
          <el-tabs v-model="projectTab" style="margin-left: 10px">
            <el-tab-pane name="project">
              <template #label>
                <span> {{ `${testType === 'api' ? '服务' : testType === 'ui' ? '项目' : 'app'}列表` }} </span>
              </template>
              <el-input v-model="filterText" placeholder="输入关键字进行过滤"/>
              <el-scrollbar :style="{height: treeHeight}">
                <el-tree
                    ref="projectTreeRef"
                    class="filter-tree"
                    :data="projectDataList"
                    :props="defaultProps"
                    :filter-node-method="filterNode"
                    node-key="id"
                    @node-click="clickTree"
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

        <el-col :xs="21" :sm="22" :md="21" :lg="20" :xl="20">
          <div style="margin-left: 5px">
            <el-tabs v-model="taskTab">
              <el-tab-pane name="task">
                <template #label>
                  <span> 任务列表 </span>
                  <el-popover class="el_popover_class" placement="top-start" trigger="hover" content="添加任务">
                    <template #reference>
                      <el-button
                          v-show="queryItems.project_id"
                          type="text"
                          style="margin-left: 10px"
                          @click="showEditDrawer(undefined)"
                      ><Plus></Plus></el-button>
                    </template>
                  </el-popover>
                </template>

                <el-table
                    v-loading="tableIsLoading"
                    element-loading-text="正在获取数据"
                    element-loading-spinner="el-icon-loading"
                    :data="tableDataList"
                    stripe
                    :height="tableHeight"
                    @row-dblclick="rowDblclick">

                  <el-table-column label="排序" width="40" align="center">
                    <template #header>
                      <el-tooltip class="item" effect="dark" placement="top-start">
                        <template #content>
                          <div>可拖拽数据前的图标进行自定义排序</div>
                        </template>
                        <span style="color: #409EFF"><Help></Help></span>
                      </el-tooltip>
                    </template>
                    <template #default="scope">
                      <el-button
                          text
                          style="text-align: center"
                          @dragstart="handleDragStart($event, scope.row, scope.$index)"
                          @dragover="handleDragOver($event, scope.$index)"
                          @drop="handleDrop($event, scope.$index)"
                          @dragend="handleDragEnd"
                          draggable="true"
                          class="drag-button"
                          :data-index="scope.$index"
                      >
                        <SortThree></SortThree>
                      </el-button>
                    </template>
                  </el-table-column>

                  <el-table-column label="序号" header-align="center" width="40">
                    <template #default="scope">
                      <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
                    </template>
                  </el-table-column>

                  <el-table-column show-overflow-tooltip prop="name" align="center" label="任务名称" min-width="23%">
                    <template #default="scope">
                      <span> {{ scope.row.name }} </span>
                    </template>
                  </el-table-column>

                  <el-table-column show-overflow-tooltip prop="cron" label="cron表达式" align="center" min-width="22%">
                    <template #default="scope">
                      <span> {{ scope.row.cron }} </span>
                    </template>
                  </el-table-column>

                  <el-table-column show-overflow-tooltip prop="skip_holiday" label="节假/调休" align="center" min-width="10%">
                    <template #default="scope">
                      <el-tag :type="scope.row.skip_holiday === 1 ? 'warning' : 'success'">
                        {{ scope.row.skip_holiday === 1 ? "不执行" : "执行" }}
                      </el-tag>
                    </template>
                  </el-table-column>

                  <el-table-column show-overflow-tooltip prop="receive_type" label="发送报告" align="center" min-width="19%">
                    <template #default="scope">
                      <el-tag v-if="scope.row.is_send === 'not_send'" type="warning">不发送</el-tag>
                      <el-tag v-else type="success">{{
                          scope.row.is_send === 'always' ? '始终' :
                              scope.row.is_send === 'on_success' ? '全通过' : '不通过'
                        }} =>
                        {{
                          scope.row.receive_type === 'ding_ding' ? "钉钉" :
                              scope.row.receive_type === 'we_chat' ? "企业微信" : "邮件"
                        }}</el-tag>
                    </template>
                  </el-table-column>

<!--                  <el-table-column prop="merge_notify" label="通知" align="center" min-width="10%">-->
<!--                    <template #header>-->
<!--                      <span>通知</span>-->
<!--                      <el-tooltip class="item" effect="dark" placement="top-start">-->
<!--                        <template #content>-->
<!--                          <div>1、不合并通知：达到触发发送通知的条件时，每个环境都会发一份通知</div>-->
<!--                          <div>2、合并通知：达到触发发送通知的条件时，汇总每个环境的通知，只通知一次</div>-->
<!--                          <div>注：当选择了多个环境时，才能在编辑抽屉中设置此选项</div>-->
<!--                        </template>-->
<!--                        <span style="margin-left:5px;color: #409EFF"><Help></Help></span>-->
<!--                      </el-tooltip>-->
<!--                    </template>-->
<!--                    <template #default="scope">-->
<!--                      <el-tag :type="scope.row.merge_notify === 1 ? 'success' : 'primary'">-->
<!--                        {{ scope.row.merge_notify === 1 ? "合并" : "不合并" }}-->
<!--                      </el-tag>-->
<!--                    </template>-->
<!--                  </el-table-column>-->

                  <el-table-column prop="push_hit" label="问题" align="center" min-width="9%">
                    <template #header>
                      <span>问题</span>
                      <el-tooltip class="item" effect="dark" placement="top-start">
                        <template #content>
                          <div>当触发任务的方式为
                            <span style="color: red">【定时巡检】</span>
                            或者
                            <span style="color: red">【流水线】</span>
                            ，且执行结果为
                            <span style="color: red">【不通过】</span>
                            时，如果设置的是
                            <span style="color: red">【要记录】</span>
                            ，将
                            <span style="color: red"> 自动 </span>
                            把此次的执行记录同步到自动化测试问题记录中</div>
                        </template>
                        <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                      </el-tooltip>
                    </template>
                    <template #default="scope">
                      <el-tag :type="scope.row.push_hit === 1 ? 'success' : 'warning'">
                        {{ scope.row.push_hit === 1 ? "记录" : "不记录" }}
                      </el-tag>
                    </template>
                  </el-table-column>

                  <el-table-column prop="status" label="状态" align="center" min-width="8%">
                    <template #header>
                      <span>状态</span>
                      <el-tooltip class="item" effect="dark" placement="top-start">
                        <template #content>
                          <div>启用中的任务才会按cron表达式定时执行</div>
                        </template>
                        <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                      </el-tooltip>
                    </template>
                    <template #default="scope">
                      <el-switch
                          v-model="scope.row.status"
                          :inactive-value="'disable'"
                          :active-value="'enable'"
                          @change="changeStatus(scope.row)"
                      />
                    </template>
                  </el-table-column>

                  <el-table-column show-overflow-tooltip prop="create_user" align="center" label="创建人" min-width="8%">
                    <template #default="scope">
                      <span>{{ userDict[scope.row.create_user] }}</span>
                    </template>
                  </el-table-column>

                  <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" width="320">
                    <template #default="scope">
                      <div class="action-buttons">
                        <el-button size="small" type="primary" @click="clickRun(scope.row)">运行</el-button>
                        <el-button size="small" @click="showEditDrawer(scope.row)">修改</el-button>
                        <el-popconfirm width="250px" title="复制此任务并生成新的任务?" @confirm="copyData(scope.row)">
                          <template #reference>
                            <el-button size="small" type="success">复制</el-button>
                          </template>
                        </el-popconfirm>
                        <el-button size="small" type="info" @click="showReport(scope.row)">查看报告</el-button>
                        <el-popconfirm width="250px" :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row)">
                          <template #reference>
                            <el-button
                                :loading="scope.row.isLoading"
                                size="small"
                                type="danger"
                            >删除
                            </el-button>
                          </template>
                        </el-popconfirm>
                      </div>
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
              </el-tab-pane>
            </el-tabs>

          </div>
        </el-col>
      </el-row>
    </div>
    <EditDrawer :test-type="testType" :user-list="userList"></EditDrawer>
    <selectRunEnv :test-type="testType"></selectRunEnv>
    <showRunProcess :test-type="testType"></showRunProcess>
    <el-drawer v-model="reportTableIsShow" title="报告列表" size="80%">
      <ReportTable :test-type="testType" :user-dict="userDict" :user-list="userList"></ReportTable>
    </el-drawer>

  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, watch, nextTick, computed} from "vue";
import {Help, Plus, SortThree} from "@icon-park/vue-next";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './drawer.vue'

import {GetProject, GetProjectList} from "@/api/autotest/project";
import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage, ElTree} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {
  ChangeTaskSort,
  CopyTask,
  DeleteTask,
  DisableTask,
  EnableTask,
  GetTaskList,
  RunTask
} from "@/api/autotest/task";
import {RunCase} from "@/api/autotest/case";
import SelectRunEnv from "@/components/select-run-env.vue";
import ShowRunProcess from "@/components/show-run-process.vue";
import {GetUserList} from "@/api/system/user";
import ReportTable from "@/components/autotest/report/report-table.vue";

const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})

interface Tree {
  [key: string]: any
}

let treeHeight = computed(() => {
  if (innerHeight < 800) {  // 小屏
    return `${innerHeight * 0.7}px`
  } else {  // 大屏
    return `${innerHeight * 0.81}px`
  }
})
const projectTreeRef = ref<InstanceType<typeof ElTree>>()
const filterText = ref('')
watch(filterText, (val) => {
  projectTreeRef.value!.filter(val)
})
const filterNode = (value: string, data: Tree) => {
  if (!value) return true
  return data.name.includes(value)
}

const defaultProps = {children: 'children', label: 'name'}
const projectTab = ref('project')
const taskTab = ref('task')
const tableIsLoading = ref(false)
const reportTableIsShow = ref(false)
const userList = ref({})
const userDict = ref({})
const projectDataList = ref([])
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  project_id: undefined
})
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.73}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.83}px`
  }
}

const handleResize = () => {
  setTableHeight();
}
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])
const project = ref()
const triggerFrom = 'task-index'
const runTaskId = ref()

const rowDblclick = async (row: any, column: any, event: any) => {
  try {
    await toClipboard(row[column.property]);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}

const clickTree = (row) => {
  queryItems.value.project_id = row.id
  project.value = row
  getTableDataList()
  bus.emit(busEvent.treeIsChoice, {eventType: 'project-tree', content: row})
}

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const showEditDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'edit-task', content: row});
}

const getUserList = () => {
  GetUserList({}).then((response: object) => {
    if (response && response.data && response.data.data) {
      userList.value = response.data.data
      response.data.data.forEach(item => {
        userDict.value[item.id] = item.name
      })
    } else {
      console.warn('用户列表数据格式异常:', response)
      userList.value = []
    }
  }).catch((error) => {
    console.error('获取用户列表失败:', error)
    userList.value = []
  })
}

const clickRun = (row) => {
  runTaskId.value = row.id
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'select-run-env',
    triggerFrom: triggerFrom,
    showSelectRunModel: true,
    runName: row.name,
    business_id: project.value.business_id,
    runArgs: undefined,
    runEnv: row.env_list[0] // 默认选择任务设置的第一个环境
  })
}

const runTask = (runConf) => {
  RunTask(props.testType, {
    id_list: [runTaskId.value],
    env_list: runConf.runEnv,
    is_async: runConf.runType,
    browser: runConf.browser,
    server_id: runConf.runServer,
    phone_id: runConf.runPhone,
    no_reset: runConf.noReset,
    temp_variables: runConf.temp_variables,
    'trigger_type': 'page',
    extend: {}  // 添加必需的 extend 字段
  }).then(response => {
    if (response && response.data) {
      bus.emit(busEvent.drawerIsShow, {
        eventType: 'run-process',
        batch_id: response.data.batch_id,
        report_id: response.data.report_id
      })
    } else {
      console.error('任务运行失败：响应数据为空', response)
    }
  })
}

const copyData = (row: { id: any; }) => {
  tableIsLoading.value = true
  CopyTask(props.testType, {id: row.id}).then(response => {
    tableIsLoading.value = false
    if (response) {
      getTableDataList()
    }
  })
}

const showReport = (row) => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'show-report-table',
    projectId: queryItems.value.project_id,
    businessId: undefined,
    runType: 'task',
    triggerId: row.id
  })
  reportTableIsShow.value = true
}

const deleteData = (row: { id: any, isLoading: boolean; }) => {
  row.isLoading = true
  DeleteTask(props.testType, {id: row.id}).then(response => {
    row.isLoading = false
    if (response) {
      getTableDataList()
    }
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetTaskList(props.testType, queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    if (response && response.data) {
      tableDataList.value = response.data.data || []
      tableDataTotal.value = response.data.total || 0
    } else {
      console.warn('任务列表数据格式异常:', response)
      tableDataList.value = []
      tableDataTotal.value = 0
    }
  }).catch((error) => {
    tableIsLoading.value = false
    console.error('获取任务列表失败:', error)
    tableDataList.value = []
    tableDataTotal.value = 0
  })
}

const changeStatus = (row: { status?: any; id?: any; }) => {
  if (row.status === 'disable') {
    disableTask(row.id)
  } else {
    enableTask(row.id)
  }
}

const enableTask = (taskId: number) => {
  tableIsLoading.value = true
  EnableTask(props.testType, {id: taskId}).then(response => {
    tableIsLoading.value = false
    if (response) {
      getTableDataList()
    }
  })
}

const disableTask = (taskId: number) => {
  tableIsLoading.value = true
  DisableTask(props.testType, {id: taskId}).then(response => {
    tableIsLoading.value = false
    if (response) {
      getTableDataList()
    }
  })
}

const getProjectList = () => {
  GetProjectList(props.testType, {page_no: 1, page_size: 1000}).then(response => {
    if (response && response.data && response.data.data) {
      projectDataList.value = response.data.data
    } else {
      console.warn('项目列表数据格式异常:', response)
      projectDataList.value = []
    }
    if (tableDataList.value.length < 1) {
      nextTick(() => {
        projectTreeRef.value.$el.querySelector(".el-tree-node__content").click()
      })
    }
  }).catch((error) => {
    console.error('获取项目列表失败:', error)
    projectDataList.value = []
  })
}

// 记录拖拽前的数据顺序
const handleDragStart = (event, row, index) => {
  oldIndex.value = index;
  dragRow.value = row;
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/html", event.target);
  event.target.classList.add('drag-dragging');
};

const handleDragOver = (event, index) => {
  event.preventDefault();  // 必须调用这个方法才能使 drop 生效
};

const handleDragEnd = (event) => {
  // 恢复拖拽操作的样式
  event.target.classList.remove('drag-dragging');
};

const handleDrop = (event, newIndex) => {
  event.preventDefault();
  const updatedData = [...tableDataList.value];
  // 移除当前拖拽的行数据
  updatedData.splice(oldIndex.value, 1);
  // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow.value);
  // 恢复样式
  event.target.classList.remove('drag-dragging');
  newIdList.value = updatedData.map(item => item.id).slice()
  sortTable()
};

const sortTable = () => {
  tableIsLoading.value = true
  ChangeTaskSort(props.testType, {
    id_list: newIdList.value,
    page_no: queryItems.value.page_no,
    page_size: queryItems.value.page_size
  }).then(response => {
    tableIsLoading.value = false
    if (response){
      getTableDataList()
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
  getUserList()
  getProjectList()
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
  window.removeEventListener('resize', handleResize);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'task-editor') {
    getTableDataList()
  } else if (message.eventType === 'select-run-env' && message.triggerFrom === triggerFrom) {
    runTask(message)
  }
}

</script>

<style scoped lang="scss">
// 操作按钮样式
.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
  align-items: center;
  flex-wrap: nowrap;
  white-space: nowrap;
  
  .el-button {
    margin: 0;
    padding: 5px 8px;
    font-size: 12px;
  }
}

.first-col {
  width: 20% !important;
}

.second-col {
  width: 79% !important;
}

</style>
