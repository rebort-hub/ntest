import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/api-test',
    component: Layout,
    redirect: '/api-test/project',
    hideMenu: false,
    meta: { title: '接口自动化', icon: 'api' },
    children: [
      {
        path: 'project',
        component: createNameComponent(() => import('@/views/api-test/project/index.vue')),
        meta: { title: '接口服务管理', icon: 'folderOpen' }
      },
      {
        path: 'api',
        component: createNameComponent(() => import('@/views/api-test/module/index.vue')),
        meta: { title: '接口管理', icon: 'api' }
      },
      {
        path: 'case',
        component: createNameComponent(() => import('@/views/api-test/case-suite/index.vue')),
        meta: { title: '用例管理', icon: 'cubeFive' }
      },
      {
        path: 'task',
        component: createNameComponent(() => import('@/views/api-test/task/index.vue')),
        meta: { title: '任务管理', icon: 'calendar' }
      },
      {
        path: 'report-show',
        // @ts-ignore
        hideMenu: true,  // 不显示菜单
        component: createNameComponent(() => import('@/views/api-test/report/show.vue')),
        meta: { title: '查看测试报告', icon: 'chartHistogram' }
      },
      {
        path: 'report',
        component: createNameComponent(() => import('@/views/api-test/report/index.vue')),
        meta: { title: '测试报告', icon: 'chartHistogram' }
      },
      {
        path: 'ai-code',
        component: createNameComponent(() => import('@/views/api-test/ai-code-generator/index.vue')),
        meta: { title: 'AI接口生成', icon: 'chartHistogram' }
      },
    ]
  }
]

export default route
