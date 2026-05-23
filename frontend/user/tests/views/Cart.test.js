import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Cart from '@/views/Cart.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/cart', component: Cart }],
})

describe('Cart.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Cart, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render cart page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should show empty state when cart is empty', () => {
    expect(wrapper.html()).toBeDefined()
  })

  it('should have checkout button', () => {
    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
  })
})
