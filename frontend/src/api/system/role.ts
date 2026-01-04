import request from '@/utils/system/request'
import {baseDirSystemURL} from '../base-url'

const currentBaseDir = baseDirSystemURL + '/role'

// 权限列表
export function GetRoleList(params: object) {
    return request({url: currentBaseDir + '/list', method: 'get', params: params})
}

// 修改排序
export function ChangeRoleSort(data: object) {
    return request({url: currentBaseDir + '/sort', method: 'put', data: data})
}

// 获取权限信息
export function GetRole(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}

// 新增权限
export function PostRole(data: object) {
    return request({url: currentBaseDir, method: 'post', data: data})
}

// 修改权限
export function PutRole(data: object) {
    return request({url: currentBaseDir, method: 'put', data: data})
}

// 删除权限
export function DeleteRole(data: object) {
    return request({url: currentBaseDir, method: 'delete', data: data})
}
