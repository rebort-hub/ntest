import request from '@/utils/system/request'
import {baseDirApiTest} from '../base-url'
const currentBaseDir = baseDirApiTest + '/stat'

// 使用总览卡片
export function GetUseCard(params: object) {
    return request({ url: currentBaseDir + '/use-card', method: 'get', params: params })
}

// 使用总览柱状图
export function GetUseChart(params: object) {
    return request({ url: currentBaseDir + '/use-chart', method: 'get', params: params })
}

// 业务线分析
export function GetAnalyseChart(params: object) {
    return request({ url: currentBaseDir + '/analyse', method: 'get', params: params })
}
