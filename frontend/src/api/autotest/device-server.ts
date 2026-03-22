import request from '@/utils/system/request'
import {baseDirAppTest} from "@/api/base-url";

const baseAddr = baseDirAppTest + '/device/server'

export function GetServerList(params: object) {
    return request({url: baseAddr + '/list', method: 'get', params: params})
}

export function PostServer(data: object) {
    return request({url: baseAddr, method: 'post', data: data})
}

export function GetServer(params: object) {
    return request({url: baseAddr, method: 'get', params: params})
}

export function PutServer(data: object) {
    return request({url: baseAddr, method: 'put', data: data})
}

export function DeleteServer(data: object) {
    return request({url: baseAddr, method: 'delete', data: data})
}

export function ChangeServerSort(data: object) {
    return request({url: baseAddr + '/sort', method: 'put', data: data})
}

export function CopyServer(data: object) {
    return request({url: baseAddr + '/copy', method: 'post', data: data})
}
export function RunServer(data: object) {
    return request({url: baseAddr + '/run', method: 'post', data: data})
}
