import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/ui-test',
    component: Layout,
    redirect: '/ui-test/project',
    hideMenu: false,
    meta: { title: 'UI自动化', icon: 'bookOpen' },
    children: [
      {
        path: 'project',
        component: createNameComponent(() => import('@/views/ui-test/project/index.vue')),
        meta: { title: '项目管理', icon: 'folderOpen' }
      },
      {
        path: 'page',
        component: createNameComponent(() => import('@/views/ui-test/module/index.vue')),
        meta: { title: '页面管理', icon: 'bookOpen' }
      },
      {
        path: 'case',
        component: createNameComponent(() => import('@/views/ui-test/case-suite/index.vue')),
        meta: { title: '用例管理', icon: 'cubeFive' }
      },
      {
        path: 'task',
        component: createNameComponent(() => import('@/views/ui-test/task/index.vue')),
        meta: { title: '任务管理', icon: 'calendar' }
      },
      {
        path: 'report-show',
        // @ts-ignore
        hideMenu: true,  // 不显示按钮
        component: createNameComponent(() => import('@/views/ui-test/report/show.vue')),
        meta: { title: '查看测试报告', icon: 'chartHistogram' }
      },
      {
        path: 'report',
        component: createNameComponent(() => import('@/views/ui-test/report/index.vue')),
        meta: { title: '测试报告', icon: 'chartHistogram' }
      },
    ]
  }
]

export default route
