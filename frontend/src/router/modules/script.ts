import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/script',
    component: Layout,
    redirect: '/script/python',
    hideMenu: false,
    meta: { title: '脚本管理', icon: 'code' },
    children: [
      {
        path: 'python',
        component: createNameComponent(() => import('@/views/assist/script/index.vue')),
        meta: { title: '脚本管理中心', icon: 'code' }
      }
    ]
  }
]

export default route
