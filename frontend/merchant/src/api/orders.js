import request from '@/utils/request'

/**
 * 获取商家订单列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.status - 状态筛选
 * @returns {Promise}
 */
export function getMyOrders(params) {
  return request.get('/orders/merchant/me', { params })
}

/**
 * 更新订单状态
 * @param {number} orderId - 订单ID
 * @param {string} status - 新状态
 * @returns {Promise}
 */
export function updateOrderStatus(orderId, status) {
  return request.put(`/orders/merchant/me/${orderId}/status`, { new_status: status })
}

/**
 * 开始制作订单
 * @param {number} orderId - 订单ID
 * @returns {Promise}
 */
export function prepareOrder(orderId) {
  return request.post(`/orders/merchant/me/${orderId}/prepare`)
}

/**
 * 开始配送订单
 * @param {number} orderId - 订单ID
 * @returns {Promise}
 */
export function deliverOrder(orderId) {
  return request.post(`/orders/merchant/me/${orderId}/deliver`)
}

/**
 * 完成订单
 * @param {number} orderId - 订单ID
 * @returns {Promise}
 */
export function completeOrder(orderId) {
  return request.post(`/orders/merchant/me/${orderId}/complete`)
}

export default {
  getMyOrders,
  updateOrderStatus,
  prepareOrder,
  deliverOrder,
  completeOrder,
}
