<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showUploadFileDialog"> 上传文件</el-button>
      </div>

      <div v-show="!isSelectStepFile" class="layout-container-form-search">
        <el-select
            style="margin-right: 10px"
            v-model="queryItems.file_type"
            placeholder="请选择文件类型"
            size="small"
            filterable
            @change="changeFileType"
        >
          <el-option v-for="item in fileTypeList" :key="item.key" :label="item.value" :value="item.key"/>
        </el-select>

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
        <el-table-column prop="id" label="序号" align="center" min-width="5%">
          <template #default="scope">
            <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="文件名" prop="name" align="center" min-width="40%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="文件大小" prop="size" align="center" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.size }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="最近一次使用时间" prop="lastVisitTime" align="center" min-width="15%">
          <template #default="scope">
            <span>{{ scope.row.lastVisitTime }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="最后一次更新时间" prop="LastModifiedTime" align="center" min-width="15%">
          <template #default="scope">
            <span>{{ scope.row.LastModifiedTime }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip align="center" label="操作" width="100">
          <template #default="scope">
            <el-button
                v-show="isSelectStepFile"
                type="text"
                size="small"
                style="margin: 0; padding: 2px"
                :loading="scope.row.downloadLoading"
                @click.native="selectFile(scope.row.name)">选择</el-button>

            <el-button
                v-show="!isSelectStepFile"
                type="text"
                size="small"
                style="margin: 0; padding: 2px"
                :loading="scope.row.downloadLoading"
                @click.native="downloadFile(scope.row)">下载</el-button>

            <el-popconfirm :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row)">
              <template #reference>
                <el-button
                    v-show="!isSelectStepFile"
                    style="margin: 0; padding: 2px;color: red"
                    :loading="scope.row.deleteLoading"
                    type="text"
                    size="small">删除</el-button>
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

    <uploadFileDialog></uploadFileDialog>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import Pagination from '@/components/pagination.vue'

import uploadFileDialog from '@/components/file/upload.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {DeleteFile, DownloadFile, GetFileList} from "@/api/assist/file";

const props = defineProps({
  isSelectStepFile:{
    default: false,
    type: Boolean
  }
})

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  file_type: 'case'
})

const fileTypeList = ref([
  { 'key': 'case', 'value': '用例文件' },
  { 'key': 'callBack', 'value': '回调文件' },
  { 'key': 'temp', 'value': '临时文件' },
  { 'key': 'driver', 'value': '浏览器驱动文件' }
])

const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.73}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.82}px`
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

const showUploadFileDialog = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'uploadFile', content: queryItems.value.file_type});
}

const deleteData = (row) => {
  row.deleteLoading = true
  DeleteFile({file_name: row.name, file_type: queryItems.value.file_type}).then(response => {
    row.deleteLoading = false
    if (response){
      getTableDataList()
    }
  })
}

const downloadFile = (row) => {
  row.downloadLoading = true
  DownloadFile({ file_name: row.name, file_type: queryItems.value.file_type }).then(response => {
    row.downloadLoading = false
    const blob = new Blob([response], {
      type: 'application/vnd.ms-excel' // 将会被放入到blob中的数组内容的MIME类型
    })
    // 保存文件到本地
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob) // 生成一个url
    a.download = row.name
    a.click()
  })
}

const selectFile = (fileName: string) => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'select-step-file', content: fileName});
}

const changeFileType = () => {
  queryItems.value.page_no = 1
  queryItems.value.page_size = 20
  getTableDataList()
}
const getTableDataList = () => {
  queryItems.value.file_type = queryItems.value.file_type ? queryItems.value.file_type : 'case'
  tableIsLoading.value = true
  GetFileList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
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
  if (message.eventType === 'uploadFile') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
