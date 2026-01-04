import request from '@/utils/system/request'

const getBaseDir = (testType: string) => {
    return `/api/${testType}-test` + '/report'
}

export function DeleteReport(testType: string, data: object) {
    return request({ url: getBaseDir(testType), method: 'delete', data: data })
}

export function GetReport(testType: string, params: object) {
    return request({ url: getBaseDir(testType), method: 'get', params: params })
}

export function GetReportList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/list', method: 'get', params: params })
}

export function NotifyReport(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/notify', method: 'post', data: data })
}

export function GetReportStatus(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/status', method: 'get', data: null, params: params })
}

export function GetReportShowId(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/show-id', method: 'get', data: null, params: params })
}

export function ReportAsCase(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/as-case', method: 'post', data: data })
}

export function GetReportSuiteList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/suite-list', method: 'get', data: null, params: params })
}

export function GetReportCaseList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/case-list', method: 'get', data: null, params: params })
}

export function GetReportRerunCaseList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/rerun-case', method: 'get', data: null, params: params })
}

export function GetReportCaseDetail(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/case', method: 'get', data: null, params: params })
}

export function GetReportStepList(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/step-list', method: 'get', data: null, params: params })
}

export function GetReportStepDetail(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/step', method: 'get', data: null, params: params })
}

export function GetReportStepImg(testType: string, params: object) {
    return request({ url: getBaseDir(testType) + '/step-img', method: 'get', params: params })
}

export function ChangeReportStepStatus(testType: string, data: object) {
    return request({ url: getBaseDir(testType) + '/step-status', method: 'put', data: data })
}
