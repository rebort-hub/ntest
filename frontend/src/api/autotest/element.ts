import request from '@/utils/system/request'

const getBaseDir = (testType: string) => {
    return `/api/${testType}-test` + '/element'
}

export const getUploadDir = (testType: string) => {
    return getBaseDir(testType) + '/upload'
}

export function GetElementList(testType: string, params: object) {
    return request({url: getBaseDir(testType) + '/list', method: 'get', params: params})
}

export function PostElement(testType: string, data: object) {
    return request({url: getBaseDir(testType), method: 'post', data: data})
}

export function GetElement(testType: string, params: object) {
    return request({url: getBaseDir(testType), method: 'get', params: params})
}

export function PutElement(testType: string, data: object) {
    return request({url: getBaseDir(testType), method: 'put', data: data})
}

export function DeleteElement(testType: string, data: object) {
    return request({url: getBaseDir(testType), method: 'delete', data: data})
}

export function ChangeElementSort(testType: string, data: object) {
    return request({url: getBaseDir(testType) + '/sort', method: 'put', data: data})
}

export function ChangeElementById(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/id', method: 'put', data: data })
}

export function GetElementFrom(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/from', method: 'get', params: params })
}

export function UploadElement(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/upload', method: 'post', data: data })
}

export function DownloadElementTemplate(testType: string) {
    return request({ url: getBaseDir(testType) + '/template/download', method: 'get', responseType: 'blob' })
}
