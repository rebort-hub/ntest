import request from '@/utils/system/request'

const getBaseDir = (testType: string) => {
    return `/api/${testType}-test` + '/task'
}

export function GetTask(testType: string, params: object) {
    return request({ url: getBaseDir(testType), method: 'get', params: params })
}

export function PostTask(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'post', data: data })
}

export function PutTask(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'put', data: data })
}

export function DeleteTask(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'delete', data: data })
}

export function GetTaskList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/list', method: 'get', params: params })
}

export function EnableTask(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/status', method: 'post', data: data })
}

export function DisableTask(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/status', method: 'delete', data: data })
}

export function RunTask(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/run', method: 'post', data: data })
}

export function CopyTask(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/copy', method: 'post', data: data })
}

export function ChangeTaskSort(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/sort', method: 'put', data: data })
}
