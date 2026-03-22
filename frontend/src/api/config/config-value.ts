import request from '@/utils/system/request'
import {baseDirConfig} from '../base-url'

const currentBaseDir = baseDirConfig + '/config'


export function PostConfig(data: object) {
    return request({url: currentBaseDir, method: 'post', data: data})
}

export function GetConfig(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}

export function PutConfig(data: object) {
    return request({url: currentBaseDir, method: 'put', data: data})
}

export function PutConfigApiValidator(data: object) {
    return request({url: currentBaseDir + '/api-validator', method: 'put', data: data})
}

export function DeleteConfig(data: object) {
    return request({url: currentBaseDir, method: 'delete', data: data})
}

export function GetConfigList(params: object) {
    return request({url: currentBaseDir + '/list', method: 'get', params: params})
}

export function ChangeConfigSort(data: object) {
    return request({url: currentBaseDir + '/sort', method: 'put', data: data})
}

export function GetConfigByCode(params: object) {
    return request({ url: currentBaseDir + '/by-code', method: 'get', params: params })
}

export function GetSkipIfDataSourceMapping(params: object) {
    return request({ url: currentBaseDir + '/skip-if', method: 'get', params: params })
}

export function GetFindElementBy(params: object) {
    return request({ url: currentBaseDir + '/find-element-by', method: 'get', params: params })
}
