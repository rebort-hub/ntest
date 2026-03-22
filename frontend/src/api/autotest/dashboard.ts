import request from '@/utils/system/request'
import {baseDirApiTest} from '../base-url'
const currentBaseDir = baseDirApiTest + '/dashboard'

// title统计
export function getTitleCount() {
    return request({ url: currentBaseDir + '/card', method: 'get' })
}

// 对应的明细统计, detailType 对应的项，project、task、report...
export function getDetailCount(detailType: string) {
    return request({ url: currentBaseDir + '/' + detailType, method: 'get' })
}

