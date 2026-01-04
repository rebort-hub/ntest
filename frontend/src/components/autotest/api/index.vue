<template>
    <div style="margin-left: 5px">
      <el-tabs v-model="activeTab" class="table_padding table_api">
        <el-tab-pane name="api">
          <template #label>
            <span> 接口列表 </span>
            <el-popover class="el_popover_class" placement="top-start" trigger="hover" content="添加接口">
              <template #reference>
                <el-button
                    v-show="queryItems.module_id"
                    type="text"
                    style="margin-left: 10px"
                    @click="showAddDrawer"
                ><Plus></Plus></el-button>
              </template>
            </el-popover>
          </template>

          <el-table
              v-loading="tableIsLoading"
              element-loading-text="正在获取数据"
              element-loading-spinner="el-icon-loading"
              :data="tableDataList"
              style="width: 100%"
              :header-cell-style="{'text-align':'center'}"
              stripe
              row-key="id"
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

            <el-table-column show-overflow-tooltip prop="addr" align="center" label="接口信息" min-width="55%">
              <template #default="scope">
                <div
                    class="block"
                    :class="`block_${scope.row.method.toLowerCase()}`"
                    :style="{
                  'backgroundColor': scope.row.status === 'disable' ? '#ebebeb' : '',
                  'textDecoration': scope.row.status === 'disable' ? 'line-through' : ''
                }"
                >
                <span
                    class="block-method block_method_color"
                    :class="`block_method_${scope.row.method.toLowerCase()}`"
                    :style="{
                    'backgroundColor': scope.row.status === 'disable' ? '#ebebeb' : ''
                  }"
                >
                  {{ scope.row.method }}
                </span>
                  <span class="block-method block_url">{{ scope.row.addr }}</span>
                  <span class="block-summary-description">{{ scope.row.name }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column show-overflow-tooltip prop="level" align="center" min-width="8%">
              <template #header>
                <span> 重要级 </span>
                <el-tooltip class="item" effect="dark" placement="top-start">
                  <template #content>
                    用于标识接口的重要级别，后续可根据重要级别筛选优先做自动化测试的接口
                  </template>
                  <span style="margin-left:2px;color: #409EFF"><Help></Help></span>
                </el-tooltip>
              </template>
              <template #default="scope">
                <div style="width: 100%; margin-left:auto; margin-right:auto">
                  <el-select
                      v-model="scope.row.level"
                      size="small"
                      placeholder="选择重要程度"
                      filterable
                      :class="`api-level-${scope.row.level}`"
                      @change="selectApiLevel(scope.row)"
                  >
                    <el-option label="高" value="P0"><span style="color: #F56C6C">高</span></el-option>
                    <el-option label="中" value="P1"><span style="color: #E6A23C">中</span></el-option>
                    <el-option label="低" value="P2"><span style="color: #67C23A">低</span></el-option>
                  </el-select>
                </div>
              </template>
            </el-table-column>

            <el-table-column show-overflow-tooltip prop="status" align="center" min-width="7%">
              <template #header>
                <span>状态</span>
                <el-tooltip class="item" effect="dark" placement="top-start">
                  <template #content>
                    1、用于标识接口是否已经被废弃
                    2、关闭状态则为废弃
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

            <el-table-column show-overflow-tooltip prop="use_count" align="center" width="70">
              <template #header>
                <span> 使用 </span>
                <el-tooltip class="item" effect="dark" placement="top-start">
                  <template #content>
                    <div>
                      <div>1: 统计有多少个步骤直接使用了此接口</div>
                      <div>2: 被设计为用例的步骤后，该用例被引用的，不纳入此处统计</div>
                      <div>3: 被使用过的接口，点击使用次数数值可查看使用明细</div>
                    </div>
                  </template>
                  <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                </el-tooltip>
              </template>
              <template #default="scope">
                <el-tooltip class="item" effect="dark" placement="top-start">
                  <template #content >
                    <div>{{ scope.row.use_count > 0 ? '点击查看详情' : '未被使用过' }}</div>
                  </template>
                  <el-tag v-if="scope.row.use_count" @click="getApiToStep(scope.row)">
                    {{ scope.row.use_count }}次
                  </el-tag>
                  <el-tag v-else type="info">0次</el-tag>
                </el-tooltip>
              </template>
            </el-table-column>

            <el-table-column show-overflow-tooltip prop="create_user" align="center" label="创建人" width="60">
              <template #default="scope">
                <span>{{ userDict[scope.row.create_user] }}</span>
              </template>
            </el-table-column>

            <el-table-column fixed="right" prop="desc" align="center" label="操作" width="190">
              <template #default="scope">
                <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showEnvSelector(scope.row)">运行</el-button>
                <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showEditDrawer('edit', scope.row)">修改</el-button>
                <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showAddDrawer(scope.row)">复制</el-button>
                <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showReport(scope.row)">查看报告</el-button>
                <el-popconfirm width="250px" :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row)">
                  <template #reference>
                    <el-button style="margin: 0; padding: 2px;color: red" type="text" size="small">删除</el-button>
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

        </el-tab-pane>

        <EditDrawer :business-id="project.business_id"></EditDrawer>
        <AddDrawer :project-id="queryItems.project_id" :module-id="queryItems.module_id"></AddDrawer>
        <SelectRunEnv :test-type="'api'" :business-id="project.business_id"></SelectRunEnv>
        <ShowRunProcess :test-type="'api'"></ShowRunProcess>
        <el-dialog 
            v-model="reportTableIsShow" 
            title="报告列表" 
            width="85%"
            :close-on-click-modal="false"
            :close-on-press-escape="false"
            top="3vh"
            class="report-table-dialog">
          <ReportTable :test-type="'api'" :user-dict="userDict" :user-list="userList"></ReportTable>
        </el-dialog>
      </el-tabs>
    </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed, nextTick} from "vue";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './edit-drawer.vue'
