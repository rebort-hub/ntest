import request from '@/utils/system/request'
import {baseDirTool} from '../base-url'

const currentBaseDir = baseDirTool


export function GetExamination() {
    return request({ url: currentBaseDir + '/examination', method: 'get' })
}
