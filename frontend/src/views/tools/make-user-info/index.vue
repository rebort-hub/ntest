<template>
  <div class="layout-container">

    <el-drawer title="选择具体项" size="75%" v-model="drawerIsShow">

      <el-form>
        <el-form-item label="选择语言：" label-width="100px">
          <el-radio-group v-model="selectedLanguage">
            <el-radio
                v-for="(languageValue, languageKey) in languageDict"
                :key="languageKey"
                :label="languageKey"
            >{{ languageValue }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="选择项：" label-width="100px">
          <el-checkbox v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">全选
          </el-checkbox>
          <el-checkbox-group v-model="checkedData" @change="handleCheckedCitiesChange">
            <el-checkbox v-for="(value, key) in allOptionsMapping" :key="key" :label="key">{{ value }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="生成条数：" label-width="100px">
          <el-input-number v-model="count" :min="1" :max="100" size="small" label="生成条数"/>
        </el-form-item>
      </el-form>
      <template #footer>
      <div class="demo-drawer__footer">
        <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
        <el-button
            type="primary"
            size="small"
            :loading="makeLoadingIsShow"
            @click.native="sendRequest"
        >确定生成
        </el-button>
      </div>
      </template>
    </el-drawer>

    <div style="margin: 10px">
      <el-button
          v-show="makeUserDictList.length > 0"
          size="small"
          type="primary"
          style="display:inline-block;float: right;margin: 10px;padding-left: 10px"
          @click.native="showDownloadAsContactOptionDialog"
      >导出为通讯录文件
      </el-button>
      <el-button
          v-show="makeUserDictList.length > 0"
          size="small"
          type="primary"
          style="display:inline-block;float: right;margin: 10px;padding-left: 10px"
          @click.native="downloadAsExcel()"
      >导出为EXCEL
      </el-button>
      <el-button
          type="primary"
          size="small"
          style="margin: 10px;padding-left: 10px"
          @click.native="drawerIsShow=true"
      >选择要生成的项
      </el-button>
      <el-table
          :data="makeUserDictList"
          style="width: 100%"
          stripe
          :height="tableHeight"
          @cell-dblclick="rowDblclick">
        <el-table-column prop="id" label="序号" align="center" width="50px">
          <template #default="scope">
            <span> {{ scope.$index + 1 }} </span>
          </template>
        </el-table-column>
        <el-table-column
            v-for="optionKey in allSelectOptionKeys"
            :key="optionKey"
            show-overflow-tooltip
            :label="allOptionsMapping[optionKey]"
            :prop="optionKey"
            :min-width="`${allOptionKeys.length / allOptionsMapping.length}%`"
        >
          <template #default="scope">
            <span>{{ scope.row[optionKey] }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div>
      <el-dialog
          title="导出为通讯录选项"
          append-to-body
          v-model="showDownloadAsContactOption"
          :close-on-click-modal="false"
          width="30%"
      >
        <label for="" style="margin-right: 10px">导出条数: </label>
        <el-input-number v-model="downloadAsContactCount" :min="1" :max="makeUserDictList.length" size="small"/>
        <span style="margin-left: 20px">共 {{ makeUserDictList.length }} 条数据</span>
        <template #footer>
          <div slot="footer" class="dialog-footer">
            <el-button
                v-loading="downloadAsContactIsLoading"
                size="small"
                type="primary"
                @click="downloadAsContact">确 定</el-button>
          </div>
        </template>
      </el-dialog>
    </div>

  </div>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import {MakeUser, ExportAsContact} from '@/api/tools/make-user'
import {GetConfigByCode} from '@/api/config/config-value'
import toClipboard from "@/utils/copy-to-memory";
import {ElMessage} from "element-plus";
import exportToExcel from '@/utils/export-to-excel'
import {bus, busEvent} from "@/utils/bus-events";

const drawerIsShow = ref(true)
const makeLoadingIsShow = ref(false)
const selectedLanguage = ref(false)
const languageDict = ref({})
const allOptionsMapping = ref([])
const allOptionKeys = ref([])
const allSelectOptionKeys = ref([])
const makeUserDictList = ref([])
const checkedData = ref(['name', 'ssn', 'phone_number', 'credit_card_number', 'company_email', 'company', 'address'])
const isIndeterminate = ref(false)
const checkAll = ref(false)
const count = ref(1)
const downloadAsContactIsLoading = ref(false)
const showDownloadAsContactOption = ref(false)
const downloadAsContactCount = ref(0)
const tableHeight = ref('10px')

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.73}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.82}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

onMounted(() => {
  getMakeUserInfoMapping()
  getMakeUserLanguageMapping()
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
})

const getMakeUserInfoMapping = () => {
  GetConfigByCode({code: 'make_user_info_mapping'}).then(response => {
    allOptionsMapping.value = response.data
    allOptionKeys.value = Object.keys(allOptionsMapping.value)
  })
}

const getMakeUserLanguageMapping = () => {
  GetConfigByCode({code: 'make_user_language_mapping'}).then(response => {
    languageDict.value = response.data
    selectedLanguage.value = Object.keys(languageDict.value)[0]
  })
}

const handleCheckAllChange = (val) => {
  checkedData.value = val ? allOptionKeys.value : []
  isIndeterminate.value = false
}

const handleCheckedCitiesChange = (value) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === allOptionKeys.value.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < allOptionKeys.value.length
}

const getExportHeadersList = () => {
  const exportHeadersList: never[] = []
  for (const index in allSelectOptionKeys.value) {
    const key = allSelectOptionKeys.value[index]
    exportHeadersList.push(allOptionsMapping.value[key])
  }
  return exportHeadersList
}

const getExportContentList = () => {
  const makeUserValueList = []

  for (const index in makeUserDictList.value) {
    const user = makeUserDictList.value[index]
    makeUserValueList.push(Object.values(user))
  }
  return makeUserValueList
}

const sendRequest = () => {
  makeLoadingIsShow.value = true
  MakeUser({
    'language': selectedLanguage.value,
    'count': count.value,
    'options': checkedData.value
  }).then(response => {
    makeLoadingIsShow.value = false
    makeUserDictList.value = response.data
    allSelectOptionKeys.value = checkedData.value // 方便渲染列表，把用户选中的项记录下来
    drawerIsShow.value = false
  })
}

const rowDblclick = async (row: any, column: any, event: any) => {
  try {
    await toClipboard(row[column.property]);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}

const downloadAsExcel = () => {
  exportToExcel(makeUserDictList.value)
}

const showDownloadAsContactOptionDialog = () => {
  showDownloadAsContactOption.value = true
  downloadAsContactCount.value = makeUserDictList.value.length
}

const downloadAsContact = () => {
  downloadAsContactIsLoading.value = true
  ExportAsContact({
    'language': languageDict.value[selectedLanguage.value],
    'count': downloadAsContactCount.value,
    'data_list': makeUserDictList.value
  }).then(response => {
    downloadAsContactIsLoading.value = false
    showDownloadAsContactOption.value = false
    const blob = new Blob([response], {
      type: 'application/vnd.ms-excel' // 将会被放入到blob中的数组内容的MIME类型
    })
    // 保存文件到本地
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob) // 生成一个url
    a.download = '通讯录.vcf'
    a.click()
  })
}


</script>

<style scoped lang="scss">

</style>
