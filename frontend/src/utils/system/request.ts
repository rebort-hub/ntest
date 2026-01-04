import axios, {AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse} from 'axios'
import store from '@/store'
import router from '@/router/index'
import {ElMessage} from 'element-plus'
import {refreshTokenDir} from "@/api/system/user";

// 是否正在刷新的标记
let isRefreshing = false

// 重试队列，每一项将是一个待执行的函数形式
let retryRequestList: any[] = []

// 当access-token过期时，用refresh-token获取新的token
const refreshToken = () => {
    const newService: AxiosInstance = axios.create({baseURL: '', timeout: 500})
    newService.interceptors.request.use(
        // @ts-ignore
        (config: AxiosRequestConfig) => {
            // @ts-ignore
            config.headers['refresh-token'] = localStorage.getItem('refreshToken')
            return config
        }
    )
    return newService.get(refreshTokenDir)
}

const service: AxiosInstance = axios.create({
    baseURL: '', //baseURL,
    timeout: 60000  // 毫秒
})

const getRequestId = () =>{
    // 13位毫秒时间戳 + 6位随机数 = 19位
    const randomSuffix = Math.floor(Math.random() * 1000)
        .toString().padStart(6, '0');
    return Date.now().toString() + randomSuffix
}

// 请求拦截
service.interceptors.request.use(
    // @ts-ignore
    (config: AxiosRequestConfig) => {
        // @ts-ignore
        config.headers['access-token'] = localStorage.getItem('accessToken')
        // @ts-ignore
        config.headers['request-id'] = getRequestId()
        // @ts-ignore
        config.headers['device-id'] = localStorage.getItem('deviceId')
        return config
    },
    (error: AxiosError) => {
        ElMessage.error('发送请求失败')
        return Promise.reject(error)
    }
)

// 响应拦截
service.interceptors.response.use(
    (response: AxiosResponse) => {
        const responseBody = response.data

        // @ts-ignore
        if (response.config.url.indexOf('redirect-uri') === -1) { // 获取sso登录地址，直接返回
            // 身份验证相关
            if (responseBody.status === 401) { // 如果返回状态码为401，则跳转到登录页面
                const config = response.config

                if (!isRefreshing) {
                    isRefreshing = true
                    return refreshToken().then(refreshRes => {
                        const refreshResBody = refreshRes.data

                        // refreshToken失效
                        if (refreshResBody.status === 401) {
                            if (refreshResBody.data) { // 返回了登录地址，则自动重定向到对应的登录页（SSO）
                                window.location.href = refreshResBody.data
                            } else {  // 没有返回登录地址，则重定向平台登录页
                                let fullPath = router.currentRoute.value.fullPath
                                window.location.href = fullPath.indexOf('redirect') !== -1 ? fullPath : `/self-login`
                            }
                        } else {
                            const access_token = refreshResBody.data.access_token
                            service.defaults.headers['access-token'] = access_token
                            localStorage.setItem('accessToken', access_token)
                            localStorage.setItem('userName', refreshResBody.data.name)
                            localStorage.setItem('account', refreshResBody.data.account)
                            localStorage.setItem('permissions', JSON.stringify(refreshResBody.data.front_permissions))
                            localStorage.setItem('business', JSON.stringify(refreshResBody.data.business_list))
                            localStorage.setItem('isAdmin', refreshResBody.data.front_permissions.indexOf('admin') !== -1 ? '1' : '0')

                            config.headers['access-token'] = access_token
                            config.baseURL = '' // url已经带上了/api，避免出现/api/api的情况

                            // 已经刷新了token，将所有队列中的请求进行重试
                            retryRequestList.forEach(retryRequest => retryRequest(access_token))
                            retryRequestList = []
                            return service(config)
                        }
                    }).catch(() => {

                    }).finally(() => {
                        isRefreshing = false
                    })
                } else {
                    // 正在刷新token，返回一个未执行resolve的promise
                    return new Promise((resolve) => {
                        // 将resolve放进队列，用一个函数形式来保存，等token刷新后直接执行
                        retryRequestList.push((access_token: any) => {
                            config.baseURL = ''
                            config.headers['access-token'] = access_token
                            resolve(service(config))
                        })
                    })
                }
            } else if (responseBody.status === 403) {
                ElMessage.error(responseBody.message)
            } else {
                // 业务逻辑相关
                // @ts-ignore
                if (response.config.method !== 'get') {  // 非获取的接口，显示响应信息
                    if (responseBody.status >= 500) {
                        ElMessage.error(responseBody.message)
                        return
                    } else if (responseBody.status >= 400) {
                        if (typeof responseBody.message === 'object'){ // 脚本保存，脚本语法错误
                            ElMessage.warning(`${responseBody.message.msg}\n${responseBody.message.result}`)
                        }else {
                            ElMessage.warning(responseBody.message)
                        }
                        return
                    } else {
                        // @ts-ignore
                        if (response.config.url.indexOf('download') === -1 && 
                            response.config.url.indexOf('/steps') === -1 &&
                            response.config.url.indexOf('/requirements/') === -1 &&
                            response.config.url.indexOf('/knowledge/') === -1) { // 不显示测试步骤操作和需求管理、知识库的成功消息
                            ElMessage.success(responseBody.message)
                        }
                        return responseBody
                    }
                }
            }
        }
        return responseBody
    },
    (error: AxiosError) => {
        const badMessage: any = error.message || error
        const code = parseInt(badMessage.toString().replace('Error: Request failed with status code ', ''))
        showError({code, message: badMessage})
        return Promise.reject(error)
    }
)

// 错误处理
function showError(error: any) {
    // token过期，清除本地数据，并跳转至登录页面
    if (error.code === 403) {
        // to re-login
        store.dispatch('user/loginOut')
    } else {
        ElMessage({
            message: error.msg || error.message || '服务异常',
            type: 'error',
            duration: 3 * 1000
        })
    }

}

export default service
