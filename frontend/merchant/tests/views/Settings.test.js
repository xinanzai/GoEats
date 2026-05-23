import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Settings from '@/views/Settings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/settings', component: Settings }],
})

describe('Settings.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Settings, {
      global: {
        plugins: [createPinia(), router],
      },
    })
  })

  it('should render settings page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have settings form', () => {
    const form = wrapper.find('.el-form')
    expect(form.exists()).toBe(true)
  })

  it('should have save button', () => {
    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
  })
})
