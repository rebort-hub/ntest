import request from '@/utils/system/request'

const getBaseDir = (testType: string) => {
    return `/api/${testType}-test` + '/step'
}

export function PostStep(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'post', data: data })
}

export function GetStep(testType: string, params: object) {
    return request({ url: getBaseDir(testType), method: 'get', params: params })
}

export function PutStep(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'put', data: data })
}

export function DeleteStep(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'delete', data: data })
}

export function ChangeStepStatus(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/status', method: 'put', data: data })
}

export function PutStepHost(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/host', method: 'put', data: data })
}

export function GetStepList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/list', method: 'get', params: params })
}

export function ChangeStepSort(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/sort', method: 'put', data: data })
}

export function CopyStep(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/copy', method: 'post', data: data })
}

export function ChangeStepElement(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/element', method: 'put', data: data })
}

export function GetKeyBoardCodeMappingList() {
    return request({ url: getBaseDir('ui') + '/key-board-code', method: 'get' })
}

export function GetAssertMappingList(testType: string) {
    return request({ url: getBaseDir(testType) + '/assert-mapping', method: 'get' })
}

export function GetExtractMappingList(testType: string) {
    return request({ url: getBaseDir(testType) + '/extract-mapping', method: 'get' })
}

export function GetExecuteMappingList(testType: string) {
    return request({ url: getBaseDir(testType) + '/execute-mapping', method: 'get' })
}
