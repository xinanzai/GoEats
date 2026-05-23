import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Products from '@/views/Products.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/products', component: Products }],
})

describe('Products.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Products, {
      global: {
        plugins: [createPinia(), router],
        stubs: {
          'el-table': true,
          'el-table-column': true,
          'el-pagination': true,
          'el-input': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-dialog': true,
          'el-form': true,
          'el-form-item': true,
        },
      },
    })
  })

  it('should render products page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have search input', () => {
    expect(wrapper.findComponent({ name: 'ElInput' }).exists()).toBe(true)
  })

  it('should have product table', () => {
    expect(wrapper.findComponent({ name: 'ElTable' }).exists()).toBe(true)
  })

  it('should have add product button', () => {
    const buttons = wrapper.findAllComponents({ name: 'ElButton' })
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('should have product form dialog', () => {
    expect(wrapper.findComponent({ name: 'ElDialog' }).exists()).toBe(true)
  })
})
