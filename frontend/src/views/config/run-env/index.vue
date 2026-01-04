<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showEditDrawer(undefined, 'add')"> 添加环境</el-button>
        <el-button type="primary" @click="showToBusinessDrawer(undefined)">运行环境与业务线绑定管理</el-button>
      </div>

      <div class="layout-container-form-search">
        <el-select
            v-model="queryItems.group"
            placeholder="选择环境分组"
            clearable
            filterable
            default-first-option
            style="margin-right: 10px"
            size="small"
        >
          <el-option v-for="item in runEnvGroupList" :key="item" :label="item" :value="item"/>
        </el-select>

        <el-input
            v-model="queryItems.name"
            clearable
            size="small"
            style="width: 200px; margin-right: 10px"
            placeholder="环境名字，支持模糊搜索"/>

        <el-input
            v-model="queryItems.code"
            class="input-with-select"
            placeholder="环境code，支持模糊搜索"
            size="small"
            clearable
            style="width: 200px; margin-right: 10px"
        />

        <el-button type="primary" @click="getTableDataList()"> 搜索</el-button>
      </div>
    </div>

    <div style="margin: 10px">

      <el-table
          :data="tableDataList"
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          style="width: 100%"
          stripe
          :height="tableHeight"
          @row-dblclick="rowDblclick"
          row-key="id">

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

          <el-table-column show-overflow-tooltip prop="group" align="center" label="环境分组" min-width="10%">
            <template #default="scope">
              <span> {{ scope.row.group }} </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip prop="name" align="center"  label="环境名字" min-width="25%">
            <template #default="scope">
              <span> {{ scope.row.name }} </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip prop="code" align="center" label="环境code" min-width="20%">
            <template #default="scope">
              <span> {{ scope.row.code }} </span>
            </template>
          </el-table-column>

          <el-table-column show-overflow-tooltip prop="desc" align="center" label="备注" min-width="25%">
            <template #default="scope">
              <span> {{ scope.row.desc }} </span>
            </template>
          </el-table-column>

          <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" width="80">
            <template #default="scope">
              <el-button type="text" size="small" style="margin: 0; padding: 2px" @click.native="showEditDrawer(scope.row, 'edit')">修改</el-button>
              <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showEditDrawer(scope.row, 'copy')">复制</el-button>
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

    <EditDrawer :runEnvGroupList="runEnvGroupList"></EditDrawer>
    <AddDrawer :runEnvGroupList="runEnvGroupList"></AddDrawer>
    <ToBusinessDrawer></ToBusinessDrawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import {ElMessage} from "element-plus";

import Pagination from '@/components/pagination.vue'
import EditDrawer from './eidt-drawer.vue'
import AddDrawer from './add-drawer.vue'
import ToBusinessDrawer from './to-business.vue'

import {RunEnvGroupList, GetRunEnvList, RunEnvSort} from "@/api/config/run-env";
import {bus, busEvent} from "@/utils/bus-events";
import toClipboard from "@/utils/copy-to-memory";
import {Help, SortThree} from "@icon-park/vue-next";

const tableIsLoading = ref(false)
const runEnvGroupList = ref([])
const tableDataList = ref([])
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  group: undefined,
  name: undefined,
  code: undefined
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

const showEditDrawer = (row: object | undefined, command: string) => {
  let eventType = 'edit-run-env'
  let content = undefined
  if (command == 'edit'){
    content = JSON.parse(JSON.stringify(row))
  }else if (command == 'copy'){
    content = JSON.parse(JSON.stringify(row))
    content.id = undefined
  }else {
    eventType = 'add-run-env'
  }
  bus.emit(busEvent.drawerIsShow, {eventType: eventType, content: content});
}

const showToBusinessDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'run-env-to-business'});
}

const getTableDataList = () => {
  getRunEnvGroupList()
  queryItems.value.group = queryItems.value.group ? queryItems.value.group : undefined
  queryItems.value.name = queryItems.value.name ? queryItems.value.name : undefined
  queryItems.value.code = queryItems.value.code ? queryItems.value.code : undefined
  tableIsLoading.value = true
  GetRunEnvList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

// 获取环境分组
const getRunEnvGroupList = () => {
  RunEnvGroupList({}).then((response: object) => {
    runEnvGroupList.value = response.data
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
  RunEnvSort({
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
  if (message.eventType === 'run-env') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
