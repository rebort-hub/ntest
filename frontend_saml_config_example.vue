<template>
  <div class="saml-config-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>SAML SSO 配置管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建配置
          </el-button>
        </div>
      </template>

      <!-- 配置列表 -->
      <el-table :data="configList" style="width: 100%">
        <el-table-column prop="name" label="配置名称" width="150" />
        <el-table-column prop="entity_id" label="SP Entity ID" width="200" show-overflow-tooltip />
        <el-table-column prop="idp_entity_id" label="IdP Entity ID" width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'enable' ? 'success' : 'danger'">
              {{ scope.row.status === 'enable' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_default" label="默认配置" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.is_default" type="warning">默认</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="300">
          <template #default="scope">
            <el-button size="small" @click="editConfig(scope.row)">编辑</el-button>
            <el-button size="small" @click="testConnection(scope.row)">测试连接</el-button>
            <el-button 
              size="small" 
              :type="scope.row.status === 'enable' ? 'warning' : 'success'"
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === 'enable' ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              v-if="!scope.row.is_default"
              size="small" 
              type="info"
              @click="setDefault(scope.row)"
            >
              设为默认
            </el-button>
            <el-button size="small" type="danger" @click="deleteConfig(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑SAML配置' : '新建SAML配置'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="150px">
        <el-tabs v-model="activeTab">
          <!-- 基础配置 -->
          <el-tab-pane label="基础配置" name="basic">
            <el-form-item label="配置名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入配置名称" />
            </el-form-item>
            
            <el-form-item label="SP Entity ID" prop="entity_id">
              <el-input v-model="formData.entity_id" placeholder="请输入SP Entity ID" />
            </el-form-item>
            
            <el-form-item label="ACS URL" prop="acs_url">
              <el-input v-model="formData.acs_url" placeholder="断言消费服务URL" />
            </el-form-item>
            
            <el-form-item label="SLS URL">
              <el-input v-model="formData.sls_url" placeholder="单点登出URL（可选）" />
            </el-form-item>
            
            <el-form-item label="NameID格式">
              <el-select v-model="formData.name_id_format" style="width: 100%">
                <el-option 
                  label="Email Address" 
                  value="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress" 
                />
                <el-option 
                  label="Unspecified" 
                  value="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified" 
                />
                <el-option 
                  label="Persistent" 
                  value="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" 
                />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-checkbox v-model="formData.is_default">设为默认配置</el-checkbox>
            </el-form-item>
          </el-tab-pane>

          <!-- IdP配置 -->
          <el-tab-pane label="IdP配置" name="idp">
            <el-form-item label="IdP Entity ID" prop="idp_entity_id">
              <el-input v-model="formData.idp_entity_id" placeholder="请输入IdP Entity ID" />
            </el-form-item>
            
            <el-form-item label="IdP SSO URL" prop="idp_sso_url">
              <el-input v-model="formData.idp_sso_url" placeholder="请输入IdP SSO URL" />
            </el-form-item>
            
            <el-form-item label="IdP SLS URL">
              <el-input v-model="formData.idp_sls_url" placeholder="IdP单点登出URL（可选）" />
            </el-form-item>
            
            <el-form-item label="IdP X.509证书" prop="idp_x509_cert">
              <el-input 
                v-model="formData.idp_x509_cert" 
                type="textarea" 
                :rows="6"
                placeholder="请粘贴IdP的X.509证书内容"
              />
            </el-form-item>
          </el-tab-pane>

          <!-- SP配置 -->
          <el-tab-pane label="SP配置" name="sp">
            <el-form-item label="SP X.509证书">
              <el-input 
                v-model="formData.sp_x509_cert" 
                type="textarea" 
                :rows="4"
                placeholder="SP证书（可选，用于签名）"
              />
            </el-form-item>
            
            <el-form-item label="SP私钥">
              <el-input 
                v-model="formData.sp_private_key" 
                type="textarea" 
                :rows="4"
                placeholder="SP私钥（可选，用于签名）"
              />
            </el-form-item>
          </el-tab-pane>

          <!-- 安全配置 -->
          <el-tab-pane label="安全配置" name="security">
            <el-form-item label="要求断言签名">
              <el-checkbox v-model="formData.want_assertions_signed">
                要求IdP对断言进行签名
              </el-checkbox>
            </el-form-item>
            
            <el-form-item label="要求NameID加密">
              <el-checkbox v-model="formData.want_name_id_encrypted">
                要求对NameID进行加密
              </el-checkbox>
            </el-form-item>
            
            <el-form-item label="认证请求签名">
              <el-checkbox v-model="formData.authn_requests_signed">
                对认证请求进行签名
              </el-checkbox>
            </el-form-item>
            
            <el-form-item label="登出请求签名">
              <el-checkbox v-model="formData.logout_requests_signed">
                对登出请求进行签名
              </el-checkbox>
            </el-form-item>
          </el-tab-pane>

          <!-- 属性映射 -->
          <el-tab-pane label="属性映射" name="attributes">
            <el-form-item label="用户名属性">
              <el-input 
                v-model="formData.attribute_mapping.username" 
                placeholder="用户名对应的SAML属性"
              />
            </el-form-item>
            
            <el-form-item label="邮箱属性">
              <el-input 
                v-model="formData.attribute_mapping.email" 
                placeholder="邮箱对应的SAML属性"
              />
            </el-form-item>
            
            <el-form-item label="名字属性">
              <el-input 
                v-model="formData.attribute_mapping.first_name" 
                placeholder="名字对应的SAML属性"
              />
            </el-form-item>
            
            <el-form-item label="姓氏属性">
              <el-input 
                v-model="formData.attribute_mapping.last_name" 
                placeholder="姓氏对应的SAML属性"
              />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
        
        <el-form-item label="描述">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            :rows="3"
            placeholder="配置描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

// 响应式数据
const configList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const activeTab = ref('basic')
const formRef = ref()

// 表单数据
const formData = reactive({
  name: '',
  entity_id: '',
  acs_url: '',
  sls_url: '',
  idp_entity_id: '',
  idp_sso_url: '',
  idp_sls_url: '',
  idp_x509_cert: '',
  sp_x509_cert: '',
  sp_private_key: '',
  name_id_format: 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
  attribute_mapping: {
    username: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name',
    email: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
    first_name: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname',
    last_name: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname'
  },
  want_assertions_signed: true,
  want_name_id_encrypted: false,
  authn_requests_signed: false,
  logout_requests_signed: false,
  is_default: false,
  description: ''
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  entity_id: [{ required: true, message: '请输入SP Entity ID', trigger: 'blur' }],
  acs_url: [{ required: true, message: '请输入ACS URL', trigger: 'blur' }],
  idp_entity_id: [{ required: true, message: '请输入IdP Entity ID', trigger: 'blur' }],
  idp_sso_url: [{ required: true, message: '请输入IdP SSO URL', trigger: 'blur' }],
  idp_x509_cert: [{ required: true, message: '请输入IdP X.509证书', trigger: 'blur' }]
}

// 方法
const loadConfigList = async () => {
  try {
    // 这里调用实际的API
    // const response = await api.get('/api/system/saml/config/list')
    // configList.value = response.data
    
    // 示例数据
    configList.value = [
      {
        id: 1,
        name: 'Azure AD SAML',
        entity_id: 'https://your-domain.com/saml/metadata',
        idp_entity_id: 'https://sts.windows.net/tenant-id/',
        status: 'enable',
        is_default: true,
        create_time: '2024-01-01 10:00:00'
      }
    ]
  } catch (error) {
    ElMessage.error('加载配置列表失败')
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editConfig = (config) => {
  isEdit.value = true
  Object.assign(formData, config)
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(formData, {
    name: '',
    entity_id: '',
    acs_url: '',
    sls_url: '',
    idp_entity_id: '',
    idp_sso_url: '',
    idp_sls_url: '',
    idp_x509_cert: '',
    sp_x509_cert: '',
    sp_private_key: '',
    name_id_format: 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
    attribute_mapping: {
      username: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name',
      email: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
      first_name: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname',
      last_name: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname'
    },
    want_assertions_signed: true,
    want_name_id_encrypted: false,
    authn_requests_signed: false,
    logout_requests_signed: false,
    is_default: false,
    description: ''
  })
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    if (isEdit.value) {
      // 更新配置
      // await api.put('/api/system/saml/config', formData)
      ElMessage.success('配置更新成功')
    } else {
      // 创建配置
      // await api.post('/api/system/saml/config', formData)
      ElMessage.success('配置创建成功')
    }
    
    dialogVisible.value = false
    loadConfigList()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const testConnection = async (config) => {
  try {
    // await api.post('/api/system/saml/config/test', {
    //   idp_sso_url: config.idp_sso_url,
    //   idp_x509_cert: config.idp_x509_cert,
    //   entity_id: config.entity_id
    // })
    ElMessage.success('连接测试成功')
  } catch (error) {
    ElMessage.error('连接测试失败')
  }
}

const toggleStatus = async (config) => {
  try {
    // await api.put(`/api/system/saml/config/${config.id}/status`)
    config.status = config.status === 'enable' ? 'disable' : 'enable'
    ElMessage.success(`配置已${config.status === 'enable' ? '启用' : '禁用'}`)
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const setDefault = async (config) => {
  try {
    // await api.put(`/api/system/saml/config/${config.id}/default`)
    configList.value.forEach(item => {
      item.is_default = item.id === config.id
    })
    ElMessage.success('默认配置设置成功')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteConfig = async (config) => {
  try {
    await ElMessageBox.confirm('确定要删除这个配置吗？', '确认删除', {
      type: 'warning'
    })
    
    // await api.delete(`/api/system/saml/config/${config.id}`)
    ElMessage.success('配置删除成功')
    loadConfigList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 生命周期
onMounted(() => {
  loadConfigList()
})
</script>

<style scoped>
.saml-config-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  text-align: right;
}
</style>