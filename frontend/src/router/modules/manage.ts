import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/manage',
    component: Layout,
    redirect: '/manage/account',
    hideMenu: false,
    meta: { title: '测试管理', icon: 'layers' },
    children: [
      {
        path: 'kym',
        component: createNameComponent(() => import('@/views/manage/kym/index.vue')),
        meta: { title: 'KYM分析', icon: 'leftAndRightBranch' }
      },
      // {
      //   path: 'make-test-case',
      //   component: createNameComponent(() => import('@/views/manage/make-test-case/index.vue')),
      //   meta: { title: '用例编写', icon: 'everyUser' }
      // },
      {
        path: 'account',
        component: createNameComponent(() => import('@/views/manage/env/index.vue')),
        meta: { title: '地址和账号管理', icon: 'everyUser' }
      },
      {
        path: 'bug-track',
        component: createNameComponent(() => import('@/views/manage/bug-track/index.vue')),
        meta: { title: '线上问题跟踪', icon: 'bug' }
      },
      {
        path: 'todo',
        component: createNameComponent(() => import('@/views/manage/todo/index.vue')),
        meta: { title: '待办管理', icon: 'list' }
      }
    ]
  }
]

export default route
