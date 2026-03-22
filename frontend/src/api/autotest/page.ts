import request from '@/utils/system/request'

const getBaseDir = (testType: string) => {
    return `/api/${testType}-test` + '/page'
}

export function GetPageList(testType: string, params: object) {
    return request({url: getBaseDir(testType) + '/list', method: 'get', params: params})
}

export function PostPage(testType: string, data: object) {
    return request({url: getBaseDir(testType), method: 'post', data: data})
}

export function GetPage(testType: string, params: object) {
    return request({url: getBaseDir(testType), method: 'get', params: params})
}

export function PutPage(testType: string, data: object) {
    return request({url: getBaseDir(testType), method: 'put', data: data})
}

export function DeletePage(testType: string, data: object) {
    return request({url: getBaseDir(testType), method: 'delete', data: data})
}

export function ChangePageSort(testType: string, data: object) {
    return request({url: getBaseDir(testType) + '/sort', method: 'put', data: data})
}


export function CopyPage(testType: string, data: object) {
    return request({url: getBaseDir(testType) + '/copy', method: 'post', data: data})
}
