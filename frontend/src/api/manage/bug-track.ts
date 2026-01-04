import request from '@/utils/system/request'
import {baseDirManage} from '../base-url'

const currentBaseDir = baseDirManage + '/bug-track'


export function GetBugTrackList(params: object) {
    return request({ url: currentBaseDir + '/list', method: 'get', params: params })
}

export function ChangeBugSort(data: object) {
    return request({ url: currentBaseDir + '/sort', method: 'put', data: data })
}

export function ChangeBugStatus(data: object) {
    return request({ url: currentBaseDir + '/status', method: 'put', data: data })
}

export function ChangeBugReplays(data: object) {
    return request({ url: currentBaseDir + '/replay', method: 'put', data: data })
}

export function GetIterationList() {
    return request({ url: currentBaseDir + '/iteration', method: 'get' })
}

export function GetBugTrack(params: object) {
    return request({ url: currentBaseDir, method: 'get', params: params })
}

export function PostBugTrack(data: object) {
    return request({ url: currentBaseDir, method: 'post', data: data })
}

export function PutBugTrack(data: object) {
    return request({ url: currentBaseDir, method: 'put', data: data })
}

export function DeleteBugTrack(data: object) {
    return request({ url: currentBaseDir, method: 'delete', data: data })
}
