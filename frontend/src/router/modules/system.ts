import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'
const route: Route[] = [
  {
    path: '/system',
    component: Layout,
    redirect: '/system/user',
    hideMenu: false,
    meta: { title: '系统管理', icon: 'system', alwaysShow: false },
    children: [
      // {
      //   path: 'package-manage',
      //   component: createNameComponent(() => import('@/views/system/package-manage/index.vue')),
      //   meta: { title: 'python包管理', icon: 'figmaComponent' }
      // },
      {
        path: 'permission',
        component: createNameComponent(() => import('@/views/system/permission/index.vue')),
        meta: { title: '权限管理', icon: 'permissions' }
      },
      {
        path: 'role',
        component: createNameComponent(() => import('@/views/system/role/index.vue')),
        meta: { title: '角色管理', icon: 'people' }
      },
      {
        path: 'user',
        component: createNameComponent(() => import('@/views/system/user/index.vue')),
        meta: { title: '用户管理', icon: 'user' }
      },
      {
        path: 'saml',
        component: createNameComponent(() => import('@/views/system/saml/index.vue')),
        meta: { title: 'SAML SSO配置', icon: 'key' }
      },
      {
        path: 'saml/test',
        component: createNameComponent(() => import('@/views/system/saml/test.vue')),
        meta: { title: 'SAML功能测试', icon: 'experiment', hideTabs: true }
      },
      {
        path: 'job',
        component: createNameComponent(() => import('@/views/system/job/index.vue')),
        meta: { title: '系统定时任务', icon: 'calendar' }
      },
      {
        path: 'error-record',
        component: createNameComponent(() => import('@/views/system/error-record/index.vue')),
        meta: { title: '系统错误记录', icon: 'alarm' }
      },
      {
        path: 'platform-overview',
        component: createNameComponent(() => import('@/views/system/platform/overview/index.vue')),
        meta: { title: '数据总览', icon: 'chartHistogramOne' }
      },
      {
        path: 'platform-analyse',
        component: createNameComponent(() => import('@/views/system/platform/analyse/index.vue')),
        meta: { title: '业务线分析', icon: 'chartProportion' }
      },
    ]
  }
]

export default route
