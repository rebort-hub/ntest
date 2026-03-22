<template>
  <el-drawer v-model="drawerIsShow" title="接口归属信息" size="95%">
    <el-table
      ref="showApiFromRef"
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

    <el-table-column prop="id" label="序号" align="center" min-width="5%">
      <template #default="scope">
        <span> {{ scope.$index + 1 }} </span>
      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="from" label="接口归属" align="left" min-width="30%">
      <template #default="scope">
        <span>{{ scope.row.from }}</span>
      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="addr" align="center" label="接口信息" min-width="40%">
      <template #default="scope">
        <div
            class="block"
            :class="`block_${scope.row.method.toLowerCase()}`"
            :style="{
                  'backgroundColor': scope.row.status === 'disable' ? '#ebebeb' : '',
                  'textDecoration': scope.row.status === 'disable' ? 'line-through' : ''
                }"
        >
                <span
                    class="block-method block_method_color"
                    :class="`block_method_${scope.row.method.toLowerCase()}`"
                    :style="{
                    'backgroundColor': scope.row.status === 'disable' ? '#ebebeb' : ''
                  }"
                >
                  {{ scope.row.method }}
                </span>
          <span class="block-method block_url">{{ scope.row.addr }}</span>
        </div>
      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="level" align="center" min-width="7%">
      <template #header>
        <span> 重要级别 </span>
        <el-tooltip class="item" effect="dark" placement="top-start" content="标识接口的重要级别，根据重要级别筛选优先做自动化测试的接口">
          <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
        </el-tooltip>
      </template>
      <template #default="scope">
        <div style="width: 80%; margin-left:auto; margin-right:auto">
          <el-select
              v-model="scope.row.level"
              size="small"
              placeholder="选择重要程度"
              filterable
              :class="`api-level-${scope.row.level}`"
              @change="selectApiLevel(scope.row)"
          >
            <el-option label="高" value="P0"><span style="color: #F56C6C">高</span></el-option>
            <el-option label="中" value="P1"><span style="color: #E6A23C">中</span></el-option>
            <el-option label="低" value="P2"><span style="color: #67C23A">低</span></el-option>
          </el-select>
        </div>
      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="status" align="center" min-width="5%">
      <template #header>
        <span>状态</span>
        <el-tooltip class="item" effect="dark" placement="top-start" content="标识接口是否被废弃">
          <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
        </el-tooltip>
      </template>
      <template #default="scope">
        <el-switch
            v-model="scope.row.status"
            :inactive-value="'disable'"
            :active-value="'enable'"
            @change="changeStatus(scope.row)"
        />
      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="use_count" align="center" width="80">
      <template #header>
        <span> 使用次数 </span>
        <el-tooltip class="item" effect="dark" placement="top-start">
          <template #content>
            <div>
              <div>1: 统计有多少条用例里直接使用了此接口</div>
              <div>2: 被设计为用例的步骤后，该用例被引用的，不纳入统计</div>
              <div>3: 被使用过的接口，点击使用次数数值可查看使用明细</div>
            </div>
          </template>
          <span><i style="color: #409EFF" class="el-icon-question" /></span>
        </el-tooltip>
      </template>
      <template #default="scope">
        <el-tooltip class="item" effect="dark" placement="top-start">
          <template #content >
            <div>{{ scope.row.use_count > 0 ? '点击查看详情' : '未被使用过' }}</div>
          </template>
          <el-tag v-if="scope.row.use_count" @click="getApiToStep(scope.row)">
            {{ scope.row.use_count }}
          </el-tag>
          <el-tag v-else type="info">0</el-tag>
        </el-tooltip>
      </template>
    </el-table-column>

    <el-table-column fixed="right" prop="desc" align="center" label="操作" width="100">
      <template #default="scope">
        <el-button type="text" size="small" style="margin: 0; padding: 2px" @click="showEditDrawer(scope.row)">查看</el-button>
        <el-button v-if="caseId" type="text" size="small" style="margin: 0; padding: 2px" @click="apiToStep(scope.row)">转步骤</el-button>
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
import {ChangeApiLevel, ChangeApiStatus, GetApiToStep} from "@/api/autotest/api";
import {ChangeStepElement} from "@/api/autotest/step";

const props = defineProps({
  caseId: {
    default: undefined,
    type: Number
  },
  stepId: {
    default: '',
    type: Number,
  }
})

const drawerIsShow = ref(false)
const showApiFromRef = ref(null)
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

