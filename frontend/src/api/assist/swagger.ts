import request from '@/utils/system/request'
import {baseDirAssist} from '../base-url'

const currentBaseDir = baseDirAssist + '/swagger'

export function PullFromSwagger(data: object) {
    return request({ url: currentBaseDir + '/pull', method: 'post', data: data })
}

export function GetSwaggerPullLog(params: object) {
    return request({ url: currentBaseDir + '/pull-log', method: 'get', params: params })
}

export function GetSwaggerPullLogList(params: object) {
    return request({ url: currentBaseDir + '/pull-log-list', method: 'get', params: params })
}
