import request from '@/utils/system/request'
import {baseDirSystemURL} from '../base-url'
const currentBaseDir = baseDirSystemURL + '/user'
export const refreshTokenDir = currentBaseDir + '/refresh'

// 从后端获取重定向到oauth2验证的地址
export function GetSSORedirectUri() {
  return request({ url: baseDirSystemURL + '/sso/redirect-uri', method: 'get'})
}

// 使用code获取平台的token
export function GetTokenBySSOCode(data: any) {
  return request({ url: baseDirSystemURL + '/sso/token', method: 'post', data: data })
}

// 登录
export function LoginApi(data: object) {
  return request({ url: currentBaseDir + '/login', method: 'post', data })
}

// 刷新token
export function RefreshToken() {
  return request({ url: refreshTokenDir, method: 'get' })
}

// 修改密码
export function ChangePassword(data: object) {
  return request({ url: currentBaseDir + '/password', method: 'put', data: data })
}

// 用户列表
export function GetUserList(params: object) {
  return request({ url: currentBaseDir + '/list', method: 'get', params: params })
}

// 修改排序
export function ChangeUserSort(data: object) {
  return request({url: currentBaseDir + '/sort', method: 'put', data: data})
}

// 修改用户状态
export function ChangeUserStatus(data: object) {
  return request({ url: currentBaseDir + '/status', method: 'put', data: data })
}

// 重置密码
export function ResetPassword(data: object) {
  return request({ url: currentBaseDir + '/reset-password', method: 'put', data: data })
}

// 获取用户的角色
export function GetUserRoles(params: object) {
  return request({ url: currentBaseDir + '/role', method: 'get', params: params })
}

// 修改用户的密码
export function ChangeUserEmail(data: object) {
  return request({ url: currentBaseDir + '/email', method: 'put', data: data })
}

// 获取用户信息
export function GetUser(params: object) {
  return request({ url: currentBaseDir, method: 'get', params: params })
}

// 新增用户
export function PostUser(data: object) {
  return request({ url: currentBaseDir, method: 'post', data: data })
}

// 修改用户
export function PutUser(data: object) {
  return request({ url: currentBaseDir, method: 'put', data: data })
}

// 删除用户
export function DeleteUser(data: object) {
  return request({ url: currentBaseDir, method: 'delete', data: data })
}


































// TODO 解除依赖
/** 获取用户信息Api */
export function getInfoApi(data: object) {
  return request({
    url: '/user/info',
    method: 'post',
    baseURL: '/mock',
    data
  })
}

/** 退出登录Api */
export function loginOutApi() {
  return request({
    url: '/user/out',
    method: 'post',
    baseURL: '/mock'
  })
}
