import type { Route } from '../index.type'
import { createNameComponent } from '../createNode'

const route: Route[] = [
  {
    path: '/saml',
    redirect: '/saml/callback',
    hideMenu: true,
    children: [
      {
        path: 'callback',
        component: createNameComponent(() => import('@/views/system/login/saml-callback.vue')),
        meta: { 
          title: 'SAML登录回调', 
          hideTabs: true,
          hideMenu: true,
          noAuth: true  // 不需要认证
        }
      }
    ]
  }
]

export default route