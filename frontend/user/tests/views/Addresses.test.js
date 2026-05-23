import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Addresses from '@/views/Addresses.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/addresses', component: Addresses }],
})

describe('Addresses.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Addresses, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render addresses page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have add address button', () => {
    const html = wrapper.html()
    expect(html).toContain('新增')
  })
})
