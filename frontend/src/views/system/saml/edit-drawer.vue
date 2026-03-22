<template>
  <div>
    <el-drawer
      v-model="drawerIsShow"
      :title="drawerTitle"
      direction="rtl"
      size="900px"
      :close-on-click-modal="false"
      @close="closeDrawer"
      class="saml-config-drawer"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="150px"
        style="padding-right: 20px"
      >
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 基础配置 -->
          <el-tab-pane label="基础配置" name="basic">
            <el-form-item label="配置名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入配置名称" />
            </el-form-item>
            
            <el-form-item label="SP Entity ID" prop="entity_id">
              <el-input v-model="formData.entity_id" placeholder="请输入SP Entity ID" />
              <div class="form-tip">
                通常格式：https://your-domain.com/saml/metadata
              </div>
            </el-form-item>
            
            <el-form-item label="ACS URL" prop="acs_url">
              <el-input v-model="formData.acs_url" placeholder="断言消费服务URL" />
              <div class="form-tip">
                格式：https://your-domain.com/api/system/saml/acs
              </div>
            </el-form-item>
            
            <el-form-item label="SLS URL">
              <el-input v-model="formData.sls_url" placeholder="单点登出URL（可选）" />
              <div class="form-tip">
                格式：https://your-domain.com/api/system/saml/sls
              </div>
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
              <div class="form-tip">
                Azure AD示例：https://sts.windows.net/tenant-id/<br>
                ADFS示例：http://your-adfs-server.com/adfs/services/trust
              </div>
            </el-form-item>
            
            <el-form-item label="IdP SSO URL" prop="idp_sso_url">
              <el-input v-model="formData.idp_sso_url" placeholder="请输入IdP SSO URL" />
              <div class="form-tip">
                Azure AD示例：https://login.microsoftonline.com/tenant-id/saml2<br>
                ADFS示例：https://your-adfs-server.com/adfs/ls/
              </div>
            </el-form-item>
            
            <el-form-item label="IdP SLS URL">
              <el-input v-model="formData.idp_sls_url" placeholder="IdP单点登出URL（可选）" />
            </el-form-item>
            
            <el-form-item label="IdP X.509证书" prop="idp_x509_cert">
              <el-input 
                v-model="formData.idp_x509_cert" 
                type="textarea" 
                :rows="8"
                placeholder="请粘贴IdP的X.509证书内容，包含 -----BEGIN CERTIFICATE----- 和 -----END CERTIFICATE-----"
              />
              <div class="form-tip">
                从IdP管理界面下载证书文件，复制完整内容到此处
              </div>
            </el-form-item>
          </el-tab-pane>

          <!-- SP配置 -->
          <el-tab-pane label="SP配置" name="sp">
            <el-alert
              title="SP证书和私钥用于对SAML请求进行签名，如果IdP不要求签名可以留空"
              type="info"
              :closable="false"
              style="margin-bottom: 20px"
            />
            
            <el-form-item label="SP X.509证书">
              <el-input 
                v-model="formData.sp_x509_cert" 
                type="textarea" 
                :rows="6"
                placeholder="SP证书（可选，用于签名）"
              />
            </el-form-item>
            
            <el-form-item label="SP私钥">
              <el-input 
                v-model="formData.sp_private_key" 
                type="textarea" 
                :rows="6"
                placeholder="SP私钥（可选，用于签名）"
              />
            </el-form-item>
          </el-tab-pane>

          <!-- 安全配置 -->
          <el-tab-pane label="安全配置" name="security">
            <el-form-item label="断言签名">
              <el-checkbox v-model="formData.want_assertions_signed">
                要求IdP对断言进行签名
              </el-checkbox>
            </el-form-item>
            
            <el-form-item label="NameID加密">
              <el-checkbox v-model="formData.want_name_id_encrypted">
                要求对NameID进行加密
              </el-checkbox>
            </el-form-item>
            
            <el-form-item label="认证请求签名">
              <el-checkbox v-model="formData.authn_requests_signed">
                对认证请求进行签名（需要配置SP证书和私钥）
              </el-checkbox>
            </el-form-item>
            
            <el-form-item label="登出请求签名">
              <el-checkbox v-model="formData.logout_requests_signed">
                对登出请求进行签名（需要配置SP证书和私钥）
              </el-checkbox>
            </el-form-item>
          </el-tab-pane>

          <!-- 属性映射 -->
          <el-tab-pane label="属性映射" name="attributes">
            <el-alert
              title="配置SAML属性到用户字段的映射关系"
              type="info"
              :closable="false"
              style="margin-bottom: 20px"
            />
            
            <el-form-item label="用户名属性">
              <el-input 
                v-model="formData.attribute_mapping.username" 
                placeholder="用户名对应的SAML属性"
              />
              <div class="form-tip">
                常用值：http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name
              </div>
            </el-form-item>
            
            <el-form-item label="邮箱属性">
              <el-input 
                v-model="formData.attribute_mapping.email" 
                placeholder="邮箱对应的SAML属性"
              />
              <div class="form-tip">
                常用值：http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress
              </div>
            </el-form-item>
            
            <el-form-item label="名字属性">
              <el-input 
                v-model="formData.attribute_mapping.first_name" 
                placeholder="名字对应的SAML属性"
              />
              <div class="form-tip">
                常用值：http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname
              </div>
            </el-form-item>
            
            <el-form-item label="姓氏属性">
              <el-input 
                v-model="formData.attribute_mapping.last_name" 
                placeholder="姓氏对应的SAML属性"
              />
              <div class="form-tip">
                常用值：http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname
              </div>
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
        
        <el-form-item label="描述" style="margin-top: 20px">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            :rows="3"
            placeholder="配置描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="text-align: right">
          <el-button @click="closeDrawer">取消</el-button>
          <el-button type="primary" @click="testConnection" :loading="testLoading">
            测试连接
          </el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { bus, busEvent } from '@/utils/bus-events'
