import request from '@/utils/system/request'
import {baseDirAssist} from '../base-url'

const currentBaseDir = baseDirAssist + '/data-pool'

export function GetAutoTestUser(params: object) {
    return request({ url: currentBaseDir + '/auto-test-user', method: 'get', params: params })
}

export function GetDataPoolList(params: object) {
    return request({ url: currentBaseDir + '/list', method: 'get', params: params })
}

export function PostDataPool(data: object) {
    return request({url: currentBaseDir + '', method: 'post', data: data})
}

export function GetDataPool(params: object) {
    return request({url: currentBaseDir + '', method: 'get', params: params})
}

export function PutDataPool(data: object) {
    return request({url: currentBaseDir + '', method: 'put', data: data})
}

export function DeleteDataPool(data: object) {
    return request({url: currentBaseDir + '', method: 'delete', data: data})
}

export function GetDataPoolUseStatus(params: object) {
    return request({ url: currentBaseDir + '/use-status', method: 'get', params: params })
}

export function GetDataPoolBusinessStatus(params: object) {
    return request({ url: currentBaseDir + '/business-status', method: 'get', params: params })
}
