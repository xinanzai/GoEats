import request from '@/utils/request'

/**
 * 商家注册
 * @param {Object} data - 注册数据
 * @param {string} data.username - 用户名
 * @param {string} data.phone - 手机号
 * @param {string} data.password - 密码
 * @param {string} data.business_name - 商家名称
 * @param {string} data.contact_phone - 联系电话
 * @param {string} data.address - 商家地址
 * @param {string} data.description - 商家描述（选填）
 * @returns {Promise}
 */
export function merchantRegister(data) {
  return request.post('/auth/merchant/register', data)
}

/**
 * 商家登录
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
  merchantRegister,
  login,
  getCurrentUser,
  refreshToken,
}
