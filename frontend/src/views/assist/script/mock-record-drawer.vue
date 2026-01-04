<template>
  <div>
    <el-drawer v-model="drawerIsShow" title="调用记录列表" size="70%">
      <el-table
          v-loading="tableIsLoading"
          row-key="id"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="tableDataList"
          style="width: 100%"
          stripe
          :height="tableHeight"
          @cell-dblclick="cellDblclick">

        <el-table-column prop="id" label="序号" align="center" min-width="10%">
          <template #default="scope">
            <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="脚本文件名" prop="name" align="center" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="创建时间" prop="create_time" align="center" min-width="15%">
          <template #default="scope">
            <span>{{ paramsISOTime(scope.row.create_time) }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="请求" prop="request" align="center" min-width="30%">
          <template #default="scope">
            <span> {{ scope.row.request }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="响应" prop="response" align="center" min-width="30%">
          <template #default="scope">
            <span> {{ scope.row.response }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip align="center" label="操作" width="80">
          <template #default="scope">
            <el-button type="text" size="small" style="margin: 0; padding: 2px"
                       @click.native="showDetailDrawer(scope.row)">详情
            </el-button>
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
    </el-drawer>

    <el-drawer v-model="detailIsShow" :append-to-body="true" title="调用记录详情" size="60%">
      <div style="margin-right: 20px;margin-left: 20px">

        <div style="margin-bottom: 20px">
          <label class="label-style">创建时间：</label>
          <span>{{ paramsISOTime(currentDetail.create_time) }}</span>
        </div>

        <div style="margin-bottom: 20px">
          <label class="label-style">请求参数：</label>
          <show-json :json-data="currentDetail.request"/>
        </div>

        <div v-if="currentDetail.response" style="margin-bottom: 20px">
          <label class="label-style">响应参数：</label>
          <show-json :json-data="currentDetail.response"/>
        </div>

        <div v-if="currentDetail.error" style="margin-bottom: 20px">
          <label class="label-style">脚本错误：</label>
          <div>{{currentDetail.error}}</div>
        </div>

      </div>
    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {GetScriptMockRecord, GetScriptMockRecordList} from "@/api/assist/script";
import Pagination from "@/components/pagination.vue";
import toClipboard from "@/utils/copy-to-memory";
import {ElMessage} from "element-plus";
import showJson from "@/components/show-json.vue";
import {paramsISOTime} from "@/utils/parse-data";

const drawerIsShow = ref(false)
const detailIsShow = ref(false)
const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  name: undefined
})
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

const currentDetail = ref({
  create_time: undefined,
  request: undefined,
  response: undefined,
  error: undefined
})


const cellDblclick = async (row: any, column: any, event: any) => {
  try {
    await toClipboard(row[column.property]);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}

const getTableDataList = () => {
  GetScriptMockRecordList(queryItems.value).then(response => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
  window.removeEventListener('resize', handleResize);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'script-mock-record') {
    queryItems.value.name = message.content
    getTableDataList()
    drawerIsShow.value = true
  }
}

const showDetailDrawer = (row: {response: string, request: object, create_time: object}) => {
  currentDetail.value = JSON.parse(JSON.stringify(row))
  currentDetail.value.response = undefined
  currentDetail.value.error = undefined
  try {
    currentDetail.value.response = JSON.parse(row.response)
  }catch(error) {
    currentDetail.value.error = row.response
  }
  detailIsShow.value = true
}

</script>


<style scoped lang="scss">
.el-collapse-item-title {
  font-weight: 600;
  font-size: 15px;
  margin-left: 10px;
  color: #409eff
}
</style>
