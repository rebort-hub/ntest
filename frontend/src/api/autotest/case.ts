import request from '@/utils/system/request'

const getBaseDir = (testType: string) => {
    return `/api/${testType}-test` + '/case'
}

export function PostCase(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'post', data: data })
}

export function GetCase(testType: string, params: object) {
    return request({ url: getBaseDir(testType), method: 'get', params: params })
}

export function PutCase(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'put', data: data })
}

export function DeleteCase(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'delete', data: data })
}

export function RunCase(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/run', method: 'post', data: data })
}

export function ChangeCaseStatus(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/status', method: 'put', data: data })
}

export function GetCaseList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/list', method: 'get', params: params })
}

export function GetMakeDataCaseList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/make-data-list', method: 'get', params: params })
}

export function GetCaseName(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/name', method: 'get', params: params })
}

export function CopyCase(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/copy', method: 'post', data: data })
}

export function CopyCaseStep(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/copy-step', method: 'post', data: data })
}

export function ChangeCaseSort(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/sort', method: 'put', data: data })
}

export function ChangeCaseParent(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/parent', method: 'put', data: data })
}

export function GetCaseFrom(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/from', method: 'get', params: params })
}

export function GetCaseFromProject(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/project', method: 'get', params: params })
}
