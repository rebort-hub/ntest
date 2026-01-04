<template>
    <div>
      <el-table
          ref="phoneTableRef"
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="tableDataList"
          style="width: 100%"
          :header-cell-style="{'text-align':'center'}"
          stripe
          row-key="id"
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

        <el-table-column show-overflow-tooltip prop="name" align="center" label="设备名称" min-width="25%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="os" align="center" label="系统类型" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.os }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="os_version" align="center" label="系统版本" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.os_version }} </span>
          </template>
        </el-table-column>

        <el-table-column prop="device_id" align="center" min-width="20%">
          <template #header>
            <span> 设备id </span>
            <el-tooltip class="item" effect="dark" placement="top-start" content="使用adb devices查看">
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </el-tooltip>
          </template>
          <template #default="scope">
            <span> {{ scope.row.device_id }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="screen" align="center" label="分辨率" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.screen }} </span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" prop="desc" align="center" label="操作" width="110">
          <template #default="scope">
            <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showEditDrawer(scope.row)">修改</el-button>
            <el-popconfirm width="250px" title="复制此服务器并生成新的服务器?" @confirm="copyData(scope.row)">
              <template #reference>
                <el-button style="margin: 0; padding: 2px" type="text" :loading="scope.row.copyIsLoading" size="small">复制</el-button>
              </template>
            </el-popconfirm>
            <el-popconfirm width="250px" :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row)">
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
        <EditDrawer></EditDrawer>
        <AddDrawer></AddDrawer>
    </div>

</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, watch, computed} from "vue";
import {Help, SortThree} from "@icon-park/vue-next";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './edit-drawer.vue'
import AddDrawer from './add-drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {GetConfigByCode} from "@/api/config/config-value";
import {ChangePhoneSort, CopyPhone, DeletePhone, GetPhoneList} from "@/api/autotest/device-phone";

const phoneTableRef = ref(null)
const tableIsLoading = ref(false)
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newIdList = ref([])
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true
})

const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.71}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.81}px`
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

const deleteData = (row: { id: any; }) => {
  DeletePhone({id: row.id}).then(response => {
    if (response){
      getTableDataList()
    }
  })
}

const showEditDrawer = (row: any) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'edit-phone', content: row})
}

const copyData = (row: { copyIsLoading: boolean; id: any; }) => {
  row.copyIsLoading = true
  CopyPhone({ 'id': row.id }).then(response => {
    row.copyIsLoading = false
    if (response) {
      getTableDataList()
    }
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetPhoneList(queryItems.value).then((response: object) => {
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
  ChangePhoneSort({
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

const getPhoneOsMapping = () => {
  if (busEvent.data.phoneOsMapping.length < 1){
    GetConfigByCode({ code: 'phone_os_mapping' }).then(response => {
      busEvent.data.phoneOsMapping = response.data
    })
  }
}
const getDeviceExtends = () => {
  if (Object.keys(busEvent.data.deviceExtends).length < 1){
    GetConfigByCode({ code: 'device_extends' }).then(response => {
      busEvent.data.deviceExtends = response.data
    })
  }
}

onMounted(() => {
  getTableDataList()
  getPhoneOsMapping()
  getDeviceExtends()
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
  setTableHeight()
  window.addEventListener('resize', handleResize);

})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
  window.removeEventListener('resize', handleResize);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'phone-editor') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
