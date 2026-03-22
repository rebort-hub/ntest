import request from '@/utils/system/request'
import {baseDirAssist} from '../base-url'

const currentBaseDir = baseDirAssist + '/hit'


export function PostHit(data: object) {
    return request({ url: currentBaseDir, method: 'post', data: data })
}

export function GetHit(params: object) {
    return request({ url: currentBaseDir, method: 'get', params: params })
}

export function PutHit(data: object) {
    return request({ url: currentBaseDir, method: 'put', data: data })
}

export function DeleteHit(data: object) {
    return request({ url: currentBaseDir, method: 'delete', data: data })
}

export function GetHitList(params: object) {
    return request({ url: currentBaseDir + '/list', method: 'get', params: params })
}

export function GetHitTypeList() {
    return request({ url: currentBaseDir + '/type-list', method: 'get' })
}
