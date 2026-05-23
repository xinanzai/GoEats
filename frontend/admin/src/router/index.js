import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', guest: true }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', requiresAuth: true }
      },
      {
        path: 'merchants',
        name: 'Merchants',
        component: () => import('@/views/Merchants.vue'),
        meta: { title: '商家管理', requiresAuth: true }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理', requiresAuth: true }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/Orders.vue'),
        meta: { title: '订单管理', requiresAuth: true }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/Statistics.vue'),
        meta: { title: '数据统计', requiresAuth: true }
      },
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404 - 页面不存在' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title || '外卖点餐系统 - 平台管理端'

  const token = localStorage.getItem('access_token')
  const userInfo = JSON.parse(localStorage.getItem('user_info') || 'null')

  // 白名单页面直接放行
  if (to.meta.guest) {
    // 如果已登录且为管理员，访问登录页时重定向到首页
    if (token && userInfo?.role === 'admin') {
      next('/dashboard')
      return
    }
    next()
    return
  }

  // 需要认证的页面
  if (to.meta.requiresAuth) {
    // 未登录跳转登录页
    if (!token) {
      next('/login')
      return
    }

    // 检查用户角色是否为管理员
    if (userInfo?.role !== 'admin') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      next('/login')
      return
    }

    next()
    return
  }

  // 其他页面直接放行
  next()
})

export default router