import { 
  createSamlConfig, 
  updateSamlConfig, 
  testSamlConnection,
  type SamlConfig 
} from '@/api/system/saml'

const drawerIsShow = ref(false)
const drawerTitle = ref('')
const isEdit = ref(false)
const activeTab = ref('basic')
const submitLoading = ref(false)
const testLoading = ref(false)
const formRef = ref()

const formData = reactive<SamlConfig>({
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

const rules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  entity_id: [{ required: true, message: '请输入SP Entity ID', trigger: 'blur' }],
  acs_url: [{ required: true, message: '请输入ACS URL', trigger: 'blur' }],
  idp_entity_id: [{ required: true, message: '请输入IdP Entity ID', trigger: 'blur' }],
  idp_sso_url: [{ required: true, message: '请输入IdP SSO URL', trigger: 'blur' }],
  idp_x509_cert: [{ required: true, message: '请输入IdP X.509证书', trigger: 'blur' }]
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
  activeTab.value = 'basic'
}

const showDrawer = (data: any) => {
  if (data.eventType === 'editSamlConfig') {
    drawerTitle.value = '编辑SAML配置'
    isEdit.value = true
    Object.assign(formData, data.content)
  } else {
    drawerTitle.value = '新建SAML配置'
    isEdit.value = false
    resetForm()
  }
  drawerIsShow.value = true
}

const closeDrawer = () => {
  drawerIsShow.value = false
  resetForm()
  bus.emit(busEvent.drawerIsClose)
}

const testConnection = async () => {
  // 验证必要字段
  if (!formData.idp_sso_url || !formData.idp_x509_cert || !formData.entity_id) {
    ElMessage.warning('请先填写IdP SSO URL、IdP证书和SP Entity ID')
    return
  }
  
  testLoading.value = true
  try {
    const response = await testSamlConnection({
      idp_sso_url: formData.idp_sso_url,
      idp_x509_cert: formData.idp_x509_cert,
      entity_id: formData.entity_id
    })
    
    // 检查响应
    if (response && response.status === 200) {
      ElMessage.success(response.message || '连接测试成功')
    } else {
      ElMessage.error(response.message || '连接测试失败')
    }
  } catch (error: any) {
    console.error('连接测试失败:', error)
    
    // 提供详细的错误信息
    let errorMessage = '连接测试失败'
    if (error.response && error.response.data) {
      const data = error.response.data
      if (data.message) {
        errorMessage = data.message
      } else if (data.detail) {
        errorMessage = data.detail
      }
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessage.error(errorMessage)
  } finally {
    testLoading.value = false
  }
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
    
    submitLoading.value = true
    
    if (isEdit.value) {
      await updateSamlConfig(formData)
      ElMessage.success('配置更新成功')
    } else {
      await createSamlConfig(formData)
      ElMessage.success('配置创建成功')
    }
    
    closeDrawer()
  } catch (error) {
    ElMessage.error('操作失败，请检查输入')
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  bus.on(busEvent.drawerIsShow, showDrawer)
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, showDrawer)
})
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.saml-config-drawer {
  --el-drawer-padding-primary: 24px;
}

:deep(.el-drawer__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 0;
}

:deep(.el-drawer__title) {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

:deep(.el-drawer__body) {
  padding: 24px;
  height: calc(100% - 140px);
  overflow-y: auto;
}

:deep(.el-drawer__footer) {
  padding: 16px 24px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
}

:deep(.el-tabs__content) {
  padding: 24px 0;
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #e4e7ed;
}

:deep(.el-tab-pane) {
  padding: 0 8px;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-input__wrapper) {
  border-radius: 6px;
}

:deep(.el-textarea__inner) {
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-alert) {
  border-radius: 6px;
}

/* 滚动条样式 */
:deep(.el-drawer__body) {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

:deep(.el-drawer__body::-webkit-scrollbar) {
  width: 8px;
}

:deep(.el-drawer__body::-webkit-scrollbar-track) {
  background: #f1f1f1;
  border-radius: 4px;
}

:deep(.el-drawer__body::-webkit-scrollbar-thumb) {
  background: #c1c1c1;
  border-radius: 4px;
}

:deep(.el-drawer__body::-webkit-scrollbar-thumb:hover) {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .saml-config-drawer {
    --el-drawer-size: 100vw;
  }
}
</style>