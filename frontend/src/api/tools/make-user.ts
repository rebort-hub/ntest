import request from '@/utils/system/request'
import {baseDirTool} from '../base-url'

const currentBaseDir = baseDirTool


export function MakeUser(data: object) {
    return request({url: currentBaseDir + '/make-user', method: 'post', data: data})
}

export function ExportAsContact(data: object) {
    return request({url: currentBaseDir + '/make-user/contact/download', method: 'post', data: data, responseType: 'blob' })
}
