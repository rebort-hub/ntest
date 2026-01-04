import request from '@/utils/system/request'
import {baseDirAssist} from '../base-url'

const currentBaseDir = baseDirAssist


export function GetCallBackList(params: object) {
    return request({url: currentBaseDir + '/call-back/list', method: 'get', params: params})
}

export function GetCallBack(params: object) {
    return request({url: currentBaseDir + '/call-back', method: 'get', params: params})
}
