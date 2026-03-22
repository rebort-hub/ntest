import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'

const route: Route[] = [
    {
        path: '/playwright-agents',
        component: Layout,
        redirect: '/playwright-agents/dashboard',
        hideMenu: false,
        meta: { title: 'Playwright', icon: 'code' },
        children: [
            {
                path: 'dashboard',
                component: createNameComponent(() => import('@/views/playwright-agents/dashboard/index.vue')),
                meta: { title: 'Playwright控制台', icon: 'chartHistogramOne' }
            },
            {
                path: 'execution',
                component: createNameComponent(() => import('@/views/playwright-agents/execution/index.vue')),
                meta: { title: 'Playwright执行记录', icon: 'list' }
            }
        ]
    },
    // 独立路由
    {
        path: '/playwright-agents-planner',
        component: Layout,
        redirect: '/playwright-agents-planner/index',
        meta: { hidden: true },
        children: [
            {
                path: 'index',
                component: createNameComponent(() => import('@/views/playwright-agents/planner/index.vue')),
                meta: { title: '测试规划器', icon: 'bookOpen', hideTabs: false }
            }
        ]
    },
    {
        path: '/playwright-agents-generator',
        component: Layout,
        redirect: '/playwright-agents-generator/index',
        meta: { hidden: true },
        children: [
            {
                path: 'index',
                component: createNameComponent(() => import('@/views/playwright-agents/generator/index.vue')),
                meta: { title: '代码生成器', icon: 'code', hideTabs: false }
            }
        ]
    },
    {
        path: '/playwright-agents-healer',
        component: Layout,
        redirect: '/playwright-agents-healer/index',
        meta: { hidden: true },
        children: [
            {
                path: 'index',
                component: createNameComponent(() => import('@/views/playwright-agents/healer/index.vue')),
                meta: { title: '自愈修复器', icon: 'tool', hideTabs: false }
            }
        ]
    }
]

export default route
