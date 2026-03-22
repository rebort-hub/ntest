<template>
  <div>

    <!-- 使用示例 -->
    <el-collapse accordion>
      <el-collapse-item>
        <template #title>
          <div style="color:red"> 点击查看示例</div>
        </template>

        <div style="margin-left: 20px">
          <div style="margin-left: 20px; margin-bottom: 5px">
            示例数据： {"status": 200, "message": "获取成功", "list": [{"id": 1},{"id": 2}]}
          </div>
          <div style="margin-left: 20px">

            <!-- 断言整数 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>断言整数</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
                <el-input size="small" disabled :placeholder="'status'" style="width: 90%" />
              </el-col>

              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'相等'" style="width: 90%" />
              </el-col>

              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'整数'" style="width: 90%" />
                <el-input size="small" disabled :placeholder="'200'" style="width: 90%" />
              </el-col>
            </el-row>

            <!-- 断言普通字符串 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>断言普通字符串</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
                <el-input size="small" disabled :placeholder="'message'" style="width: 90%" />
              </el-col>

              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'相等'" style="width: 90%" />
              </el-col>

              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'普通字符串'" style="width: 90%" />
                <el-input size="small" disabled :placeholder="'获取成功'" style="width: 90%" />
              </el-col>
            </el-row>

            <!-- 断言自定义变量 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>断言自定义变量</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
                <el-input size="small" disabled :placeholder="'status'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'相等'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'自定义变量'" style="width: 90%" />
                <el-input size="small" disabled :placeholder="'$extract_name_2'" style="width: 90%" />
              </el-col>
            </el-row>

            <!-- 断言自定义函数 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>断言自定义函数</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
                <el-input size="small" disabled :placeholder="'status'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'相等'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'自定义函数'" style="width: 90%" />
                <el-input size="small" disabled :placeholder="'${do_something(status)}'" style="width: 90%" />
              </el-col>
            </el-row>

            <!-- 断言自定义函数+自定义变量 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>断言自定义函数+自定义变量</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
                <el-input size="small" disabled :placeholder="'status'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'相等'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'自定义函数'" style="width: 90%" />
                <el-input
                    size="small"
                    disabled
                    :placeholder="'${do_something($extract_name_2)}'"
                    style="width: 90%"
                />
              </el-col>
            </el-row>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <el-table ref="validateDataTableRef" :data="tempData" stripe size="small" row-key="id">

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
          <div>{{ scope.$index + 1 }}</div>
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="8%">
        <template #header>
          <span><span style="color: red">*</span>是否执行</span>
        </template>
        <template #default="scope">
          <el-switch
              v-model="scope.row.status"
              :inactive-value="0"
              :active-value="1"
          />
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="10%">
        <template #header>
          <span><span style="color: red">*</span>断言类型</span>
        </template>
        <template #default="scope">
          <el-select
              v-model="scope.row.validate_type"
              :disabled="testType === 'api'"
              placeholder="断言类型"
              style="width: 100%"
              size="small"
              @change="selectValidateType($event, scope.row)"
          >
            <el-option
                v-for="(item) in validateTypeList"
                :key="item.value"
                :label="item.label"
                :value="item.value"
            />
          </el-select>
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="30%">
        <template #header>
          <span><span style="color: red">*</span>数据源</span>
        </template>
        <template #default="scope">
          <el-row>
            <el-select
                v-model="scope.row.data_source"
                :placeholder="scope.row.validate_type === 'data' ? '选择数据源' : '选择元素'"
                style="width: 100%"
                filterable
                clearable
                default-first-option
                size="small"
            >
              <div v-show="scope.row.validate_type === 'data'">
                <el-option
                    v-for="(item) in busEvent.data.responseDataSource"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                />
              </div>
              <div v-show="scope.row.validate_type === 'page'">
                <el-option v-for="(item) in elementList" :key="item.id" :label="item.name" :value="item.id.toString()" />
              </div>
            </el-select>
          </el-row>
          <el-row>
            <el-input
                v-model="scope.row.key"
                :disabled="scope.row.validate_type === 'page'"
                type="textarea"
                size="small"
                :rows="1"
                :placeholder="getDataSourcePlaceholder(scope.row)"
            />
          </el-row>
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="25%">
        <template #header>
          <span><span style="color: red">*</span>断言方法</span>
        </template>
        <template #default="scope">
          <el-select
              v-if="scope.row.validate_type === 'data'"
              v-model="scope.row.validate_method"
              placeholder="选择断言方法"
              style="width: 100%"
              filterable
              clearable
              size="small"
              @change="selectValidateMethod($event, scope.row)"
          >
            <el-option
                v-for="(item) in busEvent.data.apiAssertMapping"
                :key="item.value"
                :label="item.value"
                :value="item.value"
            />
          </el-select>
          <el-select
              v-if="scope.row.validate_type !== 'data'"
              v-model="scope.row.validate_method"
              placeholder="选择断言方法"
              style="width: 100%"
              filterable
              clearable
              size="small"
              @change="selectValidateMethod($event, scope.row)"
          >
            <el-option
                v-for="(item) in busEvent.data.uiAssertMapping"
                :key="item.value"
                :label="item.value"
                :value="item.value"
            />
          </el-select>
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="30%">
        <template #header>
          <span><span style="color: red">*</span>预期结果</span>
        </template>
        <template #default="scope">
          <el-row>
            <el-select
                v-model="scope.row.data_type"
                placeholder="选择预期结果数据类型"
                :disabled="disabledAssertType.indexOf(scope.row.validate_method) !== -1"
                style="width: 100%"
                filterable
                clearable
                default-first-option
                size="small"
                @change="selectDataType($event, scope.row)"
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
                v-model="scope.row.value"
                size="small"
                type="textarea"
                :disabled="assertOne.indexOf(scope.row.validate_method) !== -1 || scope.row.disabled"
                :rows="scope.row.value ? 2 : 1"
                :placeholder="
                assertBatch.indexOf(scope.row.validate_method) !== -1 ? `请填写具体字段，如: ['key1', 'key2']` :
                scope.row.validate_method === '契约校验' ?
                  '详见：https://pypi.org/project/pactverify/，注：契约校验标识符改用@':
                  '预期结果'
              "
            />
          </el-row>
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

          <el-tooltip class="item" effect="dark" placement="top-end" content="添加到预置断言">
            <el-button
                type="text"
                size="small"
                style="margin: 2px; padding: 0"
                @click.native="showAddToApiValidator(scope.row)"
            ><Export></Export></el-button>
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

    <el-dialog
        title="添加预置断言 - 设置别名"
        append-to-body
        v-model="showAddValidator"
        :close-on-click-modal="false"
        width="30%"
    >
      <div>
        <el-input label="别名" v-model="addValidatorLabel" size="small" placeholder="断言作用、描述"/>
      </div>

      <template #footer>
      <span class="dialog-footer">
          <el-button size="small" @click="showAddValidator = false"> {{ '取消' }}</el-button>
          <el-button type="primary" size="small" @click.native="addDefaultValidator()">添加</el-button>
      </span>
      </template>

    </el-dialog>

    <el-drawer v-model="showSelectValidator" title="选择预置断言" size="60%">
      <el-table
          ref="validatorTableRef"
          element-loading-text="正在获取数据"
          element-loading-spinner="el-icon-loading"
          :data="defaultValidator"
          key="label"
          stripe
          :height="tableHeight">

        <el-table-column type="selection" width="20" />

        <el-table-column prop="id" label="序号" align="center" min-width="6%">
          <template #default="scope">
            <span>{{ scope.$index + 1 }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="label" label="描述" align="center" min-width="40%">
          <template #default="scope">
            <span>{{ scope.row.label }}</span>
          </template>
        </el-table-column>

        <el-table-column fixed="right" prop="desc" align="center" label="操作" min-width="6%">
          <template #default="scope">
            <el-button type="text" size="small" @click.native="addDefaultValidatorToData(scope.row)">添加</el-button>
          </template>
        </el-table-column>
      </el-table>

    </el-drawer>

  </div>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref, watch} from "vue";
