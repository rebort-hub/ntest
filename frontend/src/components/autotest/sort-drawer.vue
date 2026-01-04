<template>
  <div>
    <el-table
      ref="caseSuiteSortTableRef"
      v-loading="tableIsLoading"
      :data="tableDataList"
      stripe
      size="small"
      row-key="id">

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
          <span> {{ (pageNum - 1) * pageSize + scope.$index + 1 }} </span>
        </template>
      </el-table-column>

      <el-table-column label="名字" min-width="80%">
        <template #default="scope">
          <div>{{ scope.row.name }}</div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {GetCaseSuiteList, ChangeCaseSuiteSort} from "@/api/autotest/case-suite";
import {GetModuleList, ChangeModuleSort} from "@/api/autotest/module";
import {Help, SortThree} from "@icon-park/vue-next";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  useType:{
    default: 'module',
    type: String
  }
})

const caseSuiteSortTableRef = ref(null)
const tableIsLoading = ref(false)
const tableDataList = ref([])
const projectId = ref()
const parent = ref()
const pageNum = ref(1)
const pageSize = ref(9999)
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])

const getTableDataList = () => {
  let getFunc = props.useType === 'module' ?  GetModuleList : GetCaseSuiteList
  tableIsLoading.value = true
  getFunc(props.testType,{project_id: projectId.value, parent: parent.value}).then(response => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
  })
}

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'sort-case-suite') {
    projectId.value = message.content.project_id
    parent.value = message.content.parent
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
  // // 移除当前拖拽的行数据
  updatedData.splice(oldIndex.value, 1);
  // // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow.value);
  // 恢复样式
  event.target.classList.remove('drag-dragging');
  newIdList.value = updatedData.map(item => item.id).slice()
  sortTable()
};

const sortTable = () => {
  let sortFunc = props.useType === 'module' ?  ChangeModuleSort : ChangeCaseSuiteSort
  tableIsLoading.value = true
  sortFunc(props.testType,{
    id_list: newIdList.value,
    page_no: pageNum.value,
    page_size: pageSize.value
  }).then(response => {
    tableIsLoading.value = false
    if (response){
      getTableDataList()
    }
  })
}

</script>

<style scoped lang="scss">
// 拖拽按钮样式
.drag-button {
  cursor: grab;
  color: #409eff;
  
  &:hover {
    color: #66b1ff;
  }
  
  &:active {
    cursor: grabbing;
  }
}

// 拖拽中的样式
.drag-dragging {
  opacity: 0.5;
  cursor: grabbing !important;
}

// 表格样式优化
:deep(.el-table) {
  .el-table__header {
    th {
      background-color: #fafafa;
    }
  }
  
  .el-table__row {
    &:hover {
      background-color: #f5f7fa;
    }
  }
}

// 工具提示样式
:deep(.el-tooltip__trigger) {
  cursor: help;
}
</style>
