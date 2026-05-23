import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Orders from '@/views/Orders.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/orders', component: Orders }],
})

describe('Orders.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Orders, {
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
          'el-date-picker': true,
        },
      },
    })
  })

  it('should render orders page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have order table', () => {
    expect(wrapper.findComponent({ name: 'ElTable' }).exists()).toBe(true)
  })

  it('should have status filter', () => {
    expect(wrapper.findComponent({ name: 'ElSelect' }).exists()).toBe(true)
  })

  it('should have date range picker', () => {
    expect(wrapper.findComponent({ name: 'ElDatePicker' }).exists()).toBe(true)
  })

  it('should have pagination', () => {
    expect(wrapper.findComponent({ name: 'ElPagination' }).exists()).toBe(true)
  })
})
