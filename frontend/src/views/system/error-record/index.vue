<template>
  <div class="layout-container">

    <div style="margin: 10px">
      <el-table
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="tableDataList"
          style="width: 100%"
          stripe
          :height="tableHeight">
        <el-table-column prop="id" label="序号" align="center" min-width="10%" >
          <template #default="scope">
            <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="数据id" prop="id" align="center" min-width="5%">
          <template #default="scope">
            <span> {{ scope.row.id }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="创建时间" prop="create_time" align="center" min-width="15%">
          <template #default="scope">
            <span> {{ paramsISOTime(scope.row.create_time) }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="触发人" prop="create_user" align="center" min-width="10%">
          <template #default="scope">
            <span>{{ userDict[scope.row.create_user] }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="请求方法" prop="method" align="center" min-width="10%">
          <template #default="scope">
            <span>{{ scope.row.method }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="接口地址" prop="url" align="center" min-width="20%">
          <template #default="scope">
            <span>{{ scope.row.url }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip align="center" label="操作" width="80">
          <template #default="scope">
            <el-button type="text" size="small" @click.native="showEditDrawer(scope.row)">查看详情</el-button>
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

    <showDetailDrawer></showDetailDrawer>
  </div>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import showDetailDrawer from './show-detail.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {GetErrorRecordList} from "@/api/system/error-record";
import Pagination from "@/components/pagination.vue";
import {GetUserList} from "@/api/system/user";
import {paramsISOTime} from "@/utils/parse-data";

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.77}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.86}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const tableDataTotal = ref(0)
const queryItems = ref({page_no: 1, page_size:20})
const userDict = ref({})

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const showEditDrawer = (row: object) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'error-record', content: row});
}

const getUserList = () => {
  GetUserList({page_no: 1, page_size: 1000}).then(response => {
    response.data.data.forEach(user => {
      userDict.value[user.id] = user.name
    })
  })
}

const getTableDataList = () => {
  GetErrorRecordList(queryItems.value).then(response => {
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

onMounted(() => {
  getUserList()
  getTableDataList()
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
})

</script>

<style scoped lang="scss">

</style>
