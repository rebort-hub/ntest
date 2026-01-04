<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改问题记录' : '新增问题记录'" size="60%">
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="80px">

        <el-form-item label="所属服务" prop="project_id" class="is-required" size="small">
          <el-select
              v-model="formData.project_id"
              placeholder="选择服务"
              size="small"
              style="width: 100%"
              filterable
              default-first-option
          >
            <el-option v-for="item in projectListData" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="运行环境" prop="env" class="is-required" size="small">
          <el-select
              v-model="formData.env"
              filterable
              default-first-option
              placeholder="运行环境"
              size="small"
              style="width:100%"
          >
            <el-option v-for="item in runEnvListData" :key="item.code" :label="item.name" :value="item.code" />
          </el-select>
        </el-form-item>

        <el-form-item label="报告id" prop="report_id" class="is-required" size="small">
          <el-input v-model="formData.report_id" size="small" />
        </el-form-item>

        <el-form-item label="触发时间" prop="date" class="is-required" size="small">
          <el-date-picker
              v-model="formData.date"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="测试类型" prop="test_type" class="is-required" size="small">
          <el-select
              v-model="formData.test_type"
              style="width: 100%"
              placeholder="选择测试类型"
              size="small"
              filterable
              default-first-option
          >
            <el-option v-for="item in runTestTypeListData" :key="item.key" :label="item.label" :value="item.key" />
          </el-select>
        </el-form-item>

        <el-form-item label="问题类型" prop="hit_type" class="is-required" size="small">
          <el-select
              v-model="formData.hit_type"
              filterable
              allow-create
              default-first-option
              placeholder="问题类型，可手动输入"
              size="small"
              style="width:100%"
          >
            <el-option v-for="item in hitTypeListData" :key="item.key" :label="item.value" :value="item.key" />
          </el-select>
        </el-form-item>

        <el-form-item label="问题详情" prop="hit_detail" class="is-required" size="small">
          <el-input v-model="formData.hit_detail" size="small" type="textarea" :placeholder="'问题详情'" />
        </el-form-item>

        <el-form-item label="备注" prop="desc" size="small">
          <el-input v-model="formData.desc" size="small" type="textarea" :placeholder="'备注'" />
        </el-form-item>

      </el-form>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm"
          >
            {{ '保存' }}
          </el-button>
        </div>
      </template>

    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref, watch} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {GetProjectList} from "@/api/autotest/project";
import {GetHit, GetHitTypeList, PostHit, PutHit} from "@/api/assist/hit";
import {GetConfigByCode} from "@/api/config/config-value";
import {GetRunEnvList} from "@/api/config/run-env";

const props = defineProps({
  runEnvList: {
    default: [],
    type: Array
  },
  projectList: {
    default: [],
    type: Array
  },
  runTestTypeList: {
    default: [],
    type: Array
  },
  hitTypeList: {
    default: [],
    type: Array
  },
})

watch(() => props.projectList, (newValue, oldValue) => {
  if (newValue){
    projectListData.value = newValue
  }
})

watch(() => props.hitTypeList, (newValue, oldValue) => {
  if (newValue){
    hitTypeListData.value = newValue
  }
})

watch(() => props.runTestTypeList, (newValue, oldValue) => {
  if (newValue){
    runTestTypeListData.value = newValue
  }
})

onMounted(() => {
  runEnvListData.value = props.runEnvList
  projectListData.value = props.projectList
  hitTypeListData.value = props.hitTypeList
  runTestTypeListData.value = props.runTestTypeList

  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const getProjectList = () => {
  if (!projectListData.value || projectListData.value.length < 1) {
    GetProjectList('api', {page_no: 1, page_size: 99999}).then(response => {
      projectListData.value = response.data.data
    })
  }
}

const getHitTypeList = () => {
  if (!hitTypeListData.value || hitTypeListData.value.length < 1) {
    GetHitTypeList().then(response => {
      hitTypeListData.value = response.data
    })
  }
}

const getRunTestType = () => {
  if (!runTestTypeListData.value || runTestTypeListData.value.length < 1) {
    GetConfigByCode({ code: 'test_type' }).then(response => {
      runTestTypeListData.value = response.data
    })
  }
}

const getRunEnvList = () => {
  if (!runEnvListData.value || runEnvListData.value.length < 1){
    GetRunEnvList({}).then(response => {
      runEnvListData.value = response.data.data
    })
  }
}

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'hit') {
    resetForm()
    if (message.content){
      if (message.content.id){  // 修改记录
        getHit(message.content.id)
      }else {  // 测试报告详情过来的新增记录
        formData.value.date = message.content.date
        formData.value.test_type = message.content.test_type
        formData.value.env = message.content.run_env
        formData.value.report_id = message.content.report_id
        formData.value.project_id = message.content.project_id
      }
    }
    drawerIsShow.value = true
  }
}

const getHit = (dataId: number) => {
  GetHit({id: dataId}).then(response => {
      formData.value = response.data
  })
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'hit'});
};

const drawerIsShow = ref(false)
const projectListData = ref([])
const hitTypeListData = ref([])
const runTestTypeListData = ref([])
const runEnvListData = ref([])
const submitButtonIsLoading = ref(false)
const formData = ref({
  id: undefined,
  date: undefined,
  hit_type: undefined,
  hit_detail: undefined,
  test_type: undefined,
  project_id: undefined,
  env: undefined,
  report_id: undefined,
  desc: undefined
})

const formRules = {
  project_id: [
    {required: true, message: '请选择服务', trigger: 'blur'}
  ],
  env: [
    {required: true, message: '请选择运行环境', trigger: 'blur'}
  ],
  report_id: [
    {required: true, message: '请输入报告id', trigger: 'blur'}
  ],
  date: [
    {required: true, message: '请选择触发时间', trigger: 'blur'}
  ],
  test_type: [
    {required: true, message: '请选择测试类型', trigger: 'blur'}
  ],
  hit_type: [
    {required: true, message: '请选择问题类型', trigger: 'blur'}
  ],
  hit_detail: [
    {required: true, message: '请输入问题内容', trigger: 'blur'}
  ]
}
const ruleFormRef = ref(null)

const resetForm = () => {
  formData.value = {
    id: undefined,
    date: undefined,
    hit_type: undefined,
    hit_detail: undefined,
    test_type: undefined,
    project_id: undefined,
    env: undefined,
    report_id: undefined,
    desc: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields()
  getProjectList()
  getHitTypeList()
  getRunTestType()
  getRunEnvList()
}

const submitForm = () => {
  if (formData.value.id) {
    changeData()
  } else {
    addData()
  }
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostHit(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}
const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutHit(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}

</script>


<style scoped lang="scss">

</style>
