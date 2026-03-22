import request from '@/utils/system/request'
import {baseDirAssist} from '../base-url'

const currentBaseDir = baseDirAssist + '/error-record'


export function GetErrorRecordList(params: object) {
    return request({url: currentBaseDir + '-list', method: 'get', params: params})
}

export function GetErrorRecord(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}
