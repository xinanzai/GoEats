import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页', keepAlive: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', guest: true }
  },
  {
    path: '/merchant/:id',
    name: 'MerchantDetail',
    component: () => import('@/views/MerchantDetail.vue'),
    meta: { title: '商家详情' }
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('@/views/Cart.vue'),
    meta: { title: '购物车', requiresAuth: true }
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('@/views/Checkout.vue'),
    meta: { title: '确认订单', requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/views/Orders.vue'),
    meta: { title: '我的订单', requiresAuth: true }
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: () => import('@/views/OrderDetail.vue'),
    meta: { title: '订单详情', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/addresses',
    name: 'Addresses',
    component: () => import('@/views/Addresses.vue'),
    meta: { title: '地址管理', requiresAuth: true }
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
  document.title = to.meta.title || '外卖点餐系统'

  const token = localStorage.getItem('access_token')
  const authStore = useAuthStore()

  // 白名单页面（游客可访问）
  if (to.meta.guest) {
    // 如果已登录，访问登录/注册页时重定向到首页
    if (token && (to.name === 'Login' || to.name === 'Register')) {
      next('/')
      return
    }
    next()
    return
  }

  // 需要认证的页面
  if (to.meta.requiresAuth) {
    if (!token) {
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      })
      return
    }
    // 如果token存在但没有用户信息，尝试获取
    if (!authStore.userInfo) {
      try {
        await authStore.fetchUserInfo()
      } catch (error) {
        authStore.logout()
        next({
          path: '/login',
          query: { redirect: to.fullPath },
        })
        return
      }
    }
    next()
    return
  }

  // 其他页面直接放行
  next()
})

router.afterEach(() => {
  // 页面加载完成后滚动到顶部
  window.scrollTo(0, 0)
})

export default router
