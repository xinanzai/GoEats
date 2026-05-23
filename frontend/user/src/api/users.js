import request from '@/utils/request'

/**
 * 获取用户个人信息
 * @returns {Promise} 返回用户信息
 */
export function getUserProfile() {
  return request.get('/users/profile')
}

/**
 * 更新用户个人信息
 * @param {Object} profileData - 用户信息
 * @returns {Promise} 返回更新后的用户信息
 */
export function updateUserProfile(profileData) {
  return request.put('/users/profile', profileData)
}

/**
 * 修改密码
 * @param {Object} passwordData - 密码数据
 * @param {string} passwordData.old_password - 旧密码
 * @param {string} passwordData.new_password - 新密码
 * @returns {Promise}
 */
export function changePassword(passwordData) {
  return request.put('/users/password', passwordData)
}

/**
 * 获取用户地址列表
 * @returns {Promise} 返回地址列表
 */
export function getUserAddresses() {
  return request.get('/users/addresses')
}

/**
 * 添加用户地址
 * @param {Object} addressData - 地址数据
 * @returns {Promise} 返回创建的地址信息
 */
export function createUserAddress(addressData) {
  return request.post('/users/addresses', addressData)
}

/**
 * 更新用户地址
 * @param {number} addressId - 地址ID
 * @param {Object} addressData - 地址数据
 * @returns {Promise} 返回更新后的地址信息
 */
export function updateUserAddress(addressId, addressData) {
  return request.put(`/users/addresses/${addressId}`, addressData)
}

/**
 * 删除用户地址
 * @param {number} addressId - 地址ID
 * @returns {Promise}
 */
export function deleteUserAddress(addressId) {
  return request.delete(`/users/addresses/${addressId}`)
}

/**
 * 设置默认地址
 * @param {number} addressId - 地址ID
 * @returns {Promise} 返回设置后的地址信息
 */
export function setDefaultAddress(addressId) {
  return request.put(`/users/addresses/${addressId}/set-default`)
}