import AddDrawer from './add-drawer.vue'
import SelectRunEnv from '@/components/select-run-env.vue'
import ShowRunProcess from '@/components/show-run-process.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {
  ChangeApiLevel,
  ChangeApiStatus,
  GetApiToStep,
  GetApiList,
  DeleteApi,
  ChangeApiSort,
  RunApi
} from "@/api/autotest/api";
import {Plus, Help, SortThree} from "@icon-park/vue-next";
import {GetUserList} from "@/api/system/user";
import ReportTable from "@/components/autotest/report/report-table.vue";
import {GetProject} from "@/api/autotest/project";

const tableIsLoading = ref(false)
const reportTableIsShow = ref(false)
const activeTab = ref('api')
const newIdList = ref([])
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const tableDataList = ref([])
const userList = ref([])
const userDict = ref({})
const selectApi = ref({})
const project = ref({})
const runTrigger = 'api-index'
const runEvent = 'select-run-env'
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  module_id: undefined,
  project_id: undefined
})

const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.68}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.79}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

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

const getUserList = () => {
  GetUserList({}).then((response: object) => {
    userList.value = response.data.data
    response.data.data.forEach(item => {
      userDict.value[item.id] = item.name
    })
  })
}

const getApiToStep = (row: { id: any; }) => {
  tableIsLoading.value = true
  GetApiToStep({ id: row.id }).then(response => {
    tableIsLoading.value = false
    if (response){
      bus.emit(busEvent.drawerIsShow, {eventType: 'api-use', content: response.data})
    }
  })
}

const selectApiLevel = (row: { id: any; level: any; }) => {
  tableIsLoading.value = true
  ChangeApiLevel({id: row.id, level: row.level}).then(response => {
    tableIsLoading.value = false
  })
}

const changeStatus = (row: { id: any; status: any; }) => {
  tableIsLoading.value = true
  ChangeApiStatus({id: row.id, status: row.status}).then(response => {
    tableIsLoading.value = false
  })
}

const deleteData = (row: { id: any; }) => {
  DeleteApi({id: row.id}).then(response => {
    if (response){
      getTableDataList()
    }
  })
}

const showReport = (row) => {
  reportTableIsShow.value = true
  // 使用nextTick确保弹窗完全打开后再发送事件
  nextTick(() => {
    bus.emit(busEvent.drawerIsShow, {
      eventType: 'show-report-table',
      projectId: queryItems.value.project_id,
      businessId: project.value.business_id,
      runType: 'api',
      triggerId: row.id
    })
  })
}

const showAddDrawer = (row) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'add-api', content: row})
}

const showEditDrawer = (command: string, row: any) => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'api-editor',
    content: row,
    command: command,
    module_id: queryItems.value.module_id,
    project_id: queryItems.value.project_id
  })
}

