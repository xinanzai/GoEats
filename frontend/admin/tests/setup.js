import { config } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

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

config.global.plugins = [ElementPlus]

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  config.global.components[key] = component
}

global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}
