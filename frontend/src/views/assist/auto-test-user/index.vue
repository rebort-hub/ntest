<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">

      <div class="layout-container-form-search">
        <el-select
            style="margin-right: 10px"
            v-model="queryItems.env"
            placeholder="请选择环境"
            size="small"
            filterable
            default-first-option
        >
          <el-option
              v-for="(env) in envList"
              :key="env.code"
              :label="env.name"
              :value="env.code"
          />
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

        <el-table-column label="数据id" prop="id" align="center" min-width="8%">
          <template #default="scope">
            <span> {{ scope.row.id }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="手机号/账号" prop="mobile" align="center" min-width="10%">
          <template #default="scope">
            <span> {{ scope.row.mobile }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="密码" prop="password" align="center" min-width="22%">
          <template #default="scope">
            <span> {{ scope.row.password }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="access_token" prop="access_token" align="center" min-width="25%">
          <template #default="scope">
            <span>{{ scope.row.access_token }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="refresh_token" prop="refresh_token" align="center" min-width="25%">
          <template #default="scope">
            <span>{{ scope.row.refresh_token }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="公司名称" prop="company_name" align="center" min-width="25%">
          <template #default="scope">
            <span>{{ scope.row.company_name }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="角色" prop="role" align="center" min-width="10%">
          <template #default="scope">
            <span>{{ scope.row.role }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="所属环境" prop="env" align="center" min-width="10%">
          <template #default="scope">
            <span>{{ envDict[scope.row.env] }}</span>
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
  </div>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import Pagination from '@/components/pagination.vue'

import {GetRunEnvList} from "@/api/config/run-env";
import {GetAutoTestUser} from "@/api/tools/data-pool";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {bus, busEvent} from "@/utils/bus-events";

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  env: undefined
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

const envList = ref([])
const envDict = ref({})

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

const getTableDataList = () => {
  queryItems.value.env = queryItems.value.env ? queryItems.value.env : undefined
  tableIsLoading.value = true
  GetAutoTestUser(queryItems.value).then(response => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

onMounted(() => {
  GetRunEnvList({page_no: 1, page_size: 99999}).then(response => {
    if (response.data.data.length > 0) {
      queryItems.value.env = response.data.data[0].code
    }
    response.data.data.forEach((env: { code: string; name: any; }) => {
      if (!(env.code in envDict.value)) {
        envList.value.push(env)
      }
      envDict.value[env.code] = env.name
    })

    getTableDataList()
  })
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
})

</script>

<style scoped lang="scss">

</style>
