import request from '@/utils/request'

/**
 * 获取商品列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页大小
 * @param {number} params.merchant_id - 商家ID
 * @param {number} params.category_id - 分类ID
 * @param {string} params.search - 搜索关键词
 * @returns {Promise} 返回商品列表和分页信息
 */
export function getProductList(params) {
  return request.get('/products', { params })
}

/**
 * 获取商品详情
 * @param {number} productId - 商品ID
 * @returns {Promise} 返回商品详情
 */
export function getProductDetail(productId) {
  return request.get(`/products/${productId}`)
}
