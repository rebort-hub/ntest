<template>
  <div>
    <el-dialog 
      v-model="drawerIsShow" 
      :title="formData.id ? '修改缺陷' : '新增缺陷'" 
      width="700px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      destroy-on-close
      top="5vh"
      class="bug-track-dialog"
    >
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="100px"
          size="small">

        <el-form-item label="业务线" prop="business_id">
          <el-select
              v-model="formData.business_id"
              placeholder="请选择业务线"
              clearable
              filterable
              style="width: 100%"
          >
            <el-option v-for="item in businessList" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
        </el-form-item>

        <el-form-item label="迭代" prop="iteration">
          <el-select
              v-model="formData.iteration"
              placeholder="请选择或输入迭代"
              clearable
              filterable
              allow-create
              style="width: 100%"
          >
            <el-option v-for="iteration in iterationList" :key="iteration" :label="iteration" :value="iteration" />
          </el-select>
        </el-form-item>

        <el-form-item label="缺陷描述" prop="name">
          <el-input v-model="formData.name" placeholder="请输入缺陷描述" clearable />
        </el-form-item>

        <el-form-item label="缺陷详情" prop="detail">
          <el-input 
              v-model="formData.detail" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入缺陷详情"
              clearable
          />
        </el-form-item>

        <el-form-item label="缺陷来源" prop="bug_from">
          <el-input v-model="formData.bug_from" placeholder="请输入缺陷来源" clearable />
        </el-form-item>

        <el-form-item label="发现时间" prop="trigger_time">
          <el-date-picker
              v-model="formData.trigger_time"
              type="datetime"
              placeholder="请选择发现时间"
              style="width: 100%"
              :picker-options="pickerOptions"
          />
        </el-form-item>

        <el-form-item label="原因" prop="reason">
          <el-input 
              v-model="formData.reason" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入原因"
              clearable
          />
        </el-form-item>

        <el-form-item label="解决方案" prop="solution">
          <el-input 
              v-model="formData.solution" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入解决方案"
              clearable
          />
        </el-form-item>

        <el-form-item label="跟进人" prop="manager">
          <el-select
              v-model="formData.manager"
              placeholder="请选择跟进人"
              filterable
              style="width: 100%"
          >
            <el-option v-for="item in userList" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="是否复盘" prop="replay">
          <el-select
              v-model="formData.replay"
              placeholder="请选择是否复盘"
              filterable
              style="width: 100%"
          >
            <el-option v-for="(value, key) in isReplayMapping" :key="parseInt(key)" :label="value" :value="parseInt(key)"/>
          </el-select>
        </el-form-item>

        <el-form-item label="复盘结论" prop="conclusion">
          <el-input 
              v-model="formData.conclusion" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入复盘结论"
              clearable
          />
        </el-form-item>

      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm"
          >
            保存
          </el-button>
        </div>
      </template>

    </el-dialog>
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
:deep(.bug-track-dialog) {
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
    max-height: calc(90vh - 140px);
    
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
  
  .el-dialog__footer {
    border-top: 1px solid #ebeef5;
    padding: 15px 20px;
    flex-shrink: 0;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
