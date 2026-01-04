import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'
const route: Route[] = [
  {
    path: '/',
    component: Layout,
    redirect: '/index',
    meta: { title: '首页', icon: 'home' },
    children: [
      {
        path: 'index',
        component: createNameComponent(() => import('@/views/dashboard/index.vue')),
        meta: { title: '首页', icon: 'home', hideClose: true }
      }
    ]
  }
]

export default route
