<template>
  <div>
    <el-drawer
        title="消息发送记录"
        size="80%"
        :append-to-body="true"
        v-model="queueDrawerIsShow"
    >
      <el-table
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="tableDataList"
          style="width: 100%"
          stripe
          :height="tableHeight"
          row-key="id"
          @cell-dblclick="rowDblclick">

        <el-table-column prop="id" label="序号" align="center" min-width="6%" >
          <template #default="scope">
            <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="消息tag" prop="tag" align="center" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.tag }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="自定义内容" prop="options" align="center" min-width="30%">
          <template #default="scope">
            <span> {{ scope.row.options }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="消息内容" prop="message" align="center" min-width="30%">
          <template #default="scope">
            <span> {{ scope.row.message }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="状态" prop="status" align="center" min-width="10%">
          <template #default="scope">
            <el-tag type="success" v-show="scope.row.status == 'success'">成功</el-tag>
            <el-tag type="danger" v-show="scope.row.status != 'success'">失败</el-tag>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="响应" prop="response" align="center" min-width="30%">
          <template #default="scope">
            <span> {{ scope.row.response }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="发送时间" prop="create_time" align="center" min-width="20%">
          <template #default="scope">
            <span>{{ paramsISOTime(scope.row.create_time) }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="发送人" prop="create_user" align="center" min-width="8%">
          <template #default="scope">
            <span>{{ userDict[scope.row.create_user] }}</span>
          </template>
        </el-table-column>

        <el-table-column align="center" label="操作" width="90">
          <template #default="scope">
            <el-button
                type="text"
                size="small"
                @click="showReSendMsgDrawer('sendMsg', scope.row)"
            >再次发送
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
  </div>

</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from "vue";

import {bus, busEvent} from "@/utils/bus-events";
import {GetQueueTopicLogList} from "@/api/tools/queue";
import toClipboard from "@/utils/copy-to-memory";
import {ElMessage} from "element-plus";
import Pagination from "@/components/pagination.vue";
import {paramsISOTime} from "@/utils/parse-data";

const props = defineProps({
  userDict: {
    default: {},
    type: Object
  }
})

const queueDrawerIsShow = ref(false)
const tableIsLoading = ref(false)
const tableDataList = ref([])
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

const tableDataTotal = ref(0)
const queryItems = ref({page_no: 1, page_size:20, topic_id: undefined})

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const showReSendMsgDrawer = (command: string, row: object) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'queue-topic', command: command, content: {
      topic_id: row.topic_id, tag: row.tag, message_type: row.message_type, message: row.message, options: row.options
    }})
}

const rowDblclick = async (row: any, column: any, event: any) => {
  try {
    await toClipboard(row[column.property]);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetQueueTopicLogList(queryItems.value).then(response => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
  })
}

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
  bus.on(busEvent.drawerIsCommit, reSendMsgIsCommit);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
  bus.off(busEvent.drawerIsCommit, reSendMsgIsCommit);
  window.removeEventListener('resize', handleResize);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'queue-topic-msg-log') {
    queryItems.value.topic_id = message.content
    getTableDataList()
    queueDrawerIsShow.value = true
  }
}

const reSendMsgIsCommit = (message: any) => {
  if (message.eventType === 'queue-topic-commit') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
