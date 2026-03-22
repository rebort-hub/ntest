<template>
  <el-drawer v-model="drawerIsShow" title="接口使用情况" size="85%">
    <el-table
      ref="showApiUseRef"
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

    <el-table-column prop="id" label="序号" align="center" min-width="8%">
      <template #default="scope">
        <span> {{ scope.$index + 1 }} </span>
      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="from" label="接口对应步骤" align="center" min-width="50%">
      <template #default="scope">
        <span>{{ scope.row.from }}</span>
      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="name" label="用例名称" align="center" min-width="25%">
      <template #default="scope">
        <span>{{ scope.row.name }}</span>
      </template>
    </el-table-column>

      <el-table-column show-overflow-tooltip prop="level" align="center" min-width="17%">
        <template #header>
          <span> 调试结果 </span>
          <el-tooltip class="item" effect="dark" placement="top-start">
            <template #content>
              <div>1: 批量运行时，只有调试结果为通过的才会执行</div>
              <div>2: 请务必将用例调试通过后再设为调试通过</div>
            </template>
            <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </template>
        <template #default="scope">
          <div>
            <div style="width: 80%; margin-left:auto; margin-right:auto">
              <el-select
                  slot="prepend"
                  v-model="scope.row.status"
                  size="small"
                  placeholder="选择调试结果"
                  filterable
                  :class="`case-status-${scope.row.status}`"
                  @change="changeCaseIsRun(scope.row)"
              >
                <el-option label="未调试-不执行" :value="0"><span style="color: #dcdfe6">未调试-不执行</span></el-option>
                <el-option label="调试通过-要执行" :value="1"><span style="color: #67C23A">调试通过-要执行</span></el-option>
                <el-option label="调试通过-不执行" :value="2"><span style="color: #909399">调试通过-不执行</span></el-option>
                <el-option label="调试不通过-不执行" :value="3"><span style="color: #F56C6C">调试不通过-不执行</span></el-option>
              </el-select>
            </div>
          </div>
        </template>
      </el-table-column>

  </el-table>
  </el-drawer>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import {Help} from "@icon-park/vue-next";

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import toClipboard from "@/utils/copy-to-memory";
import {ChangeCaseStatus} from "@/api/autotest/case";

const drawerIsShow = ref(false)
const showApiUseRef = ref(null)
const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.83}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.88}px`
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

onMounted(() => {
  bus.on(busEvent.drawerIsShow, busDrawerIsShow);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, busDrawerIsShow);
  window.removeEventListener('resize', handleResize);
})

const busDrawerIsShow = (message: any) => {
  if (message.eventType === 'api-use') {
    tableDataList.value = message.content
    drawerIsShow.value = true
  }
}

const changeCaseIsRun = (row: { id: any; status: any; }) => {
  ChangeCaseStatus('api', { id_list: [row.id], status: row.status }).then(response => {})
}
</script>

<style scoped lang="scss">

.case-status-0 :deep(.el-input__wrapper){
  background-color: #dcdfe6;
}

.case-status-1 :deep(.el-input__wrapper){
  background-color: #67C23A;
}

.case-status-2 :deep(.el-input__wrapper){
  background-color: #909399;
}

.case-status-3 :deep(.el-input__wrapper){
  background-color: #F56C6C;
}

</style>
