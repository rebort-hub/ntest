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

        <el-table-column show-overflow-tooltip label="触发人" prop="create_user" align="center" min-width="15%">
          <template #default="scope">
            <span> {{ userDict[scope.row.create_user] }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="错误类型" prop="name" align="center" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip align="center" label="操作" width="80">
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


    <el-dialog 
      v-model="drawerIsShow" 
      title="错误详情" 
      width="900px"
      :close-on-click-modal="false"
      destroy-on-close
      top="5vh"
      class="error-detail-dialog"
    >
      <div class="error-detail-content">
        <pre class="error-detail-pre">{{ currentRow.detail }}</pre>
      </div>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import Pagination from '@/components/pagination.vue'

import {GetUserList} from "@/api/system/user";
import {GetErrorRecord, GetErrorRecordList} from "@/api/assist/error-record";
import {bus, busEvent} from "@/utils/bus-events";
import {paramsISOTime} from "@/utils/parse-data";

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const userDict = ref({})
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
  GetErrorRecord({id: row.id}).then(response => {
    currentRow.value = response.data
    drawerIsShow.value = true
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetErrorRecordList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

onMounted(() => {
  GetUserList({}).then((response: object) => {
    response.data.data.forEach((user: any) => {
      userDict.value[user.id] = user.name
    })
  })

  getTableDataList()
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
})

</script>

<style scoped lang="scss">
:deep(.error-detail-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 90vh;
    margin-top: 5vh !important;
    display: flex;
    flex-direction: column;
  }
  
  .el-dialog__header {
    border-bottom: 1px solid #ebeef5;
    padding: 20px 20px 15px;
    flex-shrink: 0;
  }
  
  .el-dialog__body {
    padding: 20px;
    flex: 1;
    overflow-y: auto;
    max-height: calc(90vh - 100px);
    
    &::-webkit-scrollbar {
      width: 8px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 4px;
      
      &:hover {
        background: #a8a8a8;
      }
    }
  }
}

.error-detail-content {
  .error-detail-pre {
    background: #f5f7fa;
    padding: 16px;
    border-radius: 4px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #303133;
    overflow: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
}
</style>
