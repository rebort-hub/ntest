<template>
    <div style="margin-left: 5px">
      <el-tabs v-model="activeTab" class="table_padding table_api">
        <el-tab-pane name="page">
          <template #label>
            <span> 页面列表 </span>
            <el-popover class="el_popover_class" placement="top-start" trigger="hover" content="添加页面">
              <template #reference>
                <el-button
                    v-show="queryItems.module_id"
                    type="text"
                    style="margin-left: 10px"
                    @click="showEditDrawer('add', undefined)"
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

            <el-table-column show-overflow-tooltip prop="name" align="center" label="页面名称" min-width="20%">
              <template #default="scope">
                <span> {{ scope.row.name }} </span>
              </template>
            </el-table-column>

            <el-table-column v-if="testType === 'ui'" show-overflow-tooltip prop="addr" align="center" min-width="50%">
              <template #header>
                <el-tooltip class="item" effect="dark" placement="top-start" >
                  <template #content>
                    <div>在页面元素处新增/修改地址（定位方式为【页面地址】）后，会自动同步到此处</div>
                  </template>
                  <span> 页面地址 <span style="margin-left:5px;color: #409EFF"><help></help></span></span>
                </el-tooltip>
              </template>
              <template #default="scope">
                <span> {{ scope.row.addr || '未设置' }} </span>
              </template>
            </el-table-column>

            <el-table-column fixed="right" prop="desc" align="center" label="操作" width="160">
              <template #default="scope">
                <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showEditDrawer('edit', scope.row)">修改</el-button>
                <el-popconfirm title="复制此页面并生成新的页面?" @confirm="copyPage(scope.row)">
                  <template #reference>
                    <el-button style="margin: 0; padding: 2px" type="text" size="small">复制</el-button>
                  </template>
                </el-popconfirm>
                <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showEditDrawer('element-list', scope.row)">元素列表</el-button>
<!--                <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showUploadDrawer(scope.row)">导入元素</el-button>-->
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

        <EditDrawer :test-type="testType"></EditDrawer>
        <AddDrawer :test-type="testType"></AddDrawer>
        <UploadDrawer :test-type="testType"></UploadDrawer>
      </el-tabs>
    </div>

</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import {Plus, Help, SortThree} from "@icon-park/vue-next";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './edit-drawer.vue'
import AddDrawer from './add-drawer.vue'
import UploadDrawer from './upload-drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import { getFindElementOption } from '@/utils/get-config'
import {GetPageList, DeletePage, ChangePageSort, CopyPage} from "@/api/autotest/page";

const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})

const tableIsLoading = ref(false)
const activeTab = ref('page')
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])
const tableDataList = ref([])
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

const deleteData = (row: { id: any; }) => {
  DeletePage(props.testType, {id: row.id}).then(response => {
    if (response){
      getTableDataList()
    }
  })
}

const showEditDrawer = (command: string, row: any) => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: command === 'add' ? 'add-page' : 'edit-page',
    content: row,
    command: command,
    module_id: queryItems.value.module_id,
    project_id: queryItems.value.project_id
  })
}

// const showUploadDrawer = (row: any) => {
//   bus.emit(busEvent.drawerIsShow, {eventType: 'upload-element', content: row})
// }

const copyPage = (row: { id: any; }) => {
  tableIsLoading.value = true
  CopyPage(props.testType, {id: row.id}).then(response => {
    tableIsLoading.value = false
    getTableDataList()
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetPageList(props.testType, queryItems.value).then((response: object) => {
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
  ChangePageSort(props.testType, {
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
  getFindElementOption(props.testType)
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
  if (message.eventType === 'page-editor') {
    getTableDataList()
  }
}

const treeIsChoice = (message: any) => {
  if (message.eventType === 'module') {
    queryItems.value.module_id = message.content.id
    queryItems.value.project_id = message.content.project_id
    queryItems.value.page_no = 1
    queryItems.value.page_size = 20
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
