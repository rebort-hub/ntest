<template>
  <div>
    <div v-show="showErrorMsg" style="color: red; margin: 15px">* 语法错误，请检查!</div>
    <div style="float: right">
      <div>
        <el-button
            type="primary"
            size="small"
            :disabled="showErrorMsg"
            style="margin-left:20px;margin-bottom: 10px"
            @click="formatDataToJson()"
        >格式化
        </el-button>
      </div>

      <div>
        <el-button
            type="primary"
            size="small"
            v-show="!showErrorMsg"
            style="margin-left:20px;margin-bottom: 10px"
            @click="clickShowKVInput"
        >填入 k=v 格式
        </el-button>
      </div>

      <div>
        <el-button
            type="primary"
            size="small"
            v-show="!showErrorMsg"
            style="margin-left:20px"
            @click="copyAsKV()"
        >复制为 k=v 格式
        </el-button>
      </div>

    </div>

    <v-ace-editor
        ref="jsonEditorRef"
        v-model:value="tempData"
        lang="json5"
        :theme="aceConfig.theme"
        :options="aceConfig.options"
        :readonly="aceConfig.readOnly"
        :style="{height: tableHeight}"
    />

    <el-drawer v-model="showKVInput" title="输入k=v内容" size="60%">

      <el-input
          v-model="KVString"
          size="small"
          type="textarea"
          :rows="20"
          placeholder="请输入k=v格式的内容"
      />

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="showKVInput = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              @click="SaveKVString"
          >
            {{ '保存' }}
          </el-button>
        </div>
      </template>

    </el-drawer>

  </div>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, reactive, ref, watch} from 'vue'
import {VAceEditor} from "vue3-ace-editor";
import 'ace-builds/src-noconflict/mode-json5';
import 'ace-builds/src-noconflict/theme-chrome';
import {ElMessage} from "element-plus";
import {getFindElementOption} from "@/utils/get-config";
import {bus, busEvent} from "@/utils/bus-events";
import {Help} from "@icon-park/vue-next";
import toClipboard from "@/utils/copy-to-memory";

const aceConfig = reactive({
  theme: 'chrome', //主题
  readOnly: false, //是否只读
  options: {
    enableBasicAutocompletion: true,  // 启动代码补全功能
    enableSnippets: true,  // 启动代码段
    enableLiveAutocompletion: true,  // 启用实时自动完成
    tabSize: 2,
    showPrintMargin: false, // 去除编辑器里的竖线
    fontSize: 16,
    useWorker: true // 使用 web worker 进行语法检查
  }
})
const tempData = ref('{}')
const showErrorMsg = ref(false)
const props = defineProps({
  jsonData: {
    default: '{}',
    type: String
  },
  height:{
    default: undefined,
    type: String
  }
})
const jsonEditorRef = ref(null)
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (props.height === undefined) {
    if (window.innerHeight < 800){  // 小屏
      tableHeight.value = `${window.innerHeight * 0.5}px`
    }else {  // 大屏
      tableHeight.value =  `${window.innerHeight * 0.64}px`
    }
  }else {
    tableHeight.value = props.height
  }
}

const handleResize = () => {
  setTableHeight();
}

const showKVInput = ref(false)
const KVString = ref('')
const SaveKVString = () => {
  if(KVString.value.length > 0){
    const result = {}
    const KVStringParam = KVString.value.split('&')

    KVStringParam.forEach(item => {
      const [key, value] = item.split('=');
      if (key) {
        result[decodeURIComponent(key)] = decodeURIComponent(value); // 解码 URL 编码的值
      }
    })

    tempData.value = JSON.stringify(result)
  }
  showKVInput.value = false
}

const clickShowKVInput = () => {
  KVString.value = ""
  showKVInput.value = true
}

const copyAsKV = async () => {
  const data = getJsonData()
  if (data){
    const kvStr = Object.keys(data)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(data[key])}`)
        .join('&');
    try {
      await toClipboard(kvStr);
      ElMessage.success("已复制到粘贴板")
    } catch (e) {
      console.error(e);
    }
  }else {
    ElMessage.warning("空数据，无需复制")
  }
}


watch(() => props.jsonData, (newValue, oldValue) => {
  tempData.value = JSON.stringify(newValue, null, 4)
})

watch(() => tempData.value, (newValue, oldValue) => {
  if (newValue){
    try {
      JSON.parse(newValue)
      showErrorMsg.value = false
    }catch (e) {
      showErrorMsg.value = true
    }
  }
})

const formatDataToJson = () => {
  tempData.value = JSON.stringify(JSON.parse(tempData.value), null, 4)
}

const getJsonData = () => {
  try {
    return JSON.parse(tempData.value)
  }catch (e) {
    ElMessage.warning('json数据格式错误')
    throw new Error('json数据格式错误')
  }
}

onMounted(() => {
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
})

defineExpose({
  tempData, getJsonData
})

</script>

<style scoped lang="scss">

</style>
