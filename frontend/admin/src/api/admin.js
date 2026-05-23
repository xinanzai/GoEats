import request from '@/utils/request'

/**
 * 获取仪表盘统计数据
 * @returns {Promise}
 */
export function getDashboardStats() {
  return request.get('/admin/dashboard')
}

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词
 * @param {string} params.role - 角色筛选
 * @param {string} params.status - 状态筛选
 * @returns {Promise}
 */
export function getUserList(params) {
  return request.get('/admin/users', { params })
}

/**
 * 获取用户详情
 * @param {number} id - 用户ID
 * @returns {Promise}
 */
export function getUserDetail(id) {
  return request.get(`/admin/users/${id}`)
}

/**
 * 更新用户信息
 * @param {number} id - 用户ID
 * @param {Object} data - 更新数据
 * @returns {Promise}
 */
export function updateUser(id, data) {
  return request.put(`/admin/users/${id}`, data)
}

/**
 * 切换用户状态
 * @param {number} id - 用户ID
 * @param {Object} data - 状态数据
 * @param {string} data.status - 状态: active/inactive
 * @returns {Promise}
 */
export function toggleUserStatus(id, data) {
  return request.put(`/admin/users/${id}/status`, data)
}

/**
 * 重置用户密码
 * @param {number} id - 用户ID
 * @param {Object} data - 密码数据
 * @param {string} data.new_password - 新密码
 * @returns {Promise}
 */
export function resetUserPassword(id, data) {
  return request.put(`/admin/users/${id}/reset-password`, data)
}

export default {
  getDashboardStats,
  getUserList,
  getUserDetail,
  updateUser,
  toggleUserStatus,
  resetUserPassword,
}
