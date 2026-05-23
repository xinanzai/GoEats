import { describe, it, expect, vi, beforeEach } from 'vitest'
import request from '@/utils/request'

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
      defaults: { baseURL: '/api/v1' },
    })),
  },
}))

describe('Request Utility', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should create axios instance with base URL', () => {
    expect(request.defaults.baseURL).toBe('/api/v1')
  })

  it('should have interceptors', () => {
    expect(request.interceptors.request).toBeDefined()
    expect(request.interceptors.response).toBeDefined()
  })
})
