<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="上传用例集文件" 
        width="70%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="3vh"
        class="upload-case-suite-dialog">

      <div
          v-loading.fullscreen.lock="drawerIsLoading"
          element-loading-text="正在处理中"
          element-loading-spinner="el-icon-loading"
      />

      <div style="margin: 0">
        <div style="margin-bottom: 20px; padding: 15px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px;">
          <div style="margin-bottom: 8px;"><strong>📋 导入说明：</strong></div>
          <div style="margin-bottom: 8px;">1、<span style="color: red; font-size: 16px; font-weight: bold;">只支持XMind8版本</span> 
            <a href="https://xmind.cn/download/xmind8/" target="_blank" style="color: #3a8ee6; text-decoration: underline;">点击下载XMind8</a>
          </div>
          <div style="margin-bottom: 8px;">2、必须<span style="color: red; font-weight: bold;">按照模板填写内容</span>，请先下载模板参考格式</div>
          <div>3、导入后，<span style="color: red; font-weight: bold;">默认类型为流程用例集</span>，若要修改为其他类型，<span style="color: red; font-weight: bold;">只需修改一级用例集即可</span>，子用例集会跟随修改</div>
        </div>

        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="12">
            <div style="text-align: center; padding: 20px; border: 2px dashed #d9d9d9; border-radius: 6px; background-color: #fafafa;">
              <el-upload
                  class="upload-demo"
                  :action="getUploadDir(testType)"
                  :headers="uploadHeaders"
                  :show-file-list="false"
                  :on-success="uploadFile"
                  drag
              >
                <div style="padding: 20px;">
                  <i class="el-icon-upload" style="font-size: 48px; color: #409eff; margin-bottom: 10px;"></i>
                  <div style="margin-bottom: 10px; font-size: 16px; color: #606266;">将 XMind 文件拖到此处，或</div>
                  <el-button type="primary" size="default">选择 XMind 文件</el-button>
                </div>
              </el-upload>
            </div>
          </el-col>

          <el-col :span="12">
            <div style="text-align: center; padding: 20px; border: 1px solid #e4e7ed; border-radius: 6px; background-color: #f8f9fa;">
              <div style="margin-bottom: 15px; font-size: 16px; color: #606266;">📥 下载导入模板</div>
              <div style="margin-bottom: 15px; font-size: 14px; color: #909399;">请按照模板格式填写用例集内容</div>
              <el-button type="success" size="default" @click="downloadTemplate">
                <i class="el-icon-download" style="margin-right: 5px;"></i>
                下载模板文件
              </el-button>
            </div>
          </el-col>
        </el-row>

        <!-- 示例图片 -->
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="margin-bottom: 10px; font-size: 16px; color: #606266; font-weight: bold;">📖 模板示例</div>
          <el-image 
              src="/images/uploadCase.jpg" 
              style="max-width: 100%; border: 1px solid #e4e7ed; border-radius: 6px;"
              :preview-src-list="['/images/uploadCase.jpg']"
              fit="contain"
          />
        </div>

        <div v-if="uploadFailTotal > 0" style="margin-top: 20px; padding: 15px; background-color: #fef0f0; border: 1px solid #fde2e2; border-radius: 6px;">
          <div style="margin-bottom: 10px; color: #f56c6c; font-weight: bold;">
            ❌ 导入失败：共 {{ uploadFailTotal }} 条记录导入失败
          </div>
          <div style="color: #909399; font-size: 14px;">
            失败详情：{{ uploadFailList }}
          </div>
        </div>
      </div>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {DownloadSuiteTemplate, UploadCaseSuite} from "@/api/autotest/case-suite";
import {bus, busEvent} from "@/utils/bus-events";
import {getUploadDir} from "@/api/autotest/case-suite";

const props = defineProps({
  testType: {
    default: '',
    type: String,
  }
})

const uploadHeaders =  { 'access-token': localStorage.getItem('access-token') }
const uploadFailList = ref([])
const uploadFailTotal = ref(0)
const projectId = ref()
const drawerIsShow = ref(false)
const drawerIsLoading = ref(false)
let submitButtonIsLoading = ref(false)


onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'upload-case-suite') {
    uploadFailList.value = []
    uploadFailTotal.value = 0
    projectId.value = message.content.project_id
    drawerIsShow.value = true
  }
}


const downloadTemplate = () => {
  DownloadSuiteTemplate(props.testType).then(response => {
    const blob = new Blob([response], { type: 'application/vnd.xmind.workbook' })
    // 保存文件到本地
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob) // 生成一个url
    a.download = '用例集导入模板.xmind'
    a.click()
  })
}

const uploadFile = (response: any, file: { raw: string | Blob; }) => {
  const form = new FormData()
  form.append('project_id', projectId.value)
  form.append('file', file.raw)

  drawerIsLoading.value = true
  UploadCaseSuite(props.testType, form).then((response) => {
    drawerIsLoading.value = false
    bus.emit(busEvent.drawerIsCommit, {eventType: 'upload-case-suite'});
    uploadFailList.value = response.data.suite.fail.data
    uploadFailTotal.value = response.data.suite.fail.total
  })
}

</script>


<style scoped lang="scss">
// 上传用例集弹窗样式
:deep(.upload-case-suite-dialog) {
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

// 图片预览样式
:deep(.el-image) {
  .el-image__inner {
    transition: all 0.3s ease;
    
    &:hover {
      transform: scale(1.02);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }
}

// 响应式适配
@media (max-width: 1200px) {
  :deep(.upload-case-suite-dialog) {
    .el-dialog {
      width: 90% !important;
      margin: 2vh auto !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.upload-case-suite-dialog) {
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

// 加载动画优化
:deep(.el-loading-mask) {
  background-color: rgba(255, 255, 255, 0.9);
  
  .el-loading-spinner {
    .el-loading-text {
      color: #409eff;
      font-weight: 500;
    }
  }
}
</style>
