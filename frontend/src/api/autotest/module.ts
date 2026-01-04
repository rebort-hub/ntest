import request from '@/utils/system/request'

const getBaseDir = (testType: string) => {
    return `/api/${testType}-test` + '/module'
}

export function PostModule(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'post', data: data })
}

export function GetModule(testType: string, params: object) {
    return request({ url: getBaseDir(testType), method: 'get', params: params })
}

export function PutModule(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'put', data: data })
}

export function DeleteModule(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'delete', data: data })
}

export function ChangeModuleSort(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/sort', method: 'put', data: data })
}

export function RunModule(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/run', method: 'post', data: data })
}

export function GetModuleTree(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/tree', method: 'get', params: params })
}

export function GetModuleList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/list', method: 'get', params: params })
}
