import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/config',
    component: Layout,
    redirect: '/config/value',
    hideMenu: false,
    meta: { title: '配置管理', icon: 'setting' },
    children: [
      {
        path: 'type',
        component: createNameComponent(() => import('@/views/config/config-type/index.vue')),
        meta: { title: '配置分类', icon: 'settingThree' }
      },
      {
        path: 'value',
        component: createNameComponent(() => import('@/views/config/config-value/index.vue')),
        meta: { title: '配置参数', icon: 'settingTwo' }
      },
      {
        path: 'run-env',
        component: createNameComponent(() => import('@/views/config/run-env/index.vue')),
        meta: { title: '运行环境', icon: 'mindmapMap' }
      },
      {
        path: 'business',
        component: createNameComponent(() => import('@/views/config/config-business/index.vue')),
        meta: { title: '业务线管理', icon: 'hamburgerButton' }
      },
      {
        path: 'notify',
        component: createNameComponent(() => import('@/views/config/notify/index.vue')),
        meta: { title: '通知管理', icon: 'comment' }
      }
    ]
  }
]

export default route
