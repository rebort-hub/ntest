<template>
  <div>
    <div style="text-align: center; margin-bottom: 5px">
      <el-radio v-model="tempBodyType" label="form">form-data</el-radio>
      <el-radio v-model="tempBodyType" label="urlencoded">form-urlencoded</el-radio>
      <el-radio v-model="tempBodyType" label="json">json</el-radio>
      <el-radio v-model="tempBodyType" label="text">xml / 文本</el-radio>
    </div>

    <div v-show="tempBodyType === 'form'">
      <dataFormView ref="dataFormViewRef" :current-data="tempDataForm" :is-show-data-type="true" :use-from="'data-form'"/>
    </div>

    <div v-show="tempBodyType === 'urlencoded'">
      <el-collapse accordion size="smail">
        <el-collapse-item>
          <template #title>
            <div style="color:red"> 点击查看示例</div>
          </template>
          <div style="margin-left: 20px">
            可以使用自定义函数，也可以使用自定义变量
            <pre>
  {
    "key1": "123",
    "key2": "$extract_name_2",  // 自定义变量（提取的变量）
    "key3": "some_data$extract_name_2",  // 字符串+自定义变量拼接
    "key4": "${do_something()}",  // 自定义函数
    "key5": "${do_something(1, b=2)}",  // 带参数的自定义函数
    "key6": "${do_something($extract_name_1)}",  // 自定义函数传自定义变量为参数
    "key7": "${do_something($extract_name_1, b=$extract_name_2)}",  // 自定义函数指定位置传参
    "key8": "some_data${do_something($extract_name_1, b=$extract_name_2)}",  // 字符串+自定义函数拼接
    "key9": "${do_something($extract_name_1, b=$extract_name_2)}some_data"   // 字符串+自定义函数拼接
  }
  <span style="margin-top: 5px"><span style="color: red">注</span>：不支持 自定义变量+字符串的拼接，如：$extract_name_2some_data</span>
              </pre>
          </div>
        </el-collapse-item>
      </el-collapse>
      <jsonEditorView ref="urlencodedEditorViewRef" :json-data="dataUrlencoded" />
    </div>

    <div v-show="tempBodyType === 'json'">
      <el-collapse accordion>
        <el-collapse-item>
          <template #title>
            <div style="color:red"> 点击查看示例</div>
          </template>
          <div style="margin-left: 20px">
            可以使用自定义函数，也可以使用自定义变量
            <pre>
  {
    "key1": "123",
    "key2": "$extract_name_2",  // 自定义变量（提取的变量）
    "key3": "some_data$extract_name_2",  // 字符串+自定义变量拼接
    "key4": "${do_something()}",  // 自定义函数
    "key5": "${do_something(1, b=2)}",  // 带参数的自定义函数
    "key6": "${do_something($extract_name_1)}",  // 自定义函数传自定义变量为参数
    "key7": "${do_something($extract_name_1, b=$extract_name_2)}",  // 自定义函数指定位置传参
    "key8": "some_data${do_something($extract_name_1, b=$extract_name_2)}",  // 字符串+自定义函数拼接
    "key9": "${do_something($extract_name_1, b=$extract_name_2)}some_data"   // 字符串+自定义函数拼接
  }
  <span style="margin-top: 5px"><span style="color: red">注</span>：不支持 自定义变量+字符串的拼接，如：$extract_name_2some_data</span>
              </pre>
          </div>
        </el-collapse-item>
      </el-collapse>
      <jsonEditorView ref="jsonEditorViewRef" :json-data="dataJson" />
    </div>

    <div v-show="tempBodyType === 'text'">
      <el-input v-model="tempDataText" type="textarea" :rows="17" placeholder="请输入内容" />
    </div>

  </div>
</template>

<script lang="ts" setup>
import {ref, watch} from "vue";
import jsonEditorView from '@/components/editor/json-editor.vue'
import dataFormView from '@/components/input/key-value-row.vue'
import {ElMessage} from "element-plus";

const props = defineProps({
  bodyType: {
    default: [],
    type: Array,
  },
  dataJson: {
    default: {},
    type: Object,
  },
  dataForm: {
    default: [],
    type: Array,
  },
  dataText: {
    default: '',
    type: String,
  },
  dataUrlencoded: {
    default: '',
    type: String,
  },
})

const tempBodyType = ref('json')
const tempDataJson = ref({})
const tempDataForm = ref([])
const tempDataUrlencoded = ref({})
const tempDataText = ref(null)

const dataFormViewRef = ref(null)
const jsonEditorViewRef = ref(null)
const urlencodedEditorViewRef = ref(null)

watch(() => props.bodyType, (newValue, oldValue) => {
  tempBodyType.value = newValue || 'json'
})

watch(() => props.dataJson, (newValue, oldValue) => {
  tempDataJson.value = JSON.stringify(newValue) || JSON.stringify({})
})

watch(() => props.dataForm, (newValue, oldValue) => {
  tempDataForm.value = newValue
})

watch(() => props.dataText, (newValue, oldValue) => {
  tempDataText.value = newValue
})

watch(() => props.dataUrlencoded, (newValue, oldValue) => {
  tempDataUrlencoded.value = JSON.stringify(newValue) || JSON.stringify({})
})

const getDataJson = () => {
  try {
    return JSON.parse(jsonEditorViewRef.value.tempData)
  }catch (e) {
    ElMessage.warning('json参数数据格式错误')
    throw new Error('json参数数据格式错误');
  }
}

const getDataForm = () => {
  let dataForm = dataFormViewRef.value.tempData
  dataForm.forEach( (item: { key: any; value: any; data_type: any; remark: any; }, index: any) => {
    if (item.key || item.value || item.data_type || item.remark){
      if (!item.key || !item.value || !item.data_type || !item.remark){
        ElMessage.warning(`form参数，第 ${index + 1} 行，请完善数据`)
        throw new Error(`form参数，第 ${index + 1} 行，请完善数据: ${JSON.stringify(item)}`);
      }
    }
  })
  return dataForm
}

const getUrlencoded = () => {
  let data = urlencodedEditorViewRef.value.tempData
  try {
    return JSON.parse(data)
  }catch (e) {
    ElMessage.warning('urlencoded参数数据格式错误')
    throw new Error('urlencoded参数数据格式错误');
  }
}

defineExpose({
  tempBodyType, getDataJson, getDataForm, getUrlencoded, tempDataText
})

</script>

<style scoped>

</style>
