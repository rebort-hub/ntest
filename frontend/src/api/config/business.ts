import request from '@/utils/system/request'
import {baseDirConfig} from '../base-url'

const currentBaseDir = baseDirConfig + '/business'


export function PostBusiness(data: object) {
    return request({url: currentBaseDir, method: 'post', data: data})
}

export function GetBusiness(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}

export function PutBusiness(data: object) {
    return request({url: currentBaseDir, method: 'put', data: data})
}

export function DeleteBusiness(data: object) {
    return request({url: currentBaseDir, method: 'delete', data: data})
}

export function GetBusinessList(params: object) {
    return request({ url: currentBaseDir + '/list', method: 'get', params: params })
}

export function ChangeBusinessSort(data: object) {
    return request({ url: currentBaseDir + '/sort', method: 'put', data: data })
}

export function BusinessToUser(data: object) {
    return request({ url: currentBaseDir + '/user', method: 'put', data: data })
}
