<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="上传元素" 
        width="50%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="3vh"
        class="upload-element-dialog">

      <div style="padding: 20px 0;">
        <el-row :gutter="20">
          <el-col :span="12">
            <div style="text-align: center; padding: 20px; border: 2px dashed #d9d9d9; border-radius: 6px; background-color: #fafafa;">
              <el-upload
                  class="upload-demo"
                  :action="getUploadDir(testType)"
                  :show-file-list="false"
                  :on-success="uploadFile"
                  drag
              >
                <div style="padding: 20px;">
                  <i class="el-icon-upload" style="font-size: 48px; color: #409eff; margin-bottom: 10px;"></i>
                  <div style="margin-bottom: 10px; font-size: 16px; color: #606266;">将元素文件拖到此处，或</div>
                  <el-button size="small" type="primary">选择文件</el-button>
                </div>
              </el-upload>
            </div>
          </el-col>

          <el-col :span="12">
            <div style="text-align: center; padding: 20px; border: 1px solid #e4e7ed; border-radius: 6px; background-color: #f8f9fa;">
              <div style="margin-bottom: 15px; font-size: 16px; color: #606266;">📥 下载导入模板</div>
              <div style="margin-bottom: 15px; font-size: 14px; color: #909399;">请按照模板格式填写元素信息</div>
              <el-button size="small" type="success" @click="downloadTemplate">
                <i class="el-icon-download" style="margin-right: 5px;"></i>
                下载模板
              </el-button>
            </div>
          </el-col>
        </el-row>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false">关闭</el-button>
        </div>
      </template>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {DownloadElementTemplate, getUploadDir, UploadElement} from "@/api/autotest/element";

const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'upload-element') {
    pageId.value = message.content
    drawerIsShow.value = true
  }
}

const uploadFile = (response: any, file: { raw: string | Blob; }) =>{
  const form = new FormData()
  form.append('file', file.raw)
  form.append('page_id', pageId.value)
  UploadElement(props.testType, form).then((response) => {
        if (response) {
          bus.emit(busEvent.drawerIsCommit, {eventType: 'element-upload-success'});
          drawerIsShow.value = false
        }
      }
  )
}

const downloadTemplate = () => {
  DownloadElementTemplate(props.testType).then(response => {
    const blob = new Blob([response], {
      type: 'application/vnd.ms-excel' // 将会被放入到blob中的数组内容的MIME类型
    })
    // 保存文件到本地
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob) // 生成一个url
    a.download = '元素导入模板'
    a.click()
  })
}

const drawerIsShow = ref(false)
const pageId = ref()
const submitButtonIsLoading = ref(false)

</script>


<style scoped lang="scss">
// 上传元素弹窗样式
:deep(.upload-element-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 94vh;
    margin-top: 3vh !important;
    margin-bottom: 3vh;
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
    overflow: auto;
  }
  
  .el-dialog__footer {
    border-top: 1px solid #ebeef5;
    padding: 15px 20px;
    flex-shrink: 0;
  }
}

.dialog-footer {
  text-align: right;
  
  .el-button {
    margin-left: 10px;
  }
}

// 上传区域样式优化
:deep(.el-upload) {
  width: 100%;
  
  .el-upload-dragger {
    width: 100%;
    border: 2px dashed #d9d9d9;
    border-radius: 6px;
    background-color: #fafafa;
    transition: all 0.3s ease;
    
    &:hover {
      border-color: #409eff;
      background-color: #f0f9ff;
    }
  }
}

// 图标样式
.el-icon-upload {
  font-size: 48px !important;
  color: #409eff !important;
  margin-bottom: 10px !important;
}

.el-icon-download {
  font-size: 14px !important;
  margin-right: 5px !important;
}

// 按钮样式优化
:deep(.el-button) {
  &.el-button--primary {
    background-color: #409eff;
    border-color: #409eff;
    
    &:hover {
      background-color: #66b1ff;
      border-color: #66b1ff;
    }
  }
  
  &.el-button--success {
    background-color: #67c23a;
    border-color: #67c23a;
    
    &:hover {
      background-color: #85ce61;
      border-color: #85ce61;
    }
  }
}

// 卡片样式优化
.el-col {
  .el-upload,
  > div {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 150px;
  }
}

// 响应式适配
@media (max-width: 1200px) {
  :deep(.upload-element-dialog) {
    .el-dialog {
      width: 70% !important;
      margin: 2vh auto !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.upload-element-dialog) {
    .el-dialog {
      width: 100% !important;
      margin: 0 !important;
      height: 100vh;
      border-radius: 0;
    }
    
    .el-dialog__body {
      padding: 15px;
    }
  }
  
  // 移动端布局调整
  .el-row {
    .el-col {
      margin-bottom: 15px !important;
    }
  }
  
  // 移动端上传区域
  :deep(.el-upload-dragger) {
    padding: 15px !important;
    
    .el-icon-upload {
      font-size: 36px !important;
    }
  }
}
</style>
