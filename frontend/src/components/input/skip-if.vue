<template>
  <div>
    <el-table ref="skipIfDataTableRef" :data="tempData" stripe size="small" row-key="id">

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

      <el-table-column label="序号" header-align="center" width="40">
        <template #default="scope">
          <div>{{ scope.$index + 1 }}</div>
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="8%">
        <template #header>
          <span><span style="color: red">*</span>是否执行</span>
        </template>
        <template #default="scope">
          <el-switch v-model="scope.row.status" :inactive-value="0" :active-value="1" />
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="20%">
        <template #header>
          <span><span style="color: red">*</span>跳过类型</span>
        </template>
        <template #default="scope">
          <el-select
              v-model="scope.row.skip_type"
              placeholder="跳过类型"
              style="width: 100%"
              filterable
              clearable
              default-first-option
              size="small"
              @change="selectValidateType($event, scope.row)"
          >
            <el-option
                v-for="(item) in busEvent.data.skipIfTypeMappingList"
                :key="item.value"
                :label="item.label"
                :value="item.value"
            />
          </el-select>
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="20%">
        <template #header>
          <span><span style="color: red">*</span>数据源</span>
        </template>
        <template #default="scope">
          <el-row>
            <el-select
                v-model="scope.row.data_source"
                placeholder="选择数据源"
                style="width: 100%"
                filterable
                clearable
                default-first-option
                size="small"
            >
              <el-option
                  v-for="(item) in useType === 'step' ? busEvent.data.stepSkipIfDataSourceMapping : busEvent.data.caseSkipIfDataSourceMapping"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
          </el-row>
          <el-row>
            <el-input
                v-model="scope.row.check_value"
                :disabled="['run_device', 'run_server', 'run_env'].indexOf(scope.row.data_source) !== -1"
                type="textarea"
                size="small"
                :rows="1"
                :placeholder="getDataSourcePlaceholder(scope.row.data_source)"
            />
          </el-row>
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="20%">
        <template #header>
          <span><span style="color: red">*</span>判断类型</span>
        </template>
        <template #default="scope">
          <el-select
              v-model="scope.row.comparator"
              placeholder="断言类型"
              style="width: 100%"
              filterable
              clearable
              default-first-option
              size="small"
              @change="selectValidateType($event, scope.row)"
          >
            <el-option
                v-for="(item) in busEvent.data.apiAssertMapping"
                :key="item.value"
                :label="item.value"
                :value="item.value"
            />
          </el-select>
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="20%">
        <template #header>
          <span><span style="color: red">*</span>预期值</span>
        </template>
        <template #default="scope">

          <!-- 预期值为常量 -->
          <div v-show="['run_device', 'run_server', 'run_env'].indexOf(scope.row.data_source) === -1">
            <el-row>
              <el-select
                  v-model="scope.row.data_type"
                  placeholder="选择预期结果数据类型"
                  :disabled="scope.row.comparator === '值为真' || scope.row.comparator === '值为假'"
                  style="width: 100%"
                  filterable
                  clearable
                  default-first-option
                  size="small"
              >
                <el-option
                    v-for="(item) in busEvent.data.dataTypeMapping"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                />
              </el-select>
            </el-row>
            <el-row>
              <el-input
                  v-model="scope.row.expect"
                  size="small"
                  type="textarea"
                  :disabled="scope.row.comparator === '值为真' || scope.row.comparator === '值为假'"
                  :rows="1"
                  :placeholder="
                  scope.row.comparator === '契约校验' ?
                    '详见：https://pypi.org/project/pactverify/，注：契约校验标识符改用@':
                    '预期结果'
                "
              />
            </el-row>
          </div>

          <!-- 预期值为运行环境、原先服务器、运行设备 -->
          <div v-show="['run_device', 'run_server', 'run_env'].indexOf(scope.row.data_source) !== -1">
            <el-select
                v-show="scope.row.data_source === 'run_server'"
                v-model="scope.row.expect"
                placeholder="选择服务器"
                style="width: 100%"
                filterable
                clearable
                default-first-option
                size="small"
            >
              <el-option v-for="(s) in busEvent.data.runServerList" :key="s.id" :label="s.name" :value="s.id" />
            </el-select>
            <el-select
                v-show="scope.row.data_source === 'run_device'"
                v-model="scope.row.expect"
                placeholder="选择设备"
                style="width: 100%"
                filterable
                clearable
                default-first-option
                size="small"
            >
              <el-option v-for="(p) in busEvent.data.runPhoneList" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
            <el-select
                v-show="scope.row.data_source === 'run_env'"
                v-model="scope.row.expect"
                placeholder="选择环境"
                style="width: 100%"
                filterable
                clearable
                default-first-option
                size="small"
            >
              <el-option v-for="(env) in busEvent.data.runEnvList" :key="env.code" :label="env.name" :value="env.code" />
            </el-select>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="操作" header-align="center" width="90">
        <template #default="scope">

          <el-tooltip class="item" effect="dark" placement="top-end" content="添加一行">
            <el-button
                v-show="scope.$index === 0 || scope.$index === tempData.length - 1"
                type="text"
                size="small"
                style="margin: 2px; padding: 0"
                @click.native="addRow(true)"
            ><Plus></Plus></el-button>
          </el-tooltip>

          <el-tooltip class="item" effect="dark" placement="top-end" content="复制当前行">
            <el-button
                type="text"
                size="small"
                style="margin: 2px; padding: 0"
                @click.native="copyRow(scope.row)"
            ><Copy></Copy></el-button>
          </el-tooltip>

          <el-tooltip class="item" effect="dark" placement="top-end" content="删除当前行">
            <el-button
                v-show="isShowDelButton(scope.$index)"
                type="text"
                size="small"
                style="color: red;margin: 2px; padding: 0"
                @click.native="delRow(scope.$index)"
            ><Minus></Minus></el-button>
          </el-tooltip>

          <el-tooltip class="item" effect="dark" placement="top-end" content="清除数据">
            <el-button
                v-show="tempData.length === 1"
                type="text"
                size="small"
                style="color: red;margin: 2px; padding: 0"
                @click.native="clearData()"
            ><Clear></Clear></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, ref, watch} from "vue";
