import request from '@/utils/system/request'
import {baseDirManage} from '../base-url'

const currentBaseDir = baseDirManage + '/env'

export function GetEnvList(params: object) {
    return request({url: currentBaseDir + '/list', method: 'get', params: params})
}

export function ChangeEnvSort(data: object) {
    return request({url: currentBaseDir + '/sort', method: 'put', data: data})
}

export function CopyEnv(data: object) {
    return request({url: currentBaseDir + '/copy', method: 'post', data: data})
}

export function GetEnv(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}

export function PostEnv(data: object) {
    return request({url: currentBaseDir, method: 'post', data: data})
}

export function PutEnv(data: object) {
    return request({url: currentBaseDir, method: 'put', data: data})
}

export function DeleteEnv(data: object) {
    return request({url: currentBaseDir, method: 'delete', data: data})
}

export function GetAccountList(params: object) {
    return request({url: currentBaseDir + '/account/list', method: 'get', params: params})
}

export function ChangeAccountSort(data: object) {
    return request({url: currentBaseDir + '/account/sort', method: 'put', data: data})
}

export function GetAccount(params: object) {
    return request({url: currentBaseDir + '/account', method: 'get', params: params})
}

export function PostAccount(data: object) {
    return request({url: currentBaseDir + '/account', method: 'post', data: data})
}

export function PutAccount(data: object) {
    return request({url: currentBaseDir + '/account', method: 'put', data: data})
}

export function DeleteAccount(data: object) {
    return request({url: currentBaseDir + '/account', method: 'delete', data: data})
}
