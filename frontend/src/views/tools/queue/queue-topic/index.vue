<template>
  <div>
    <el-drawer
        title="topic管理"
        size="85%"
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

        <el-table-column show-overflow-tooltip label="topic名" prop="topic" align="center" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.topic }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="备注" prop="desc" align="center" min-width="15%">
          <template #default="scope">
            <span>{{ scope.row.desc }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="创建者" prop="create_user" align="center" min-width="5%">
          <template #default="scope">
            <span>{{ userDict[scope.row.create_user] }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip align="center" label="操作" width="180">
          <template #default="scope">
            <el-button
                style="margin: 0; padding: 2px"
                type="text"
                size="small"
                @click="showEditQueueDrawer('update', scope.row)"
            >修改
            </el-button>

            <el-button
                type="text"
                size="small"
                style="margin: 0; padding: 2px"
                @click="showEditQueueDrawer('copy', scope.row)"
            >复制
            </el-button>

            <el-button
                style="margin: 0; padding: 2px;color: #FF6600"
                type="text"
                size="small"
                @click="showEditQueueDrawer('sendMsg', scope.row)"
            >发消息
            </el-button>

            <el-button
                type="text"
                size="small"
                style="margin: 0; padding: 2px"
                @click="showMsgLogDrawer(scope.row)"
            >发送记录
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

      <template #footer>
        <div slot="footer" class="demo-drawer__footer">
          <el-button
              size="small"
              type="primary"
              style="float: left"
              @click="showEditQueueDrawer"
          >添加topic</el-button>
        </div>
      </template>
    </el-drawer>
  </div>

  <topicEditDrawer :queue-instance-id="queryItems.instance_id"></topicEditDrawer>
  <msgLogDrawer :user-dict="props.userDict"></msgLogDrawer>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import topicEditDrawer from './edit-drawer.vue'
import msgLogDrawer from './msg-log-drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ChangQueueTopicSort, GetQueueTopicList} from "@/api/tools/queue";
import toClipboard from "@/utils/copy-to-memory";
import {ElMessage} from "element-plus";
import Pagination from "@/components/pagination.vue";
import {Help, SortThree} from "@icon-park/vue-next";

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
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])

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
const queryItems = ref({page_no: 1, page_size:20, instance_id: undefined})

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const showEditQueueDrawer = (command: string, row: object | null) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'queue-topic', command: command, content: {topic_id: row ? row.id : row}})
}

const showMsgLogDrawer = (row: any) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'queue-topic-msg-log', content: row.id})
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
  GetQueueTopicList(queryItems.value).then(response => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
  })
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
  ChangQueueTopicSort({
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
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
  bus.on(busEvent.drawerIsCommit, onShowDrawerCommitEvent);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
  bus.off(busEvent.drawerIsCommit, onShowDrawerCommitEvent);
  window.removeEventListener('resize', handleResize);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'queue-topic-list') {
    queryItems.value.instance_id = message.content.id
    getTableDataList()
    queueDrawerIsShow.value = true
  }
}

const onShowDrawerCommitEvent = (message: any) => {
  if (message.eventType === 'queue-topic-commit') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
