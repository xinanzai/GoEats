import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Merchants from '@/views/Merchants.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/merchants', component: Merchants }],
})

describe('Merchants.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Merchants, {
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
        },
      },
    })
  })

  it('should render merchants page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have search input', () => {
    expect(wrapper.findComponent({ name: 'ElInput' }).exists()).toBe(true)
  })

  it('should have status filter', () => {
    expect(wrapper.findComponent({ name: 'ElSelect' }).exists()).toBe(true)
  })

  it('should have merchant table', () => {
    expect(wrapper.findComponent({ name: 'ElTable' }).exists()).toBe(true)
  })

  it('should have approval buttons', () => {
    const buttons = wrapper.findAllComponents({ name: 'ElButton' })
    expect(buttons.length).toBeGreaterThan(0)
  })
})
