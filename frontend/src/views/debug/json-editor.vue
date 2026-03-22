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
        lang="json"
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
import 'ace-builds/src-noconflict/mode-json';
import 'ace-builds/src-noconflict/theme-monokai';
import 'ace-builds/src-noconflict/ext-language_tools';

//ace编辑器配置
const aceConfig = reactive({
  lang: 'json', //解析json
  theme: 'monokai', //主题
  arr: [
    /*所有主题*/
    "ambiance",
    "chaos",
    "chrome",
    "clouds",
    "clouds_midnight",
    "cobalt",
    "crimson_editor",
    "dawn",
    "dracula",
    "dreamweaver",
    "eclipse",
    "github",
    "gob",
    "gruvbox",
    "idle_fingers",
    "iplastic",
    "katzenmilch",
    "kr_theme",
    "kuroir",
    "merbivore",
    "merbivore_soft",
    "monokai",
    "mono_industrial",
    "pastel_on_dark",
    "solarized_dark",
    "solarized_light",
    "sqlserver",
    "terminal",
    "textmate",
    "tomorrow",
    "tomorrow_night",
    "tomorrow_night_blue",
    "tomorrow_night_bright",
    "tomorrow_night_eighties",
    "twilight",
    "vibrant_ink",
    "xcode",
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
  textareashow: '{"A":"A1"}'
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
