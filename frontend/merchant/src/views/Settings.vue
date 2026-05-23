<template>
  <div class="settings-view">
    <el-card>
      <div class="page-header">
        <h2>店铺设置</h2>
      </div>

      <el-tabs v-model="activeTab" type="card">
        <el-tab-pane label="基本信息" name="basic">
          <el-form
            ref="basicFormRef"
            :model="basicForm"
            :rules="basicRules"
            label-width="120px"
            class="settings-form"
          >
            <el-form-item label="店铺名称" prop="business_name">
              <el-input
                v-model="basicForm.business_name"
                placeholder="请输入店铺名称"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="店铺描述" prop="description">
              <el-input
                v-model="basicForm.description"
                type="textarea"
                :rows="4"
                placeholder="请输入店铺描述（选填）"
                maxlength="500"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="店铺Logo">
              <div class="logo-upload">
                <el-upload
                  class="logo-uploader"
                  action=""
                  :show-file-list="false"
                  :on-change="handleLogoChange"
                  :before-upload="beforeLogoUpload"
                  :disabled="saving || uploading"
                >
                  <el-avatar :size="100" :src="basicForm.logo" v-if="basicForm.logo">
                    <img :src="getImageUrl(basicForm.logo)" alt="Logo" class="logo-image" />
                  </el-avatar>
                  <el-avatar :size="100" v-else class="logo-placeholder">
                    <el-icon :size="40"><Shop /></el-icon>
                  </el-avatar>
                </el-upload>
                <div class="upload-actions">
                  <el-button
                    v-if="basicForm.logo"
                    type="danger"
                    text
                    size="small"
                    @click="basicForm.logo = ''"
                  >
                    清除
                  </el-button>
                  <span class="upload-tip">点击头像上传Logo，支持 jpg、png 格式，最大10MB</span>
                </div>
              </div>
            </el-form-item>

            <el-form-item label="创建时间">
              <span class="readonly-text">{{ formatDateTime(merchantInfo.created_at) }}</span>
            </el-form-item>

            <el-form-item label="审核状态">
              <el-tag :type="getStatusType(merchantInfo.status)" size="small">
                {{ getStatusText(merchantInfo.status) }}
              </el-tag>
            </el-form-item>

            <el-form-item v-if="merchantInfo.status === 'rejected'" label="拒绝原因">
              <span class="rejection-reason">{{ merchantInfo.rejection_reason || '无' }}</span>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleSaveBasic" :loading="saving">
                保存基本信息
              </el-button>
              <el-button @click="handleResetBasic">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="联系方式" name="contact">
          <el-form
            ref="contactFormRef"
            :model="contactForm"
            :rules="contactRules"
            label-width="120px"
            class="settings-form"
          >
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input
                v-model="contactForm.contact_phone"
                placeholder="请输入联系电话"
                maxlength="20"
              />
              <span class="form-tip">此号码将用于接收订单通知</span>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleSaveContact" :loading="saving">
                保存联系方式
              </el-button>
              <el-button @click="handleResetContact">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="店铺地址" name="address">
          <el-form
            ref="addressFormRef"
            :model="addressForm"
            :rules="addressRules"
            label-width="120px"
            class="settings-form"
          >
            <el-form-item label="店铺地址" prop="address">
              <el-input
                v-model="addressForm.address"
                type="textarea"
                :rows="3"
                placeholder="请输入详细地址"
                maxlength="255"
                show-word-limit
              />
              <span class="form-tip">此地址将用于配送员取餐</span>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleSaveAddress" :loading="saving">
                保存店铺地址
              </el-button>
              <el-button @click="handleResetAddress">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Shop, Upload } from '@element-plus/icons-vue'
import { getMyMerchant, updateMyMerchant } from '@/api/merchants'
import { uploadMerchantLogo } from '@/api/upload'

const saving = ref(false)
const uploading = ref(false)
const activeTab = ref('basic')
const merchantInfo = ref({})
const basicFormRef = ref(null)
const contactFormRef = ref(null)
const addressFormRef = ref(null)

