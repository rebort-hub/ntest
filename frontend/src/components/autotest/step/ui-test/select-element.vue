<template>
  <div>
    <el-form label-width="60px">

      <el-row>
        <el-col :span="8">
          <el-form-item label="选服务" size="small" style="margin-bottom: 5px">
            <el-select
                v-model="queryItems.project_id"
                placeholder="请选择服务"
                size="small"
                style="min-width: 100%"
                filterable
                default-first-option
                @change="selectProject"
            >
              <el-option v-for="(item) in projectList" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
        </el-col>

        <el-col :span="8">
          <el-form-item label="选模块" size="small" style="margin-bottom: 5px">
            <el-cascader
                v-model="queryItems.module_id"
                placeholder="选择模块"
                filterable
                size="small"
                style="min-width: 100%"
                :options="moduleTree"
                :props="{ checkStrictly: true, value: 'id', label: 'name' }"
                clearable
                @change="selectModule"
            />
          </el-form-item>
        </el-col>

        <el-col :span="8">
          <el-form-item label="选页面" size="small" style="margin-bottom: 5px">
            <el-select
                v-model="queryItems.page_id"
                placeholder="选页面"
                size="small"
                style="min-width: 100%"
                filterable
                default-first-option
                @change="selectPage"
            >
              <el-option v-for="(item) in pageList" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <div>
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
      >
        <el-table-column prop="num" align="center" label="序号" min-width="10%">
          <template #default="scope">
            <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="name" align="center" label="元素名称" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="by" align="center" label="定位方式" min-width="20%">
          <template #default="scope">
            <span> {{ busEvent.data.findElementOptionDict[scope.row.by] }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="element" align="center" label="定位元素" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.element }} </span>
          </template>
        </el-table-column>

        <el-table-column align="center" label="操作" min-width="10%">
          <template #default="scope">
            <el-button type="primary" size="small" @click.native="elementToStep(scope.row)">转步骤</el-button>
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
    </div>

  </div>
</template>

<script lang="ts" setup>

import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import {GetApi, GetApiFrom, GetApiList, GetApiToStep} from "@/api/autotest/api";
import {GetProjectList} from "@/api/autotest/project";
import {GetModuleList} from "@/api/autotest/module";
import {bus, busEvent} from "@/utils/bus-events";
import apiFromDrawer from "@/components/autotest/api/from-drawer.vue";
import apiUseDrawer from "@/components/autotest/api/use-drawer.vue";

import {ElMessage} from "element-plus";
import Pagination from "@/components/pagination.vue";
import toClipboard from "@/utils/copy-to-memory";
import {arrayToTree} from "@/utils/parse-data";
import {GetElementList} from "@/api/autotest/element";
import {GetPageList} from "@/api/autotest/page";
import {ChangeStepElement} from "@/api/autotest/step";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  projectId: {
    default: '',
    type: Number,
  },
  caseId: {
    default: '',
    type: Number,
  },
  stepId: {
    default: '',
    type: Number
  },
})

const queryItems = ref({
  page_no: 1,
  page_size: 99999,
  detail: true,
  project_id: undefined,
  module_id: undefined,
  page_id: undefined
})
const tableIsLoading = ref(false)
const tableDataList = ref([])
const projectList = ref([])
const moduleTree = ref([])
const pageList = ref([])
const tableDataTotal = ref(0)
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.54}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.70}px`
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

const getTableDataList = () => {
  tableIsLoading.value = true
  GetElementList(props.testType, queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

const getProjectList = () => {
  if (projectList.value.length < 1){
    GetProjectList(props.testType, {page_no: 1, page_size: 99999}).then((response: object) => {
      projectList.value = response.data.data
    })
  }
}

const selectProject = (projectId: any) => {
  GetModuleList(props.testType, { project_id: projectId, page_no: 1, page_size: 99999 }).then(response => {
    moduleTree.value = arrayToTree(response.data.data, null)
  })
}

const selectModule = (moduleList: any) => {
  queryItems.value.module_id = moduleList
  if (moduleList.length > 0) {
    queryItems.value.module_id = moduleList.slice(-1)[0] // 取列表中的最后一个
    GetPageList(props.testType, queryItems.value).then((response: object) => {
      tableIsLoading.value = false
      pageList.value = response.data.data
    })
  }
}

const selectPage = (pageId: any) => {
  queryItems.value.page_id = pageId
  tableIsLoading.value = true
  GetElementList(props.testType, { page_id: pageId, page_no: 1, page_size: 99999, detail: true }).then(response => {
    tableIsLoading.value = false
    tableDataTotal.value = response.data.total
    tableDataList.value = response.data.data
  })
}

// 新增步骤或者更换步骤选择的元素
const elementToStep = (row: any) => {
  if (props.stepId){ // 步骤更换元素
    ChangeStepElement(props.testType, {id: props.stepId, element_id: row.id}).then(response => {
      if (response){
        bus.emit(busEvent.drawerIsCommit, {eventType: 'change-step-element', elementId: row.id})
      }
    })
  }else { // 新增步骤
    const step = JSON.parse(JSON.stringify(row));
    step.element_id = step.id
    step.id = undefined
    bus.emit(busEvent.drawerIsShow, {eventType: 'step-editor', content: step})
  }
}

onMounted(() => {
  getProjectList()
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
  window.removeEventListener('resize', handleResize);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'select-step') {
    queryItems.value.project_id = undefined
    queryItems.value.module_id = undefined
  }
}

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

</style>
