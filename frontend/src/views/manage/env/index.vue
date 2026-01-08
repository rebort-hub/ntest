<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showEditDrawer(undefined)"> 添加环境</el-button>
      </div>

      <div class="layout-container-form-search">
        <el-select
            v-model="queryItems.business_list"
            placeholder="选择业务线"
            clearable
            filterable
            multiple
            default-first-option
            style="margin-right: 10px"
            size="small"
        >
          <el-option v-for="item in businessList" :key="item.id" :label="item.name" :value="item.id"/>
        </el-select>

        <el-input
            v-model="queryItems.name"
            clearable
            size="small"
            style="width: 200px; margin-right: 10px"
            placeholder="环境名关键字，支持模糊搜索"/>

        <el-input
            v-model="queryItems.addr"
            placeholder="域名地址关键字，支持模糊搜索"
            size="small"
            clearable
            style="width: 200px; margin-right: 10px"
        />

        <el-button type="primary" @click="getTableDataList"> 搜索</el-button>
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
          @row-dblclick="rowDblclick">

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

        <el-table-column show-overflow-tooltip prop="business" align="center" label="业务线" min-width="15%">
          <template #default="scope">
            <span> {{ businessDict[scope.row.business] }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="name" align="center" label="环境名" min-width="15%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="value" align="center" label="环境域名" min-width="30%">
          <template #default="scope">
            <a :href="scope.row.value" target="_blank" style="color: #3a8ee6">
              {{ scope.row.value }}
            </a>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="desc" align="center" label="备注" min-width="15%">
          <template #default="scope">
            <span> {{ scope.row.desc }} </span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" width="140">
          <template #default="scope">
            <el-button style="margin: 0; padding: 2px" type="text" size="small" @click.native="showEditDrawer(scope.row, undefined)">修改</el-button>
            <el-button style="margin: 0; padding: 2px" type="text" size="small" @click.native="showEditDrawer(scope.row, true)">账号列表</el-button>
            <el-popconfirm :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row.id)">
              <template #reference>
                <el-button style="margin: 0; padding: 2px;color: red" type="text" size="small">删除</el-button>
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

    <editEnvDrawer :business-list="businessList"></editEnvDrawer>
    <accountListDrawer></accountListDrawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import Pagination from '@/components/pagination.vue'
import editEnvDrawer from './edit-env-drawer.vue'
import accountListDrawer from './account-list-drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";

import {GetBusinessList} from "@/api/config/business";
import {GetEnvList, DeleteEnv, ChangeEnvSort} from "@/api/manage/env";
import {Help, SortThree} from "@icon-park/vue-next";

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: undefined,
  name: undefined,
  addr: undefined,
  business_list: undefined
})

const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])

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

const businessList = ref([])
const businessDict = ref({})

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

const showEditDrawer = (row: object | undefined, isAccountList: boolean | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: isAccountList ? 'account-list' : 'env', content: row});
}

const getBusinessList = () => {
  GetBusinessList({page_no: 1, page_size: 99999}).then(response => {
    businessList.value = response.data.data
    businessList.value.forEach(business => {
      businessDict.value[business.id] = business.name
    })
  })
}

const getTableDataList = () => {
  let queryData = {
    page_no: queryItems.value.page_no ? queryItems.value.page_no : undefined,
    page_size: queryItems.value.page_size ? queryItems.value.page_size : undefined,
    detail: true,
    name: queryItems.value.name ? queryItems.value.name : undefined,
    addr: queryItems.value.addr ? queryItems.value.addr : undefined,
    business_list: ''
  }
  if (queryItems.value.business_list){
    queryData.business_list = queryItems.value.business_list + ''
  }
  tableIsLoading.value = true
  GetEnvList(queryData).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

const deleteData = (dataId: object) => {
  DeleteEnv({id: dataId}).then(response => {
    if (response){
      getTableDataList()
    }
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
  ChangeEnvSort({
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
  getBusinessList()
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
  if (message.eventType === 'env') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">
.status-select-todo :deep(.el-input__wrapper){
  background-color: #F56C6C;
}

.status-select-doing :deep(.el-input__wrapper){
  background-color: #409EFF;
}

.status-select-done :deep(.el-input__wrapper){
  background-color: #58D68D;
}

.replays-select-0 :deep(.el-input__wrapper){
  background-color: #F56C6C;
}

.replays-select-1 :deep(.el-input__wrapper){
  background-color: #58D68D;
}

</style>
