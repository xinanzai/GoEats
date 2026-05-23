import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Users from '@/views/Users.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/users', component: Users }],
})

describe('Users.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Users, {
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

  it('should render users page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have search input', () => {
    expect(wrapper.findComponent({ name: 'ElInput' }).exists()).toBe(true)
  })

  it('should have role filter', () => {
    expect(wrapper.findComponent({ name: 'ElSelect' }).exists()).toBe(true)
  })

  it('should have user table', () => {
    expect(wrapper.findComponent({ name: 'ElTable' }).exists()).toBe(true)
  })

  it('should have pagination', () => {
    expect(wrapper.findComponent({ name: 'ElPagination' }).exists()).toBe(true)
  })
})
