<template>
  <div>
    <div>
      <el-popconfirm width="250px" title="确定删除所选中的测试用例?" @confirm="deleteData(null)">
        <template #reference>
          <el-button
              :disabled="selectedList.length < 1"
              type="danger"
              size="small">批量删除</el-button>
        </template>
      </el-popconfirm>

      <el-popconfirm width="280px" title="确定把所选步骤状态改为【要执行】?" @confirm="changeStatus(null, 'enable')">
        <template #reference>
          <el-button
              :disabled="selectedList.length < 1"
              type="primary"
              size="small">批量改为要执行</el-button>
        </template>
      </el-popconfirm>

      <el-popconfirm width="280px" title="确定把所选步骤状态改为【不执行】?" @confirm="changeStatus(null, 'disable')">
        <template #reference>
          <el-button
              :disabled="selectedList.length < 1"
              type="info"
              size="small">批量改为不执行</el-button>
        </template>
      </el-popconfirm>

      <el-table
          ref="stepTableRef"
          class="stepTable"
          row-key="id"
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="tableDataList"
          stripe
          :height="tableHeight"
          :row-class-name="hiddenExpandRowIcon"
          :expand-row-keys="expandIdList"
          @expand-change="changeExpandStatus"
          @selection-change="clickSelectAll"
          @row-dblclick="rowDblclick">

        <el-table-column type="selection" width="20" />

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

        <el-table-column type="expand" width="20">
          <template #default="scope">
            <expandStep
                :ref="`${scope.row.id}_${scope.$index}_${scope.row.quote_case}`"
                :test-type="testType"
                :current-case-id="caseId"
                :case-id="scope.row.quote_case"
                :step-list="scope.row.stepList"
            />
          </template>
        </el-table-column>

        <el-table-column label="序号" header-align="center" width="40">
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
            <span style="margin-left: 5px"> {{ scope.row.name }} </span>
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
                width="1300px"
            >
              <showCaseDesc
                  :test-type="testType"
                  :case-desc="scope.row.desc"
                  :case-skip-if="scope.row.skip_if"
                  :case-variables="scope.row.variables"
                  :case-extracts="scope.row.output"
                  :case-id="scope.row.quote_case"
              />
              <template #reference>
                <span> {{ scope.row.desc || '-' }} </span>
              </template>
            </el-popover>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="create_user" align="center" label="创建人" width="60">
          <template #default="scope">
            <span>{{ userDict[scope.row.create_user] }}</span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" prop="desc" align="center" label="操作" width="140">
          <template #default="scope">
            <el-button v-if="scope.row.quote_case" type="text" size="small" style="margin: 0; padding: 2px" @click.native="showEditNameDrawer(scope.row)">改名</el-button>

            <el-button v-if="!scope.row.quote_case" type="text" size="small" style="margin: 0; padding: 2px" @click="showEditDrawer(scope.row)">修改</el-button>

            <el-popconfirm width="250px" :title="`复制用例【${scope.row.name}】下的所有步骤，并在【当前用例】下生成对应的步骤?`" @confirm="copyCaseStepToCurrentCase(scope.row)">
              <template #reference>
                <el-button v-if="scope.row.quote_case" style="margin: 0; padding: 2px" type="text" size="small">拉取</el-button>
              </template>
            </el-popconfirm>

            <el-popconfirm width="250px" :title="`复制步骤【${scope.row.name}】，并在【当前用例】下生成新的步骤?`" @confirm="copyData(scope.row)">
              <template #reference>
                <el-button style="margin: 0; padding: 2px" type="text" size="small">复制</el-button>
              </template>
            </el-popconfirm>

            <el-popconfirm width="250px" :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row)">
              <template #reference>
                <el-button style="margin: 0; padding: 2px;color: red" type="text" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

    </div>

    <EditApiStepDrawer
      v-if="testType === 'api'"
      :case-id="caseId"
      :test-type="testType"
      :project-id="projectId"
    ></EditApiStepDrawer>

    <EditUiStepDrawer
        v-if="testType !== 'api'"
        :case-id="caseId"
        :test-type="testType"
        :project-id="projectId"
    ></EditUiStepDrawer>

    <AddStepDrawer :test-type="testType" :case-id="caseId" :project-id="projectId"></AddStepDrawer>
    <editQuoteCaseNameDrawer :test-type="testType"></editQuoteCaseNameDrawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, computed, onBeforeUnmount, watch} from "vue";
