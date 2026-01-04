import request from '@/utils/system/request'
import {baseDirAssist} from '../base-url'

const currentBaseDir = baseDirAssist + '/script'


export function PostScript(data: object) {
    return request({url: currentBaseDir, method: 'post', data: data})
}

export function GetScript(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}

export function PutScript(data: object) {
    return request({url: currentBaseDir, method: 'put', data: data})
}

export function DeleteScript(data: object) {
    return request({url: currentBaseDir, method: 'delete', data: data})
}

export function GetScriptList(params: object) {
    return request({url: currentBaseDir + '/list', method: 'get', params: params})
}

export function DebugScript(data: object) {
    return request({url: currentBaseDir + '/debug', method: 'POST', data: data})
}

export function CopyScript(data: object) {
    return request({url: currentBaseDir + '/copy', method: 'post', data: data})
}

export function ScriptSort(data: object) {
    return request({url: currentBaseDir + '/sort', method: 'put', data: data})
}

export function GetScriptMockRecordList(params: object) {
    return request({url: currentBaseDir + '/mock-list', method: 'get', params: params})
}

export function GetScriptMockRecord(params: object) {
    return request({url: currentBaseDir + '/mock-record', method: 'get', params: params})
}
