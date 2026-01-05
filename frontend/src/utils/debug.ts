// 调试工具
export const debugRouter = {
    // 检查路由权限
    checkPermissions: () => {
        const permissions = localStorage.getItem('permissions')
        const isAdmin = localStorage.getItem('isAdmin')
        const accessToken = localStorage.getItem('accessToken')

        console.group('🔍 路由权限调试信息')
        console.log('访问令牌:', accessToken ? '✅ 存在' : '❌ 不存在')
        console.log('管理员权限:', isAdmin === '1' ? '✅ 是管理员' : '❌ 非管理员')
        console.log('用户权限列表:', permissions ? JSON.parse(permissions) : '❌ 无权限')
        console.groupEnd()

        return {
            hasToken: !!accessToken,
            isAdmin: isAdmin === '1',
            permissions: permissions ? JSON.parse(permissions) : []
        }
    },

    // 检查特定路径权限
    checkPathPermission: (path: string) => {
        const { permissions, isAdmin } = debugRouter.checkPermissions()

        if (isAdmin) {
            console.log(`🔓 管理员权限，允许访问: ${path}`)
            return true
        }

        const hasPermission = permissions.some((permission: string) =>
            permission === path || path.startsWith(permission + '/')
        )

        console.log(`🔍 路径权限检查: ${path}`)
        console.log(`结果: ${hasPermission ? '✅ 有权限' : '❌ 无权限'}`)

        return hasPermission
    }
}

// 在开发环境下暴露到全局
// @ts-ignore
if (import.meta.env && import.meta.env.DEV) {
    // @ts-ignore
    window.debugRouter = debugRouter
}