<template>
  <div>
    <el-dialog 
      v-model="dialogIsShow" 
      title="修改用户" 
      width="60%" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="custom-dialog"
    >
      <div class="dialog-content">
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="80px">

        <el-form-item label="用户名" prop="name" class="is-required" size="small">
          <el-input v-model="formData.name" size="small"/>
        </el-form-item>

        <el-form-item label="账号" prop="account" class="is-required" size="small">
          <el-input v-model="formData.account" :disabled="formData.id && !formData.sso_user_id" size="small"/>
        </el-form-item>

        <el-form-item label="邮箱" prop="email" size="small">
          <el-input v-model="formData.email" size="small"/>
        </el-form-item>

        <el-form-item label="邮箱密码" prop="email_password" size="small">
          <el-input v-model="formData.email_password" size="small"/>
        </el-form-item>

        <el-form-item label="角色" prop="role_list" class="is-required" size="small">
          <el-select
              v-model="formData.role_list"
              placeholder="请选择角色"
              multiple
              filterable
              style="width:100%"
          >
            <el-option
                v-for="role in roleList"
                :key="role.name"
                :label="role.name"
                :value="role.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="业务线" prop="business_list" class="is-required" size="small">
          <div style="text-align: center">
            <el-transfer
                class="custom-transfer"
                v-model="formData.business_list"
                :data="businessList"
                filterable
                filter-placeholder="请输入业务线名字"
                :titles="['可选业务线', '已有业务线']"
                :props="{key: 'id', label: 'name'}"
            />
          </div>
        </el-form-item>

      </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="dialogIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="changeData"
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
import {bus, busEvent} from "@/utils/bus-events";
import {PutUser} from "@/api/system/user";

const props = defineProps({
  roleList: {
    default: [],
    type: Array
  },
  businessList: {
    default: [],
    type: Array
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'editUser') {
    resetForm()
    formData.value = message.content
    dialogIsShow.value = true
  }
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'user'});
};

const dialogIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const formData = ref({
  id: undefined,
  name: '',
  account: '',
  email: null,
  email_password: null,
  business_list: [],
  role_list: []
})

const formRules = {
  name: [
    {required: true, message: '请输入用户名', trigger: 'blur'}
  ],
  account: [
    {required: true, message: '请输入账号', trigger: 'blur'}
  ],
  business_list: [
    {required: true, message: '请选择业务线', trigger: 'blur'}
  ],
  role_list: [
    {required: true, message: '请选择角色', trigger: 'blur'}
  ],
}
const ruleFormRef = ref(null)
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: '',
    account: '',
    email: null,
    email_password: null,
    business_list: [],
    role_list: []
  }
  ruleFormRef.value && ruleFormRef.value.resetFields()
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutUser(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          dialogIsShow.value = false
        }
      })
    }
  })
}

</script>


<style scoped lang="scss">
.custom-dialog {
  border-radius: 8px;
  
  :deep(.el-dialog__header) {
    border-bottom: 1px solid #e4e7ed;
    padding: 16px 20px;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px;
  }
  
  :deep(.el-dialog__footer) {
    border-top: 1px solid #e4e7ed;
    padding: 12px 20px;
  }
}

.dialog-content {
  max-height: 60vh;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.custom-transfer :deep(.el-transfer-panel){
  width: 300px; /* 单个面板的宽度 */
}

@media (max-width: 768px) {
  .custom-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 5vh auto;
    }
  }
  
  .custom-transfer :deep(.el-transfer-panel){
    width: 250px;
  }
}
</style>