const getProject = () => {
  GetProject('api', {id: queryItems.value.project_id}).then(response => {
    project.value = response.data
  })
}

const showEnvSelector = (row) => {
  selectApi.value = row
  bus.emit(busEvent.drawerIsShow, {
    eventType: runEvent,
    triggerFrom: runTrigger,
    showSelectRunModel: false,
    runName: row.name,
    business_id: project.value.business_id,
    args: null
  })
}

const runApis = (runConf: { runEnv: any; }) => {
  RunApi('api',{
    project_id: selectApi.value.project_id,
    id_list: [selectApi.value.id],
    env_list: runConf.runEnv
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

const getTableDataList = () => {
  tableIsLoading.value = true
  GetApiList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

const sortTable = () => {
  tableIsLoading.value = true
  ChangeApiSort({
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
  bus.on(busEvent.treeIsChoice, treeIsChoice);
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.treeIsChoice, treeIsChoice);
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
  window.removeEventListener('resize', handleResize);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'api-editor') {
    getTableDataList()
  } else if (message.eventType === 'select-run-env' && message.triggerFrom === runTrigger) {
    runApis(message)
  }
}

const treeIsChoice = (message: any) => {
  if (message.eventType === 'module') {
    queryItems.value.module_id = message.content.id
    queryItems.value.project_id = message.content.project_id
    queryItems.value.page_no = 1
    queryItems.value.page_size = 20
    getProject()
    getTableDataList()
  }
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

</script>

<style scoped lang="scss">
.block_post {
  border: 1px solid #49cc90;
  background-color: rgba(73, 204, 144, .1)
}

.block_method_post {
  background-color: #49cc90;
}

.block_put {
  border: 1px solid #fca130;
  background-color: rgba(252, 161, 48, .1)
}

.block_method_put {
  background-color: #fca130;
}

.block_get {
  border: 1px solid #61affe;
  background-color: rgba(97, 175, 254, .1)
}

.block_method_get {
  background-color: #61affe;
}

.block_delete {
  border: 1px solid #f93e3e;
  background-color: rgba(249, 62, 62, .1)
}

.block_method_delete {
  background-color: #f93e3e;
}

.block_patch {
  border: 1px solid #50e3c2;
  background-color: rgba(80, 227, 194, .1)
}

.block_method_patch {
  background-color: #50e3c2;
}

.block_head {
  border: 1px solid #e6a23c;
  background-color: rgba(230, 162, 60, .1)
}

.block_method_head {
  background-color: #e6a23c;
}

.block_options {
  border: 1px solid #409eff;
  background-color: rgba(64, 158, 255, .1)
}

.block_method_options {
  background-color: #409eff;
}

.block {
  position: relative;
  border-radius: 4px;
  /*height: 48px;*/
  overflow: hidden;
  padding: 5px;
  display: flex;
  align-items: center;
}

.block_url {
  word-break: normal;
  width: auto;
  display: block;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow: hidden;
  -webkit-box-flex: 1;
  -ms-flex: 1;
  font-family: Open Sans, sans-serif;
  color: #3b4151;
}

.block_name {
  padding-left: 5px;
  word-break: normal;
  width: auto;
  display: block;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow: hidden;
  -webkit-box-flex: 1;
  -ms-flex: 1;
  font-family: Open Sans, sans-serif;
  color: #3b4151;
}

.block_method_color {
  cursor: pointer;
  color: #fff;
}

.block-method {
  font-size: 14px;
  font-weight: 600;
  min-width: 50px;
  padding: 0px 10px;
  text-align: center;
  border-radius: 5px;
  text-shadow: 0 1px 0 rgba(0, 0, 0, .1);
  font-family: Titillium Web, sans-serif;
}

.block-summary-description {
  word-break: normal;
  width: auto;
  display: block;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow: hidden;
  -webkit-box-flex: 1;
  -ms-flex: 1;
  font-family: Open Sans, sans-serif;
  color: #3b4151;
}


.api-level-P0 :deep(.el-input__wrapper){
  background-color: #F56C6C;
}

.api-level-P1 :deep(.el-input__wrapper){
  background-color: #E6A23C;
}

.api-level-P2 :deep(.el-input__wrapper){
  background-color: #67C23A;
}

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
