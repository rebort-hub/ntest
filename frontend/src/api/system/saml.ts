import request from '@/utils/system/request'
import { baseDirSystemURL } from '../base-url'

const currentBaseDir = baseDirSystemURL + '/saml'

// SAML认证相关API
export function samlLogin(params?: object) {
  return request({ url: currentBaseDir + '/login', method: 'get', params })
}

export function samlLogout(params?: object) {
  return request({ url: currentBaseDir + '/logout', method: 'get', params })
}

export function getSamlMetadata(params?: object) {
  return request({ url: currentBaseDir + '/metadata', method: 'get', params })
}

// SAML配置管理API
export function getSamlConfigList(params?: object) {
  return request({ url: currentBaseDir + '/config/list', method: 'get', params })
}

export function createSamlConfig(data: object) {
  return request({ url: currentBaseDir + '/config', method: 'post', data })
}

export function updateSamlConfig(data: object) {
  return request({ url: currentBaseDir + '/config', method: 'put', data })
}

export function getSamlConfigDetail(configId: number) {
  return request({ url: currentBaseDir + '/config/' + configId, method: 'get' })
}

export function deleteSamlConfig(configId: number) {
  return request({ url: currentBaseDir + '/config/' + configId, method: 'delete' })
}

export function toggleSamlConfigStatus(configId: number) {
  return request({ url: currentBaseDir + '/config/' + configId + '/status', method: 'put' })
}

export function setDefaultSamlConfig(configId: number) {
  return request({ url: currentBaseDir + '/config/' + configId + '/default', method: 'put' })
}

export function testSamlConnection(data: object) {
  return request({ url: currentBaseDir + '/config/test', method: 'post', data })
}

// SAML配置类型定义
export interface SamlConfig {
  id?: number
  name: string
  entity_id: string
  acs_url: string
  sls_url?: string
  idp_entity_id: string
  idp_sso_url: string
  idp_sls_url?: string
  idp_x509_cert: string
  sp_x509_cert?: string
  sp_private_key?: string
  name_id_format: string
  attribute_mapping: {
    username: string
    email: string
    first_name: string
    last_name: string
  }
  want_assertions_signed: boolean
  want_name_id_encrypted: boolean
  authn_requests_signed: boolean
  logout_requests_signed: boolean
  is_default: boolean
  status?: string
  description?: string
  create_time?: string
  update_time?: string
}

export interface SamlTestConnection {
  idp_sso_url: string
  idp_x509_cert: string
  entity_id: string
}