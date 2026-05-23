import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/store/auth'

vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  register: vi.fn(),
  getCurrentUser: vi.fn(),
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
  })

  describe('computed properties', () => {
    it('should be logged in when token exists', () => {
      authStore.token = 'test-token'
      expect(authStore.isLoggedIn).toBe(true)
    })

    it('should return userProfile when userInfo exists', () => {
      authStore.userInfo = { username: 'test', role: 'user' }
      expect(authStore.userProfile).toEqual({ username: 'test', role: 'user' })
    })
  })

  describe('logout', () => {
    it('should clear token and userInfo', () => {
      authStore.token = 'test-token'
      authStore.userInfo = { role: 'user' }
      authStore.logout()
      expect(authStore.token).toBe('')
      expect(authStore.userInfo).toBeNull()
    })

    it('should remove items from localStorage', () => {
      localStorage.setItem('access_token', 'test-token')
      localStorage.setItem('user_info', JSON.stringify({ role: 'user' }))
      authStore.logout()
      expect(localStorage.getItem('access_token')).toBeNull()
      expect(localStorage.getItem('user_info')).toBeNull()
    })
  })
})
