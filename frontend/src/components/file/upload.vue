<template>
  <el-dialog
      title="上传文件"
      v-loading="dialogIsLoading"
      v-model="dialogIsShow"
      :close-on-click-modal="false"
      width="30%"
  >
<!--        :modal-append-to-body="false"-->
    <el-upload
        style="margin-bottom: 100px"
        ref="upload"
        multiple
        class="upload-demo"
        :action="uploadUrl"
        :auto-upload="false"
        :on-change="onChange"
        :on-remove="removeFileFromCash"
        :file-list="tempFileList"
    >
      <el-button size="small" type="primary">选择文件</el-button>
    </el-upload>

    <div slot="footer" class="dialog-footer">
      <el-button
          style="float: left"
          v-show="tempFileList.length > 0"
          size="small"
          type="primary"
          @click="submitUpload">上传到服务器</el-button>

      <el-button size="small" style="float: right" @click="dialogIsShow = false">关闭</el-button>
    </div>

  </el-dialog>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref} from "vue";

import { uploadApi, CheckFileIsExist, PostFile } from '@/api/assist/file'

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessageBox} from "element-plus";

const tempFileList = ref([])
const uploadUrl = uploadApi
const dialogIsShow = ref(false)
const dialogIsLoading = ref(false)
const fileType = ref('case')
const ruleFormRef = ref(null)

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'uploadFile') {
    resetForm()
    fileType.value = message.content
    dialogIsShow.value = true
  }
}

const resetForm = () => {
  tempFileList.value = []
  ruleFormRef.value && ruleFormRef.value.resetFields()
}


const onChange = (file: { name: any; }, fileList: any) => {
  // 检验文件是否已存在
  CheckFileIsExist({ file_type: fileType.value, file_name: file.name }).then(response => {

    if (response.message.indexOf('已存在') !== -1) {
      // 确认是否继续上传，不上传则从缓存中删除
      ElMessageBox.confirm(`${response.message}，是否覆盖?`, '提示', {
        confirmButtonText: '覆盖',
        cancelButtonText: '不覆盖',
        type: 'warning'
      }).then(() => {
      }).catch(() => {
        // 选择不覆盖，则把文件从缓存中删除
        removeFileFromCash(file, fileList, true)
      })
    }
  })
  tempFileList.value = fileList
}

// 从缓存中删除文件
const removeFileFromCash = (file: { name: any; }, fileList: any[], isCover: boolean) => {
  // 从文件列表点x组件会自动删
  // isCover 为 true，则代表用户选择了不覆盖文件，需要执行删除代码
  if (isCover) {
    fileList.splice(fileList.indexOf(file), 1)
  }
  tempFileList.value = fileList
}

// 提交上传的文件到服务器
const submitUpload = () => {
  // 把文件添加到form
  const form = new FormData()
  form.append('file_type', fileType.value)
  tempFileList.value.forEach(file => {
    form.append('files', file.raw)
  })

  // 上传form到服务器
  dialogIsLoading.value = true
  PostFile(form).then((response) => {
    dialogIsLoading.value = false
    if (response){
      tempFileList.value = []
      bus.emit(busEvent.drawerIsCommit, {eventType: 'uploadFile'})
      dialogIsShow.value = false
    }
  }
  )
}

</script>

<style scoped>

</style>
