import request from '@/utils/system/request'
import {baseDirSystemURL} from '../base-url'

// 获取包列表
export function GetPackageList() {
    return request({ url: baseDirSystemURL + '/package/list', method: 'get'})
}

// 安装包
export function InstallPackage(data: {name: string, version: string}) {
    return request({ url: baseDirSystemURL + '/package/install', method: 'post', data: data })
}
