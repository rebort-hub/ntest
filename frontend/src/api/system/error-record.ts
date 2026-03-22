import request from '@/utils/system/request'
import {baseDirSystemURL} from '../base-url'

// 获取错误列表
export function GetErrorRecordList(params: object) {
    return request({ url: baseDirSystemURL + '/error-record/list', method: 'get', params: params })
}

// 获取错误
export function GetErrorRecord(params: object) {
    return request({ url: baseDirSystemURL + '/error-record', method: 'get', params: params })
}