import {Clear, Copy, Help, Minus, Plus, SortThree, Export} from "@icon-park/vue-next";
import {GetConfigByCode, PutConfigApiValidator} from "@/api/config/config-value";
import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";

const props = defineProps({
  currentData: {
    default: [],
    type: Array,
  },
  elementList: {
    default: [],
    type: Array,
  },
  testType: {
    default: 'api',
    type: String,
  },
})

watch(() => props.currentData, (newValue, oldValue) => {
  // console.log('validate.props.currentData: ', newValue)
  // console.log('validate.props.oldValue: ', oldValue)
  initTempData(newValue)
})

const defaultValidator = ref([])
const showSelectValidator = ref(false)
const validatorTableRef = ref()
const tableHeight = ref(`${window.innerHeight * 0.8}px`)

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.8}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.85}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const tempData = ref([])
const validateTypeList =  [{ 'label': '数据', 'value': 'data' }, { 'label': '页面', 'value': 'page' }]
const assertOne = ['值为真', '值为假', '值为null', '值不为null', '值为true', '值不为true', '值为false', '值不为false']
const assertBatch = [
  '批量判断字段值均为真', '批量判断字段值均为假',
  '批量判断字段值均为true', '批量判断字段值均不为true',
  '批量判断字段值均为false', '批量判断字段值均不为false',
  '批量判断字段值均为null', '批量判断字段值均不为null'
]
const disabledAssertType = [
  '值为真', '值为假', '值为null', '值不为null', '值为true', '值不为true', '值为false', '值不为false',
  '批量判断字段值均为真', '批量判断字段值均为假',
  '批量判断字段值均为true', '批量判断字段值均不为true',
  '批量判断字段值均为false', '批量判断字段值均不为false',
  '批量判断字段值均为null', '批量判断字段值均不为null'
]
const validateDataTableRef = ref(null)
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据

