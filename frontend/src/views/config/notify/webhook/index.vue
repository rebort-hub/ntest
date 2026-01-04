<template>
  <div >
    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showEditDrawer(undefined, 'add')"> 添加webhook</el-button>
      </div>

      <div class="layout-container-form-search">
        <el-input
            v-model="queryItems.name"
            clearable
            size="small"
            style="width: 200px; margin-right: 10px"
            placeholder="webhook名字，支持模糊搜索"/>

        <el-input
            v-model="queryItems.addr"
            clearable
            size="small"
            style="width: 400px; margin-right: 10px"
            placeholder="webhook地址，支持模糊搜索"/>

        <el-select
            v-model="queryItems.webhook_type"
            size="small"
            clearable
            placeholder="webhook类型"
            style="margin-right: 10px">
          <el-option v-for="(value, key) in webHookType" :key="key" :label="value" :value="key"/>
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

        <el-table-column show-overflow-tooltip prop="name" align="center" label="名字" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="name" align="center" label="类型" min-width="10%">
          <template #default="scope">
            <span> {{ webHookType[scope.row.webhook_type] }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="name" align="center" label="地址" min-width="40%">
          <template #default="scope">
            <span> {{ scope.row.addr }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="desc" align="center" label="备注" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.desc }} </span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" width="120">
          <template #default="scope">
            <el-button type="text" size="small" style="margin: 0; padding: 2px" @click.native="showEditDrawer(scope.row, 'edit')">修改</el-button>
            <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showEditDrawer(scope.row, 'copy')">复制</el-button>
            <el-popconfirm width="250px" title="此操作将发送一条测试信息到此webhook，用于验证此webhook配置是否正确，确定触发测试?" @confirm="debugWebHook(scope.row.id)">
              <template #reference>
                <el-button style="margin: 0; padding: 2px" type="text" size="small">测试</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <pagination
          v-show="tableDataListTotal > 0"
          :pageNum="queryItems.page_no"
          :pageSize="queryItems.page_size"
          :total="tableDataListTotal"
          @pageFunc="changePagination"
      />
    </div>

    <EditDrawer></EditDrawer>
    <AddDrawer></AddDrawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, computed, onBeforeUnmount} from "vue";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './edit-drawer.vue'
import AddDrawer from './add-drawer.vue'

import {GetWebHookList, DebugWebHook, ChangeWebHookSort} from "@/api/config/webhook";
import {bus, busEvent} from "@/utils/bus-events";
import {Help, SortThree} from "@icon-park/vue-next";

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataListTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  addr: undefined,
  name: undefined,
  webhook_type: undefined
})
const webHookType = {
  'ding_ding': '钉钉',
  'we_chat': '企业微信',
  'fei_shu': '飞书'
}

const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.68}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.76}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const showEditDrawer = (row: object | undefined, command: string) => {
  let eventType = 'edit-webhook'
  let content = undefined
  if (command == 'add'){
    eventType = 'add-webhook'
  }else {
    content = JSON.parse(JSON.stringify(row))
  }
  bus.emit(busEvent.drawerIsShow, {eventType: eventType, content: content, command: command});
}

const debugWebHook = (webhookId: number) => {
  tableIsLoading.value = true
  DebugWebHook({id: webhookId}).then(response => {
    tableIsLoading.value = false
  })
}

// 获取列表
const getTableDataList = () => {
  queryItems.value.name = queryItems.value.name ? queryItems.value.name : undefined
  queryItems.value.addr = queryItems.value.addr ? queryItems.value.addr : undefined
  queryItems.value.webhook_type = queryItems.value.webhook_type ? queryItems.value.webhook_type : undefined
  tableIsLoading.value = true
  GetWebHookList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataListTotal.value = response.data.total
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
  ChangeWebHookSort({
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
  if (message.eventType === 'webhook') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
