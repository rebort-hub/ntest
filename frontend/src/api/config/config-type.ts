import request from '@/utils/system/request'
import {baseDirConfig} from '../base-url'

const currentBaseDir = baseDirConfig + '/type'


export function PostConfigType(data: object) {
    return request({url: currentBaseDir, method: 'post', data: data})
}

export function GetConfigType(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}

export function PutConfigType(data: object) {
    return request({url: currentBaseDir, method: 'put', data: data})
}

export function DeleteConfigType(data: object) {
    return request({url: currentBaseDir, method: 'delete', data: data})
}

export function GetConfigTypeList(params: object) {
    return request({url: currentBaseDir + '/list', method: 'get', params: params})
}

export function ChangeConfigTypeSort(data: object) {
    return request({url: currentBaseDir + '/sort', method: 'put', data: data})
}
