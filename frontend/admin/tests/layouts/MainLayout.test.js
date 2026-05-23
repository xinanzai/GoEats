import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: 'home' } },
    { path: '/dashboard', component: { template: 'dashboard' } },
  ],
})

describe('MainLayout.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(MainLayout, {
      global: {
        plugins: [createPinia(), router],
        stubs: {
          'router-view': true,
          'router-link': true,
          'el-icon': true,
        },
      },
    })
  })

  it('should render the layout', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have sidebar menu', () => {
    expect(wrapper.findComponent({ name: 'ElMenu' }).exists()).toBe(true)
  })

  it('should have logout button', () => {
    const logoutButton = wrapper.find('button')
    expect(logoutButton.exists()).toBe(true)
  })

  it('should have router-view', () => {
    expect(wrapper.findComponent({ name: 'RouterView' }).exists()).toBe(true)
  })
})
