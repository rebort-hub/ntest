<template>
  <div>
    <h3>Ace Editor 测试</h3>
    <div style="height: 300px; border: 1px solid #ccc;">
      <VAceEditor
        v-model:value="code"
        lang="python"
        theme="monokai"
        :options="{
          enableBasicAutocompletion: true,
          enableSnippets: true,
          enableLiveAutocompletion: true,
          fontSize: 14
        }"
        style="height: 100%; width: 100%;"
      />
    </div>
    <p>当前代码: {{ code }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { VAceEditor } from 'vue3-ace-editor'
import 'ace-builds/src-noconflict/mode-python'
import 'ace-builds/src-noconflict/theme-monokai'
import 'ace-builds/src-noconflict/ext-language_tools'

const code = ref(`print("Hello World")
def test_function():
    return "This is a test"`)
</script>
</script>