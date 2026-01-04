<template>
  <div>
    <JsonViewer
        :value="props.jsonData"
        :expand-depth=5
        :copyable="{copyText: '复制', copiedText: '复制成功'}"
        :show-array-index="false"
        :show-double-quotes="true"
        boxed
    />

  </div>
</template>

<script setup lang="ts">
import {JsonViewer} from "vue3-json-viewer"

const props = defineProps({
  jsonData: {
    default: {},
    type: Object
  }
})

</script>

<style scoped lang="scss">

</style>
