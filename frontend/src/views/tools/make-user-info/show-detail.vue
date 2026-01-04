<template>
  <div>
      <el-drawer title="错误详情" size="70%" v-model="drawerIsShow">
        <div style="margin: 10px">
          <div>
            <label class="label-style">请求方法：</label>
            <el-input :value="detailData.method" size="small" disabled />
          </div>

          <div style="margin-top: 20px">
            <label class="label-style">接口地址：</label>
            <el-input :value="detailData.url" size="small" disabled />
          </div>

          <div style="margin-top: 20px">
            <label class="label-style">头部信息：</label>
            <showJson :json-data="detailData.headers"/>
          </div>

          <div style="margin-top: 20px">
            <label class="label-style">url参数：</label>
            <showJson :json-data="detailData.params"/>
          </div>

          <div style="margin-top: 20px">
            <label class="label-style">form参数：</label>
            <showJson :json-data="detailData.data_form"/>
          </div>

          <div style="margin-top: 20px">
            <label class="label-style">json参数：</label>
            <showJson :json-data="detailData.data_json"/>
          </div>

          <div style="margin-top: 30px">
            <label class="label-style">错误详情：</label>
            <pre class="el-collapse-item-content" style="overflow: auto">{{ detailData.detail }}</pre>
          </div>
        </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount} from "vue";

import {bus, busEvent} from "@/utils/bus-events";
import showJson from '@/components/show-json.vue'
import {GetErrorRecord} from "@/api/system/error-record";

const drawerIsShow = ref(false)
const detailData = ref({
  method: '', url: '', detail: '', headers: {}, params: {}, data_form: {}, data_json: {},
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const getDetailData = (dataId: number) => {
  GetErrorRecord({id: dataId}).then(response => {
    detailData.value = response.data
  })
}

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'error-record') {
    getDetailData(message.content.id)
    drawerIsShow.value = true
  }
}



</script>

<style scoped lang="scss">

</style>
