import request from '@/utils/request'

/**
 * 获取当前商家信息
 * @returns {Promise}
 */
export function getMyMerchant() {
  return request.get('/merchants/me')
}

/**
 * 更新当前商家信息
 * @param {Object} data - 更新数据
 * @returns {Promise}
 */
export function updateMyMerchant(data) {
  return request.put('/merchants/me', data)
}

/**
 * 获取商家分类列表
 * @returns {Promise}
 */
export function getMyCategories() {
  return request.get('/merchants/me/categories')
}

/**
 * 创建商家分类
 * @param {Object} data - 分类数据
 * @param {string} data.name - 分类名称
 * @returns {Promise}
 */
export function createCategory(data) {
  return request.post('/merchants/me/categories', data)
}

/**
 * 更新商家分类
 * @param {number} id - 分类ID
 * @param {Object} data - 更新数据
 * @returns {Promise}
 */
export function updateCategory(id, data) {
  return request.put(`/merchants/me/categories/${id}`, data)
}

/**
 * 删除商家分类
 * @param {number} id - 分类ID
 * @returns {Promise}
 */
export function deleteCategory(id) {
  return request.delete(`/merchants/me/categories/${id}`)
}

export default {
  getMyMerchant,
  updateMyMerchant,
  getMyCategories,
  createCategory,
  updateCategory,
  deleteCategory,
}
