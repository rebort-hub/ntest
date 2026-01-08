<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showEditDrawer(undefined)"> 添加数据</el-button>
      </div>

      <div class="layout-container-form-search">
        <el-select
            v-model="queryItems.env"
            placeholder="选择选择环境"
            clearable
            filterable
            default-first-option
            style="margin-right: 10px"
            size="small"
        >
          <el-option v-for="env in runEnvList" :key="env.code" :label="env.name" :value="env.code"/>
        </el-select>

        <el-input
            v-model="queryItems.mobile"
            clearable
            size="small"
            style="width: 200px; margin-right: 10px"
            placeholder="手机号，支持模糊搜索"/>

        <el-input
            v-model="queryItems.business_order_no"
            placeholder="流水号，支持模糊搜索"
            size="small"
            clearable
            style="width: 200px; margin-right: 10px"
        />

        <el-select
            v-model="queryItems.business_status"
            size="small"
            clearable
            placeholder="选择业务状态"
            style="margin-right: 10px">
          <el-option v-for="status in businessStatusList" :key="status" :label="status" :value="status" />
        </el-select>

        <el-select
            v-model="queryItems.use_status"
            size="small"
            clearable
            placeholder="选择使用状态"
            style="margin-right: 10px">
          <el-option v-for="(value, key) in useStatusList" :key="key" :label="value" :value="key" />
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
          @row-dblclick="rowDblclick">

        <el-table-column prop="id" label="序号" align="center" min-width="5%">
          <template #default="scope">
            <span> {{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="env" align="center" label="环境" min-width="10%">
          <template #default="scope">
            <span> {{ runEnvDict[scope.row.env] }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="mobile" align="center" label="手机号" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.mobile }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="password" align="center" label="密码" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.password }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="business_order_no" align="center" label="订单号" min-width="15%">
          <template #default="scope">
            <span> {{ scope.row.business_order_no }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="amount" align="center" label="金额" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.amount }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="business_status" align="center" label="业务状态" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.business_status }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="use_status" align="center" label="使用状态" min-width="10%">
          <template #default="scope">
            <el-tag
                size="small"
                :type="scope.row.use_status === 'not_used' ? 'success' :
              scope.row.use_status === 'used' ? 'danger' : ''"
            >{{ useStatusList[scope.row.use_status] }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="desc" align="center" label="描述" min-width="10%">
          <template #default="scope">
            <span>{{ scope.row.desc }}</span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" min-width="5%">
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

    <EditDrawer
        :run-env-list="runEnvList"
        :business-status-list="businessStatusList"
        :use-status-list="useStatusList"
    ></EditDrawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {GetRunEnvList} from "@/api/config/run-env";
import {GetDataPoolBusinessStatus, GetDataPoolList, GetDataPoolUseStatus} from "@/api/tools/data-pool";

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  detail: true,
  env: undefined,
  mobile: undefined,
  business_order_no: undefined,
  business_status: undefined,
  use_status: undefined
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

const runEnvList = ref([])
const runEnvDict = ref({})
const businessStatusList = ref([])
const useStatusList = ref([])

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

const showEditDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'data-pool', content: row});
}

const getRunEnvList = () => {
  GetRunEnvList({page_no: 1, page_size: 1000}).then(response => {
    runEnvList.value = response.data.data
    runEnvList.value.forEach(env => {
      runEnvDict.value[env.code] = env.name
    })
  })
}

const getDataPoolBusinessStatus = () => {
  GetDataPoolBusinessStatus({page_no: 1, page_size: 1000}).then(res => {
    businessStatusList.value = res.data
  })
}
const getDataPoolUseStatus = () => {
  GetDataPoolUseStatus({page_no: 1, page_size: 1000}).then(res => {
    useStatusList.value = res.data
  })
}

const getTableDataList = () => {
  queryItems.value.type = queryItems.value.type ? queryItems.value.type : undefined
  queryItems.value.name = queryItems.value.name ? queryItems.value.name : undefined
  queryItems.value.value = queryItems.value.value ? queryItems.value.value : undefined
  queryItems.value.create_user = queryItems.value.create_user ? queryItems.value.create_user : undefined
  tableIsLoading.value = true
  GetDataPoolList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

onMounted(() => {
  getRunEnvList()
  getDataPoolUseStatus()
  getDataPoolBusinessStatus()
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
  if (message.eventType === 'data-pool') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
