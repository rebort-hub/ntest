import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/flowchart',
    component: Layout,
    redirect: '/flowchart/editor',
    hideMenu: false,
    meta: { title: '流程图管理', icon: 'flowChart' },
    children: [
      {
        path: 'editor',
        component: createNameComponent(() => import('@/views/flowchart/editor/index.vue')),
        meta: { title: '流程图编辑器', icon: 'flowChart' }
      }
    ]
  }
]

export default route