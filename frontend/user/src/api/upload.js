import request from '@/utils/request'

/**
 * 上传文件（通用）
 * @param {File} file - 要上传的文件
 * @param {string} directory - 可选的子目录
 * @returns {Promise}
 */
export function uploadFile(file, directory = '') {
  const formData = new FormData()
  formData.append('file', file)
  if (directory) {
    formData.append('directory', directory)
  }
  return request.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 上传用户头像
 * @param {File} file - 头像图片文件
 * @returns {Promise}
 */
export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upload/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
