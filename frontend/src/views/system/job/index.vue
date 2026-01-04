<template>
  <div class="layout-container">

    <div style="margin: 10px">
      <el-table
          v-loading="tableIsLoading"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="tableDataList"
          style="width: 100%"
          stripe
          :height="tableHeight">
        <el-table-column prop="id" label="序号" align="center" width="40" >
          <template #default="scope">
            <span> {{ scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="任务名" prop="name" align="center" min-width="25%">
          <template #default="scope">
            <span> {{ scope.row.name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="任务方法名" prop="func_name" align="center" min-width="15%">
          <template #default="scope">
            <span> {{ scope.row.func_name }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="定时表达式" prop="cron" align="center" min-width="10%">
          <template #default="scope">
            <span>{{ scope.row.cron }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="下次执行时间" prop="next_run_time" align="center" min-width="20%">
          <template #default="scope">
            <span>{{ scope.row.next_run_time }}</span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip label="启用" prop="status" align="center" width="60">
          <template #default="scope">
            <el-switch v-model="scope.row.status" :loading="scope.row.loading" @change="changStatus(scope.row)" />
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip align="center" label="操作" width="140">
          <template #default="scope">
            <el-popconfirm title="确定执行一次?" @confirm="runJob(scope.row)">
              <template #reference>
                <el-button style="margin: 0; padding: 2px;" type="text" size="small">触发执行</el-button>
              </template>
            </el-popconfirm>
            <el-button type="text" size="small" style="margin: 0; padding: 2px" @click.native="showEditDrawer(scope.row.func_name)">查看记录</el-button>
          </template>
        </el-table-column>
      </el-table>

    </div>

    <ShowLogDrawer></ShowLogDrawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import ShowLogDrawer from './show-log.vue'

import {bus, busEvent} from "@/utils/bus-events";
import {GetJobFuncList, DeleteJob, PostJob, JobRun} from "@/api/system/job";

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.84}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.89}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const showEditDrawer = (funcName: string) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'job', content: funcName});
}

const changStatus = (row: object) => {
  if (row.id) { // 关闭任务
    row.loading = true
    DeleteJob({ func_name: row.func_name }).then(response => {
      row.loading = false
      if (response) {
        getTableDataList()
      }
    })
  } else { // 启用任务
    row.loading = true
    PostJob({ func_name: row.func_name }).then(response => {
      row.loading = false
      if (response) {
        getTableDataList()
      }
    })
  }
}

const runJob = (row: object) => {
  JobRun({ func_name: row.func_name }).then(response => {})
}

const getTableDataList = () => {
  GetJobFuncList().then(response => {
    response.data.forEach((item: { status: boolean; id: undefined; }) => {
      item.status = item.id !== undefined
    })
    tableDataList.value = response.data
  })
}

onMounted(() => {
  getTableDataList()
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
})

</script>

<style scoped lang="scss">

</style>
