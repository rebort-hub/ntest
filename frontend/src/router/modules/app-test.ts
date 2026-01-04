import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/app-test',
    component: Layout,
    redirect: '/app-test/project',
    hideMenu: false,
    meta: { title: 'App自动化', icon: 'android' },
    children: [
      {
        path: 'device',
        component: createNameComponent(() => import('@/views/app-test/device/index.vue')),
        meta: { title: '设备管理', icon: 'devices' }
      },
      {
        path: 'project',
        component: createNameComponent(() => import('@/views/app-test/project/index.vue')),
        meta: { title: 'App管理', icon: 'android' }
      },
      {
        path: 'page',
        component: createNameComponent(() => import('@/views/app-test/module/index.vue')),
        meta: { title: '页面管理', icon: 'bookOpen' }
      },
      {
        path: 'case',
        component: createNameComponent(() => import('@/views/app-test/case-suite/index.vue')),
        meta: { title: '用例管理', icon: 'cubeFive' }
      },
      {
        path: 'task',
        component: createNameComponent(() => import('@/views/app-test/task/index.vue')),
        meta: { title: '任务管理', icon: 'calendar' }
      },
      {
        path: 'report-show',
        // @ts-ignore
        hideMenu: true,  // 不显示按钮
        component: createNameComponent(() => import('@/views/app-test/report/show.vue')),
        meta: { title: '查看测试报告', icon: 'chartHistogram' }
      },
      {
        path: 'report',
        component: createNameComponent(() => import('@/views/app-test/report/index.vue')),
        meta: { title: '测试报告', icon: 'chartHistogram' }
      },
    ]
  }
]

export default route