const showAddValidator = ref(false);
const addValidatorLabel = ref('');
const currentValidator = ref({});
const showAddToApiValidator = (row: any) => {
  addValidatorLabel.value = '';
  currentValidator.value = row;
  showAddValidator.value = true
}

const addDefaultValidator = () => {
  const data = JSON.parse(JSON.stringify(currentValidator.value));
  delete data.id
  PutConfigApiValidator({label: addValidatorLabel.value, value: currentValidator.value}).then(response => {
    showAddValidator.value = false
  })
}

const addDefaultValidatorToData = (row) => {
  row.value['id'] = `${Date.now()}`
  tempData.value.push(row.value)
}

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

const getDataSourcePlaceholder = (row: { validate_type: string; data_source: string; }) => {
  if (row.validate_type === 'data') {
    if (!row.data_source) {
      return '实际结果提取表达式'
    } else if (row.data_source === 'regexp') {
      return '请填写正确的正则表达式'
    } else if (row.data_source === 'func') {
      return '请填写正确的自定义函数表达式'
    } else if (row.data_source === 'variable') {
      return '请填写正确的自定义变量表达式'
    } else {
      return 'jsonpath表达式，若要提取整个对象，则不填写'
    }
  }
}

const selectValidateType = (data: { validate_type: string; }, row: any) => {
  row.key = null
  row.data_source = null
  row.validate_method = null
}

const selectValidateMethod = (data: string | string[], row: any) => {
  if (['值为真', '值为true'].indexOf(data) !== -1) {
    row.data_type = 'str'
    row.value = 'True'
    return true
  } else if (['值为假', '值为false'].indexOf(data) !== -1) {
    row.data_type = 'str'
    row.value = 'False'
    return true
  } else if (data === '值为null') {
    row.data_type = 'str'
    row.value = 'null'
    return true
  } else if (data === '值不为null') {
    row.data_type = 'str'
    row.value = 'not null'
    return true
  } else if (data === '值不为true') {
    row.data_type = 'str'
    row.value = 'not true'
    return true
  } else if (data === '值不为false') {
    row.data_type = 'str'
    row.value = 'not false'
    return true
  } else if (data.indexOf('批量') !== -1) {
    row.data_type = 'list'
    row.value = '["key1", "key2"]'
    return true
  }
}

const selectDataType = (data: string | string[], row: any) => {
  if (['True', 'False'].indexOf(data) > 0){
    row.value = data
    row.disabled = true
  }else {
    row.disabled = false
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
        validate_type: props.testType === 'api' ? 'data' : 'page',
        data_source:  null,
        key: null,
        validate_method: null,
        data_type: null,
        value: null
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

const getSelectValidator = (message: any) => {
  if (message.eventType === 'showSelectValidator') {
    GetConfigByCode({"code": `${props.testType}_default_validator`}).then(response => {
      defaultValidator.value = response.data
      showSelectValidator.value = true
    })
  }
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
  const updatedData = [...tempData.value];
  // // 移除当前拖拽的行数据
  updatedData.splice(oldIndex.value, 1);
  // // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow.value);
  tempData.value = updatedData;
  // 恢复样式
  event.target.classList.remove('drag-dragging');
};

onMounted(() => {
  getConfigByCode()
  initTempData(undefined)
  bus.on(busEvent.drawerIsShow, getSelectValidator)
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, getSelectValidator)
  window.removeEventListener('resize', handleResize);
})

const getValidates = () => {
  tempData.value.forEach( (item: { status: any; key: any; value: any; validate_method: any; data_source: any; data_type: any; validate_type: any; }, index: any) => {
    if (item.status){
      if (item.data_source || item.validate_method || item.value || item.data_type || (item.validate_type === 'data' && item.key)){
        if (!item.data_source || !item.validate_method|| !item.value || !item.data_type){
          ElMessage.warning(`断言，第 ${index + 1} 行，请完善数据`)
          throw new Error(`断言，第 ${index + 1} 行，请完善数据: ${JSON.stringify(item)}`);
        }
      }
    }
  })
  return tempData.value
}

defineExpose({
  getValidates
})

</script>

<style scoped>

</style>
