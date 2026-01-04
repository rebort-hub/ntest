import request from '@/utils/system/request'
import {baseDirConfig} from '../base-url'

const currentBaseDir = baseDirConfig + '/webhook'


export function PostWebHook(data: object) {
    return request({url: currentBaseDir, method: 'post', data: data})
}

export function GetWebHook(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}

export function PutWebHook(data: object) {
    return request({url: currentBaseDir, method: 'put', data: data})
}

export function DeleteWebHook(data: object) {
    return request({url: currentBaseDir, method: 'delete', data: data})
}

export function DebugWebHook(data: object) {
    return request({ url: currentBaseDir + '/debug', method: 'post', data: data })
}

export function GetWebHookList(params: object) {
    return request({ url: currentBaseDir + '/list', method: 'get', params: params })
}

export function ChangeWebHookSort(data: object) {
    return request({ url: currentBaseDir + '/sort', method: 'put', data: data })
}

export function WebHookSort(data: object) {
    return request({ url: currentBaseDir + '/sort', method: 'put', data: data })
}