const basicForm = reactive({
  business_name: '',
  description: '',
  logo: ''
})

const contactForm = reactive({
  contact_phone: ''
})

const addressForm = reactive({
  address: ''
})

const originalBasicForm = reactive({
  business_name: '',
  description: '',
  logo: ''
})

const originalContactForm = reactive({
  contact_phone: ''
})

const originalAddressForm = reactive({
  address: ''
})

const basicRules = {
  business_name: [
    { required: true, message: '请输入店铺名称', trigger: 'blur' },
    { min: 2, max: 100, message: '店铺名称长度在2到100个字符', trigger: 'blur' }
  ]
}

const contactRules = {
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ]
}

const addressRules = {
  address: [
    { required: true, message: '请输入店铺地址', trigger: 'blur' },
    { min: 5, max: 255, message: '地址长度在5到255个字符', trigger: 'blur' }
  ]
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  return url
}

function beforeLogoUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }
  return false
}

async function handleLogoChange(file) {
  if (uploading.value) return
  try {
    uploading.value = true
    const response = await uploadMerchantLogo(file.raw)
    basicForm.logo = response.data.url
    ElMessage.success('Logo上传成功')
  } catch (error) {
    console.error('Logo上传失败:', error)
  } finally {
    uploading.value = false
  }
}

function getStatusType(status) {
  const typeMap = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || ''
}

function getStatusText(status) {
  const textMap = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return textMap[status] || status
}

async function fetchMerchantInfo() {
  try {
    const data = await getMyMerchant()
    merchantInfo.value = data

    basicForm.business_name = data.business_name || ''
    basicForm.description = data.description || ''
    basicForm.logo = data.logo || ''

    contactForm.contact_phone = data.contact_phone || ''

    addressForm.address = data.address || ''

    Object.assign(originalBasicForm, { ...basicForm })
    Object.assign(originalContactForm, { ...contactForm })
    Object.assign(originalAddressForm, { ...addressForm })
  } catch (error) {
    console.error('获取商家信息失败:', error)
  }
}

async function handleSaveBasic() {
  try {
    await basicFormRef.value.validate()
    saving.value = true
    const updateData = {
      business_name: basicForm.business_name,
      description: basicForm.description,
      logo: basicForm.logo || null
    }
    await updateMyMerchant(updateData)
    ElMessage.success('基本信息保存成功')
    Object.assign(originalBasicForm, { ...basicForm })
    fetchMerchantInfo()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

function handleResetBasic() {
  Object.assign(basicForm, originalBasicForm)
  basicFormRef.value?.clearValidate()
}

async function handleSaveContact() {
  try {
    await contactFormRef.value.validate()
    saving.value = true
    await updateMyMerchant({
      contact_phone: contactForm.contact_phone
    })
    ElMessage.success('联系方式保存成功')
    Object.assign(originalContactForm, { ...contactForm })
    fetchMerchantInfo()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

function handleResetContact() {
  Object.assign(contactForm, originalContactForm)
  contactFormRef.value?.clearValidate()
}

async function handleSaveAddress() {
  try {
    await addressFormRef.value.validate()
    saving.value = true
    await updateMyMerchant({
      address: addressForm.address
    })
    ElMessage.success('店铺地址保存成功')
    Object.assign(originalAddressForm, { ...addressForm })
    fetchMerchantInfo()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

function handleResetAddress() {
  Object.assign(addressForm, originalAddressForm)
  addressFormRef.value?.clearValidate()
}

onMounted(() => {
  fetchMerchantInfo()
})
</script>

<style scoped>
.settings-view {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.settings-form {
  max-width: 700px;
  margin-top: 20px;
}

.logo-upload {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.logo-uploader {
  cursor: pointer;
}

.logo-uploader :deep(.el-avatar) {
  transition: all 0.3s;
}

.logo-uploader:hover :deep(.el-avatar) {
  opacity: 0.8;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.upload-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-placeholder {
  background-color: #f5f7fa;
  color: #909399;
}

.readonly-text {
  color: #606266;
}

.rejection-reason {
  color: #f56c6c;
}

.form-tip {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}
</style>
