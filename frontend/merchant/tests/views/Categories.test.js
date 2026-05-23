import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Categories from '@/views/Categories.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/categories', component: Categories }],
})

describe('Categories.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(Categories, {
      global: {
        plugins: [createPinia(), router],
        stubs: {
          'el-table': true,
          'el-table-column': true,
          'el-button': true,
          'el-dialog': true,
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
        },
      },
    })
  })

  it('should render categories page', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should have category table', () => {
    expect(wrapper.findComponent({ name: 'ElTable' }).exists()).toBe(true)
  })

  it('should have add category button', () => {
    expect(wrapper.findComponent({ name: 'ElButton' }).exists()).toBe(true)
  })
})
