<template>
  <div>
    <el-drawer title="执行记录" size="70%" v-model="drawerIsShow">
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

          <el-table-column show-overflow-tooltip label="执行时间" prop="create_time" align="center" min-width="15%">
            <template #default="scope">
              <span> {{ paramsISOTime(scope.row.create_time) }} </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip label="任务方法名" prop="func_name" align="center" min-width="20%">
            <template #default="scope">
              <span> {{ scope.row.func_name }} </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip label="业务线" prop="business_id" align="center" min-width="10%">
            <template #default="scope">
              <span> {{ businessDict[scope.row.business_id] }} </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip label="状态" prop="status" align="center" min-width="10%">
            <template #default="scope">
              <el-tag :type="statusTagMapping[scope.row.status]" size="small">
                {{ statusContentMapping[scope.row.status] }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip align="center" label="操作" min-width="15%">
            <template #default="scope">
              <el-button type="text" size="small" @click.native="showDetail(scope.row)">详情</el-button>
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
    </el-drawer>

    <el-drawer title="执行记录" size="60%" v-model="detailDrawerIsShow">
      <div style="margin: 10px">
        <showJson :json-data="detailData"/>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";

import Pagination from '@/components/pagination.vue'
import {bus, busEvent} from "@/utils/bus-events";
import showJson from '@/components/show-json.vue'

import {GetJobRunLog, GetJobRunLogList} from "@/api/system/job";
import {GetBusinessList} from "@/api/config/business";
import {paramsISOTime} from "@/utils/parse-data";

const businessDict = ref({})
const statusTagMapping = ref({0: 'info', 1: 'danger', 2: 'success'})
const statusContentMapping = ref({0: '执行中', 1: '执行失败', 2: '执行成功'})
const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const drawerIsShow = ref(false)
const detailDrawerIsShow = ref(false)
const detailData = ref({})
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  func_name: '',
  detail: true
})
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.75}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.83}px`
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

const showDetail = (row: object) => {
  GetJobRunLog({id: row.id}).then(response => {
    detailData.value = response.data.detail
    detailDrawerIsShow.value = true
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetJobRunLogList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

onMounted(() => {
  getBusinessList()
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
  window.removeEventListener('resize', handleResize);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'job') {
    queryItems.value.func_name = message.content
    getTableDataList()
    drawerIsShow.value = true
  }
}

const getBusinessList = () => {
  GetBusinessList({page_no: 1, page_size: 1000}).then(response => {
    response.data.data.forEach((item: { id: string | number; name: any; }) => {
      businessDict.value[item.id] = item.name
    })
  })
}

</script>

<style scoped lang="scss">

</style>
