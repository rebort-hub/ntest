import request from '@/utils/system/request'
import {baseDirManage} from '../base-url'

const currentBaseDir = baseDirManage + '/weekly'
const weeklyConfigBaseDir = baseDirManage + '/config'


export function GetWeeklyConfigList(params: object) {
    return request({ url: weeklyConfigBaseDir + '/list', method: 'get', params: params })
}

export function postWeeklyConfig(data: object) {
    return request({ url: weeklyConfigBaseDir, method: 'post', data: data })
}

export function getWeeklyConfig(params: object) {
    return request({ url: weeklyConfigBaseDir, method: 'get', params: params })
}

export function PutWeeklyConfig(data: object) {
    return request({ url: weeklyConfigBaseDir, method: 'put', data: data })
}

export function DeleteWeeklyConfig(data: object) {
    return request({ url: weeklyConfigBaseDir, method: 'delete', data: data })
}

export function weeklyListData(params: object) {
    return request({ url: currentBaseDir + '/list', method: 'get', params: params })
}

export function downloadWeeklyData(params: object) {
    return request({ url: currentBaseDir + '/download', method: 'get', params: params, responseType: 'blob' })
}

export function PostWeekly(data: object) {
    return request({ url: currentBaseDir, method: 'post', data: data })
}

export function GetWeekly(params: object) {
    return request({ url: currentBaseDir, method: 'get', params: params })
}

export function PutWeekly(data: object) {
    return request({ url: currentBaseDir, method: 'put', data: data })
}

export function DeleteWeekly(data: object) {
    return request({ url: currentBaseDir, method: 'delete', data: data })
}
