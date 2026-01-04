import type { Route } from '../index.type'
import Layout from '@/layout/index.vue'
import { createNameComponent } from '../createNode'
const route: Route[] = [
  {
    path: '/default',
    component: Layout,
    redirect: '/404',
    hideMenu: true,
    meta: { title: '系统管理1', icon: 'system' },
    children: [
      {
        path: '/404',
        component: createNameComponent(() => import('@/views/system/404.vue')),
        meta: { title: '404', hideTabs: true, icon: 'system' }
      },
      {
        path: '/401',
        component: createNameComponent(() => import('@/views/system/401.vue')),
        meta: { title: '401', hideTabs: true, icon: 'system' }
      },
      {
        path: '/redirect/:path(.*)',
        component: createNameComponent(() => import('@/views/system/redirect.vue')),
        meta: { title: '重定向页面', hideTabs: true, icon: 'system' }
      }
    ]
  },
  {
    path: '/self-login',
    component: createNameComponent(() => import('@/views/system/login/self-login.vue')),
    hideMenu: true,
    meta: { title: '登录', hideTabs: false, icon: 'system' }
  },
  {
    path: '/login',
    component: createNameComponent(() => import('@/views/system/login/self-login.vue')),
    hideMenu: true,
    meta: { title: '登录', hideTabs: false, icon: 'system' }
  },
  {
    path: '/sso-login',
    component: createNameComponent(() => import('@/views/system/login/sso-login.vue')),
    hideMenu: true,
    meta: { title: 'sso登录', hideTabs: false, icon: 'system' }
  },
  // {
  //   // 找不到路由重定向到404页面
  //   path: "/:pathMatch(.*)",
  //   component: Layout,
  //   redirect: "/404",
  //   hideMenu: true,
  //   meta: { title: '' },
  // },
]

export default route
