import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, getCurrentUser, refreshToken } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  async function loginAction(loginData) {
    try {
      const res = await login(loginData)
      token.value = res.access_token
      localStorage.setItem('access_token', res.access_token)
      await fetchUserInfo()

      if (userInfo.value?.role !== 'admin') {
        await logout()
        throw new Error('您没有管理员权限')
      }

      return true
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  async function fetchUserInfo() {
    try {
      const data = await getCurrentUser()
      userInfo.value = data
      localStorage.setItem('user_info', JSON.stringify(data))
      return data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      logout()
      throw error
    }
  }

  async function handleTokenRefresh() {
    try {
      const res = await refreshToken()
      token.value = res.access_token
      localStorage.setItem('access_token', res.access_token)
      return true
    } catch (error) {
      console.error('Token刷新失败:', error)
      logout()
      return false
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    loginAction,
    fetchUserInfo,
    handleTokenRefresh,
    logout,
  }
})
