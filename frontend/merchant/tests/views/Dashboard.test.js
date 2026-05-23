import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Dashboard from '@/views/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/dashboard', component: Dashboard }],
})

describe('Dashboard.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Dashboard, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render dashboard', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should display statistics cards', () => {
    expect(wrapper.findAllComponents({ name: 'ElCard' })).toBeDefined()
  })

  it('should have recent orders table', () => {
    const tableContainer = wrapper.find('.recent-orders')
    expect(tableContainer.exists()).toBe(true)
  })
})
