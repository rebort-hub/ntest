<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button
            type="primary"
            size="small"
            style="margin-left: 10px"
            @click.native="showEditDrawer('add', null)"
        >新增实例
        </el-button>
      </div>

      <div class="layout-container-form-search">
        <el-select
            style="margin-right: 10px; width: 100%"
            v-model="queryItems.queue_type"
            placeholder="实例类型"
            filterable
            default-first-option
            clearable
            size="small"
            class="filter-item"
        >
          <el-option v-for="(value, key) in queueTypeDict" :key="key" :label="value" :value="key" />
        </el-select>

        <el-input
            style="margin-right: 10px"
            v-model="queryItems.host"
            placeholder="实例地址，支持模糊搜索"
            size="small"
            clearable
        />

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

        <el-table-column show-overflow-tooltip label="实例类型" prop="queue_type" align="center" min-width="6%">
          <template #default="scope">
            <span> {{ queueTypeDict[scope.row.queue_type] }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="实例地址" prop="host" align="center" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.host }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="实例id" prop="instance_id" align="center" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.instance_id }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="端口" prop="port" align="center" min-width="5%">
          <template #default="scope">
            <span>{{ scope.row.port }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="备注" prop="desc" align="center" min-width="5%">
          <template #default="scope">
            <span>{{ scope.row.desc }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="创建人" prop="create_user" align="center" min-width="5%">
          <template #default="scope">
            <span>{{ userDict[scope.row.create_user] }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip align="center" label="操作" width="140">
          <template #default="scope">
            <el-button
                type="text"
                size="small" style="margin: 0; padding: 2px"
                @click="showEditDrawer('edit', scope.row)"
            >修改
            </el-button>

            <el-button
                type="text"
                size="small" style="margin: 0; padding: 2px"
                @click="showEditDrawer('copy', scope.row)"
            >复制
            </el-button>

            <el-button
                type="text"
                size="small" style="margin: 0; padding: 2px"
                @click="showQueueList(scope.row)"
            >topic列表
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
    </div>
    <queueInstanceEditDrawer :queue-type-dict="queueTypeDict"></queueInstanceEditDrawer>
    <queueTopicListDrawer :user-dict="userDict"></queueTopicListDrawer>
  </div>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import queueInstanceEditDrawer from './edit-drawer.vue'
import queueTopicListDrawer from '../queue-topic/index.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ChangQueueInstanceSort, GetQueueInstanceList} from "@/api/tools/queue";
import Pagination from "@/components/pagination.vue";
import {GetUserList} from "@/api/system/user";
import toClipboard from "@/utils/copy-to-memory";
import {ElMessage} from "element-plus";
import {Help, SortThree} from "@icon-park/vue-next";

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
const queryItems = ref({page_no: 1, page_size:20, host: undefined, queue_type: undefined})
const userDict = ref({})
const queueTypeDict =  { 'active_mq': 'active_mq', 'rocket_mq': 'rocket_mq', 'rabbit_mq': 'rabbit_mq'}

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const showEditDrawer = (command: string, row: object | null) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'queue-instance-info', command: command, content: row});
}

const showQueueList = (row: any) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'queue-topic-list', content: row})
}

const rowDblclick = async (row: any, column: any, event: any) => {
  try {
    await toClipboard(row[column.property]);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}

const getUserList = () => {
  GetUserList({page_no: 1, page_size: 1000}).then(response => {
    response.data.data.forEach(user => {
      userDict.value[user.id] = user.name
    })
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
  ChangQueueInstanceSort({
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

const getTableDataList = () => {
  queryItems.value.host = queryItems.value.host ? queryItems.value.host : undefined
  queryItems.value.queue_type = queryItems.value.queue_type ? queryItems.value.queue_type : undefined
  tableIsLoading.value = true
  GetQueueInstanceList(queryItems.value).then(response => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

onMounted(() => {
  getUserList()
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
  if (message.eventType === 'queue-instance-info') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
