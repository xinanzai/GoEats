import request from '@/utils/request'

/**
 * 获取商家列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页大小
 * @param {string} params.search - 搜索关键词
 * @returns {Promise} 返回商家列表和分页信息
 */
export function getMerchantList(params) {
  return request.get('/merchants', { params })
}

/**
 * 获取商家详情
 * @param {number} merchantId - 商家ID
 * @returns {Promise} 返回商家详情
 */
export function getMerchantDetail(merchantId) {
  return request.get(`/merchants/${merchantId}`)
}

/**
 * 获取商家分类列表
 * @param {number} merchantId - 商家ID
 * @returns {Promise} 返回分类列表
 */
export function getMerchantCategories(merchantId) {
  return request.get('/categories', { params: { merchant_id: merchantId } })
}
