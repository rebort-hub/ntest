<template>
    <div>
      <el-table
          ref="serverTableRef"
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="tableDataList"
          style="width: 100%"
          :header-cell-style="{'text-align':'center'}"
          stripe
          row-key="id"
          :height="tableHeight"
          @row-dblclick="rowDblclick"
          class="device-table">

        <el-table-column label="排序" width="50" align="center">
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

        <el-table-column label="序号" header-align="center" width="60">
          <template #default="scope">
            <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="name" align="center" label="服务器名称" min-width="25%">
          <template #default="scope">
            <div class="server-name-cell">
              <el-icon class="server-icon"><Monitor /></el-icon>
              <span class="server-name">{{ scope.row.name }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="os" align="center" label="服务器系统类型" min-width="10%">
          <template #default="scope">
            <el-tag :type="getOsTagType(scope.row.os)" size="small">
              {{ scope.row.os }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="ip" align="center" label="服务器ip地址" min-width="15%">
          <template #default="scope">
            <div class="ip-cell">
              <code class="ip-code">{{ scope.row.ip }}</code>
              <el-button 
                text 
                size="small" 
                @click="copyText(scope.row.ip)"
                class="copy-btn"
                title="复制IP地址"
              >
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="port" align="center" label="服务器端口" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.port }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="appium_version" align="center" label="appium版本" min-width="10%">
          <template #default="scope">
            <el-tag type="info" size="small">
              v{{ scope.row.appium_version }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" align="center" label="最近一次访问状态" min-width="15%">
          <template #default="scope">
            <el-tag size="small" :type="appiumServerRequestStatusMappingTagType[scope.row.status]">
              {{ appiumServerRequestStatusMappingContent[scope.row.status] }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column fixed="right" prop="desc" align="center" label="操作" width="260">
          <template #default="scope">
            <div class="action-buttons">
              <el-button type="success" size="small" @click="runServer(scope.row)">访问</el-button>
              <el-button type="primary" size="small" @click="showEditDrawer(scope.row)">修改</el-button>
              <el-popconfirm width="250px" title="复制此服务器并生成新的服务器?" @confirm="copyData(scope.row)">
                <template #reference>
                  <el-button size="small" :loading="scope.row.copyIsLoading">复制</el-button>
                </template>
              </el-popconfirm>
              <el-popconfirm width="250px" :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row)">
                <template #reference>
                  <el-button type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
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
import {onMounted, ref, onBeforeUnmount} from "vue";
import {Help, SortThree} from "@icon-park/vue-next";
import {Monitor, CopyDocument} from "@element-plus/icons-vue";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './edit-drawer.vue'
import AddDrawer from './add-drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {appiumServerRequestStatusMappingContent, appiumServerRequestStatusMappingTagType} from "@/components/autotest/mapping";
import {ChangeServerSort, CopyServer, DeleteServer, GetServerList, RunServer} from "@/api/autotest/device-server";
import {GetConfigByCode} from "@/api/config/config-value";

const serverTableRef = ref(null)
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

const getOsTagType = (os: string) => {
  switch (os) {
    case 'Linux': return 'success'
    case 'Windows': return 'primary'
    case 'macOS': return 'warning'
    default: return 'info'
  }
}

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

const copyText = async (text: string) => {
  try {
    await toClipboard(text);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
    ElMessage.error("复制失败")
  }
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
  DeleteServer({id: row.id}).then(response => {
    if (response){
      getTableDataList()
    }
  })
}

const showEditDrawer = (row: any) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'edit-server', content: row})
}

const runServer = (row: { id: any; }) => {
  tableIsLoading.value = true
  RunServer({ 'id': row.id }).then(response => {
    tableIsLoading.value = false
    getTableDataList()
  })
}

const copyData = (row: { copyIsLoading: boolean; id: any; }) => {
  row.copyIsLoading = true
  CopyServer({ 'id': row.id }).then(response => {
    row.copyIsLoading = false
    if (response) {
      getTableDataList()
    }
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetServerList(queryItems.value).then((response: object) => {
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
  ChangeServerSort({
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

const getConfigByCode = () => {
  if (busEvent.data.serverOsMapping.length < 1){
    GetConfigByCode({ code: 'server_os_mapping' }).then(response => {
      busEvent.data.serverOsMapping = response.data
    })
  }
}

onMounted(() => {
  getTableDataList()
  getConfigByCode()
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
  setTableHeight()
  window.addEventListener('resize', handleResize);

})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
  window.removeEventListener('resize', handleResize);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'server-editor') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">
// 轻量的样式优化，保持Element Plus原生风格
.device-table {
  border-radius: 4px;
  overflow: hidden;
  
  .server-name-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    
    .server-icon {
      color: #409eff;
      font-size: 16px;
      flex-shrink: 0;
    }
    
    .server-name {
      font-weight: 500;
    }
  }
  
  .ip-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .ip-code {
      background: #f5f7fa;
      padding: 2px 6px;
      border-radius: 3px;
      font-size: 12px;
      color: #606266;
      flex: 1;
    }
    
    .copy-btn {
      color: #409eff;
      padding: 2px;
      
      &:hover {
        background-color: #ecf5ff;
      }
    }
  }
  
  .drag-button {
    cursor: grab;
    
    &:hover {
      color: #409eff;
    }
    
    &:active {
      cursor: grabbing;
    }
  }

  // 操作按钮布局
  .action-buttons {
    display: flex;
    gap: 4px;
    justify-content: center;
    flex-wrap: nowrap;
    
    .el-button {
      flex-shrink: 0;
    }
  }
}

// 拖拽时的样式
:deep(.drag-dragging) {
  opacity: 0.6;
}
</style>
