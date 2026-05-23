import request from '@/utils/request'

/**
 * 创建订单
 * @param {Object} orderData - 订单数据
 * @param {number} orderData.merchant_id - 商家ID
 * @param {number} orderData.address_id - 收货地址ID
 * @param {Array} orderData.items - 订单项列表
 * @param {string} orderData.remark - 备注
 * @returns {Promise} 返回创建的订单信息
 */
export function createOrder(orderData) {
  return request.post('/orders', orderData)
}

/**
 * 获取用户订单列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页大小
 * @param {string} params.status - 订单状态筛选
 * @returns {Promise} 返回订单列表和分页信息
 */
export function getUserOrders(params) {
  return request.get('/orders/users/me', { params })
}

/**
 * 获取订单详情
 * @param {number} orderId - 订单ID
 * @returns {Promise} 返回订单详情
 */
export function getOrderDetail(orderId) {
  return request.get(`/orders/users/me/${orderId}`)
}

/**
 * 取消订单
 * @param {number} orderId - 订单ID
 * @returns {Promise} 返回取消后的订单信息
 */
export function cancelOrder(orderId) {
  return request.post(`/orders/users/me/${orderId}/cancel`)
}

/**
 * 支付订单
 * @param {number} orderId - 订单ID
 * @returns {Promise} 返回支付后的订单信息
 */
export function payOrder(orderId) {
  return request.post(`/orders/users/me/${orderId}/pay`)
}
