import request from '@/utils/system/request'
import {baseDirConfig} from '../base-url'

// OAuth配置相关接口
const currentBaseDir = baseDirConfig + '/oauth'

export interface OAuthConfig {
  id: number
  name: string
  provider: string
  client_id: string
  client_secret: string
  authorize_url: string
  token_url: string
  user_info_url?: string
  redirect_uri: string
  scope: string
  status: 'enabled' | 'disabled'
  is_default: boolean
  user_id_field: string
  username_field: string
  email_field: string
  avatar_field: string
  description?: string
  created_at: string
  updated_at: string
}

export interface CreateOAuthConfigData {
  name: string
  provider: string
  client_id: string
  client_secret: string
  authorize_url: string
  token_url: string
  user_info_url?: string
  redirect_uri: string
  scope: string
  status: 'enabled' | 'disabled'
  user_id_field: string
  username_field: string
  email_field: string
  avatar_field: string
  description?: string
}

export interface UpdateOAuthConfigData extends Partial<CreateOAuthConfigData> {}

export interface OAuthConfigQueryParams {
  page_no?: number
  page_size?: number
  provider?: string
  status?: string
  name?: string
}

export interface OAuthProvider {
  value: string
  label: string
  icon: string
  color: string
  preset: {
    authorize_url: string
    token_url: string
    user_info_url: string
    scope: string
    user_id_field: string
    username_field: string
    email_field: string
    avatar_field: string
  }
}

export interface TestConnectionData {
  client_id: string
  client_secret: string
  authorize_url: string
  token_url: string
  user_info_url?: string
}

// OAuth配置管理API
export const oauthApi = {
  // 获取OAuth配置列表
  getOAuthConfigs: (params?: OAuthConfigQueryParams) => {
    return request({
      url: `${currentBaseDir}/list`,
      method: 'get',
      params
    })
  },

  // 创建OAuth配置
  createOAuthConfig: (data: CreateOAuthConfigData) => {
    return request({
      url: `${currentBaseDir}/create`,
      method: 'post',
      data
    })
  },

  // 更新OAuth配置
  updateOAuthConfig: (id: number, data: UpdateOAuthConfigData) => {
    return request({
      url: `${currentBaseDir}/${id}`,
      method: 'put',
      data
    })
  },

  // 删除OAuth配置
  deleteOAuthConfig: (id: number) => {
    return request({
      url: `${currentBaseDir}/${id}`,
      method: 'delete'
    })
  },

  // 设置默认OAuth配置
  setDefaultOAuthConfig: (config_id: number) => {
    return request({
      url: `${currentBaseDir}/set-default`,
      method: 'post',
      data: { config_id }
    })
  },

  // 批量删除OAuth配置
  batchDeleteOAuthConfigs: (config_ids: number[]) => {
    return request({
      url: `${currentBaseDir}/batch-delete`,
      method: 'post',
      data: { config_ids }
    })
  },

  // 测试OAuth配置连接
  testOAuthConfig: (id: number) => {
    return request({
      url: `${currentBaseDir}/${id}/test`,
      method: 'get'
    })
  },

  // 测试OAuth连接（用于创建/编辑时）
  testConnection: (data: TestConnectionData) => {
    return request({
      url: `${currentBaseDir}/test-connection`,
      method: 'post',
      data
    })
  },

  // 获取支持的OAuth提供商列表
  getOAuthProviders: () => {
    return request({
      url: `${currentBaseDir}/providers`,
      method: 'get'
    })
  }
}