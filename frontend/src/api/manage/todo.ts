import request from '@/utils/system/request'
import {baseDirManage} from '../base-url'

const currentBaseDir = baseDirManage + '/todo'


export function GetTodoList(params: object) {
    return request({url: currentBaseDir + '/list', method: 'get', params: params})
}

export function ChangeTodoSort(data: object) {
    return request({url: currentBaseDir + '/sort', method: 'put', data: data})
}

export function ChangeTodoStatus(data: object) {
    return request({url: currentBaseDir + '/status', method: 'put', data: data})
}

export function GetTodo(params: object) {
    return request({url: currentBaseDir, method: 'get', params: params})
}

export function PostTodo(data: object) {
    return request({url: currentBaseDir, method: 'post', data: data})
}

export function PutTodo(data: object) {
    return request({url: currentBaseDir, method: 'put', data: data})
}

export function DeleteTodo(data: object) {
    return request({url: currentBaseDir, method: 'delete', data: data})
}
