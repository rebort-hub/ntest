<template>
  <div>
    <el-dialog 
      v-model="dialogVisible" 
      title="修改用户邮箱" 
      width="500px"
      :close-on-click-modal="false">
      <el-form
          ref="ruleFormRef"
          :model="formData"
          label-width="80px">

        <el-form-item label="用户名" prop="name" class="is-required" size="small">
          <el-input disabled v-model="formData.name" size="small"/>
        </el-form-item>

        <el-form-item label="邮箱" prop="email" size="small">
          <el-input v-model="formData.email" size="small" placeholder="请输入邮箱地址"/>
        </el-form-item>

      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button size="small" @click="dialogVisible = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="changeData">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {ChangeUserEmail} from "@/api/system/user";

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'edit-user-email') {
    resetForm()
    formData.value = message.content
    dialogVisible.value = true
  }
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'user'});
};

const dialogVisible = ref(false)
let submitButtonIsLoading = ref(false)
const formData = ref({
  id: undefined,
  name: undefined,
  email: null,
})

const ruleFormRef = ref(null)
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: undefined,
    email: null
  }
}

const changeData = () => {
  submitButtonIsLoading.value = true
  ChangeUserEmail(formData.value).then(response => {
    submitButtonIsLoading.value = false
    if (response) {
      sendEvent()
      dialogVisible.value = false
    }
  })
}

</script>

<style scoped lang="scss">

</style>
