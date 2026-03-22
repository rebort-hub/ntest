<template>
  <div>
    <el-dialog 
      v-model="dialogIsShow" 
      :title="formData.id ? '修改角色' : '新增角色'" 
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

          <el-form-item label="角色名" prop="name" class="is-required" size="small">
            <el-input v-model="formData.name" size="small"/>
          </el-form-item>

          <el-form-item label="备注" prop="desc" size="small">
            <el-input v-model="formData.desc" type="textarea" autosize size="small"/>
          </el-form-item>

          <el-form-item label="继承角色" size="small">
            <el-select
                v-model="formData.extend_role"
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
                  :disabled="role.id === formData.id"
              />
            </el-select>
            <el-popover class="el_popover_class" placement="top-start" trigger="hover">
              <div>
                <div>若此处选择了角色，则当前角色会拥有此处选中角色的权限</div>
              </div>
              <el-button slot="reference" type="text" icon="el-icon-question" />
            </el-popover>
          </el-form-item>

          <el-tabs v-model="activeName">
            <el-tab-pane label="前端权限" name="front">
              <div style="text-align: center">
                <el-transfer
                    class="custom-transfer"
                    v-model="formData.front_permission"
                    :data="frontPermissionList"
                    filterable
                    filter-placeholder="请输入权限名"
                    :titles="['可选权限', '已有权限']"
                    :props="{key: 'id', label: 'name'}"
                />
              </div>
            </el-tab-pane>
            <el-tab-pane label="后端权限" name="api">
              <div style="text-align: center">
                <el-transfer
                    class="custom-transfer"
                    v-model="formData.api_permission"
                    :data="apiPermissionList"
                    filterable
                    filter-placeholder="请输入权限名"
                    :titles="['可选权限', '已有权限']"
                    :props="{key: 'id', label: 'name'}"
                />
              </div>
            </el-tab-pane>
          </el-tabs>

        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="dialogIsShow = false">取消</el-button>
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
import {bus, busEvent} from "@/utils/bus-events";
import {GetPermissionList} from "@/api/system/permission";
import {GetRole, PostRole, PutRole} from "@/api/system/role";

const props = defineProps({
  roleList: {
    default: [],
    type: Array
  }
})

onMounted(() => {
  GetPermissionList({ page_no: 1, page_size: 1000 }).then(response => {
    apiPermissionList.value = []
    frontPermissionList.value = []
    response.data.data.forEach((permission: { source_type: string; }) => {
      if (permission.source_type === 'api') {
        apiPermissionList.value.push(permission)
      } else {
        frontPermissionList.value.push(permission)
      }
    })
  })

  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'role') {
    resetForm()
    if (message.content){
      getRole(message.content.id)
    }
    dialogIsShow.value = true
  }
}

const getRole = (dataId: number) => {
  GetRole({id: dataId}).then(response => {
    formData.value = response.data.data
    formData.value.front_permission = response.data.front_permission
    formData.value.api_permission = []
    response.data.all_permissions.forEach((permissionId: number) => {
      if (formData.value.front_permission.indexOf(permissionId) === -1){
        formData.value.api_permission.push(permissionId)
      }
    })
  })
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'role'});
};

const dialogIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const activeName = ref('front')
const apiPermissionList = ref([])
const frontPermissionList = ref([])

const formData = ref({
  id: undefined,
  name: '',
  desc: '',
  extend_role: [],
  front_permission: [],
  api_permission: []
})

const formRules = {
  name: [
    {required: true, message: '请输入角色名', trigger: 'blur'}
  ]
}
const ruleFormRef = ref(null)
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: '',
    desc: '',
    extend_role: [],
    front_permission: [],
    api_permission: []
  }
  ruleFormRef.value && ruleFormRef.value.resetFields()
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
      PostRole(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          dialogIsShow.value = false
        }
      })
    }
  })
}
const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutRole(formData.value).then(response => {
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
    max-height: 60vh;
    overflow-y: auto;
  }
  
  :deep(.el-dialog__footer) {
    border-top: 1px solid #e4e7ed;
    padding: 16px 20px;
  }
}

.dialog-content {
  .el-form {
    .el-form-item {
      margin-bottom: 20px;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.custom-transfer :deep(.el-transfer-panel){
  width: 350px; /* 单个面板的宽度 */
}

// 响应式设计
@media (max-width: 768px) {
  .custom-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 5vh auto;
    }
    
    :deep(.el-dialog__body) {
      padding: 15px;
      max-height: 60vh;
    }
    
    .el-form {
      :deep(.el-form-item__label) {
        width: 60px !important;
      }
    }
    
    .custom-transfer :deep(.el-transfer-panel){
      width: 280px;
    }
  }
}
</style>
