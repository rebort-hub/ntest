import request from '@/utils/system/request'
import {baseDirApiTest} from "@/api/base-url";

const baseAddr = baseDirApiTest + '/api'

export function PostApi(data: object) {
    return request({ url: baseAddr, method: 'post', data: data })
}

export function PutApi(data: object) {
    return request({ url: baseAddr, method: 'put', data: data })
}

export function GetApi(params: object) {
    return request({ url: baseAddr, method: 'get', params: params })
}

export function DeleteApi(data: object) {
    return request({ url: baseAddr, method: 'delete', data: data })
}

export function UploadApi(data: object) {
    return request({ url: baseAddr + '/upload', method: 'post', data: data })
}

export function DownloadApiTemplate(testType: string) {
    return request({ url: baseAddr + '/template/download', method: 'get', responseType: 'blob' })
}

export function GetApiList(params: object) {
    return request({ url: baseAddr + '/list', method: 'get', params: params })
}

export function RunApi(test_type: string, data: object) {
    return request({ url: baseAddr + '/run', method: 'post', data: data })
}

export function ChangeApiSort(data: object) {
    return request({ url: baseAddr + '/sort', method: 'put', data: data })
}

export function GetApiFrom(params: object) {
    return request({ url: baseAddr + '/from', method: 'get', params: params })
}

export function GetApiToStep(params: object) {
    return request({ url: baseAddr + '/to-step', method: 'get', params: params })
}

export function ChangeApiLevel(data: object) {
    return request({ url: baseAddr + '/level', method: 'put', data: data })
}

export function ChangeApiStatus(data: object) {
    return request({ url: baseAddr + '/status', method: 'put', data: data })
}
