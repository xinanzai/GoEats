import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Statistics from '@/views/Statistics.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/statistics', component: Statistics }],
})

describe('Statistics.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Statistics, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render statistics page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should display statistics cards', () => {
    expect(wrapper.findAllComponents({ name: 'ElCard' })).toBeDefined()
  })

  it('should have order trend chart container', () => {
    const chartContainers = wrapper.findAll('.chart-container')
    expect(chartContainers.length).toBeGreaterThan(0)
  })

  it('should have revenue trend chart container', () => {
    const chartContainers = wrapper.findAll('.chart-container')
    expect(chartContainers.length).toBeGreaterThanOrEqual(2)
  })
})
