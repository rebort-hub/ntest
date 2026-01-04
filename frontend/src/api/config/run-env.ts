import request from '@/utils/system/request'
import {baseDirConfig} from '../base-url'

const currentBaseDir = baseDirConfig + '/run-env'


export function PostRunEnv(data: object) {
    return request({url: currentBaseDir, method: 'post', data: data})
}

export function GetRunEnv(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}

export function PutRunEnv(data: object) {
    return request({url: currentBaseDir, method: 'put', data: data})
}

export function DeleteRunEnv(data: object) {
    return request({url: currentBaseDir, method: 'delete', data: data})
}

export function RunEnvGroupList(params: object) {
    return request({ url: currentBaseDir + '/group', method: 'get', params: params })
}

export function GetRunEnvList(params: object) {
    return request({ url: currentBaseDir + '/list', method: 'get', params: params })
}

export function RunEnvSort(data: object) {
    return request({ url: currentBaseDir + '/sort', method: 'put', data: data })
}

export function RunEnvToBusiness(data: object) {
    return request({ url: currentBaseDir + '/business', method: 'put', data: data })
}
