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
          'el-tabs': true,
          'el-tab-pane': true,
          'el-table': true,
          'el-table-column': true,
          'el-button': true,
          'el-dialog': true,
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

  it('should have status tabs', () => {
    expect(wrapper.findComponent({ name: 'ElTabs' }).exists()).toBe(true)
  })
})
