import request from '@/utils/request'

/**
 * 获取商家仪表盘统计数据
 * 使用商家订单列表API聚合数据
 * @returns {Promise}
 */
export function getDashboardStats() {
  return request.get('/merchants/me/stats')
}

export default {
  getDashboardStats,
}
