<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showEditDrawer(undefined)"> 添加业务线</el-button>
        <el-button type="primary" @click="showBusinessToUserDrawer(undefined)"> 业务线与用户的绑定管理</el-button>
      </div>

      <div class="layout-container-form-search">
        <el-input
            v-model="queryItems.name"
            clearable
            size="small"
            style="width: 200px; margin-right: 10px"
            placeholder="业务线，支持模糊搜索"/>

        <el-input
            v-model="queryItems.code"
            clearable
            size="small"
            style="width: 200px; margin-right: 10px"
            placeholder="业务线code，支持模糊搜索"/>

        <el-select
            v-model="queryItems.create_user"
            size="small"
            clearable
            placeholder="创建人"
            style="margin-right: 10px">
          <el-option v-for="user in userList" :key="user.id" :label="user.name" :value="user.id"/>
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

        <el-table-column show-overflow-tooltip prop="name" align="center" label="业务线" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="code" align="center" label="code" min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.code }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="desc" align="center" label="备注" min-width="30%">
          <template #default="scope">
            <span> {{ scope.row.desc }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="create_user" align="center" label="创建者" min-width="10%">
          <template #default="scope">
            <span>{{ parseUser(scope.row.create_user) }}</span>
          </template>
        </el-table-column>
        <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" width="80">
          <template #default="scope">
            <el-button type="text" size="small" @click.native="showEditDrawer(scope.row)">修改</el-button>
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

    <EditDrawer></EditDrawer>
    <ToBusinessDrawer></ToBusinessDrawer>
  </div>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, Ref, ref} from "vue";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './drawer.vue'
import ToBusinessDrawer from './to-user.vue'

import {bus, busEvent} from "@/utils/bus-events";

import {GetUserList} from "@/api/system/user";
import {ChangeBusinessSort, GetBusinessList} from "@/api/config/business";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {Help, SortThree} from "@icon-park/vue-next";

const tableIsLoading = ref(false)
const tableDataList = ref([])
const userList = ref([])
const userDict: Ref<{ id: number | undefined; name: string | undefined; }> = ref({id: undefined, name: undefined})
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  create_user: undefined,
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

const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const rowDblclick = async (row: any, column: any, event: any) => {
  try {
    await toClipboard(row[column.property]);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}

const showEditDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'config-business', content: row});
}
const showBusinessToUserDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'business-to-user', content: userList.value});
}

// 解析用户
const parseUser = (userId: number) => {
  return userDict.value[userId]
}

// 获取配置类型列表
const getTableDataList = () => {
  queryItems.value.create_user = queryItems.value.create_user ? queryItems.value.create_user : undefined
  queryItems.value.name = queryItems.value.name ? queryItems.value.name : undefined
  queryItems.value.code = queryItems.value.code ? queryItems.value.code : undefined
  tableIsLoading.value = true
  GetBusinessList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
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
  ChangeBusinessSort({
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
  // 获取用户列表
  GetUserList({}).then((response: object) => {
    userList.value = response.data.data
    response.data.data.forEach((user: any) => {
      userDict.value[user.id] = user.name
    })
  })

  // 获取配置类型列表
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
  if (message.eventType === 'config-business') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
