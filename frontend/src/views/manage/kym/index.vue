<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-button type="primary" @click="showDialog"> 添加KYM分析 </el-button>
      </div>

      <div class="layout-container-form-search">
        <el-select
            v-model="queryItems.project"
            placeholder="请选择服务"
            size="small"
            filterable
            default-first-option
            @change="getKYMByProject"
        >
          <el-option v-for="item in projectList" :key="item.key" :label="item.value" :value="item.key" />
        </el-select>

        <el-button
            type="primary"
            :loading="saveLoading"
            size="small"
            style="margin-left: 20px"
            @click.native="changeKYM"
        >保存修改
        </el-button>

        <el-button
            v-show="queryItems.project"
            type="primary"
            size="small"
            style="margin-left: 20px"
            @click.native="downloadXmidSetup"
        >下载xmind8安装包
        </el-button>

        <el-tooltip class="item" effect="dark" content="下载后需用xmind8打开" placement="top-start">
          <el-button
              v-show="queryItems.project"
              type="primary"
              size="small"
              style="margin-left: 20px"
              @click.native="exportKymAsXmind"
          >导出为xmind
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <!-- 脑图 -->
    <div ref="mindMap" id="map" :style="{marginTop: '5px', width: '100%', height: mapHeight}" />

    <!-- 新增KYM分析 -->
    <el-dialog
        :close-on-click-modal="false"
        title="新增KYM分析"
        v-model="dialogIsShow"
        width="40%"
    >
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-position="right"
          label-width="90px"
      >
        <el-form-item label="服务名" class="is-required" prop="project" size="small">
          <el-input v-model="formData.project" placeholder="服务名称" />
        </el-form-item>

      </el-form>
      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="dialogIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              size="small"
              type="primary"
              :loading="submitButtonIsLoading"
              @click="addKYMProject"
          >
            {{ '保存' }}
          </el-button>
        </div>
      </template>

    </el-dialog>
  </div>

</template>

<script setup lang="ts">
import {computed, onMounted, ref} from "vue";
// 使用方法详见：https://inspiring-golick-3c01b9.netlify.app/
import MindElixir from 'mind-elixir'
import {GetProjectKYM, PutProjectKYM, PostKYM, GetKYMProjectList, GetKymAsXmind} from '@/api/manage/kym'

const submitButtonIsLoading = ref(false)
const dialogIsShow = ref(false)
const saveLoading = ref(false)
const getLoading = ref(false)
const mindMap = ref(null)
const kymData = ref({
  'nodeData': {
    'topic': '新建服务',
    'root': true,
    'children': []
  }
})
const mapHeight = computed(() =>{
  if (innerHeight < 800){  // 小屏
    return `${innerHeight * 0.8}px`
  }else {  // 大屏
    return `${innerHeight * 0.87}px`
  }
})
const queryItems = ref({project: ''})
const projectList = ref([])

const ruleFormRef = ref(null)
const formData = ref({project: undefined})
const formRules = {
  project: [
    {required: true, message: '请输入服务名', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {project: undefined}
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const getKYMProjectList = () => {
  GetKYMProjectList().then(response => {
    projectList.value = response.data
  })
}

const initMindElixir = () => {
  new MindElixir({
    el: mindMap.value,
    direction: MindElixir.SIDE,
    draggable: true, // 启用拖动 default true
    contextMenu: true, // 启用右键菜单 default true
    toolBar: true, // 启用工具栏 default true
    nodeMenu: true, // 启用节点菜单 default true
    keypress: true, // 启用快捷键 default true
    locale: 'zh_CN', // 设置语言，支持[zh_CN,zh_TW,en,ja,pt]
    overflowHidden: false, // default false
    primaryLinkStyle: 1 // 线条形状，1为弧线，2为直线 default 1
    // primaryNodeVerticalGap: 15, //节点之间的垂直距离 default 25
    // primaryNodeHorizontalGap: 15, //节点之间的水平距离 default 65
  }).init(kymData.value)
}

const clickChangeButton = (row) => {
  row.enabled = true
}

const addKYMProject = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostKYM(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          dialogIsShow.value = false
          projectList.value.push({ 'key': formData.value.project, 'value': formData.value.project})

          queryItems.value.project = formData.value.project
          kymData.value = response.data.kym

          initMindElixir() // 挂载分析图
        }
      })
    }
  })
}

const getKYMByProject = (value) => {
  getLoading.value = true
  GetProjectKYM({ project: value }).then(response => {
    getLoading.value = false
    kymData.value = response.data.kym
    initMindElixir() // 挂载分析图
  })
}

const filter = (data) => {
  data['parent'] = null
  if (data['children'] && data['children'].length > 0) {
    for (var index in data['children']) {
      filter(data['children'][index])
    }
  }
}

const changeKYM = () => {
  saveLoading.value = true
  filter(kymData.value['nodeData'])
  PutProjectKYM({ project: queryItems.value.project, kym: kymData.value }).then(response => {
    saveLoading.value = false
    if (response) {
      initMindElixir() // 挂载分析图
    }
  })
}

const downloadXmidSetup = () => {
  window.open('https://dl2.xmind.cn/xmind-8-update9-windows.exe')
}

const exportKymAsXmind = () => {
  GetKymAsXmind({ project: queryItems.value.project }).then(response => {
    const blob = new Blob([response], {
      type: 'application/vnd.ms-excel' // 将会被放入到blob中的数组内容的MIME类型
    })
    // 保存文件到本地
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob) // 生成一个url
    a.download = queryItems.value.project + '.xmind'
    a.click()
  })
}

const getData = () => {
  filter(kymData.value['nodeData'])
}


const showDialog = () => {
  resetForm()
  dialogIsShow.value = true
}

onMounted(() => {
  getKYMProjectList()
})

</script>

<style scoped lang="scss">

</style>