const getApiToStep = (row: { id: any; }) => {
  tableIsLoading.value = true
  GetApiToStep({ id: row.id }).then(response => {
    tableIsLoading.value = false
    if (response){
      bus.emit(busEvent.drawerIsShow, {eventType: 'api-use', content: response.data})
    }
  })
}

const selectApiLevel = (row: { id: any; level: any; }) => {
  tableIsLoading.value = true
  ChangeApiLevel({id: row.id, level: row.level}).then(response => {
    tableIsLoading.value = false
  })
}

const changeStatus = (row: { id: any; status: any; }) => {
  tableIsLoading.value = true
  ChangeApiStatus({id: row.id, status: row.status}).then(response => {
    tableIsLoading.value = false
  })
}

const showEditDrawer = (row: any) => {
  bus.emit(busEvent.drawerIsShow, { eventType: 'api-editor', content: row, command: 'edit' })
}

const apiToStep = (row: any) => {
  if (props.stepId){ // 步骤更换接口
    ChangeStepElement('api', {id: props.stepId, element_id: row.id}).then(response => {
      if (response){
        bus.emit(busEvent.drawerIsCommit, {eventType: 'change-step-element', apiId: row.id})
      }
    })
  }else { // 新增步骤
    const step = JSON.parse(JSON.stringify(row));
    step.api_id = step.id
    step.id = undefined
    bus.emit(busEvent.drawerIsShow, {eventType: 'step-editor', content: step})
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
  if (message.eventType === 'api-from') {
    tableDataList.value = message.content
    drawerIsShow.value = true
  }
}

</script>

<style scoped lang="scss">
.block_post {
  border: 1px solid #49cc90;
  background-color: rgba(73, 204, 144, .1)
}

.block_method_post {
  background-color: #49cc90;
}

.block_put {
  border: 1px solid #fca130;
  background-color: rgba(252, 161, 48, .1)
}

.block_method_put {
  background-color: #fca130;
}

.block_get {
  border: 1px solid #61affe;
  background-color: rgba(97, 175, 254, .1)
}

.block_method_get {
  background-color: #61affe;
}

.block_delete {
  border: 1px solid #f93e3e;
  background-color: rgba(249, 62, 62, .1)
}

.block_method_delete {
  background-color: #f93e3e;
}

.block_patch {
  border: 1px solid #50e3c2;
  background-color: rgba(80, 227, 194, .1)
}

.block_method_patch {
  background-color: #50e3c2;
}

.block_head {
  border: 1px solid #e6a23c;
  background-color: rgba(230, 162, 60, .1)
}

.block_method_head {
  background-color: #e6a23c;
}

.block_options {
  border: 1px solid #409eff;
  background-color: rgba(64, 158, 255, .1)
}

.block_method_options {
  background-color: #409eff;
}

.block {
  position: relative;
  border-radius: 4px;
  /*height: 48px;*/
  overflow: hidden;
  padding: 5px;
  display: flex;
  align-items: center;
}

.block_url {
  word-break: normal;
  width: auto;
  display: block;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow: hidden;
  -webkit-box-flex: 1;
  -ms-flex: 1;
  font-family: Open Sans, sans-serif;
  color: #3b4151;
}

.block_name {
  padding-left: 5px;
  word-break: normal;
  width: auto;
  display: block;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow: hidden;
  -webkit-box-flex: 1;
  -ms-flex: 1;
  font-family: Open Sans, sans-serif;
  color: #3b4151;
}

.block_method_color {
  cursor: pointer;
  color: #fff;
}

.block-method {
  font-size: 14px;
  font-weight: 600;
  min-width: 50px;
  padding: 0px 10px;
  text-align: center;
  border-radius: 5px;
  text-shadow: 0 1px 0 rgba(0, 0, 0, .1);
  font-family: Titillium Web, sans-serif;
}

.block-summary-description {
  word-break: normal;
  width: auto;
  display: block;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow: hidden;
  -webkit-box-flex: 1;
  -ms-flex: 1;
  font-family: Open Sans, sans-serif;
  color: #3b4151;
}


.api-level-P0 :deep(.el-input__wrapper){
  background-color: #F56C6C;
}

.api-level-P1 :deep(.el-input__wrapper){
  background-color: #E6A23C;
}

.api-level-P2 :deep(.el-input__wrapper){
  background-color: #67C23A;
}



</style>
