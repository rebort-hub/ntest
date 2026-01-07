<template>
  <div>

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
<!--        <el-button type="primary" @click="showEditDrawer(undefined)"> 添加用户</el-button>-->
      </div>

      <div class="layout-container-form-search">
        <el-input
            v-model="queryItems.name"
            clearable
            size="small"
            style="width: 200px; margin-right: 10px"
            placeholder="用户名，支持模糊搜索"/>

        <el-input
            v-model="queryItems.account"
            clearable
            size="small"
            style="width: 200px; margin-right: 10px"
            placeholder="账号，支持模糊搜索"/>

        <el-button type="primary" @click="getTableDataList()"> 搜索</el-button>
      </div>
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
        <el-table-column prop="id" label="序号" align="center" min-width="10%">
          <template #default="scope">
            <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="用户名" prop="name" align="center" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="邮箱" prop="email" align="center" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.email }} </span>
          </template>
        </el-table-column>

<!--        <el-table-column show-overflow-tooltip label="创建时间" prop="create_time" align="center" min-width="20%">-->
<!--          <template #default="scope">-->
<!--            <span>{{ paramsISOTime(scope.row.create_time) }}</span>-->
<!--          </template>-->
<!--        </el-table-column>-->

        <el-table-column show-overflow-tooltip align="center" label="操作" width="100">
          <template #default="scope">
            <div class="action-buttons">
              <el-button type="warning" size="small" @click.native="showEditDrawer(scope.row)">
                <el-icon><Edit /></el-icon>
                修改
              </el-button>
            </div>
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

    <EditDrawer></EditDrawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './edit-drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {GetUserList} from "@/api/system/user";
import {paramsISOTime} from "@/utils/parse-data";
import {Edit} from "@icon-park/vue-next";

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  name: undefined,
  account: undefined
})

const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.69}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.76}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const showEditDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'edit-user-email', content: row})
}

const getTableDataList = () => {
  queryItems.value.name = queryItems.value.name ? queryItems.value.name : undefined
  queryItems.value.account = queryItems.value.account ? queryItems.value.account : undefined
  tableIsLoading.value = true
  GetUserList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = []
    response.data.data.forEach((item: any) => {
      tableDataList.value.push(item)
    })
    tableDataTotal.value = response.data.total
  })
}

onMounted(() => {
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
  if (message.eventType === 'user') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">
.action-buttons {
  display: flex;
  flex-wrap: nowrap;
  gap: 4px;
  align-items: center;
}

.action-buttons .el-button {
  margin-left: 0 !important;
  margin-right: 0 !important;
}
</style>
