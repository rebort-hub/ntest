<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showEditDrawer(undefined, 'project')"> 添加 </el-button>
      </div>

      <div class="layout-container-form-search">
        <el-input
            v-model="queryItems.name"
            :placeholder="`${testType === 'api' ? '服务' : testType === 'ui' ? '项目' : 'app'}名，支持关键字查询`"
            size="small"
            clearable
            style="width: 200px; margin-right: 10px"
        />

        <el-select
            v-model="queryItems.business_id"
            placeholder="选择业务线"
            filterable
            default-first-option
            clearable
            size="small"
            @clear="clearBusinessId"
            style="width: 200px; margin-right: 10px"
        >
          <el-option
              v-for="business in businessList"
              :key="business.id"
              :label="business.name"
              :value="business.id"
          />
        </el-select>

        <el-select
            v-model="queryItems.manager"
            :placeholder="'选择负责人'"
            filterable
            default-first-option
            clearable
            style="width: 200px; margin-right: 10px"
            size="small"
        >
          <el-option v-for="user in userList" :key="user.name" :label="user.name" :value="user.id" />
        </el-select>

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
          @row-dblclick="rowDblclick"
          row-key="id"
      >

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

        <el-table-column prop="id" label="序号" width="60" align="center">
          <template #default="scope">
            <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column
            show-overflow-tooltip
            prop="name"
            align="center"
            :label="`${testType === 'api' ? '服务' : testType === 'ui' ? '项目' : 'app'}名称`"
            min-width="20%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column
            v-if="testType === 'api'"
            show-overflow-tooltip
            align="center"
            label="swagger"
            prop="swagger"
            min-width="35%"
        >
          <template #default="scope">
            <div v-if="scope.row.swagger">
              <span>{{ scope.row.swagger }}</span>
            </div>
            <div v-else>
              <el-tag type="warning">未设置</el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column
            v-if="testType === 'api'"
            show-overflow-tooltip
            align="center"
            label="拉取状态"
            min-width="10%"
        >
          <template #default="scope">
            <el-tooltip
                v-if="scope.row.last_pull_status !== 1"
                content="点击查看详情"
                class="item"
                effect="dark"
                placement="top-start"
            >
              <el-tag
                  :type="swaggerPullStatusMappingTagType[scope.row.last_pull_status]"
                  @click="showSwaggerPullLog(scope.row)"
              >
                {{ swaggerPullStatusMappingContent[scope.row.last_pull_status] }}
              </el-tag>
            </el-tooltip>

            <el-tag
                v-else
                :type="swaggerPullStatusMappingTagType[scope.row.last_pull_status]"
                @click="showSwaggerPullLog(scope.row)"
            >
              {{ swaggerPullStatusMappingContent[scope.row.last_pull_status] }}
            </el-tag>

          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="business_id" align="center" label="业务线" min-width="10%">
          <template #default="scope">
            <span> {{ businessDict[scope.row.business_id] }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="manager" align="center" label="负责人" min-width="10%">
          <template #default="scope">
            <span> {{ userDict[scope.row.manager] }} </span>
          </template>
        </el-table-column>

        <el-table-column v-if="testType === 'app'" show-overflow-tooltip align="center" label="app_package" min-width="15%">
          <template #default="scope">
            <span>{{ scope.row.app_package }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="update_user" align="center" label="最后修改" min-width="10%">
          <template #default="scope">
            <span>{{ userDict[scope.row.update_user] }}</span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" width="220">
          <template #default="scope">
            <div class="action-buttons">
              <el-button 
                  v-show="scope.row.swagger"
                  class="action-btn pull-btn" 
                  type="primary" 
                  size="small" 
                  @click="showPullSwaggerDrawer(scope.row)">
                拉取
              </el-button>
              
              <el-button 
                  class="action-btn edit-btn" 
                  type="warning" 
                  size="small" 
                  @click="showEditDrawer(scope.row, 'project')">
                修改
              </el-button>
              
              <el-button 
                  class="action-btn env-btn" 
                  type="success" 
                  size="small" 
                  @click="showEditDrawer(scope.row, 'env')">
                环境
              </el-button>
              
              <el-popconfirm width="250px" :title="`确定删除【${ scope.row.name }】?`" @confirm="deleteData(scope.row.id)">
                <template #reference>
                  <el-button 
                      class="action-btn delete-btn" 
                      type="danger" 
                      size="small">
                    删除
                  </el-button>
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
    </div>

    <EditProjectDrawer
        :test-type="testType"
        :user-list="userList"
        :business-list="businessList"
    ></EditProjectDrawer>

    <EditEnvDrawer :test-type="testType"></EditEnvDrawer>

    <selectPullOptionDialog></selectPullOptionDialog>
    <showSwaggerPullLogDrawer :user-dict="userDict"></showSwaggerPullLogDrawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed, watch} from "vue";
import Pagination from '@/components/pagination.vue'
import EditProjectDrawer from './edit-project-drawer.vue'
import EditEnvDrawer from './edit-env-drawer.vue'
import selectPullOptionDialog from './select-pull-option-dialog.vue'
import showSwaggerPullLogDrawer from './show-swagger-pull-log.vue'

import {GetUserList} from "@/api/system/user";
import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {swaggerPullStatusMappingContent, swaggerPullStatusMappingTagType} from "@/components/autotest/mapping";
import {GetBusinessList} from "@/api/config/business";
import {ChangeProjectSort, DeleteProject, GetProjectList} from "@/api/autotest/project";
import {Help, SortThree} from "@icon-park/vue-next";

const props = defineProps({
  testType: {
    default: 'api',
    type: String
  }
})

const tableIsLoading = ref(false)
const businessList = ref([])
const businessDict = ref({})
const tableDataList = ref([])
const newIdList = ref([])
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const userList = ref([])
const userDict = ref({})
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  name: undefined,
  manager: undefined,
  business_id: undefined,
  create_user: undefined
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

const showSwaggerPullLog = (row: any) => {
  if (row.last_pull_status !== 1) {
    bus.emit(busEvent.drawerIsShow, {eventType: 'show-swagger-pull-log', content: row})
  }
}

const getBusinessList = () => {
  GetBusinessList({page_no: 1, page_size: 1000}).then((response: any) => {
    if (response && response.data && response.data.data) {
      businessList.value = response.data.data
      businessList.value.forEach(business => {
        businessDict.value[business.id] = business.name
      })
    } else {
      console.warn('业务线列表数据格式异常:', response)
      businessList.value = []
    }
  }).catch((error) => {
    console.error('获取业务线列表失败:', error)
    businessList.value = []
  })
}

const showEditDrawer = (row: any, type: string | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: type === 'project' ? 'project-editor' : 'project-env-editor', content: row});
}
const showPullSwaggerDrawer = (row: any) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'pull-from-swagger', content: row});
}

