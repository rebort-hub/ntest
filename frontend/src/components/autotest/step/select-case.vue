<template>
  <div>
    <el-form label-width="60px">
      <el-row>
        <el-col :span="12">
          <el-form-item label="选服务" size="small">
            <el-select
                ref="projectSelectorView"
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

        <el-col :span="12">
          <el-form-item label="用例集" size="small">
            <el-cascader
                v-model="queryItems.suite_id"
                placeholder="用例集"
                filterable
                size="small"
                style="min-width: 95%"
                :options="caseSuiteTree"
                :props="{ checkStrictly: true, value: 'id', label: 'name' }"
                clearable
                @change="selectCaseSuite"
            />
            <el-tooltip class="item" effect="dark" placement="top-start" content="引用用例的详情">
              <template #content>
                <div>1、若选择的服务是当前服务，可引用类型为<span style="color: red">基础用例集</span>和<span style="color: red">引用用例集</span>的用例集</div>
                <div>2、若选择的服务不是当前服务，只可引用类型为<span style="color: red">引用用例集</span>的用例集</div>
              </template>
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </el-tooltip>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <!-- 列表 -->
    <div>
      <el-table
          ref="selectStepTableRef"
          class="selectStepTable"
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="tableDataList"
          style="width: 100%"
          :header-cell-style="{'text-align':'center'}"
          stripe
          row-key="id"
          :height="tableHeight"
          :expand-row-keys="expandIdList"
          @expand-change="changeExpandStatus"
          @row-dblclick="rowDblclick">
      >

        <el-table-column type="expand">
          <template #default="scope">
            <expandStep
                :ref="`${scope.row.id}_${scope.$index}`"
                :test-type="testType"
                :current-case-id="caseId"
                :case-id="scope.row.id"
                :step-list="scope.row.stepList"
            />
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="name" label="用例名称" align="left" min-width="65%">
          <template #default="scope">
            <el-tag size="small" :type="scope.row.suite_id ? 'danger': scope.row.quote_case ? 'warning' : 'success'">
              {{ scope.row.suite_id ? '用例' : scope.row.quote_case ? '引用用例' : '步骤' }}
            </el-tag>
            <span style="margin-left: 5px"> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="desc" align="left" label="描述" min-width="20%">
          <template #default="scope">
            <el-popover
                v-show="scope.row.quote_case"
                trigger="hover"
                placement="bottom-start"
                style="margin-right: 10px"
                popper-class="down-popover"
                width="1300px"
            >
              <showCaseDesc
                  :ref="scope.row.id"
                  :case-desc="scope.row.desc"
                  :case-skip-if="scope.row.skip_if"
                  :case-variables="scope.row.variables"
                  :case-extracts="scope.row.output"
                  :project-id="queryItems.project_id"
              />
              <template #reference>
                <span> {{ scope.row.desc || '-' }} </span>
              </template>
            </el-popover>
          </template>
        </el-table-column>

        <el-table-column align="center" label="操作" width="80">
          <template #default="scope">

            <el-popconfirm width="250px" :title="`复制用例【${scope.row.name}】下的所有步骤，并在【当前用例】下生成对应的步骤?`" @confirm="copyCaseStepToCurrentCase(scope.row)">
              <template #reference>
                <el-button style="margin: 0; padding: 2px" :loading="scope.row.loading" type="text" size="small">拉取</el-button>
              </template>
            </el-popconfirm>

            <el-popconfirm title="引用此用例为当前用例的步骤" @confirm="quoteCaseAsStep(scope.row)">
              <template #reference>
                <el-button style="margin: 0; padding: 2px" :loading="scope.row.loading" type="text" size="small">引用</el-button>
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
    </div>
  </div>
</template>

<script lang="ts" setup>

import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import {Help} from "@icon-park/vue-next";
import {GetProjectList} from "@/api/autotest/project";
import showCaseDesc from '../case/show-desc.vue'
import expandStep from './expand-step.vue'
import {bus, busEvent} from "@/utils/bus-events";

import {ElMessage} from "element-plus";
import Pagination from "@/components/pagination.vue";
import toClipboard from "@/utils/copy-to-memory";
import {arrayToTree} from "@/utils/parse-data";
import {GetCaseSuiteList} from "@/api/autotest/case-suite";
import {CopyCaseStep, GetCaseList} from "@/api/autotest/case";
import {CopyStep, GetStepList, PostStep} from "@/api/autotest/step";

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
  }
})

