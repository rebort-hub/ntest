import request from '@/utils/system/request'
import {baseDirAssist} from '../base-url'

const currentBaseDir = baseDirAssist + '/shell-command'


export function GetShellCommandList() {
    return request({url: currentBaseDir + '/list', method: 'get'})
}

export function GetShellCommandRecordList(params: object) {
    return request({url: currentBaseDir + '/record-list', method: 'get', params: params})
}

export function GetShellCommandRecord(params: object) {
    return request({url: currentBaseDir + '/record', method: 'get', params: params})
}

export function SendShellCommand(data: object) {
    return request({url: currentBaseDir + '/send', method: 'post', data: data})
}
