<template>
  <div>
    <VAceEditor
        ref="editorRef"
        v-model:value="tempData"
        lang="python"
        :theme="aceConfig.theme"
        :options="aceConfig.options"
        :readonly="aceConfig.readOnly"
        :style="{height: tableHeight}"
        @init="initEditor"
    />
  </div>
</template>

<script setup lang="ts">
import {reactive, ref, watch, onMounted, onBeforeUnmount, computed} from 'vue'
import {VAceEditor} from "vue3-ace-editor";
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/theme-monokai';
import 'ace-builds/src-noconflict/ext-language_tools';

import ace from 'ace-builds';
import modeUrl from 'ace-builds/src-noconflict/mode-python?url';
ace.config.setModuleUrl('ace/mode/python', modeUrl);

import themeUrl from 'ace-builds/src-noconflict/theme-monokai?url';
ace.config.setModuleUrl('ace/theme/monokai', themeUrl);

import {bus, busEvent} from "@/utils/bus-events";

const initEditor = (editor: any) => {
  // 保存编辑器引用
  editorInstance.value = editor;
  // 设置编辑器的一些初始选项，例如语言、主题等
  // 可选：在这里添加编辑器的其他配置
};

const aceConfig = reactive({
  theme: 'monokai', //主题
  readOnly: false, //是否只读
  options: {
    enableBasicAutocompletion: true,  // 启动代码补全功能
    enableSnippets: true,  // 启动代码段
    enableLiveAutocompletion: true,  // 启用实时自动完成
    tabSize: 2,
    showPrintMargin: false, // 去除编辑器里的竖线
    fontSize: 16
  }
})
const editorRef = ref()
const editorInstance = ref()

// 先定义props
const props = defineProps({
  pythonCode: {
    default: '',
    type: String
  }
})

// 然后使用props初始化tempData
const tempData = ref(props.pythonCode || '')
const tableHeight = ref('450px') // 设置合适的初始高度

const setTableHeight = () => {
  // 计算可用高度，充分利用容器空间
  const availableHeight = window.innerHeight - 300 // 减去页面头部、导航等固定高度
  const minHeight = 400
  const maxHeight = 800
  
  const calculatedHeight = Math.max(minHeight, Math.min(maxHeight, availableHeight))
  tableHeight.value = `${calculatedHeight}px`
}

const handleResize = () => {
  setTableHeight();
}

watch(() => props.pythonCode, (newValue, oldValue) => {
  tempData.value = newValue
})

onMounted(() => {
  // 初始化时设置初始值
  tempData.value = props.pythonCode
  bus.on(busEvent.drawerIsShow, findAndSelectText);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, findAndSelectText);
  window.removeEventListener('resize', handleResize);
})

const findAndSelectText = (message: any) => {
  if (message.eventType === 'find-code') {
    editorInstance.value.find(message.content, {
      // 查找选项
      backwards: false,
      wrap: true,
      caseSensitive: false,
      wholeWord: false,
      regExp: false,
    })
  }
}

defineExpose({
  tempData
})

</script>

<style scoped lang="scss">

</style>
