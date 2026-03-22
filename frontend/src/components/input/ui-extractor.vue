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
            1、此处提取的数据只在运行时有效 <br>
            2、若在此处设置的key与服务/用例设置的公共变量的一致，则会使用此处提取到的值
          </div>
          <div style="margin-left: 20px; margin-bottom: 5px">
            示例数据： {"status": 200, "data_list": [{"id": 1},{"id": 2}]}
          </div>
          <div style="margin-left: 20px">

            <!-- 提取整个响应对象 -->
            <el-row>
              <el-col :span="5">
                <div>提取整个响应对象</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_1'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="''" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 提取json中的status -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>提取json中的status</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_2'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'status'" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 提取json中的data_list -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>提取json中的data_list</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_2'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'data_list'" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 提取list中的第一个值的id -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>提取list中的第一个值的id</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_3'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'响应cookies'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'data_list.0.id'" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 提取list中的第二个值的id -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>提取list中的第二个值的id</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_4'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'data_list.1.id'" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 提取list中的最后一个值的id -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>提取list中的最后一个值的id</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_5'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'data_list.-1.id'" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 提取list中的倒数第二个值的id -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>提取list中的倒数第二个值的id</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_6'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'data_list.-2.id'" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 正则表达式提取 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>正则表达式提取</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_7'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'正则表达式（从响应体提取）'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'[{(.+?)},{'" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 自定义函数 不传参提取 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>自定义函数 不传参提取</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_8'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'${do_something()}'" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 自定义函数+提取表达式 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>自定义函数+提取表达式</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_9'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'${do_something(status)}'" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 自定义函数+自定义变量 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>自定义函数+自定义变量</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_10'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'响应体'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input
                    size="small"
                    disabled
                    :placeholder="'${do_something($extract_name_8, a=status)}'"
                    style="width: 95%"
                />
              </el-col>
            </el-row>

            <!-- 常量 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>常量</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_11'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'常量'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'123'" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 自定义变量二次提取 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>自定义变量二次提取</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_12'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'自定义变量'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled placeholder="$extract_name_2.1.id" style="width: 95%" />
              </el-col>
            </el-row>

            <!-- 自定义变量二次提取 -->
            <el-row style="margin-top: 5px">
              <el-col :span="5">
                <div>自定义变量二次赋值</div>
              </el-col>
              <el-col :span="5">
                <el-input size="small" disabled :placeholder="'extract_name_12'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled :placeholder="'自定义变量'" style="width: 90%" />
              </el-col>
              <el-col :span="7">
                <el-input size="small" disabled placeholder="$extract_name_2" style="width: 95%" />
              </el-col>
            </el-row>

          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <el-table
        ref="extractDataTableRef"
        :data="tempData"
        stripe
        size="small"
        row-key="id">

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

      <el-table-column header-align="center" min-width="7%">
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

      <el-table-column header-align="center" min-width="23%">
        <template #header>
          <span><span style="color: red">*</span>变量key</span>
        </template>
        <template #default="scope">
          <el-input v-model="scope.row.key" size="small" type="textarea" :rows="1" :placeholder="placeholderKey" />
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="23%">
        <template #header>
          <span><span style="color: red">*</span>提取方式</span>
        </template>
        <template #default="scope">
          <el-row>
            <el-select
                v-model="scope.row.extract_type"
                placeholder="选择提取方式"
                style="width: 100%"
                filterable
                clearable
                default-first-option
                size="small"
            >
              <el-option
                  v-for="(item) in busEvent.data.uiExtractMappingList"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
          </el-row>
        </template>
      </el-table-column>

      <el-table-column label="元素/表达式" header-align="center" min-width="23%">
        <template #default="scope">
          <!-- 选择自定义函数，则输入自定义函数 -->
          <el-input
              v-if="['const', 'func', 'variable'].indexOf(scope.row.extract_type) !== -1"
              v-model="scope.row.value"
              size="small"
              type="textarea"
              :rows="1"
              :placeholder="`请填写正确的自定义${
              scope.row.extract_type === 'func' ? '函数表达式'
              : scope.row.extract_type === 'variable' ? '变量表达式'
                : '常量'}`"
          />

          <!-- 选择页面元素提取，则选择具体元素 -->
          <el-select
              v-else
              v-model="scope.row.value"
              :disabled="scope.row.extract_type && (scope.row.extract_type.indexOf('cookie') !== -1 ||
              scope.row.extract_type.indexOf('session_storage') !== -1 ||
              scope.row.extract_type.indexOf('local_storage') !== -1 ||
              scope.row.extract_type.indexOf('title') !== -1)"
              placeholder="选择元素"
              style="width: 100%"
              filterable
              clearable
              default-first-option
              size="small"
          >
            <el-option v-for="(item) in elementList" :key="item.id" :label="item.name" :value="item.id.toString()" />
          </el-select>
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="21%">
        <template #header>
          <span><span style="color: red">*</span>备注</span>
        </template>
        <template #default="scope">
          <el-input v-model="scope.row.remark" size="small" type="textarea" :rows="1" :placeholder="placeholderDesc" />
        </template>
      </el-table-column>

      <el-table-column v-if="!isDisabledCol" label="操作" header-align="center" width="90">
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
import {busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import {GetExtractMappingList} from "@/api/autotest/step";
import {Clear, Copy, Help, Minus, Plus, SortThree} from "@icon-park/vue-next";

const props = defineProps({
  testType: {
    default: 'ui',
    type: String,
  },
  currentData: {
    default: [],
    type: Array,
  },
  placeholderKey: {
    default: '',
    type: String,
  },
  placeholderValue: {
    default: '',
    type: String,
  },
  placeholderDesc: {
    default: '',
    type: String,
  },
  elementList: {
    default: [],
    type: Array,
  },
  isDisabledCol: {
    default: false,
    type: Boolean,
  },
})

watch(() => props.currentData, (newValue, oldValue) => {
  initTempData(newValue)
})

const tempData = ref([])
const extractDataTableRef = ref(null)
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const newList = ref([])

const initTempData = (data: string | any[] | undefined) => {
  if (data && data.length > 0) { // 有数据
    tempData.value = []
    props.currentData.forEach((data, index) => {
      data['id'] = `${Date.now()}_${index}`
      data['data_source'] = 'page'
      tempData.value.push(JSON.parse(JSON.stringify(data)))
    })
  } else {
    addRow(undefined)
  }
}

const getExtractMappingList= () => {
  if (busEvent.data.uiExtractMappingList.length < 1){
    GetExtractMappingList(props.testType).then(response => {
      busEvent.data.uiExtractMappingList = response.data
    })
  }
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    data_source: 'page',
    status: 0,
    key: null,
    extract_type: null,
    value: null,
    remark: null
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
  getExtractMappingList()
  initTempData(undefined)
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

const needSelectElement = (extractType: string | any[]) => {
  const res = extractType.indexOf('title') !== -1
      || extractType.indexOf('cookie') !== -1
      || extractType.indexOf('local_storage') !== -1
      || extractType.indexOf('session_storage') !== -1
  return !res
}

const getExtracts = () => {
  tempData.value.forEach( (item: { status: any; key: any; value: any; remark: any; extract_type: any; }, index: any) => {
    if (item.status === 1){
      if (item.key || item.extract_type || item.value || item.remark){
        if (!item.key || !item.remark || !item.extract_type || (needSelectElement(item.extract_type) && !item.value)){
          ElMessage.warning(`数据提取，第 ${index + 1} 行，请完善数据`)
          throw new Error(`数据提取，第 ${index + 1} 行，请完善数据: ${JSON.stringify(item)}`);
        }
      }
    }
  })
  return tempData.value
}

defineExpose({
  getExtracts
})

</script>

<style scoped>

</style>