const getTableDataList = () => {
  queryItems.value.manager = queryItems.value.manager ? queryItems.value.manager : undefined
  queryItems.value.name = queryItems.value.name ? queryItems.value.name : undefined
  queryItems.value.business_id = queryItems.value.business_id ? queryItems.value.business_id : undefined
  queryItems.value.create_user = queryItems.value.create_user ? queryItems.value.create_user : undefined
  tableIsLoading.value = true
  GetProjectList(props.testType, queryItems.value).then((response: any) => {
    tableIsLoading.value = false
    if (response && response.data) {
      tableDataList.value = response.data.data || []
      tableDataTotal.value = response.data.total || 0
    } else {
      console.warn('项目列表数据格式异常:', response)
      tableDataList.value = []
      tableDataTotal.value = 0
    }
  }).catch((error) => {
    tableIsLoading.value = false
    console.error('获取项目列表失败:', error)
    tableDataList.value = []
    tableDataTotal.value = 0
  })
}

const sortTable = () => {
  tableIsLoading.value = true
  ChangeProjectSort(props.testType, {
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

const deleteData = (dataId: number) => {
  DeleteProject(props.testType, {id: dataId}).then(response => {
    if (response){
      getTableDataList()
    }
  })
}

const getUserList = () => {
  GetUserList({}).then((response: any) => {
    if (response && response.data && response.data.data) {
      userList.value = response.data.data
      userList.value.forEach(item => {
        userDict.value[item.id] = item.name
      })
    } else {
      console.warn('用户列表数据格式异常:', response)
      userList.value = []
    }
  }).catch((error) => {
    console.error('获取用户列表失败:', error)
    userList.value = []
  })
}

const clearBusinessId = () => {
  queryItems.value.business_id = undefined
}

onMounted(() => {
  getUserList()
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
  if (message.eventType === 'project-editor') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">
// 操作按钮样式优化 - 安全版本（无图标）
.action-buttons {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  justify-content: center;
  align-items: center;
  padding: 2px 0;
  
  .action-btn {
    min-width: 36px;
    height: 28px;
    padding: 4px 6px;
    font-size: 12px;
    border-radius: 4px;
    transition: all 0.2s ease;
    font-weight: 500;
    border: 1px solid;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }
    
    // 拉取按钮 - 蓝色主题
    &.pull-btn {
      background-color: #409eff;
      border-color: #409eff;
      color: white;
      
      &:hover {
        background-color: #337ecc;
        border-color: #337ecc;
        box-shadow: 0 2px 6px rgba(64, 158, 255, 0.4);
      }
    }
    
    // 修改按钮 - 橙色主题
    &.edit-btn {
      background-color: #e6a23c;
      border-color: #e6a23c;
      color: white;
      
      &:hover {
        background-color: #cf9236;
        border-color: #cf9236;
        box-shadow: 0 2px 6px rgba(230, 162, 60, 0.4);
      }
    }
    
    // 环境按钮 - 绿色主题
    &.env-btn {
      background-color: #67c23a;
      border-color: #67c23a;
      color: white;
      
      &:hover {
        background-color: #529b2e;
        border-color: #529b2e;
        box-shadow: 0 2px 6px rgba(103, 194, 58, 0.4);
      }
    }
    
    // 删除按钮 - 红色主题
    &.delete-btn {
      background-color: #f56c6c;
      border-color: #f56c6c;
      color: white;
      
      &:hover {
        background-color: #dd6161;
        border-color: #dd6161;
        box-shadow: 0 2px 6px rgba(245, 108, 108, 0.4);
      }
    }
  }
}

// 响应式适配
@media (max-width: 1400px) {
  .action-buttons {
    gap: 4px;
    
    .action-btn {
      min-width: 36px;
      height: 26px;
      padding: 3px 6px;
      font-size: 11px;
    }
  }
}

@media (max-width: 1200px) {
  .action-buttons {
    gap: 3px;
    
    .action-btn {
      min-width: 32px;
      height: 24px;
      padding: 2px 5px;
      font-size: 10px;
    }
  }
}

@media (max-width: 768px) {
  .action-buttons {
    flex-wrap: wrap;
    gap: 2px;
    
    .action-btn {
      min-width: 30px;
      height: 22px;
      padding: 1px 4px;
      font-size: 9px;
    }
  }
}

// 拖拽按钮样式
.drag-button {
  cursor: grab;
  color: #909399;
  
  &:hover {
    color: #409eff;
  }
  
  &.drag-dragging {
    cursor: grabbing;
    opacity: 0.5;
  }
}
</style>
