import axios from 'axios'
import { showToast, showFailToast } from 'vant'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      const message = data?.message || data?.detail || '请求失败'

      switch (status) {
        case 400:
          showFailToast(message || '请求参数错误')
          break
        case 401:
          showFailToast('登录已过期，请重新登录')
          localStorage.removeItem('access_token')
          localStorage.removeItem('user_info')
          window.location.href = '/login'
          break
        case 403:
          showFailToast('没有权限执行此操作')
          break
        case 404:
          showFailToast('请求的资源不存在')
          break
        case 409:
          showFailToast(message || '资源冲突')
          break
        case 422:
          showFailToast(message || '数据校验失败')
          break
        case 429:
          showFailToast('请求过于频繁，请稍后再试')
          break
        case 500:
          showFailToast('服务器内部错误')
          break
        default:
          showFailToast(message || '网络错误')
      }
    } else if (error.request) {
      showFailToast('网络连接失败，请检查网络设置')
    } else {
      showFailToast('请求配置错误')
    }
    return Promise.reject(error)
  }
)

export default request
