<template>
  <div class="oauth-config-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>第三方OAuth 2.0授权配置</h2>
        <p>管理第三方OAuth 2.0授权登录配置，支持多种OAuth提供商</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新增OAuth配置
        </el-button>
        <el-button @click="loadConfigs">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="提供商">
          <el-select v-model="searchForm.provider" placeholder="选择OAuth提供商" clearable style="width: 200px">
            <el-option label="全部" value="" />
            <el-option v-for="provider in oauthProviders" :key="provider.value" :label="provider.label" :value="provider.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable style="width: 150px">
            <el-option label="全部" value="" />
            <el-option label="启用" value="enabled" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置名称">
          <el-input v-model="searchForm.name" placeholder="输入配置名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadConfigs">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 配置列表 -->
    <el-card class="table-card">
      <el-table 
        v-loading="loading" 
        :data="configs" 
        stripe 
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="name" label="配置名称" min-width="150">
          <template #default="scope">
            <div class="config-name">
              <el-icon class="provider-icon" :color="getProviderColor(scope.row.provider)">
                <component :is="getProviderIcon(scope.row.provider)" />
              </el-icon>
              <span>{{ scope.row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="provider" label="OAuth提供商" width="120">
          <template #default="scope">
            <el-tag :type="getProviderTagType(scope.row.provider)">
              {{ getProviderLabel(scope.row.provider) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="client_id" label="Client ID" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-switch
              v-model="scope.row.status"
              active-value="enabled"
              inactive-value="disabled"
              @change="toggleStatus(scope.row)"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="is_default" label="默认配置" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.is_default" type="success" size="small">默认</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button 
                type="primary" 
                size="small" 
                @click="testConfig(scope.row)"
                :loading="testingId === scope.row.id"
              >
                <el-icon><Connection /></el-icon>
                测试
              </el-button>
              <el-button 
                type="warning" 
                size="small" 
                @click="editConfig(scope.row)"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button 
                v-if="!scope.row.is_default" 
                type="success" 
                size="small" 
                @click="setDefault(scope.row)"
              >
                <el-icon><Star /></el-icon>
                默认
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click="deleteConfig(scope.row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="searchForm.page_no"
          v-model:page-size="searchForm.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadConfigs"
          @current-change="loadConfigs"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingConfig ? '编辑OAuth配置' : '创建OAuth配置'"
      width="800px"
      @closed="resetForm"
    >
      <el-form
        ref="configFormRef"
        :model="configForm"
        :rules="configFormRules"
        label-width="140px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="配置名称" prop="name">
              <el-input v-model="configForm.name" placeholder="请输入配置名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="OAuth提供商" prop="provider">
              <el-select v-model="configForm.provider" placeholder="选择OAuth提供商" @change="onProviderChange">
                <el-option v-for="provider in oauthProviders" :key="provider.value" :label="provider.label" :value="provider.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Client ID" prop="client_id">
              <el-input v-model="configForm.client_id" placeholder="请输入Client ID" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Client Secret" prop="client_secret">
              <el-input 
                v-model="configForm.client_secret" 
                type="password" 
                placeholder="请输入Client Secret"
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="授权端点" prop="authorize_url">
          <el-input v-model="configForm.authorize_url" placeholder="请输入授权端点URL" />
          <div class="form-tip">OAuth 2.0授权端点，用户将被重定向到此URL进行授权</div>
        </el-form-item>
        
        <el-form-item label="Token端点" prop="token_url">
          <el-input v-model="configForm.token_url" placeholder="请输入Token端点URL" />
          <div class="form-tip">用于交换授权码获取访问令牌的端点</div>
        </el-form-item>
        
        <el-form-item label="用户信息端点" prop="user_info_url">
          <el-input v-model="configForm.user_info_url" placeholder="请输入用户信息端点URL" />
          <div class="form-tip">获取用户基本信息的API端点</div>
        </el-form-item>
        
        <el-form-item label="回调地址" prop="redirect_uri">
          <el-input v-model="configForm.redirect_uri" placeholder="请输入回调地址" />
          <div class="form-tip">OAuth授权完成后的回调地址，需要在OAuth提供商处配置</div>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="授权范围" prop="scope">
              <el-input v-model="configForm.scope" placeholder="请输入授权范围" />
              <div class="form-tip">如：openid profile email</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-switch
                v-model="configForm.status"
                active-value="enabled"
                inactive-value="disabled"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="用户映射配置">
          <el-card class="mapping-card">
            <div class="mapping-item">
              <label>用户ID字段：</label>
              <el-input v-model="configForm.user_id_field" placeholder="如：id, sub" style="width: 200px" />
            </div>
            <div class="mapping-item">
              <label>用户名字段：</label>
              <el-input v-model="configForm.username_field" placeholder="如：name, login" style="width: 200px" />
            </div>
            <div class="mapping-item">
              <label>邮箱字段：</label>
              <el-input v-model="configForm.email_field" placeholder="如：email" style="width: 200px" />
            </div>
            <div class="mapping-item">
              <label>头像字段：</label>
              <el-input v-model="configForm.avatar_field" placeholder="如：avatar_url" style="width: 200px" />
            </div>
          </el-card>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input 
            v-model="configForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入配置描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="info" @click="testConnection" :loading="testingConnection">
          <el-icon><Connection /></el-icon>
          测试连接
        </el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingConfig ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量操作 -->
    <div v-if="selectedConfigs.length > 0" class="batch-actions">
      <el-alert
        :title="`已选择 ${selectedConfigs.length} 个配置`"
        type="info"
        :closable="false"
      >
        <template #default>
          <el-button type="danger" size="small" @click="batchDelete">
            批量删除
          </el-button>
          <el-button size="small" @click="selectedConfigs = []">
            取消选择
          </el-button>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, Edit, Delete, Connection, Star,
  Github, Google, Microsoft, Apple, Wechat, QQ
} from '@element-plus/icons-vue'
import { oauthApi, type OAuthConfig, type CreateOAuthConfigData, type OAuthProvider } from '@/api/config/oauth'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const testingConnection = ref(false)
const testingId = ref<number | null>(null)
const showCreateDialog = ref(false)
const configs = ref<OAuthConfig[]>([])
const selectedConfigs = ref<OAuthConfig[]>([])
const total = ref(0)
const editingConfig = ref<OAuthConfig | null>(null)
const oauthProviders = ref<OAuthProvider[]>([]) // 确保初始化为空数组

// 搜索表单
const searchForm = reactive({
  page_no: 1,
  page_size: 20,
  provider: '',
  status: '',
  name: ''
})

// 配置表单
const configForm = reactive<CreateOAuthConfigData>({
  name: '',
  provider: '',
  client_id: '',
  client_secret: '',
  authorize_url: '',
  token_url: '',
  user_info_url: '',
  redirect_uri: '',
  scope: 'openid profile email',
  status: 'enabled',
  user_id_field: 'id',
  username_field: 'name',
  email_field: 'email',
  avatar_field: 'avatar_url',
  description: ''
})

// 表单验证规则
const configFormRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' },
    { min: 2, max: 50, message: '配置名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  provider: [
    { required: true, message: '请选择OAuth提供商', trigger: 'change' }
  ],
  client_id: [
    { required: true, message: '请输入Client ID', trigger: 'blur' }
  ],
  client_secret: [
    { required: true, message: '请输入Client Secret', trigger: 'blur' }
  ],
  authorize_url: [
    { required: true, message: '请输入授权端点URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  token_url: [
    { required: true, message: '请输入Token端点URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  redirect_uri: [
    { required: true, message: '请输入回调地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ]
}

const configFormRef = ref()

// 方法
const loadConfigs = async () => {
  loading.value = true
  try {
    console.log('开始请求OAuth配置列表...')
    const response = await oauthApi.getOAuthConfigs(searchForm)
    
    // 详细的调试信息
    console.log('=== OAuth配置API调试信息 ===')
    console.log('完整响应对象:', response)
    console.log('响应状态:', response?.status)
    console.log('响应消息:', response?.message)
    console.log('响应数据:', response?.data)
    console.log('响应数据类型:', typeof response?.data)
    console.log('响应数据是否为数组:', Array.isArray(response?.data))
    
    if (response?.data) {
      console.log('数据内容详情:')
      if (Array.isArray(response.data)) {
        console.log('- 数据是数组，长度:', response.data.length)
        console.log('- 第一个元素:', response.data[0])
      } else if (typeof response.data === 'object') {
        console.log('- 数据是对象，键:', Object.keys(response.data))
        console.log('- items字段:', response.data.items)
        console.log('- items是否为数组:', Array.isArray(response.data.items))
        if (Array.isArray(response.data.items)) {
          console.log('- items长度:', response.data.items.length)
        }
      }
    }
    console.log('=== 调试信息结束 ===')
    
    // 检查响应状态
    if (response && (response.status === 200 || response.status === undefined)) {
      const data = response.data
      
      // 根据实际返回的数据结构进行解析
      if (Array.isArray(data)) {
        // 如果data直接是数组
        configs.value = data
        total.value = data.length
        console.log('✅ 解析为直接数组，数据量:', data.length)
      } else if (data && typeof data === 'object') {
        // 如果data是对象，检查是否有items字段
        if (Array.isArray(data.items)) {
          configs.value = data.items
          total.value = data.total || data.items.length
          console.log('✅ 解析为对象.items，数据量:', data.items.length)
        } else if (Array.isArray(data.data)) {
          // 有些API可能返回 data.data 结构
          configs.value = data.data
          total.value = data.total || data.data.length
          console.log('✅ 解析为对象.data，数据量:', data.data.length)
        } else {
          // 检查是否是单个配置对象
          if (data.id && data.name) {
            configs.value = [data]
            total.value = 1
            console.log('✅ 解析为单个对象')
          } else {
            configs.value = []
            total.value = 0
            console.log('❌ 无法解析数据结构，设为空数组')
          }
        }
      } else {
        configs.value = []
        total.value = 0
        console.log('❌ 数据不是数组或对象，设为空数组')
      }
      
      console.log('最终配置数据:', configs.value)
      console.log('配置数据数量:', configs.value.length)
      
      if (configs.value.length > 0) {
        ElMessage.success(response.message || `获取到 ${configs.value.length} 个OAuth配置`)
      } else {
        ElMessage.info('暂无OAuth配置数据')
      }
    } else {
      configs.value = []
      total.value = 0
      console.log('❌ 响应状态异常:', response?.status)
      ElMessage.error(response?.message || '获取OAuth配置失败')
    }
  } catch (error) {
    console.error('❌ 获取OAuth配置异常:', error)
    configs.value = []
    total.value = 0
    ElMessage.error('获取OAuth配置失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const loadProviders = async () => {
  try {
    console.log('开始请求OAuth提供商列表...')
    const response = await oauthApi.getOAuthProviders()
    console.log('OAuth提供商API响应:', response)
    
    if (response && response.status === 200) {
      const data = response.data || []
      // 确保数据是数组格式
      if (Array.isArray(data)) {
        oauthProviders.value = data
        console.log('✅ OAuth提供商加载成功，数量:', data.length)
      } else if (Array.isArray(data.items)) {
        oauthProviders.value = data.items
        console.log('✅ OAuth提供商加载成功（items），数量:', data.items.length)
      } else {
        console.log('⚠️ OAuth提供商数据格式异常，使用默认配置')
        oauthProviders.value = getDefaultProviders()
      }
    } else {
      console.log('⚠️ OAuth提供商API调用失败，使用默认配置')
      oauthProviders.value = getDefaultProviders()
    }
  } catch (error) {
    console.error('❌ 获取OAuth提供商失败:', error)
    console.log('使用默认OAuth提供商配置')
    oauthProviders.value = getDefaultProviders()
  }
  
  console.log('最终OAuth提供商列表:', oauthProviders.value)
}

// 获取默认的OAuth提供商配置
const getDefaultProviders = (): OAuthProvider[] => {
  return [
    {
      value: 'gitee',
      label: 'Gitee',
      icon: 'Github',
      color: '#C71D23',
      preset: {
        authorize_url: 'https://gitee.com/oauth/authorize',
        token_url: 'https://gitee.com/oauth/token',
        user_info_url: 'https://gitee.com/api/v5/user',
        scope: 'user_info',
        user_id_field: 'id',
        username_field: 'name',
        email_field: 'email',
        avatar_field: 'avatar_url'
      }
    },
    {
      value: 'github',
      label: 'GitHub',
      icon: 'Github',
      color: '#24292e',
      preset: {
        authorize_url: 'https://github.com/login/oauth/authorize',
        token_url: 'https://github.com/login/oauth/access_token',
        user_info_url: 'https://api.github.com/user',
        scope: 'user:email',
        user_id_field: 'id',
        username_field: 'login',
        email_field: 'email',
        avatar_field: 'avatar_url'
      }
    },
    {
      value: 'google',
      label: 'Google',
      icon: 'Google',
      color: '#4285f4',
      preset: {
        authorize_url: 'https://accounts.google.com/o/oauth2/v2/auth',
        token_url: 'https://oauth2.googleapis.com/token',
        user_info_url: 'https://www.googleapis.com/oauth2/v2/userinfo',
        scope: 'openid profile email',
        user_id_field: 'id',
        username_field: 'name',
        email_field: 'email',
        avatar_field: 'picture'
      }
    },
    {
      value: 'microsoft',
      label: 'Microsoft',
      icon: 'Microsoft',
      color: '#0078d4',
      preset: {
        authorize_url: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        token_url: 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        user_info_url: 'https://graph.microsoft.com/v1.0/me',
        scope: 'openid profile email',
        user_id_field: 'id',
        username_field: 'displayName',
        email_field: 'mail',
        avatar_field: 'photo'
      }
    },
    {
      value: 'wechat',
      label: '微信',
      icon: 'Wechat',
      color: '#07c160',
      preset: {
        authorize_url: 'https://open.weixin.qq.com/connect/oauth2/authorize',
        token_url: 'https://api.weixin.qq.com/sns/oauth2/access_token',
        user_info_url: 'https://api.weixin.qq.com/sns/userinfo',
        scope: 'snsapi_userinfo',
        user_id_field: 'openid',
        username_field: 'nickname',
        email_field: 'email',
        avatar_field: 'headimgurl'
      }
    },
    {
      value: 'custom',
      label: '自定义',
      icon: 'Connection',
      color: '#909399',
      preset: {
        authorize_url: '',
        token_url: '',
        user_info_url: '',
        scope: 'openid profile email',
        user_id_field: 'id',
        username_field: 'name',
        email_field: 'email',
        avatar_field: 'avatar_url'
      }
    }
  ]
}

const resetSearch = () => {
  searchForm.provider = ''
  searchForm.status = ''
  searchForm.name = ''
  searchForm.page_no = 1
  loadConfigs()
}

const handleSelectionChange = (selection: OAuthConfig[]) => {
  selectedConfigs.value = selection
}

const onProviderChange = (provider: string) => {
  if (!Array.isArray(oauthProviders.value)) {
    return
  }
  const providerConfig = oauthProviders.value.find(p => p.value === provider)
  if (providerConfig?.preset) {
    Object.assign(configForm, providerConfig.preset)
  }
}

const testConfig = async (config: OAuthConfig) => {
  testingId.value = config.id
  try {
    const response = await oauthApi.testOAuthConfig(config.id)
    if (response.status === 200) {
      ElMessage.success({
        message: response.message || 'OAuth配置测试成功！',
        duration: 3000
      })
    } else {
      ElMessage.error(response.message || 'OAuth配置测试失败')
    }
  } catch (error) {
    console.error('OAuth配置测试失败:', error)
    ElMessage.error('OAuth配置测试失败')
  } finally {
    testingId.value = null
  }
}

const testConnection = async () => {
  if (!configFormRef.value) return
  
  try {
    await configFormRef.value.validate()
    testingConnection.value = true
    
    const response = await oauthApi.testConnection({
      client_id: configForm.client_id,
      client_secret: configForm.client_secret,
      authorize_url: configForm.authorize_url,
      token_url: configForm.token_url,
      user_info_url: configForm.user_info_url
    })
    
    if (response.status === 200) {
      ElMessage.success(response.message || '连接测试成功！')
    } else {
      ElMessage.error(response.message || '连接测试失败')
    }
  } catch (error) {
    if (error !== false) {
      console.error('连接测试失败:', error)
      ElMessage.error('连接测试失败')
    }
  } finally {
    testingConnection.value = false
  }
}

const editConfig = (config: OAuthConfig) => {
  editingConfig.value = config
  Object.assign(configForm, {
    name: config.name,
    provider: config.provider,
    client_id: config.client_id,
    client_secret: config.client_secret,
    authorize_url: config.authorize_url,
    token_url: config.token_url,
    user_info_url: config.user_info_url,
    redirect_uri: config.redirect_uri,
    scope: config.scope,
    status: config.status,
    user_id_field: config.user_id_field,
    username_field: config.username_field,
    email_field: config.email_field,
    avatar_field: config.avatar_field,
    description: config.description || ''
  })
  showCreateDialog.value = true
}

const setDefault = async (config: OAuthConfig) => {
  try {
    await ElMessageBox.confirm(
      `确定要将 "${config.name}" 设置为默认OAuth配置吗？`,
      '确认操作',
      { type: 'warning' }
    )
    
    const response = await oauthApi.setDefaultOAuthConfig(config.id)
    if (response.status === 200) {
      // 更新本地数据
      configs.value.forEach(c => {
        c.is_default = c.id === config.id
      })
      ElMessage.success(response.message || '默认配置设置成功')
    } else {
      ElMessage.error(response.message || '设置默认配置失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('设置默认配置失败:', error)
      ElMessage.error('设置默认配置失败')
    }
  }
}

const deleteConfig = async (config: OAuthConfig) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除OAuth配置 "${config.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    const response = await oauthApi.deleteOAuthConfig(config.id)
    if (response.status === 200) {
      configs.value = configs.value.filter(c => c.id !== config.id)
      ElMessage.success(response.message || 'OAuth配置删除成功')
    } else {
      ElMessage.error(response.message || '删除OAuth配置失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除OAuth配置失败:', error)
      ElMessage.error('删除OAuth配置失败')
    }
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedConfigs.value.length} 个OAuth配置吗？`,
      '批量删除',
      { type: 'warning' }
    )
    
    const selectedIds = selectedConfigs.value.map(c => c.id)
    const response = await oauthApi.batchDeleteOAuthConfigs(selectedIds)
    if (response.status === 200) {
      configs.value = configs.value.filter(c => !selectedIds.includes(c.id))
      selectedConfigs.value = []
      ElMessage.success(response.message || '批量删除成功')
    } else {
      ElMessage.error(response.message || '批量删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

const toggleStatus = async (config: OAuthConfig) => {
  try {
    const response = await oauthApi.updateOAuthConfig(config.id, { status: config.status })
    if (response.status === 200) {
      const status = config.status === 'enabled' ? '启用' : '禁用'
      ElMessage.success(`OAuth配置已${status}`)
    } else {
      // 恢复状态
      config.status = config.status === 'enabled' ? 'disabled' : 'enabled'
      ElMessage.error(response.message || '状态更新失败')
    }
  } catch (error) {
    // 恢复状态
    config.status = config.status === 'enabled' ? 'disabled' : 'enabled'
    console.error('状态更新失败:', error)
    ElMessage.error('状态更新失败')
  }
}

const handleSubmit = async () => {
  if (!configFormRef.value) return
  
  try {
    await configFormRef.value.validate()
    submitting.value = true
    
    let response
    if (editingConfig.value) {
      // 更新配置
      response = await oauthApi.updateOAuthConfig(editingConfig.value.id, configForm)
      if (response.status === 200) {
        const index = configs.value.findIndex(c => c.id === editingConfig.value!.id)
        if (index !== -1) {
          configs.value[index] = response.data
        }
        ElMessage.success(response.message || 'OAuth配置更新成功')
      } else {
        ElMessage.error(response.message || '更新OAuth配置失败')
        return
      }
    } else {
      // 创建新配置
      response = await oauthApi.createOAuthConfig(configForm)
      if (response.status === 200) {
        configs.value.unshift(response.data)
        ElMessage.success(response.message || 'OAuth配置创建成功')
      } else {
        ElMessage.error(response.message || '创建OAuth配置失败')
        return
      }
    }
    
    showCreateDialog.value = false
  } catch (error) {
    if (error !== false) {
      console.error('提交OAuth配置失败:', error)
      ElMessage.error(editingConfig.value ? '更新OAuth配置失败' : '创建OAuth配置失败')
    }
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingConfig.value = null
  Object.assign(configForm, {
    name: '',
    provider: '',
    client_id: '',
    client_secret: '',
    authorize_url: '',
    token_url: '',
    user_info_url: '',
    redirect_uri: '',
    scope: 'openid profile email',
    status: 'enabled',
    user_id_field: 'id',
    username_field: 'name',
    email_field: 'email',
    avatar_field: 'avatar_url',
    description: ''
  })
  if (configFormRef.value) {
    configFormRef.value.resetFields()
  }
}

// 工具方法
const getProviderLabel = (provider: string) => {
  if (!Array.isArray(oauthProviders.value)) {
    return provider
  }
  return oauthProviders.value.find(p => p.value === provider)?.label || provider
}

const getProviderIcon = (provider: string) => {
  if (!Array.isArray(oauthProviders.value)) {
    return 'Connection'
  }
  const providerConfig = oauthProviders.value.find(p => p.value === provider)
  return providerConfig?.icon || 'Connection'
}

const getProviderColor = (provider: string) => {
  if (!Array.isArray(oauthProviders.value)) {
    return '#909399'
  }
  return oauthProviders.value.find(p => p.value === provider)?.color || '#909399'
}

const getProviderTagType = (provider: string) => {
  const typeMap: Record<string, string> = {
    github: 'info',
    gitee: 'danger',
    google: 'primary',
    microsoft: 'warning',
    wechat: 'success',
    qq: 'primary',
    dingtalk: 'primary',
    feishu: 'success',
    custom: ''
  }
  return typeMap[provider] || ''
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(async () => {
  console.log('组件挂载，开始初始化数据...')
  // 先加载提供商，再加载配置
  await loadProviders()
  await loadConfigs()
  console.log('数据初始化完成')
})
</script>

<style scoped>
.oauth-config-management {
  padding: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.header-left h2 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 20px;
}

.header-left p {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.search-card,
.table-card {
  margin-bottom: 16px;
}

.config-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.provider-icon {
  font-size: 18px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.mapping-card {
  background-color: #f5f7fa;
}

.mapping-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.mapping-item:last-child {
  margin-bottom: 0;
}

.mapping-item label {
  width: 100px;
  font-size: 14px;
  color: #606266;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
}

.action-buttons {
  display: flex;
  flex-wrap: nowrap;
  gap: 4px;
  align-items: center;
}

.action-buttons .el-button {
  margin-left: 0 !important;
  margin-right: 0 !important;
}
</style>