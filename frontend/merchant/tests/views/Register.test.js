import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Register from '@/views/Register.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/register', component: { template: 'register' } },
    { path: '/login', component: { template: 'login' } },
  ],
})

describe('Register.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Register, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render register form', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have username input', () => {
    const inputs = wrapper.findAll('.el-input')
    expect(inputs.length).toBeGreaterThan(0)
  })

  it('should have register button', () => {
    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
  })
})
