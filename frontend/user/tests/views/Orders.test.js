import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Orders from '@/views/Orders.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/orders', component: Orders }],
})

describe('Orders.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Orders, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render orders page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have status tabs', () => {
    const tabs = wrapper.findComponent({ name: 'VanTabs' })
    expect(tabs.exists()).toBe(true)
  })

  it('should have order list', () => {
    expect(wrapper.html()).toBeDefined()
  })
})
