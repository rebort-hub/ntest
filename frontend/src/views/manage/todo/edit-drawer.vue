<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.status === 'todo' ? '修改任务' : '查看任务'" size="60%">
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="80px">

<!--        <el-form-item label="标签" prop="tags" class="is-required" size="small">-->
<!--          <el-input v-model="formData.tags" size="small"/>-->
<!--        </el-form-item>-->

        <el-form-item label="任务名" prop="title" class="is-required" size="small">
          <el-input v-model="formData.title" size="small"/>
        </el-form-item>

        <el-form-item label="任务详情" prop="detail" class="is-required" size="small">
          <el-input v-model="formData.detail" type="textarea" autosize size="small"/>
        </el-form-item>

      </el-form>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              v-show="formData.status === 'todo'"
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="changeData"
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
import {bus, busEvent} from "@/utils/bus-events";
import {PutTodo, GetTodo} from "@/api/manage/todo";

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'edit-todo') {
    resetForm()
    GetTodo({id: message.content}).then(response => {
      formData.value = response.data
    })
    drawerIsShow.value = true
  }
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'get-todo-list'});
};

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const formData = ref({
  id: undefined,
  status: 'todo',
  // tags: [],
  title: undefined,
  detail: undefined,
})

const formRules = {
  // tags: [
  //   {required: true, message: '请输入tag', trigger: 'blur'}
  // ],
  title: [
    {required: true, message: '请输入title', trigger: 'blur'}
  ],
  detail: [
    {required: true, message: '请输入detail', trigger: 'blur'}
  ]
}
const ruleFormRef = ref(null)
const resetForm = () => {
  formData.value = {
    id: undefined,
    status: 'todo',
    // tags: undefined,
    title: undefined,
    detail: undefined,
  }
  ruleFormRef.value && ruleFormRef.value.resetFields()
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutTodo(formData.value).then(response => {
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

.custom-transfer :deep(.el-transfer-panel){
  width: 300px; /* 单个面板的宽度 */
}

</style>
