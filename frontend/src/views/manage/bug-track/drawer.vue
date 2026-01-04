<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改缺陷' : '新增缺陷'" size="60%">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="90px">

        <el-form-item label="业务线" class="is-required" prop="business_id" size="small">
          <el-select
              v-model="formData.business_id"
              placeholder="选择业务线"
              clearable
              filterable
              default-first-option
              style="margin-right: 10px; width: 100%"
              size="small"
          >
            <el-option v-for="item in businessList" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
        </el-form-item>

        <el-form-item label="迭代" class="is-required" prop="iteration" size="small">
          <el-select
              v-model="formData.iteration"
              placeholder="选择业务线"
              clearable
              filterable
              allow-create
              default-first-option
              style="margin-right: 10px; width: 100%"
              size="small"
          >
            <el-option v-for="iteration in iterationList" :key="iteration" :label="iteration" :value="iteration" />
          </el-select>
        </el-form-item>

        <el-form-item label="缺陷描述" prop="name" size="small">
          <el-input v-model="formData.name"  size="small" placeholder="缺陷描述"/>
        </el-form-item>

        <el-form-item label="缺陷详情" prop="detail" size="small">
          <el-input v-model="formData.detail"  size="small" type="textarea" :rows="2" placeholder="缺陷详情"/>
        </el-form-item>

        <el-form-item label="缺陷来源" class="is-required" prop="bug_from" size="small">
          <el-input v-model="formData.bug_from"  size="small" placeholder="缺陷来源"/>
        </el-form-item>

        <el-form-item label="发现时间" prop="trigger_time" size="small">
          <el-date-picker
              v-model="formData.trigger_time"
              type="datetime"
              placeholder="选择发现时间"
              style="width: 100%"
              :picker-options="pickerOptions"
          />
        </el-form-item>

        <el-form-item label="原因" prop="reason" size="small">
          <el-input v-model="formData.reason" size="small" type="textarea" :rows="2" placeholder="原因"/>
        </el-form-item>

        <el-form-item label="解决方案" prop="solution" size="small">
          <el-input v-model="formData.solution" size="small" type="textarea" :rows="2" placeholder="解决方案"/>
        </el-form-item>

        <el-form-item label="跟进人" class="is-required" prop="manager" size="small">
          <el-select
              v-model="formData.manager"
              placeholder="选择跟进人"
              filterable
              default-first-option
              style="margin-right: 10px; width: 100%"
              size="small"
          >
            <el-option v-for="item in userList" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="是否复盘" class="is-required" prop="replay" size="small">
          <el-select
              v-model="formData.replay"
              placeholder="选择是否复盘"
              filterable
              default-first-option
              style="margin-right: 10px; width: 100%"
              size="small"
          >
            <el-option v-for="(value, key) in isReplayMapping" :key="parseInt(key)" :label="value" :value="parseInt(key)"/>
          </el-select>
        </el-form-item>

        <el-form-item label="复盘结论" prop="conclusion" size="small">
          <el-input v-model="formData.conclusion" size="small" type="textarea" :rows="2" placeholder="复盘结论"/>
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

import {onBeforeUnmount, onMounted, ref} from "vue";
import {GetBugTrack, PostBugTrack, PutBugTrack} from "@/api/manage/bug-track";
import {bus, busEvent} from "@/utils/bus-events";

const props = defineProps({
  businessList: {
    default: [],
    type: Array,
  },
  iterationList: {
    default: [],
    type: Array,
  },
  userList: {
    default: [],
    type: Array,
  },
  isReplayMapping: {
    default: {},
    type: Object
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'bug-track') {
    resetForm()
    if (message.content){
      getDataPool(message.content.id)
    }
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const pickerOptions = [
  {
    text: '7天内',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: '30天内',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: '90天内',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
]
const ruleFormRef = ref(null)
const formData = ref({
  id: undefined,
  business_id: undefined,
  name: undefined,
  detail: undefined,
  iteration: undefined,
  conclusion: undefined,
  status: undefined,
  replay: 0,
  bug_from: undefined,
  trigger_time: undefined,
  manager: undefined,
  reason: undefined,
  solution: undefined
})
const formRules = {
  business_id: [
    {required: true, message: '请选择业务线', trigger: 'blur'}
  ],
  iteration: [
    {required: true, message: '请选择或输入迭代', trigger: 'blur'}
  ],
  name: [
    {required: true, message: '请输入缺陷描述', trigger: 'blur'}
  ],
  manager: [
    {required: true, message: '请选择跟进人', trigger: 'blur'}
  ],
  detail: [
    {required: true, message: '请输入缺陷详情', trigger: 'blur'}
  ],
  replay: [
    {required: true, message: '请选择是否复盘', trigger: 'blur'}
  ],
  bug_from: [
    {required: true, message: '请输入缺陷来源', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    business_id: undefined,
    name: undefined,
    detail: undefined,
    iteration: undefined,
    conclusion: undefined,
    status: undefined,
    replay: 0,
    bug_from: undefined,
    trigger_time: undefined,
    manager: undefined,
    reason: undefined,
    solution: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'bug-track'});
};

const submitForm = () =>{
  if (formData.value.id){
    changeData()
  }else {
    addData()
  }
}

const getDataPool = (rowId: number) => {
  GetBugTrack({id: rowId}).then(response => {
    formData.value = response.data
  })
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostBugTrack(formData.value).then(response => {
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
      PutBugTrack(formData.value).then(response => {
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
