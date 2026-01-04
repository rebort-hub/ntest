<template>
    <div>
      <el-table
          ref="elementTableRef"
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

        <el-table-column show-overflow-tooltip prop="name" label="元素名称" min-width="15%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="by" align="center" min-width="12%">
          <template #header>
            <span>定位方式</span>
            <el-tooltip class="item" effect="dark" placement="top-start" content="在此处新增/修改地址（定位方式为【页面地址】）后，会自动同步到页面信息的页面地址">
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </el-tooltip>
          </template>
          <template #default="scope">
            <span> {{ busEvent.data.findElementOptionDict[scope.row.by] }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="element" align="center" label="元素表达式" min-width="42%">
          <template #default="scope">
            <span> {{ scope.row.element }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="wait_time_out" align="center" min-width="10%">
          <template #header>
            <span>等待时间(秒)</span>
            <el-tooltip class="item" effect="dark" placement="top-start" content="预设等待元素出现的超时时间，再执行用例时，将会执行此时间的等待(秒)">
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </el-tooltip>
          </template>
          <template #default="scope">
            <span> {{ scope.row.wait_time_out }} </span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" prop="desc" align="center" label="操作" width="120">
          <template #default="scope">
            <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showEditDrawer('edit', scope.row)">修改</el-button>
            <el-popconfirm width="250px" title="复制此元素并生成新的元素?" @confirm="showEditDrawer('copy', scope.row)">
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
      <pagination
          v-show="tableDataTotal > 0"
          :pageNum="queryItems.page_no"
          :pageSize="queryItems.page_size"
          :total="tableDataTotal"
          @pageFunc="changePagination"
      />
        <EditDrawer :test-type="testType" :device-list="deviceList"></EditDrawer>
        <AddDrawer :test-type="testType" :device-list="deviceList"></AddDrawer>
    </div>

</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, watch, computed} from "vue";
import {Help, SortThree} from "@icon-park/vue-next";

import Pagination from '@/components/pagination.vue'
import EditDrawer from './edit-drawer.vue'
import AddDrawer from './add-drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {GetElementList, DeleteElement, ChangeElementSort} from "@/api/autotest/element";
import {GetPhoneList} from "@/api/autotest/device-phone";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  pageId: {
    default: undefined,
    type: Number
  }
})

watch(() => props.pageId, (newValue, oldValue) => {
  if (newValue){
    queryItems.value.page_id = newValue
    getTableDataList()
  }
})

const elementTableRef = ref(null)
const tableIsLoading = ref(false)
const deviceList = ref([])
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  page_id: undefined
})
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.63}px`
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

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const deleteData = (row: { id: any; }) => {
  DeleteElement(props.testType, {id: row.id}).then(response => {
    if (response){
      getTableDataList()
    }
  })
}

const showEditDrawer = (command: string, row: any) => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: command === 'add' ? 'add-element' : 'edit-element',
    content: row,
    command: command,
    page_id: queryItems.value.page_id
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetElementList(props.testType, queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
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
  ChangeElementSort(props.testType, {
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
  if (props.testType === 'app' && deviceList.value.length === 0) {
    GetPhoneList({ page_no: 1, page_size: 99999 }).then(response => {
      deviceList.value = response.data.data
    })
  }
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
  setTableHeight()
  window.addEventListener('resize', handleResize);

})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
  window.removeEventListener('resize', handleResize);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'element-editor' || message.eventType === 'element-upload-success') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
