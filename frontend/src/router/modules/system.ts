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
      {
        path: 'package-manage',
        component: createNameComponent(() => import('@/views/system/package-manage/index.vue')),
        meta: { title: 'python包管理', icon: 'figmaComponent' }
      },
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
        path: 'platform',
        component: createNameComponent(() => import('@/views/system/platform/index.vue')),
        meta: { title: '平台使用分析', hideTabs: false, icon: 'chartHistogram' },
        children: [
          {
            path: 'overview',
            component: createNameComponent( () => import('@/views/system/platform/overview/index.vue')),
            meta: { title: '数据总览', icon: 'chartHistogramOne' }
          },
          {
            path: 'analyse',
            component: createNameComponent( () => import('@/views/system/platform/analyse/index.vue')),
            meta: { title: '业务线分析', icon: 'chartProportion' }
          }
        ]
      },
    ]
  }
]

export default route
