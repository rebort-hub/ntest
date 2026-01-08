<template>
  <div style="margin: 10px">
      <el-table
          ref="expandStepTableRef"
          class="expandStepTable"
          row-key="id"
          :show-header="false"
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="stepList"
          stripe
          highlight-current-row
          :row-class-name="hiddenExpandRowIcon"
          :expand-row-keys="expandIdList"
          @expand-change="changeExpandStatus"
          @selection-change="clickSelectAll"
          @row-dblclick="rowDblclick">

        <el-table-column type="expand" width="20">
          <template #default="scope">
            <expand-step
                :ref="`${scope.row.id}_${scope.$index}_${scope.row.quote_case}`"
                :step-list="scope.row.stepList"
                :test-type="testType"
                :current-case-id="currentCaseId"
                :case-id="scope.row.quote_case"
            />
          </template>
        </el-table-column>

        <el-table-column prop="id" label="序号" align="center" width="40">
          <template #default="scope">
            <span>{{ scope.$index + 1 }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="60">
          <template #header>
            <span>状态</span>
            <el-tooltip class="item" effect="dark" placement="top-start" content="若此处设置为不运行，则执行测试时将不会运行此步骤">
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </el-tooltip>
          </template>
          <template #default="scope">
            <el-switch
                v-model="scope.row.status"
                size="small"
                :inactive-value="'disable'"
                :active-value="'enable'"
                @change="changeStatus(scope.row, null)"
            />
          </template>
        </el-table-column>

        <el-table-column align="left" prop="name" label="步骤名称" min-width="45%">
          <template #default="scope">
            <el-tag size="small" :type="scope.row.quote_case ? 'warning' : 'success'">
              {{ scope.row.quote_case ? '引用' : '步骤' }}
            </el-tag>
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column v-if="testType !== 'api'" align="right" prop="execute_type" label="执行事件" min-width="15%">
          <template #default="scope">
            <span>{{ busEvent.data.executeTypeDict[scope.row.execute_type] }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="desc" align="right" min-width="17%">
          <template #header>
            <span>详情</span>
            <el-tooltip class="item" effect="dark" placement="top-start" content="引用用例的详情">
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </el-tooltip>
          </template>
          <template #default="scope">
            <el-popover
                v-if="scope.row.quote_case"
                :ref="scope.row.id"
                trigger="hover"
                placement="bottom-start"
                style="margin-right: 10px"
                popper-class="down-popover"
            >
              <showCaseDesc
                  :data-type="testType"
                  :case-desc="scope.row.desc"
                  :case-skip-if="scope.row.skip_if"
                  :case-variables="scope.row.variables"
                  :case-extracts="scope.row.output"
                  :case-id="scope.row.quote_case"
              />
              <span slot="reference"> {{ scope.row.desc || '-' }} </span>
            </el-popover>
          </template>
        </el-table-column>

        <el-table-column fixed="right" prop="desc" align="center" label="操作" width="160">
          <template #default="scope">
            <el-button v-if="scope.row.quote_case" type="text" size="small" style="margin: 0; padding: 2px" @click.native="showEditNameDrawer(scope.row)">改名</el-button>

            <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showEditDrawer(scope.row)">修改</el-button>

            <el-popconfirm width="250px" :title="`复制用例【${scope.row.name}】下的所有步骤，并在【当前用例】下生成对应的步骤?`" @confirm="copyCaseStepToCurrentCase(scope.row)">
              <template #reference>
                <el-button v-if="scope.row.quote_case" style="margin: 0; padding: 2px" type="text" size="small">拉取</el-button>
              </template>
            </el-popconfirm>

            <el-popconfirm :title="`复制步骤【${scope.row.name}】，并在【当前用例】下生成新的步骤?`" @confirm="copyData(scope.row)">
              <template #reference>
                <el-button style="margin: 0; padding: 2px" type="text" size="small">复制</el-button>
              </template>
            </el-popconfirm>

            <el-popconfirm :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row)">
              <template #reference>
                <el-button v-if="caseId === currentCaseId" style="margin: 0; padding: 2px;color: red" type="text" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>
</template>

<script setup lang="ts">
import {ref,  watch} from "vue";
import {Help} from "@icon-park/vue-next";

import showCaseDesc from '../case/show-desc.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {ChangeStepStatus, DeleteStep, GetStepList, CopyStep} from "@/api/autotest/step";
import {CopyCaseStep} from "@/api/autotest/case";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  currentCaseId: {
    default: '',
    type: Number,
  },
  caseId: {
    default: '',
    type: Number,
  },
  stepList: {
    default: [],
    type: Array,
  }
})

