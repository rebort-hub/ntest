<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showEditDrawer(undefined)">新增问题记录</el-button>
        <el-popconfirm width="250px" title="确定删除所选中的记录?" @confirm="deleteData(null)">
          <template #reference>
            <el-button
                :disabled="selectedList.length < 1"
                type="danger"
                size="small">批量删除</el-button>
          </template>
        </el-popconfirm>
      </div>

      <div class="layout-container-form-search">
        <el-select
            v-model="queryItems.test_type"
            style="width: 100%; margin-right: 10px"
            placeholder="选择测试类型"
            size="small"
            filterable
            clearable
            default-first-option
        >
          <el-option
              v-for="item in runTestTypeList"
              :key="item.key"
              :label="item.label"
              :value="item.key"
          />
        </el-select>

        <el-select
            v-model="queryItems.hit_type"
            filterable
            clearable
            allow-create
            default-first-option
            placeholder="问题类型，可手动输入"
            size="small"
            style="width:100%; margin-right: 10px"
        >
          <el-option
              v-for="item in hitTypeList"
              :key="item.key"
              :label="item.value"
              :value="item.key"
          />
        </el-select>

        <el-input v-model="queryItems.report_id" size="small" placeholder="测试报告id" style="margin-right: 10px"/>

        <el-select
            v-model="queryItems.record_from"
            style="width: 100%; margin-right: 10px"
            placeholder="记录的来源"
            size="small"
            filterable
            clearable
            default-first-option
        >
          <el-option
              v-for="(value, key) in recordFromTypeDict"
              :key="key"
              :label="value"
              :value="key"
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
          @selection-change="clickSelectAll">

        <el-table-column type="selection" min-width="2%"/>

        <el-table-column prop="id" label="数据id" align="center" min-width="6%">
          <template #default="scope">
            <span> {{ scope.row.id }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="触发日期" prop="date" align="center" min-width="10%">
          <template #default="scope">
            <span> {{ paramsISOTime(scope.row.date) }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="所属服务" prop="project_id" align="center" min-width="10%">
          <template #default="scope">
            <span> {{ projectDictData[scope.row.project_id] }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="测试类型" prop="test_type" align="center" min-width="6%">
          <template #default="scope">
            <span>{{ runTestTypeDict[scope.row.test_type] }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="运行环境" prop="env" align="center" min-width="10%">
          <template #default="scope">
            <span>{{ envDict[scope.row.env] }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="问题类型" prop="hit_type" align="center" min-width="6%">
          <template #default="scope">
            <span>{{ scope.row.hit_type }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="问题详情" prop="hit_detail" align="center" min-width="15%">
          <template #default="scope">
            <span>{{ scope.row.hit_detail }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="报告id" prop="report_id" align="center" min-width="6%">
          <template #default="scope">
            <span>{{ scope.row.report_id }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="记录来源" prop="report_id" align="center" min-width="6%">
          <template #default="scope">
            <span>{{ recordFromTypeDict[scope.row.record_from] }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="创建人" prop="create_user" align="center" min-width="6%">
          <template #default="scope">
            <span>{{ userDict[scope.row.create_user] }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip align="center" label="操作" width="140">
          <template #default="scope">
            <el-button type="text" size="small" style="margin: 0; padding: 2px" @click.native="showReport(scope.row)">查看报告</el-button>
            <el-button type="text" size="small" style="margin: 0; padding: 2px" @click.native="showEditDrawer(scope.row)">修改</el-button>
            <el-popconfirm title="确定删除数据?" @confirm="deleteData(scope.row)">
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

    <EditDrawer
        :run-env-list="envList"
        :hit-type-list="hitTypeList"
        :project-list="projectListData"
        :run-test-type-list="runTestTypeList"
    ></EditDrawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import {useRouter} from "vue-router";
import Pagination from '@/components/pagination.vue'
import EditDrawer from './drawer.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {GetHitList, GetHitTypeList, DeleteHit} from "@/api/assist/hit";
import {GetConfigByCode} from "@/api/config/config-value";
import {GetRunEnvList} from "@/api/config/run-env";
import {GetProjectList} from "@/api/autotest/project";
import {GetUserList} from "@/api/system/user";
import {paramsISOTime} from "@/utils/parse-data";

const router = useRouter()
const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  test_type: undefined,
  hit_type: undefined,
  report_id: undefined,
  record_from: undefined,
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

const runTestTypeList = ref([])
const runTestTypeDict = ref({})
const hitTypeList = ref([])
const recordFromTypeDict = {1: '人为记录', 2: '自动记录'}
const envList = ref([])
const envDict = ref({})
const projectListData = ref([])
const projectDictData = ref({})
const userDict = ref({})
const selectedList = ref([])
const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const getUserList = () => {
  GetUserList({}).then((response: object) => {
    response.data.data.forEach(item => {
      userDict.value[item.id] = item.name
    })
  })
}

const clickSelectAll = (val: never[]) => {
  selectedList.value = val
}

const getSubmitId = (row: any) => {
  let selectedIdList: any[] = []
  if (row){
    selectedIdList = [row.id]
  }else {
    selectedList.value.forEach(item => { selectedIdList.push(item.id) })
  }
  return selectedIdList
}

const showEditDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'hit', content: row});
}

const showReport = (row: { test_type: string, report_id: any; }) => {
  // 使用路由跳转替代新窗口打开
  router.push(`/${row.test_type}-test/report-show?id=${row.report_id}`)
}

const deleteData = (row: any) => {
  DeleteHit({id_list: getSubmitId(row)}).then(response => {
    if (response){
      getTableDataList()
    }
  })
}

const getProjectList = () => {
  GetProjectList('api', {page_no: 1, page_size: 1000}).then(response => {
    projectListData.value = response.data.data
    projectListData.value.forEach(project => {
      projectDictData.value[project.id] = project.name
    })
  })
}

const getRunType = () => {
  GetConfigByCode({ code: 'test_type' }).then(response => {
    runTestTypeList.value = response.data
    runTestTypeList.value.forEach(rType => {
      runTestTypeDict.value[rType['key']] = rType['label']
    })
  })
}

const getHitTypeList = () => {
  GetHitTypeList().then(response => {
    hitTypeList.value = response.data
  })
}

const getRunEnvList = () => {
  GetRunEnvList({}).then(response => {
    envList.value = response.data.data
    envList.value.forEach(evn => {
      envDict.value[evn.code] = evn.name
    })
  })
}

const getTableDataList = () => {
  queryItems.value.record_from = queryItems.value.record_from ? queryItems.value.record_from : undefined
  queryItems.value.test_type = queryItems.value.test_type ? queryItems.value.test_type : undefined
  queryItems.value.hit_type = queryItems.value.hit_type ? queryItems.value.hit_type : undefined
  queryItems.value.report_id = queryItems.value.report_id ? queryItems.value.report_id : undefined
  tableIsLoading.value = true
  GetHitList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

onMounted(() => {
  getUserList()
  getProjectList()
  getRunEnvList()
  getHitTypeList()
  getRunType()
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
  if (message.eventType === 'hit') {
    getTableDataList()
  }
}

</script>

<style scoped lang="scss">

</style>
