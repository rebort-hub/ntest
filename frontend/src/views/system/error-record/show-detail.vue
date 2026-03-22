<template>
  <div>
    <el-dialog 
      v-model="drawerIsShow" 
      title="错误详情" 
      width="900px"
      :close-on-click-modal="false"
      destroy-on-close
      top="5vh"
      class="error-record-dialog"
    >
      <div class="error-record-content">
        <el-form label-width="100px" size="small">
          <el-form-item label="请求方法">
            <el-input
                v-model="detailData.url"
                disabled
            >
              <template #prepend>{{ detailData.method }}</template>
            </el-input>
          </el-form-item>

          <el-form-item label="头部信息">
            <showJson :json-data="detailData.headers"/>
          </el-form-item>

          <el-form-item label="URL参数">
            <showJson :json-data="detailData.params"/>
          </el-form-item>

          <el-form-item label="Form参数">
            <showJson :json-data="detailData.data_form"/>
          </el-form-item>

          <el-form-item label="JSON参数">
            <showJson :json-data="detailData.data_json"/>
          </el-form-item>

          <el-form-item label="错误详情">
            <pre class="error-detail-pre">{{ detailData.detail }}</pre>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
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
:deep(.error-record-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 90vh;
    margin-top: 5vh !important;
    display: flex;
    flex-direction: column;
  }
  
  .el-dialog__header {
    border-bottom: 1px solid #ebeef5;
    padding: 20px 20px 15px;
    flex-shrink: 0;
  }
  
  .el-dialog__body {
    padding: 20px;
    flex: 1;
    overflow-y: auto;
    max-height: calc(90vh - 100px);
    
    &::-webkit-scrollbar {
      width: 8px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 4px;
      
      &:hover {
        background: #a8a8a8;
      }
    }
  }
}

.error-record-content {
  .error-detail-pre {
    background: #f5f7fa;
    padding: 16px;
    border-radius: 4px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #303133;
    overflow: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 400px;
  }
}
</style>
