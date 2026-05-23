import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Login from '@/views/Login.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: { template: 'login' } },
    { path: '/dashboard', component: { template: 'dashboard' } },
  ],
})

describe('Login.vue', () => {
  let wrapper

  beforeEach(() => {
    localStorage.clear()
    wrapper = mount(Login, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render login form', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have phone input', async () => {
    const phoneInput = wrapper.find('.el-input input')
    expect(phoneInput.exists()).toBe(true)
  })

  it('should have password input', async () => {
    const passwordInput = wrapper.findAll('input[type="password"]')
    expect(passwordInput.length).toBeGreaterThan(0)
  })

  it('should have login button', () => {
    const loginButton = wrapper.find('button')
    expect(loginButton.exists()).toBe(true)
  })
})
