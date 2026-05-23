import request from '@/utils/request'

/**
 * 获取商家商品列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export function getMyProducts(params) {
  return request.get('/products/merchant/me', { params })
}

/**
 * 创建商品
 * @param {Object} data - 商品数据
 * @returns {Promise}
 */
export function createProduct(data) {
  return request.post('/products/merchant/me', data)
}

/**
 * 更新商品
 * @param {number} id - 商品ID
 * @param {Object} data - 更新数据
 * @returns {Promise}
 */
export function updateProduct(id, data) {
  return request.put(`/products/merchant/me/${id}`, data)
}

/**
 * 删除商品
 * @param {number} id - 商品ID
 * @returns {Promise}
 */
export function deleteProduct(id) {
  return request.delete(`/products/merchant/me/${id}`)
}

/**
 * 切换商品上架/下架状态
 * @param {number} id - 商品ID
 * @returns {Promise}
 */
export function toggleProduct(id) {
  return request.put(`/products/merchant/me/${id}/toggle`)
}

export default {
  getMyProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  toggleProduct,
}
