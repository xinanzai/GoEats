import { config } from '@vue/test-utils'
import Vant from 'vant'

const localStorageMock = (() => {
  let store = {}
  return {
    getItem(key) {
      return store[key] ?? null
    },
    setItem(key, value) {
      store[key] = value.toString()
    },
    removeItem(key) {
      delete store[key]
    },
    clear() {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})
Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
})

config.global.plugins = [Vant]

global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}
