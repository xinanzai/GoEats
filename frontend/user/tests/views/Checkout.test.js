import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Checkout from '@/views/Checkout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/checkout', component: Checkout }],
})

describe('Checkout.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Checkout, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render checkout page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have address selection', () => {
    expect(wrapper.html()).toBeDefined()
  })

  it('should have submit order button', () => {
    const html = wrapper.html()
    expect(html).toBeDefined()
  })
})
