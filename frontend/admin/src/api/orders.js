import request from '@/utils/request'

/**
 * 获取订单列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.status - 状态筛选
 * @param {string} params.search - 搜索关键词
 * @returns {Promise}
 */
export function getOrderList(params) {
  return request.get('/admin/orders', { params })
}

/**
 * 获取数据统计
 * @param {Object} params - 查询参数
 * @param {string} params.period - 统计周期: day/week/month
 * @returns {Promise}
 */
export function getStatistics(params) {
  return request.get('/admin/statistics', { params })
}

export default {
  getOrderList,
  getStatistics,
}
