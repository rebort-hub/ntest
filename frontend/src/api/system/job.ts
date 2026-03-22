import request from '@/utils/system/request'
import {baseDirSystemURL} from '../base-url'

const currentBaseDir = baseDirSystemURL + '/job'

// 任务方法列表
export function GetJobFuncList() {
    return request({ url: currentBaseDir + '/func-list', method: 'get'})
}

// 任务列表
export function GetJobList(params: object) {
    return request({ url: currentBaseDir + '/list', method: 'get', params: params })
}

// 执行任务
export function JobRun(data: object) {
    return request({ url: currentBaseDir + '/run', method: 'post', data: data })
}

// 执行任务记录列表
export function GetJobRunLogList(params: object) {
    return request({ url: currentBaseDir + '/log-list', method: 'get', params: params })
}

// 执行任务记录
export function GetJobRunLog(params: object) {
    return request({ url: currentBaseDir + '/log', method: 'get', params: params })
}

// 获取任务信息
export function GetJob(params: object) {
    return request({ url: currentBaseDir, method: 'get', params: params })
}

// 新增任务
export function PostJob(data: object) {
    return request({ url: currentBaseDir, method: 'post', data: data })
}

// 删除任务
export function DeleteJob(data: object) {
    return request({ url: currentBaseDir, method: 'delete', data: data })
}
