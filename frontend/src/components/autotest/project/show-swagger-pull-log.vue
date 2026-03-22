<template>
  <div>
    <el-dialog 
        title="拉取swagger记录" 
        v-model="drawerIsShow" 
        width="70%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="5vh"
        class="swagger-log-dialog">
      <div
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
      />

      <div class="dialog-content">
        <el-table
            :data="tableDataList"
            style="width: 100%"
            stripe
            :height="tableHeight"
            @row-dblclick="rowDblclick"
            row-key="id">

          <el-table-column prop="id" label="序号" align="center" min-width="8%">
            <template #default="scope">
              <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip prop="status" label="状态" align="center" min-width="50%">
            <template #default="scope">
              <el-tag :type="swaggerPullStatusMappingTagType[scope.row.status]">
                {{ swaggerPullStatusMappingContent[scope.row.status] }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip prop="create_time" align="center" label="操作时间" min-width="25%">
            <template #default="scope">
              <span> {{ paramsISOTime(scope.row.create_time) }} </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip prop="create_user" align="center" label="操作人员" min-width="25%">
            <template #default="scope">
              <span> {{ userDict[scope.row.create_user] }} </span>
            </template>
          </el-table-column>

          <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" min-width="20%">
            <template #default="scope">
              <el-button style="margin: 0; padding: 5px" type="text" size="small" @click="showDetail(scope.row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-wrapper">
          <pagination
              v-show="tableDataTotal > 0"
              :pageNum="queryItems.page_no"
              :pageSize="queryItems.page_size"
              :total="tableDataTotal"
              @pageFunc="changePagination"
          />
        </div>
      </div>

      <!-- 详情弹窗 -->
      <el-dialog
          title="拉取swagger详情"
          v-model="pullLogDetailIsShow"
          width="60%"
          :close-on-click-modal="false"
          :close-on-press-escape="false"
          destroy-on-close
          append-to-body
          class="swagger-detail-dialog">
        <div class="detail-content">
          <div class="detail-item">
            <label class="label-style">触发人：</label>
            <span>{{ userDict[pullLogDetailData.create_user] }}</span>
          </div>

          <div class="detail-item">
            <label class="label-style">请求参数：</label>
            <show-json :json-data="pullLogDetailData.pull_args"/>
          </div>

          <div class="detail-item">
            <label class="label-style">备注信息：</label>
            <el-input
                :value="pullLogDetailData.desc || ''"
                disabled
                style="width: 100%"
                size="small"
                type="textarea"
                :rows="2"
            />
          </div>
        </div>
      </el-dialog>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import showJson from "@/components/show-json.vue";
import { GetSwaggerPullLogList, GetSwaggerPullLog } from '@/api/assist/swagger'
import {swaggerPullStatusMappingContent, swaggerPullStatusMappingTagType} from "@/components/autotest/mapping";
import Pagination from "@/components/pagination.vue";
import toClipboard from "@/utils/copy-to-memory";
import {ElMessage} from "element-plus";
import {getFindElementOption} from "@/utils/get-config";
import {paramsISOTime} from "@/utils/parse-data";

const props = defineProps({
  userDict: {
    default: {},
    type: Object
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'show-swagger-pull-log') {
    queryItems.value.project_id = message.content.id
    getTableDataList()
    drawerIsShow.value = true
  }
}

const pullLogDetailData = ref({})
const pullLogDetailIsShow = ref(false)
const drawerIsShow = ref(false)
const tableIsLoading = ref(false)
const tableHeight = ref('10px')

const setTableHeight = () => {
  // 弹窗模式下的高度计算
  const maxDialogHeight = window.innerHeight * 0.9; // 90vh
  const headerHeight = 60; // 弹窗头部高度
  const paginationHeight = 60; // 分页组件高度
  const padding = 40; // 内边距
  const availableHeight = maxDialogHeight - headerHeight - paginationHeight - padding;
  
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${availableHeight * 0.7}px`
  }else {  // 大屏
    tableHeight.value = `${availableHeight * 0.8}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  project_id: undefined
})
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

const getTableDataList = () => {
  tableIsLoading.value = true
  GetSwaggerPullLogList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

const showDetail = (row: { id: any; }) => {
  GetSwaggerPullLog({id: row.id}).then(response => {
    pullLogDetailData.value = response.data
    pullLogDetailIsShow.value = true
  })
}

onMounted(() => {
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
})

</script>


<style scoped lang="scss">
// Swagger记录弹窗样式
:deep(.swagger-log-dialog) {
  .el-dialog {
    max-height: 90vh;
    margin-top: 5vh !important;
    margin-bottom: 5vh;
    display: flex;
    flex-direction: column;
  }
  
  .el-dialog__header {
    flex-shrink: 0;
    border-bottom: 1px solid #ebeef5;
  }
  
  .el-dialog__body {
    flex: 1;
    overflow: hidden;
    padding: 15px 20px;
  }
}

.dialog-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .el-table {
    flex: 1;
    margin-bottom: 15px;
  }
  
  .pagination-wrapper {
    flex-shrink: 0;
    display: flex;
    justify-content: center;
    padding-top: 10px;
    border-top: 1px solid #ebeef5;
  }
}

// Swagger详情弹窗样式
:deep(.swagger-detail-dialog) {
  .el-dialog {
    max-height: 80vh;
  }
  
  .el-dialog__body {
    max-height: 60vh;
    overflow-y: auto;
  }
}

.detail-content {
  .detail-item {
    margin-bottom: 20px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .label-style {
      font-weight: 600;
      color: #606266;
      margin-right: 10px;
      display: inline-block;
      min-width: 80px;
    }
  }
}

// 响应式适配
@media (max-width: 1200px) {
  :deep(.swagger-log-dialog) {
    .el-dialog {
      width: 85% !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.swagger-log-dialog) {
    .el-dialog {
      width: 95% !important;
      margin-top: 2vh !important;
    }
  }
  
  :deep(.swagger-detail-dialog) {
    .el-dialog {
      width: 90% !important;
    }
  }
}
</style>
