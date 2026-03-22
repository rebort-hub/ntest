<!--  -->
<template>
  <div class='content'>
    <el-select v-model="aceConfig.theme" class="m-2" placeholder="Select" size="large">
      <el-option v-for="item in aceConfig.arr" :key="item" :label="item" :value="item"/>
    </el-select>
    <el-button @click="jsonFormat">格式化</el-button>
    <el-button @click="jsonNoFormat">压缩</el-button>
    <v-ace-editor
        v-model:value="dataForm.textareashow"
        @init="jsonFormat"
        lang="python"
        :theme="aceConfig.theme"
        :options="aceConfig.options"
        :readonly="aceConfig.readOnly"
        style="height:300px"
        class="ace-editor"
    />
  </div>
</template>

<script setup>
import {reactive} from 'vue'
import {VAceEditor} from 'vue3-ace-editor';
// 加了这个【import "ace-builds/webpack-resolver";】可能会报错
//（若报错 则需要安装node.js的一个包 就是主题）
// 命令：npm install --save-dev file-loader
import "ace-builds/webpack-resolver";
// import 'ace-builds/src-noconflict/mode-json';
import 'ace-builds/src-noconflict/mode-python';
// import 'ace-builds/src-noconflict/theme-chrome';
import 'ace-builds/src-noconflict/theme-tomorrow_night_blue';
import 'ace-builds/src-noconflict/ext-language_tools';

//ace编辑器配置
const aceConfig = reactive({
  theme: 'tomorrow_night_blue', //主题
  arr: [
    /*所有主题*/

    "sqlserver",  // json
    "terminal",  // json
    "textmate",  // json
    "tomorrow_night",  // 通用
    "tomorrow_night_blue",  // 通用
    "tomorrow_night_bright",  // 通用
    "tomorrow_night_eighties",  // 通用
    "twilight", // json
    "chaos",  // python
    "cobalt",  // python
    "crimson_editor",  // json
    "dracula",  // python
    "dreamweaver",  // json
    "merbivore",  // python
    "monokai",  // 通用

    // 不好看
    "mono_industrial",  // 不好看
    "pastel_on_dark",  // --
    "solarized_dark",  // --
    "solarized_light",  // --
    "tomorrow",  // --
    "vibrant_ink",  // --
    "xcode",  // --
    "ambiance",  // --
    "chrome",  // --
    "clouds", // --
    "clouds_midnight", // --
    "dawn", // --
    "eclipse", // --
    "github", // --
    "gob", // --
    "gruvbox", // --
    "idle_fingers", // --
    "iplastic", // --
    "katzenmilch", // --
    "kr_theme", // --
    "kuroir", // --
    "merbivore_soft", // --
  ],
  readOnly: false, //是否只读
  options: {
    enableBasicAutocompletion: true,  // 启动代码补全功能
    enableSnippets: true,  // 启动代码段
    enableLiveAutocompletion: true,  // 启用实时自动完成
    tabSize: 2,
    showPrintMargin: false, // 去除编辑器里的竖线
    fontSize: 16
  }
});

//form
const dataForm = reactive({
  textareashow: '{"A":"A1", "b": 2, "c": [1,2,3], "d":{"a": 1}}\n\n\nclass A:\n\n   def add(a, b):\n    return a + b\n\na = A()'
});

const jsonError = (e) => {
  console.log(`JSON字符串错误：${e.message}`);
}

// JSON格式化
const jsonFormat = () => {
  try {
    dataForm.textareashow = JSON.stringify(JSON.parse(dataForm.textareashow), null, 2)
  } catch (e) {
    jsonError(e)
  }
};

// JSON压缩
const jsonNoFormat = () => {
  try {
    dataForm.textareashow = JSON.stringify(JSON.parse(dataForm.textareashow))
  } catch (e) {
    jsonError(e)
  }
}
</script>


<style scoped>

</style>
