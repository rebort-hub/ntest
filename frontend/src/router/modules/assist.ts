import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/assist',
    component: Layout,
    redirect: '/assist/hit',
    hideMenu: false,
    meta: { title: '自动化辅助中心', icon: 'branchTwo' },
    children: [
      {
        path: 'call-back',
        component: createNameComponent(() => import('@/views/assist/call-back/index.vue')),
        meta: { title: '回调记录', icon: 'return' }
      },
      {
        path: 'file',
        component: createNameComponent(() => import('@/views/assist/files/index.vue')),
        meta: { title: '文件管理', icon: 'folderOpen' }
      },
      {
        path: 'error-record',
        component: createNameComponent(() => import('@/views/assist/error-record/index.vue')),
        meta: { title: '执行错误记录', icon: 'videocameraOne' }
      },
      {
        path: 'auto-test-user',
        component: createNameComponent(() => import('@/views/assist/auto-test-user/index.vue')),
        meta: { title: '自动化用户数据', icon: 'avatar' }
      },
      {
        path: 'hit',
        component: createNameComponent(() => import('@/views/assist/hits/index.vue')),
        meta: { title: '自动化问题记录', icon: 'alarm' }
      }
    ]
  }
]

export default route
