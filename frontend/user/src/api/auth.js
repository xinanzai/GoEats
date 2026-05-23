import request from '@/utils/request'

/**
 * 用户登录
 * @param {Object} loginData - 登录数据
 * @param {string} loginData.phone - 手机号
 * @param {string} loginData.password - 密码
 * @returns {Promise} 返回 access_token
 */
export function login(loginData) {
  return request.post('/auth/login', loginData)
}

/**
 * 用户注册
 * @param {Object} registerData - 注册数据
 * @param {string} registerData.username - 用户名
 * @param {string} registerData.phone - 手机号
 * @param {string} registerData.password - 密码
 * @returns {Promise} 返回用户信息
 */
export function register(registerData) {
  return request.post('/auth/register', registerData)
}

/**
 * 获取当前用户信息
 * @returns {Promise} 返回用户信息
 */
export function getCurrentUser() {
  return request.get('/auth/me')
}

/**
 * 刷新 Token
 * @returns {Promise} 返回新的 access_token
 */
export function refreshToken() {
  return request.post('/auth/refresh')
}
