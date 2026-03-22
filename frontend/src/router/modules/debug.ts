import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/debug',
    // @ts-ignore
    hideMenu: true,  // 不显示菜单
    component: Layout,
    redirect: '/debug',
    meta: { title: '调试', icon: 'system' },
    children: [
      {
        path: 'debug',
        component: createNameComponent(() => import('@/views/debug/index.vue')),
        meta: { title: '调试', icon: 'system' }
      },
      {
        path: 'sort-table',
        component: createNameComponent(() => import('@/views/debug/sort-table.vue')),
        meta: { title: '表格拖拽排序', icon: 'system' }
      }
    ]
  }
]

export default route
