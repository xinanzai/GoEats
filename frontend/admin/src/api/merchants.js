import request from '@/utils/request'

/**
 * 获取商家列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status - 状态筛选: pending/approved/rejected
 * @returns {Promise}
 */
export function getMerchantList(params) {
  return request.get('/admin/merchants', { params })
}

/**
 * 获取商家详情
 * @param {number} id - 商家ID
 * @returns {Promise}
 */
export function getMerchantDetail(id) {
  return request.get(`/admin/merchants/${id}`)
}

/**
 * 审批商家
 * @param {number} id - 商家ID
 * @returns {Promise}
 */
export function approveMerchant(id) {
  return request.put(`/admin/merchants/${id}/approve`)
}

/**
 * 拒绝商家
 * @param {number} id - 商家ID
 * @param {Object} data - 拒绝原因
 * @param {string} data.reason - 拒绝原因
 * @returns {Promise}
 */
export function rejectMerchant(id, data) {
  return request.put(`/admin/merchants/${id}/reject`, data)
}

export default {
  getMerchantList,
  getMerchantDetail,
  approveMerchant,
  rejectMerchant,
}