import {Help, SortThree} from "@icon-park/vue-next";
import EditApiStepDrawer from './api-test/edit-api-step.vue'
import EditUiStepDrawer from './ui-test/edit-ui-step.vue'
import AddStepDrawer from './add-step-drawer.vue'
import editQuoteCaseNameDrawer from './edit-quote-case-name.vue'
import expandStep from './expand-step.vue'
import showCaseDesc from '../case/show-desc.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {ChangeStepStatus, DeleteStep, ChangeStepSort, GetStepList, CopyStep} from "@/api/autotest/step";
import {CopyCaseStep} from "@/api/autotest/case";

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
  userDict: {
    default: {},
    type: Object,
  }
})

watch(() => props.caseId, (newValue, oldValue) => {
  if (newValue){
    queryItems.value.case_id = newValue
    getTableDataList()
  }
})

const tableIsLoading = ref(false)
const stepTableRef = ref(null)
const tableDataList = ref([])
const expandIdList = ref([])
const queryItems = ref({
  page_no: 1,
  page_size: 99,
  detail: true,
  case_id: undefined
})

const selectedList = ref([])
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])

const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.64}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.76}px`
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

const clickSelectAll = (val: never[]) => {
  selectedList.value = val
}

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
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
  tableIsLoading.value = true
  ChangeStepStatus(props.testType, {id_list: getSubmitId(row), status: changeStatus}).then(response => {
    tableIsLoading.value = false
    if (response){
      getTableDataList()
    }
  })
}

const deleteData = (row: any) => {
  tableIsLoading.value = true
  DeleteStep(props.testType,{id_list: getSubmitId(row)}).then(response => {
    tableIsLoading.value = false
    if (response){
      getTableDataList()
    }
  })
}

const copyData = (row: { id: any; }) =>{
  tableIsLoading.value = true
  CopyStep(props.testType,{ id: row.id, case_id: props.caseId }).then(response => {
    tableIsLoading.value = false
    if (response) {
      getTableDataList()
    }
  })
}

const getSubmitId = (row: any) => {
  let selectedIdList: any[] = []
  if (row){
    selectedIdList = [row.id]
  }else {
    selectedList.value.forEach(item => { selectedIdList.push(item.id) })
  }
  return selectedIdList
}

const showEditNameDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'edit-step-name', content: row});
}

const showEditDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'step-editor', content: row});
}

const copyCaseStepToCurrentCase = (row: { quote_case: any; isLoading: boolean; id: any; }) => {
  CopyCaseStep(props.testType,{ from_case: row.quote_case, to_case: props.caseId }).then(response => {
    if (response) {
      getTableDataList()
    }
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetStepList(props.testType, queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    expandIdList.value = []
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
  ChangeStepSort(props.testType, {
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

const setSort = () => {
  let tbody = stepTableRef.value.$el.querySelector(".el-table__body-wrapper tbody");
  Sortable.create(tbody, {
    group: { // 相同的组之间可以相互拖拽
      name: "table",
      pull: true,
      put: true,
    },
    filter: '.canNotSort', // 不可拖动的class
    animation: 150, // ms, number 单位：ms，定义排序动画的时间
    onEnd(e: any) {
      const targetRow = tableDataList.value.splice(e.oldIndex, 1)[0]
      tableDataList.value.splice(e.newIndex, 0, targetRow)
      const tempIndex = newIdList.value.splice(e.oldIndex, 1)[0]
      newIdList.value.splice(e.newIndex, 0, tempIndex)
      sortTable()
    },
  });
}

onMounted(() => {
  queryItems.value.case_id = props.caseId
  // setSort()
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
  window.removeEventListener('resize', handleResize);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'step-editor' || message.eventType === 'step-is-copy-to-case') {
    getTableDataList()
  }
}
</script>

<style scoped lang="scss">

.stepTable :deep(.hiddenRowIcon) .el-table__expand-icon {
  display: none;
}

.stepTable :deep(.el-table__expand-icon) .cell {
  padding: 0 !important;
  margin: 0 !important;
}

</style>
