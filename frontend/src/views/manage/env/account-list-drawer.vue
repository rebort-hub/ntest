<template>
  <div>
    <el-drawer v-model="drawerIsShow" title="账号管理" size="80%">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showEditDrawer(undefined)"> 添加账号</el-button>
      </div>

      <div class="layout-container-form-search">
        <el-input v-model="queryItems.parent_name" disabled size="small" clearable style="width: 200px; margin-right: 10px" />

        <el-input
            v-model="queryItems.name"
            clearable
            size="small"
            style="width: 200px; margin-right: 10px"
            placeholder="请输入账号名，支持模糊搜索"/>

        <el-input
            v-model="queryItems.value"
            placeholder="请输入账号，支持模糊搜索"
            size="small"
            clearable
            style="width: 200px; margin-right: 10px"
        />

        <el-button type="primary" @click="getTableDataList"> 搜索</el-button>
      </div>
    </div>

    <div style="margin-top: 10px">
      <el-table
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="tableDataList"
          style="width: 100%"
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

        <el-table-column show-overflow-tooltip prop="name" align="center" label="账号名" min-width="15%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="value" align="center" label="账号" min-width="15%">
          <template #default="scope">
            <span> {{ scope.row.value }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="password" align="center" label="密码" min-width="30%">
          <template #default="scope">
            <span> {{ scope.row.password }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="desc" align="center" label="备注" min-width="15%">
          <template #default="scope">
            <span> {{ scope.row.desc }} </span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" width="110">
          <template #default="scope">
            <el-button style="margin: 0; padding: 2px" type="text" size="small" @click.native="showEditDrawer(scope.row)">修改</el-button>
            <el-button style="margin: 0; padding: 2px" type="text" size="small" @click.native="copyData(scope.row)">复制</el-button>
            <el-popconfirm :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row.id)">
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
    </div>

    <editAccountDrawer></editAccountDrawer>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import Pagination from '@/components/pagination.vue'
import editAccountDrawer from './edit-account-drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";

import {GetAccountList, DeleteAccount, CopyEnv, ChangeAccountSort} from "@/api/manage/env";
import {Help, SortThree} from "@icon-park/vue-next";

const drawerIsShow = ref(false)
const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  parent_id: undefined,
  parent_name: undefined,
  name: undefined,
  value: undefined
})

const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.7}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.8}px`
  }
}

const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])

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

const showEditDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'account',
    parent_id: queryItems.value.parent_id,
    content: row
  });
}

const copyData = (row) => {
  CopyEnv({id: row.id}).then((response: object) => {
    if (response){
      getTableDataList()
    }
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetAccountList(queryItems.value).then((response: object) => {
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
  ChangeAccountSort({
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

const deleteData = (dataId: object) => {
  DeleteAccount({id: dataId}).then(response => {
    if (response){
      getTableDataList()
    }
  })
}

onMounted(() => {
  bus.on(busEvent.drawerIsShow, drawerIsShowByBus);
  bus.on(busEvent.drawerIsCommit, drawerIsCommitByBus);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, drawerIsShowByBus);
  bus.off(busEvent.drawerIsCommit, drawerIsCommitByBus);
  window.removeEventListener('resize', handleResize);
})

const drawerIsShowByBus = (message: any) => {
  if (message.eventType === 'account-list') {
    queryItems.value.parent_id = message.content.id
    queryItems.value.parent_name = message.content.name
    drawerIsShow.value = true
    getTableDataList()
  }
}

const drawerIsCommitByBus = (message: any) => {
  if (message.eventType === 'account'){
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">
.status-select-todo :deep(.el-input__wrapper){
  background-color: #F56C6C;
}

.status-select-doing :deep(.el-input__wrapper){
  background-color: #409EFF;
}

.status-select-done :deep(.el-input__wrapper){
  background-color: #58D68D;
}

.replays-select-0 :deep(.el-input__wrapper){
  background-color: #F56C6C;
}

.replays-select-1 :deep(.el-input__wrapper){
  background-color: #58D68D;
}

</style>