watch(() => props.caseId, (newValue, oldValue) => {
  if (newValue){
    queryItems.value.case_id = newValue
    getTableDataList()
  }
})

const expandStepTableRef = ref(`expandStepTableRef_${props.caseId}_${Date.now()}`)
const tableIsLoading = ref(false)
const tableDataList = ref([])
const expandIdList = ref([])
const userList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 1000,
  detail: true,
  case_id: Number
})
const drawerIsLoading = ref(false)
const selectedList = ref([])

const rowDblclick = async (row: any, column: any, event: any) => {
  try {
    await toClipboard(row[column.property]);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}

const clickSelectAll = (val: never[]) => {
  selectedList.value = val
}

const hiddenExpandRowIcon = (row: { row: { quote_case: any; }; }) => {
  const canNotSort = expandIdList.value.length > 0 ? 'canNotSort' : '' // 是否能拖动
  const hiddenRowIcon = row.row.quote_case ? '' : 'hiddenRowIcon' // 是否展示展开/收起icon
  return `${canNotSort} ${hiddenRowIcon}`
}

const changeExpandStatus = (row: { id: any; quote_case: any; stepList: any; }, expandedRows: any) => {
  const expandIdIndex = expandIdList.value.indexOf(row.id)
  if (expandIdIndex === -1) {
    // 获取引用用例的步骤列表
    tableIsLoading.value = true
    GetStepList(props.testType, { case_id: row.quote_case }).then(response => {
      tableIsLoading.value = false
      expandIdList.value.push(row.id)
      row.stepList = response.data.data
    })
  } else {
    expandIdList.value.splice(expandIdIndex, 1)
  }
}

const changeStatus = (row: { id: any; status: number; } | null, status: number) => {
  const changeStatus = row ? row.status : status
  drawerIsLoading.value = true
  ChangeStepStatus(props.testType, {id_list: [row.id], status: changeStatus}).then(response => {
    drawerIsLoading.value = false
    if (response){
      getTableDataList()
    }
  })
}

const deleteData = (row: any) => {
  drawerIsLoading.value = true
  DeleteStep(props.testType,{id_list: [row.id]}).then(response => {
    drawerIsLoading.value = false
    if (response){
      getTableDataList()
    }
  })
}

const copyData = (row: { id: any; }) =>{
  tableIsLoading.value = true
  CopyStep(props.testType,{ id: row.id, case_id: props.currentCaseId }).then(response => {
    tableIsLoading.value = false
    bus.emit(busEvent.drawerIsCommit, {eventType: 'step-is-copy-to-case'});
    // if (response) {
    //   getTableDataList()
    // }
  })
}

const showEditNameDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'edit-step-name', content: row});
}

const showEditDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'step-editor', content: row});
}

const copyCaseStepToCurrentCase = (row: { quote_case: any; isLoading: boolean; id: any; }) => {
  CopyCaseStep(props.testType,{ from_case: row.quote_case, to_case: props.currentCaseId }).then(response => {
    if (response) {
      getTableDataList()
    }
  })
}

const getTableDataList = () => {
  queryItems.value.case_id = props.caseId
  tableIsLoading.value = true
  GetStepList(props.testType, queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
  })
}

</script>

<style scoped lang="scss">

.expandStepTable :deep(.hiddenRowIcon) .el-table__expand-icon {
  display: none;
}

.expandStepTable :deep(.el-table__expand-icon) .cell {
  padding: 0 !important;
  margin: 0 !important;
}

</style>
