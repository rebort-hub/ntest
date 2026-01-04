import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/tools',
    component: Layout,
    redirect: '/tools/data-pool',
    hideMenu: false,
    meta: { title: '造数管理', icon: 'tool' },
    children: [
      {
        path: 'make-data',
        component: createNameComponent(() => import('@/views/tools/make-business-data/index.vue')),
        meta: { title: '造数据', icon: 'followUpDateSort' }
      },
      {
        path: 'data-pool',
        component: createNameComponent(() => import('@/views/tools/data-pool/index.vue')),
        meta: { title: '数据连接池', icon: 'dataThree' }
      },
      {
        path: 'make-user-info',
        component: createNameComponent(() => import('@/views/tools/make-user-info/index.vue')),
        meta: { title: '用户生成', icon: 'idCardH' }
      },
      {
        path: 'queue',
        component: createNameComponent(() => import('@/views/tools/queue/queue-instance/index.vue')),
        meta: { title: '消息队列', icon: 'databaseEnter' }
      },
      {
        path: 'token',
        component: createNameComponent(() => import('@/views/tools/parse-token/index.vue')),
        meta: { title: '解析token', icon: 'userPositioning' }
      },
      {
        path: 'code-diff',
        component: createNameComponent(() => import('@/views/tools/code-diff/index.vue')),
        meta: { title: '代码对比', icon: 'fourArrows' } // <iconpark-icon name=""></iconpark-icon>
      },
      {
        path: 'shell-mock',
        component: createNameComponent(() => import('@/views/tools/shell-command/index.vue')),
        meta: { title: 'shell造数据', icon: 'code' } // <iconpark-icon name=""></iconpark-icon>
      }
    ]
  }
]

export default route
