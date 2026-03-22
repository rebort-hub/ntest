import request from '@/utils/system/request'
import {baseDirAssist} from '../base-url'

const currentBaseDir = baseDirAssist + '/file'

export const uploadApi = currentBaseDir

export const uploadAddr = currentBaseDir + '/upload'

export function UploadFile(data: object) {
    return request({ url: uploadAddr, method: 'post', data: data })
}

export function GetFileList(params: object) {
    return request({ url: currentBaseDir + '/list', method: 'get', params: params })
}

export function DownloadFile(params: object) {
    return request({ url: currentBaseDir + '/download', method: 'get', params: params, responseType: 'blob' })
}

export function CheckFileIsExist(params: object) {
    return request({ url: currentBaseDir + '/check', method: 'get', params: params })
}

export function PostFile(data: object) {
    return request({ url: uploadApi, method: 'post', data: data })
}

export function GetFile(params: object) {
    return request({ url: uploadApi, method: 'get', params: params })
}

export function DeleteFile(data: object) {
    return request({ url: uploadApi, method: 'delete', data: data })
}
