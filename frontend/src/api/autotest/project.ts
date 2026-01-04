import request from '@/utils/system/request'

const getBaseDir = (testType: string) => {
    return `/api/${testType}-test` + '/project'
}
const getEnvBaseDir = (testType: string) => {
    return getBaseDir(testType) + '/env'
}

export function GetProjectList(testType: string, params: object) {
    return request({url: getBaseDir(testType) + '/list', method: 'get', params: params})
}

export function PostProject(testType: string, data: object) {
    return request({url: getBaseDir(testType), method: 'post', data: data})
}

export function GetProject(testType: string, params: object) {
    return request({url: getBaseDir(testType), method: 'get', params: params})
}

export function PutProject(testType: string, data: object) {
    return request({url: getBaseDir(testType), method: 'put', data: data})
}

export function DeleteProject(testType: string, data: object) {
    return request({url: getBaseDir(testType), method: 'delete', data: data})
}

export function ChangeProjectSort(testType: string, data: object) {
    return request({url: getBaseDir(testType) + '/sort', method: 'put', data: data})
}

export function GetProjectEnv(testType: string, params: object) {
    return request({url: getEnvBaseDir(testType), method: 'get', params: params})
}

export function PutProjectEnv(testType: string, data: object) {
    return request({url: getEnvBaseDir(testType), method: 'put', data: data})
}

export function PostProjectEnv(testType: string, data: object) {
    return request({url: getEnvBaseDir(testType), method: 'post', data: data})
}

export function SynchronizationProjectEnv(testType: string, data: object) {
    return request({url: getEnvBaseDir(testType) + '/synchronization', method: 'put', data: data})
}

