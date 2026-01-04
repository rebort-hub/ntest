<template>
  <div class="layout-container">
    <div style="margin: 10px">
      <el-button type="primary" @click="showInstallPackage=true">安装包</el-button>
      <el-dialog
          title="安装第三方库"
          v-model="showInstallPackage"
          :close-on-click-modal="false"
          width="50%"
      >

        <el-form ref="ruleFormRef" :model="installForm">
          <el-form-item label="库名称" prop="name" class="is-required" size="small">
            <el-input v-model="installForm.name" size="small" placeholder="第三方库名称, 请准确填写" />
          </el-form-item>

          <el-form-item label="库版本" prop="version" size="small">
            <el-input v-model="installForm.version" size="small" placeholder="第三方库版本, 如果要指定版本，请准确填写" />
          </el-form-item>
        </el-form>

        <div slot="footer" class="dialog-footer">
          <el-button
              v-loading="installPackageIsLoading"
              style="float: left"
              v-show="installForm.name"
              size="small"
              type="primary"
              @click="installPackage">确认安装
          </el-button>

          <el-button size="small" style="float: right" @click="showInstallPackage = false">关闭</el-button>
        </div>

      </el-dialog>
    </div>

    <pre class="formatted-text">{{ packageStr }}</pre>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref} from "vue";
import {GetPackageList, InstallPackage} from "@/api/system/package";
import {Help} from "@icon-park/vue-next";

const packageStr = ref('')
const showInstallPackage = ref(false);
const installPackageIsLoading = ref(false);
const installForm = ref({
  name: '',
  version: '',
});
const ruleFormRef = ref(null)

const getTableDataList = () => {
  GetPackageList().then(response => {
    packageStr.value = response.data
  })
}

const installPackage = () => {
  installPackageIsLoading.value = true;
  InstallPackage(installForm.value).then(response => {
    installPackageIsLoading.value = false
    if (response){
      showInstallPackage.value = false
      getTableDataList()
    }
  })
}

onMounted(() => {
  getTableDataList()
})

</script>

<style scoped lang="scss">
.formatted-text {
  text-align: center;
  font-size: 14px;
  font-family: monospace; /* 使用等宽字体，保持格式 */
  white-space: pre-wrap; /* 保留换行符并处理长文本自动换行 */
  line-height: 1.5; /* 增加行高，提升可读性 */
  margin: 10px; /* 适当的外边距 */
}
</style>
