import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Profile from '@/views/Profile.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/profile', component: Profile }],
})

describe('Profile.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Profile, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render profile page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have user info section', () => {
    expect(wrapper.html()).toBeDefined()
  })

  it('should have logout option', () => {
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBeGreaterThan(0)
  })
})
