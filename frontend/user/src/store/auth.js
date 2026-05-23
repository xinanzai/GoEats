import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getCurrentUser } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const userProfile = computed(() => userInfo.value)

  async function login(loginData) {
    const res = await loginApi(loginData)
    token.value = res.access_token
    localStorage.setItem('access_token', res.access_token)
    await fetchUserInfo()
  }

  async function register(registerData) {
    await registerApi(registerData)
  }

  async function fetchUserInfo() {
    const token = localStorage.getItem('access_token')
    if (!token) {
      logout()
      throw new Error('未登录')
    }
    try {
      const data = await getCurrentUser()
      userInfo.value = data
      localStorage.setItem('user_info', JSON.stringify(data))
    } catch (error) {
      console.error('获取用户信息失败:', error)
      logout()
      throw error
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
    userProfile,
    login,
    register,
    fetchUserInfo,
    logout,
  }
})
