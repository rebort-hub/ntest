<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showEditDrawer(undefined, 'add')"> 添加权限</el-button>
      </div>

      <div class="layout-container-form-search">
        <el-input
            v-model="queryItems.name"
            clearable
            size="small"
            style="width: 400px; margin-right: 10px"
            placeholder="权限名，支持模糊搜索"/>
        <el-input
            v-model="queryItems.source_addr"
            clearable
            size="small"
            style="width: 400px; margin-right: 10px"
            placeholder="权限地址，支持模糊搜索"/>

        <el-button type="primary" @click="getTableDataList()"> 搜索</el-button>
      </div>
    </div>

    <div style="margin: 0 10px 0 10px">
      <el-tabs v-model="activeName" @tab-change="changePermissionType">
        <el-tab-pane label="前端权限" name="front" />
        <el-tab-pane label="后端权限" name="api" />
      </el-tabs>
    </div>

    <div style="margin: 10px">
      <el-table
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="tableDataList"
          style="width: 100%"
          stripe
          :height="tableHeight">

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

        <el-table-column show-overflow-tooltip label="权限类型" prop="source_type" align="center" min-width="8%">
          <template #default="scope">
            <span> {{ sourceTypeDict[scope.row.source_type] }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="权限名" prop="name" align="center" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="权限地址" prop="source_addr" align="center" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.source_addr }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="备注" prop="desc" align="center" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.desc }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="创建时间" prop="create_time" align="center" min-width="12%">
          <template #default="scope">
            <span>{{ paramsISOTime(scope.row.create_time) }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip align="center" label="操作" width="110">
          <template #default="scope">
            <el-button type="text" size="small" style="margin: 0; padding: 2px" @click.native="showEditDrawer(scope.row, 'edit')">修改</el-button>
            <el-button type="text" size="small" style="margin: 0; padding: 2px" @click.native="showEditDrawer(scope.row, 'copy')">复制</el-button>
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

    <EditDrawer :source-type-dict="sourceTypeDict" :active-name="activeName"></EditDrawer>
    <AddDrawer :source-type-dict="sourceTypeDict" :active-name="activeName"></AddDrawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './edit-drawer.vue'
import AddDrawer from './add-drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ChangePermissionSort, DeletePermission, GetPermissionList, GetPermissionType} from "@/api/system/permission";
import {Help, SortThree} from "@icon-park/vue-next";
import {paramsISOTime} from "@/utils/parse-data";

const activeName = ref('front')
const tableIsLoading = ref(false)
const tableDataList = ref([])
const sourceTypeDict = ref({})
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  source_addr: undefined,
  name: undefined,
  source_type: 'front'
})
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.66}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.77}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const showEditDrawer = (row: object | undefined, command: string) => {
  let eventType = command == 'add' ? 'add-permission' : 'edit-permission'
  bus.emit(busEvent.drawerIsShow, {eventType: eventType, content: row, 'command': command});
}

const deleteData = (dataId: number) => {
  DeletePermission({id: dataId}).then(response => {
    if (response){
      getTableDataList()
    }
  })
}

const getTableDataList = () => {
  queryItems.value.name = queryItems.value.name ? queryItems.value.name : undefined
  queryItems.value.source_addr = queryItems.value.source_addr ? queryItems.value.source_addr : undefined
  tableIsLoading.value = true
  GetPermissionList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

const changePermissionType = (name: string) => {
  queryItems.value.page_no = 1
  queryItems.value.source_type = name
  getTableDataList()
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
  ChangePermissionSort({
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

  GetPermissionType().then(response => {
    sourceTypeDict.value = response.data
  })

  getTableDataList()

  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
  window.removeEventListener('resize', handleResize);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'permission') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
