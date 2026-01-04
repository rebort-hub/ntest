import request from '@/utils/system/request'
import {baseDirManage} from '../base-url'

const currentBaseDir = baseDirManage + '/kym'


export function PostKYM(data: object) {
    return request({ url: currentBaseDir + '/project', method: 'post', data: data })
}

export function GetKYMProjectList() {
    return request({ url: currentBaseDir + '/project-list', method: 'get' })
}

export function GetKymAsXmind(params: object) {
    return request({ url: currentBaseDir + '/download', method: 'get', params: params, responseType: 'blob' })
}

export function GetProjectKYM(params: object) {
    return request({ url: currentBaseDir, method: 'get', params: params })
}

export function PutProjectKYM(data: object) {
    return request({ url: currentBaseDir, method: 'put', data: data })
}
