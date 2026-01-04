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
        <el-table-column prop="id" label="序号" align="center" min-width="5%">
          <template #default="scope">
            <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="创建时间" prop="create_time" align="center" min-width="15%">
          <template #default="scope">
            <span> {{ paramsISOTime(scope.row.create_time) }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="回调地址" prop="url" align="center" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.url }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip align="center" label="操作" width="100">
          <template #default="scope">
            <el-button type="text" size="small" @click.native="showDetail(scope.row)">查看详情</el-button>
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


    <el-drawer title="回调详情" size="60%" v-model="drawerIsShow">
      <div style="margin-bottom: 30px">
        <label>回调参数:</label>
        <show-json :json-data="currentRow.data_json"/>
      </div>

      <div>
        <label>响应数据:</label>
        <show-json :json-data="currentRow.result"/>
      </div>
    </el-drawer>

  </div>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import Pagination from '@/components/pagination.vue'

import {GetCallBack, GetCallBackList} from "@/api/assist/call-back";
import showJson from "@/components/show-json.vue";
import {bus, busEvent} from "@/utils/bus-events";
import {paramsISOTime} from "@/utils/parse-data";

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true
})
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.79}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.86}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const drawerIsShow = ref(false)
const currentRow = ref()

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const showDetail = (row: { id: any; }) => {
  GetCallBack({id: row.id}).then(response => {
    currentRow.value = response.data
    drawerIsShow.value = true
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetCallBackList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

onMounted(() => {
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