const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  suite_id: undefined,
  project_id: undefined
})
const tableIsLoading = ref(false)
const tableDataList = ref([])
const projectList = ref([])
const caseSuiteTree = ref([])
const selectStepTableRef = ref(null)
const expandIdList = ref([])
const tableDataTotal = ref(0)

const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.56}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.71}px`
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

const changeExpandStatus = (row: { id: any; stepList: any; }, expandedRows: any) => {
  const expandIdIndex = expandIdList.value.indexOf(row.id)
  if (expandIdIndex === -1) {
    // 获取引用用例的步骤列表
    tableIsLoading.value = true
    GetStepList(props.testType, { case_id: row.id }).then(response => {
      tableIsLoading.value = false
      expandIdList.value.push(row.id)
      row.stepList = response.data.data
    })
  } else {
    expandIdList.value.splice(expandIdIndex, 1)
  }
}

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetCaseList(props.testType, queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

const getProjectList = () => {
  if (projectList.value.length < 1){
    GetProjectList(props.testType, {page_no: 1, page_size: 1000}).then((response: object) => {
      projectList.value = response.data.data
    })
  }
}

const selectProject = (projectId: any) => {
  // GetCaseSuiteList(props.testType, { project_id: projectId, suite_type: 'base,quote', page_no: 1, page_size: 1000 }).then(response => {
  GetCaseSuiteList(props.testType, { project_id: projectId, suite_type: 'base,api,quote,process,make_data', page_no: 1, page_size: 1000 }).then(response => {
    caseSuiteTree.value = arrayToTree(response.data.data, null)
  })
}

const selectCaseSuite = (suiteList: any) => {
  queryItems.value.suite_id = suiteList
  if (suiteList.length > 0) {
    queryItems.value.suite_id = suiteList.slice(-1)[0] // 取列表中的最后一个
    getTableDataList()
  }
}

const sendEvent = (isReloadCase: boolean) => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'step-editor'});
  if (isReloadCase){
    bus.emit(busEvent.drawerIsCommit, {eventType: 'quote-case'}); // 引用用例，会合并用例的变量和头信息，需要重新获取用例的详情
  }
};

const copyCaseStepToCurrentCase = (row: { suite_id: any; isLoading: boolean; id: any; }) => {
  row.isLoading = true
  CopyCaseStep(props.testType,{ from_case: row.id, to_case: props.caseId }).then(response => {
    row.isLoading = false
    if (response) {
      sendEvent(true)
    }
  })
}

// const copyData = (row: { isLoading: boolean; id: any; }) => {
//   row.isLoading = true
//   CopyStep(props.testType, { id: row.id, case_id: props.caseId }).then(response => {
//     row.isLoading = false
//     if (response) {
//       sendEvent(false)
//     }
//   })
// }

const quoteCaseAsStep = (row: { id: number; name: any; isLoading: boolean}) =>  {
  if (row.id === props.caseId){
    ElMessage.error('不能自己引用自己')
  }else {
    var step = JSON.parse(JSON.stringify(row))
    step.quote_case = step['quote_case'] ? step['quote_case'] : step['id'] // 有可能是引用用例下的引用
    step.id = undefined
    step.case_id = props.caseId
    step.status = 'enable'
    step.run_times = 1
    step.run_times = 1
    step.name = row.name
    step.skip_on_fail = 1
    step.execute_type = ''
    step.send_keys = ''
    step.body_type = 'json'
    step.headers = [{'key': null, 'remark': null, 'value': null}]
    step.params = [{'key': null, 'value': null}]
    step.data_form = [{'data_type': null, 'key': null, 'remark': null, 'value': null}]
    step.data_json = {}
    step.extracts = [{'key': '', 'remark': null, 'value': ''}]
    step.validates = [{'key': '', 'remark': null, 'validate_type': '', 'value': ''}]

    row.isLoading = true
    PostStep(props.testType, step).then(response => {
      row.isLoading = false
      if (response) {
        sendEvent(true)
      }
    })

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
    queryItems.value.suite_id = undefined
  }
}

</script>


<style scoped lang="scss">

.selectStepTable :deep(.el-table__expand-icon) .cell {
  padding: 0 !important;
  margin: 0 !important;
}

</style>