import {GetConfigByCode} from "@/api/config/config-value";
import {busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import {GetRunEnvList} from "@/api/config/run-env";
import {GetServerList} from "@/api/autotest/device-server";
import {GetPhoneList} from "@/api/autotest/device-phone";
import {GetProject} from "@/api/autotest/project";
import {Clear, Copy, Help, Minus, Plus, SortThree} from "@icon-park/vue-next";

const props = defineProps({
  currentData: {
    default: [],
    type: Array,
  },
  projectId: {
    default: '',
    type: Number,
  },
  testType: {
    default: 'api',
    type: String,
  },
  useType: {
    default: '',
    type: String,
  },
})

watch(() => props.currentData, (newValue, oldValue) => {
  initTempData(newValue)
})

watch(() => props.projectId, (newValue, oldValue) => {
  if (newValue){
    GetProject(props.testType, { id: newValue }).then(response => { // 获取服务
      const project = response.data

      GetRunEnvList({ business_id: project.business_id }).then(response => { // 获取服务的业务线对应的运行环境
        busEvent.data.runEnvList = response.data.data
      })
    })
  }
})

const tempData = ref([])
const skipIfDataTableRef = ref(null)
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据

const initTempData = (data: string | any[] | undefined) => {
  if (data && data.length > 0) { // 有数据
    tempData.value = []
    props.currentData.forEach((data, index) => {
      data['id'] = `${Date.now()}_${index}`
      tempData.value.push(JSON.parse(JSON.stringify(data)))
    })
  } else {
    addRow(undefined)
  }
}

const getDataSource = () => {
  getProjectRunEnv()
  if (props.testType === 'app') {
    getRunServerList()
    getRunDeviceList()
  }
}

// 获取服务对应的运行环境
const getProjectRunEnv = () => {
  if (busEvent.data.runEnvList.length < 1 && props.projectId) {
    GetProject(props.testType, { id: props.projectId }).then(response => { // 获取服务
      const project = response.data

      GetRunEnvList({ business_id: project.business_id }).then(response => { // 获取服务的业务线对应的运行环境
        busEvent.data.runEnvList = response.data.data
      })
    })
  }
}

const getRunServerList = () => {
  if (busEvent.data.runServerList.length < 1) {
    GetServerList({ pageNum: 1, pageSize: 9999 }).then(response => {
      busEvent.data.runServerList = response.data.data
    })
  }
}

const getRunDeviceList = () => {
  if (busEvent.data.runPhoneList.length < 1) {
    GetPhoneList({ pageNum: 1, pageSize: 9999 }).then(response => {
      busEvent.data.runPhoneList = response.data.data
    })
  }
}

const getDataSourcePlaceholder = (_type: string) =>{
  if (!_type) {
    return '请选择数据源'
  } else if (_type === 'variable') {
    return '请填写自定义变量表达式'
  } else if (_type === 'func') {
    return '请填写自定义函数表达式'
  } else {
    return ''
  }
}

const selectValidateType = (data: string, row: any) => {
  if (data === '值为真') {
    row.data_type = 'str'
    row.value = 'True'
    return true
  } else if (data === '值为假') {
    row.data_type = 'str'
    row.value = 'False'
    return true
  }
}

const getConfigByCode = () => {
  if (busEvent.data.responseDataSource.length < 1){
    GetConfigByCode({ code: 'extracts_mapping' }).then(response => {
      busEvent.data.responseDataSource = response.data
    })
  }
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    status: 0,
    skip_type: null,
    data_source: null,
    check_value: null,
    comparator: null,
    data_type: null,
    expect: null
  }
}

const addRow = (isRow: undefined | boolean) => {
  if (isRow) {
    tempData.value.push(getNewData())
  } else {
    tempData.value = [getNewData()]
  }
}

const copyRow = (row: {id: string, key: null, value: null, remark: null, data_type: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  tempData.value.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(tempData.value.length === 1 && index === 0)
}

const delRow = (index: number) => {
  tempData.value.splice(index, 1)
}

const clearData = () => {
  tempData.value[0] = getNewData()
}

onMounted(() => {
  getConfigByCode()
  getDataSource()
  initTempData(props.currentData)
})

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
  const updatedData = [...tempData.value];
  // // 移除当前拖拽的行数据
  updatedData.splice(oldIndex.value, 1);
  // // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow.value);
  tempData.value = updatedData;
  // 恢复样式
  event.target.classList.remove('drag-dragging');
};

const getSkipIfData = () => {
  tempData.value.forEach((item: { status: any; skip_type: any; data_source: any; comparator: any; expect: any; }, index: number) => {
    if (item.status){
      if (item.skip_type || item.data_source || item.comparator || item.expect){
        if (!item.skip_type || !item.data_source  || !item.comparator|| !item.expect){
          ElMessage.warning(`跳过条件，第 ${index + 1} 行，请完善数据`)
          throw new Error(`跳过条件，第 ${index + 1} 行，请完善数据: ${JSON.stringify(item)}`);
        }
      }
    }
  })
  return tempData.value
}

defineExpose({
  getSkipIfData
})

</script>

<style scoped>

</style>
