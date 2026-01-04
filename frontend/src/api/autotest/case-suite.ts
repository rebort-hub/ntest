import request from '@/utils/system/request'


const getBaseDir = (testType: string) => {
    return `/api/${testType}-test` + '/suite'
}
export const getUploadDir = (testType: string) => {
    return getBaseDir(testType) + '/upload'
}

export function DownloadSuiteTemplate(testType: string) {
    return request({ url: getBaseDir(testType) + '/template/download', method: 'get', responseType: 'blob' })
}

export function ChangeCaseSuiteSort(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/sort', method: 'put', data: data })
}

export function PostCaseSuite(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'post', data: data })
}

export function GetCaseSuite(testType: string, params: object) {
    return request({ url: getBaseDir(testType), method: 'get', params: params })
}

export function PutCaseSuite(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'put', data: data })
}

export function DeleteCaseSuite(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'delete', data: data })
}

export function GetCaseSuiteList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/list', method: 'get', params: params })
}

export function RunCaseSuite(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/run', method: 'post', data: data })
}

export function UploadCaseSuite(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/upload', method: 'post', data: data })
}

export function ChangeCaseSuiteParent(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/parent', method: 'put', data: data })
}

export function CopyCaseSuite(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/copy', method: 'post', data: data })
}


export function ApiModuleToCaseSuite(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/from-module', method: 'post', data: data })
}
