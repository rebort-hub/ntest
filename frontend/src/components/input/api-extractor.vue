<template>
  <div>
    <!-- 使用示例 -->
    <el-collapse accordion>
      <el-collapse-item>
        <template #title>
          <div style="color:red"> 点击查看示例</div>
        </template>

        <div style="margin-left: 20px">
          <div style="margin-left: 20px; margin-bottom: 5px;color:red">
            1、此处提取的数据只在运行时有效 <br>
            2、若在此处设置的key与服务/用例设置的公共变量的一致，则会使用此处提取到的值 <br>
            3、若要在此处使用自定义函数，需要注意自定义函数的每一个传参如果是字母且不是要从响应体中提取，则需要以变量的形式传入 <br>
            如： <br>
            响应体为{"code":0, "a": 1} <br>
            提取表达式: ${test(code,b)} => 错误，返回b提取失败 <br>
            先定义或提取变量b，再提取表达式 ${test(code,$b)} => 执行函数逻辑 <br>
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

      <el-table-column header-align="center" min-width="20%">
        <template #header>
          <span><span style="color: red">*</span>变量key</span>
        </template>
        <template #default="scope">
          <el-input v-model="scope.row.key" size="small" type="textarea" :rows="1" :placeholder="placeholderKey" />
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
              <el-option v-for="(item) in busEvent.data.responseDataSource" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-row>
        </template>
      </el-table-column>

      <el-table-column label="提取表达式" header-align="center" min-width="20%">
        <template #default="scope">
          <el-input
              v-model="scope.row.value"
              size="small"
              type="textarea"
              :rows="1"
              :placeholder="getPlaceholder(scope.row.data_source)"
          />
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="10%">
        <template #header>
          <span>更新到头部</span>
          <el-tooltip class="item" effect="dark" placement="top-start">
            <template #content>
              <div>作用：在特殊场景中，直接把提取到的值设置到后续操作中的头部参数中</div>
              <div>1、若打开此开关，则会将此处提取到的值，以当前设置的key更新到后续步骤的头部信息中</div>
              <div>2、若在其他地方已预设头部信息包含当前的key，对于头部信息中的这个key，则会以将此处提取到的值为准</div>
              <div>注：提取后的数据会以key、value的形式存在于自定义变量池中，不管是否选择更新到头部，都可使用</div>
            </template>
            <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </template>
        <template #default="scope">
          <el-switch v-model="scope.row.update_to_header" />
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="20%">
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
import {Help, SortThree} from "@icon-park/vue-next";
import {GetConfigByCode} from "@/api/config/config-value";
import {busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import {Clear, Copy, Minus, Plus} from "@icon-park/vue-next";

const props = defineProps({
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
  dataTypeMappingList: {
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
    key: null,
    data_source: busEvent.data.responseDataSource[0].value,
    value: null,
    remark: null,
    update_to_header: null
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

const getPlaceholder = (_type: string) => {
  if (!_type) {
    return props.placeholderValue
  } else if (_type === 'regexp') {
    return '请填写正确的正则表达式'
  } else {
    return 'jsonpath表达式，若要提取整个对象，则不填写'
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
})

const getExtracts = () => {
  tempData.value.forEach( (item: { status: any; key: any; value: any; remark: any; data_source: any; }, index: any) => {
    if (item.status === 1){
      if (item.key || item.remark || item.data_source){
        if (!item.key || !item.remark || !item.data_source || (['content', 'headers', 'cookies'].indexOf(item.data_source) < 0 && !item.value)){
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
