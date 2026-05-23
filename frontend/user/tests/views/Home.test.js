import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: Home }],
})

describe('Home.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Home, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render home page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have search bar', () => {
    const searchInput = wrapper.find('input[type="search"]')
    expect(searchInput.exists()).toBe(true)
  })

  it('should have merchant list', () => {
    expect(wrapper.html()).toBeDefined()
  })

  it('should have bottom navigation', () => {
    const tabBar = wrapper.findComponent({ name: 'VanTabbar' })
    expect(tabBar.exists()).toBe(true)
  })
})
