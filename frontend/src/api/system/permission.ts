import request from '@/utils/system/request'
import {baseDirSystemURL} from '../base-url'

const currentBaseDir = baseDirSystemURL + '/permission'

// 权限类型
export function GetPermissionType() {
    return request({url: currentBaseDir + '/type', method: 'get'})
}

// 权限列表
export function GetPermissionList(params: object) {
    return request({url: currentBaseDir + '/list', method: 'get', params: params})
}

// 修改排序
export function ChangePermissionSort(data: object) {
    return request({url: currentBaseDir + '/sort', method: 'put', data: data})
}

// 获取权限信息
export function GetPermission(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}

// 新增权限
export function PostPermission(data: object) {
    return request({url: currentBaseDir, method: 'post', data: data})
}

// 修改权限
export function PutPermission(data: object) {
    return request({url: currentBaseDir, method: 'put', data: data})
}

// 删除权限
export function DeletePermission(data: object) {
    return request({url: currentBaseDir, method: 'delete', data: data})
}
