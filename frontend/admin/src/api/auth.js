import request from '@/utils/request'

/**
 * 管理员登录
 * @param {Object} data - 登录数据
 * @param {string} data.phone - 手机号
 * @param {string} data.password - 密码
 * @returns {Promise}
 */
export function login(data) {
  return request.post('/auth/login', data)
}

/**
 * 获取当前用户信息
 * @returns {Promise}
 */
export function getCurrentUser() {
  return request.get('/auth/me')
}

/**
 * 刷新Token
 * @returns {Promise}
 */
export function refreshToken() {
  return request.post('/auth/refresh')
}

export default {
  login,
  getCurrentUser,
  refreshToken,
}
