import request from '@/utils/system/request'
import {baseDirAppTest} from "@/api/base-url";

const baseAddr = baseDirAppTest + '/device/phone'

export function GetPhoneList(params: object) {
    return request({url: baseAddr + '/list', method: 'get', params: params})
}

export function PostPhone(data: object) {
    return request({url: baseAddr, method: 'post', data: data})
}

export function GetPhone(params: object) {
    return request({url: baseAddr, method: 'get', params: params})
}

export function PutPhone(data: object) {
    return request({url: baseAddr, method: 'put', data: data})
}

export function DeletePhone(data: object) {
    return request({url: baseAddr, method: 'delete', data: data})
}

export function ChangePhoneSort(data: object) {
    return request({url: baseAddr + '/sort', method: 'put', data: data})
}

export function CopyPhone(data: object) {
    return request({url: baseAddr + '/copy', method: 'post', data: data})
}
