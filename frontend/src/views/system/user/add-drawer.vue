<template>
  <div>
    <el-dialog 
      v-model="dialogIsShow" 
      title="新增用户" 
      width="800px" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      destroy-on-close
      top="3vh"
      class="add-user-dialog"
    >
      <el-form ref="ruleFormRef" :model="formData" label-width="100px" size="small">
        <div v-for="(item, index) in formData.user_list" :key="item.id" class="user-form-item">
          <div class="user-header">
            <span class="user-title">用户 {{ index + 1 }}</span>
            <div class="user-actions">
              <el-tooltip content="添加用户" placement="top">
                <el-button
                    v-show="index === 0 || index === formData.user_list.length - 1"
                    type="primary"
                    :icon="Plus"
                    circle
                    size="small"
                    @click="addRow"
                />
              </el-tooltip>
              <el-tooltip content="复制用户" placement="top">
                <el-button
                    type="info"
                    :icon="Copy"
                    circle
                    size="small"
                    @click="copyRow(item)"
                />
              </el-tooltip>
              <el-tooltip content="删除用户" placement="top">
                <el-button
                    v-show="isShowDelButton(index)"
                    type="danger"
                    :icon="Minus"
                    circle
                    size="small"
                    @click="delRow(index)"
                />
              </el-tooltip>
              <el-tooltip content="清除数据" placement="top">
                <el-button
                    v-show="formData.user_list.length === 1"
                    type="warning"
                    :icon="Clear"
                    circle
                    size="small"
                    @click="clearData()"
                />
              </el-tooltip>
            </div>
          </div>

          <el-form-item 
              label="用户名" 
              :prop="`user_list.${index}.name`" 
              :rules="[{ required: true, message: '请输入用户名', trigger: 'blur' }]">
            <el-input v-model="item.name" placeholder="请输入用户名" clearable />
          </el-form-item>

          <el-form-item 
              label="账号" 
              :prop="`user_list.${index}.account`" 
              :rules="[{ required: true, message: '请输入账号', trigger: 'blur' }]">
            <el-input v-model="item.account" placeholder="请输入账号" clearable />
          </el-form-item>

          <el-form-item 
              label="密码" 
              :prop="`user_list.${index}.password`" 
              :rules="[{ required: true, message: '请输入密码', trigger: 'blur' }]">
            <el-input v-model="item.password" type="password" placeholder="请输入密码" clearable show-password />
          </el-form-item>

          <el-form-item label="邮箱" :prop="`user_list.${index}.email`">
            <el-input v-model="item.email" placeholder="请输入邮箱" clearable />
          </el-form-item>

          <el-form-item label="邮箱密码" :prop="`user_list.${index}.email_password`">
            <el-input v-model="item.email_password" type="password" placeholder="请输入邮箱密码" clearable show-password />
          </el-form-item>

          <el-form-item 
              :prop="`user_list.${index}.business_list`" 
              :rules="[{ required: true, message: '请选择业务线', trigger: 'change' }]">
            <template #label>
              <span>业务线</span>
              <el-tooltip placement="top">
                <template #content>
                  <div>1、仅有当前业务线权限的用户才能看到此服务</div>
                  <div>2、若要修改用户业务线权限，需登录管理员账号，在用户管理处修改</div>
                </template>
                <el-icon style="margin-left: 4px; cursor: pointer;"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-select
                v-model="item.business_list"
                multiple
                filterable
                clearable
                placeholder="请选择业务线"
                style="width: 100%"
            >
              <el-option
                  v-for="business in props.businessList"
                  :key="business.id"
                  :label="business.name"
                  :value="business.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item 
              label="角色" 
              :prop="`user_list.${index}.role_list`" 
              :rules="[{ required: true, message: '请选择角色', trigger: 'change' }]">
            <el-select
                v-model="item.role_list"
                multiple
                filterable
                placeholder="请选择角色"
                style="width: 100%"
            >
              <el-option
                  v-for="role in props.roleList"
                  :key="role.id"
                  :label="role.name"
                  :value="role.id"
              />
            </el-select>
          </el-form-item>

          <el-divider v-if="index < formData.user_list.length - 1" />
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="dialogIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="addData"
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
import {ElMessage} from 'element-plus'
import {QuestionFilled} from '@element-plus/icons-vue'
import {Clear, Copy, Minus, Plus} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {PostUser} from "@/api/system/user";

const props = defineProps({
  roleList: {
    default: [],
    type: Array
  },
  businessList: {
    default: [],
    type: Array
  },
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'addUser') {
    resetForm()
    dialogIsShow.value = true
  }
}

const dialogIsShow = ref(false)
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    name: null,
    account: null,
    password: null,
    email: null,
    email_password: null,
    role_list: [],
    business_list: []
  }
}

const formData = ref({
  user_list: [getNewData()]
})

const resetForm = () => {
  formData.value = {
    user_list: [getNewData()]
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const addRow = () => {
  formData.value.user_list.push(getNewData())
}

const copyRow = (row: any) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.user_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.user_list.length === 1 && index === 0)
}

const delRow = (index: number) => {
  formData.value.user_list.splice(index, 1)
}

const clearData = () => {
  formData.value.user_list[0] = getNewData()
}

const validateUserList = () => {
  if (formData.value.user_list.length < 1) {
    ElMessage.warning('请填写用户信息')
    throw new Error('请填写用户信息')
  }
  formData.value.user_list.forEach((user, index) => {
    if (!user.name || !user.account || !user.password || user.role_list.length < 1 || user.business_list.length < 1) {
      ElMessage.warning(`第 ${index + 1} 个用户，请完善数据`)
      throw new Error(`第 ${index + 1} 个用户，请完善数据`)
    }
  })
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      validateUserList()
      submitButtonIsLoading.value = true
      PostUser(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          bus.emit(busEvent.drawerIsCommit, {eventType: 'user'});
          dialogIsShow.value = false
        }
      })
    } else {
      ElMessage.warning('请完善表单信息')
    }
  })
}

</script>


<style scoped lang="scss">
:deep(.add-user-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 90vh;
    margin-top: 3vh !important;
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
    
    // 自定义滚动条样式
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

.user-form-item {
  margin-bottom: 20px;
  
  .user-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 4px;
    
    .user-title {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
    }
    
    .user-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.el-divider {
  margin: 24px 0;
}
</style>
