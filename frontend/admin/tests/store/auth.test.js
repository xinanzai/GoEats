import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, activePinia } from 'pinia'
import { useAuthStore } from '@/store/auth'

vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  getCurrentUser: vi.fn(),
  refreshToken: vi.fn(),
}))

describe('Auth Store', () => {
  let authStore
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    authStore = useAuthStore(pinia)
    localStorage.clear()
  })

  describe('initial state', () => {
    it('should initialize with empty token', () => {
      expect(authStore.token).toBe('')
    })

    it('should initialize with null userInfo', () => {
      expect(authStore.userInfo).toBeNull()
    })

    it('should not be logged in initially', () => {
      expect(authStore.isLoggedIn).toBe(false)
    })

    it('should not be admin initially', () => {
      expect(authStore.isAdmin).toBe(false)
    })
  })

  describe('computed properties', () => {
    it('should be logged in when token exists', () => {
      authStore.token = 'test-token'
      expect(authStore.isLoggedIn).toBe(true)
    })

    it('should be admin when role is admin', () => {
      authStore.userInfo = { role: 'admin' }
      expect(authStore.isAdmin).toBe(true)
    })

    it('should not be admin when role is not admin', () => {
      authStore.userInfo = { role: 'user' }
      expect(authStore.isAdmin).toBe(false)
    })
  })

  describe('logout', () => {
    it('should clear token and userInfo', () => {
      authStore.token = 'test-token'
      authStore.userInfo = { role: 'admin' }
      authStore.logout()
      expect(authStore.token).toBe('')
      expect(authStore.userInfo).toBeNull()
    })

    it('should remove items from localStorage', () => {
      localStorage.setItem('access_token', 'test-token')
      localStorage.setItem('user_info', JSON.stringify({ role: 'admin' }))
      authStore.logout()
      expect(localStorage.getItem('access_token')).toBeNull()
      expect(localStorage.getItem('user_info')).toBeNull()
    })
  })
})
