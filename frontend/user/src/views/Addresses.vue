<template>
  <div class="addresses">
    <van-nav-bar title="地址管理" left-arrow @click-left="$router.back()" />

    <div class="address-list">
      <div v-if="loading" class="loading-wrapper">
        <van-loading type="spinner" size="24" color="#1989fa" />
      </div>
      <van-empty v-if="!loading && addresses.length === 0" description="暂无收货地址">
        <van-button type="primary" @click="showAddDialog">添加地址</van-button>
      </van-empty>

      <div
        v-for="address in addresses"
        :key="address.id"
        class="address-card"
      >
        <van-cell-group inset @click="handleSelect(address)">
          <van-cell>
            <template #title>
              <div class="address-header">
                <span class="name">{{ address.receiver }}</span>
                <span class="phone">{{ address.phone }}</span>
                <van-tag v-if="address.is_default" size="medium" type="primary" class="default-tag">
                  默认
                </van-tag>
              </div>
            </template>
            <template #label>
              <div class="address-detail">
                {{ address.province }}{{ address.city }}{{ address.district }}{{ address.detail_address }}
              </div>
            </template>
          </van-cell>
        </van-cell-group>
        <div class="address-actions">
          <van-button size="mini" @click.stop="handleEdit(address)">编辑</van-button>
          <van-button size="mini" type="primary" @click.stop="handleSetDefault(address)" v-if="!address.is_default">
            设为默认
          </van-button>
          <van-button size="mini" type="danger" @click.stop="handleDelete(address)">删除</van-button>
        </div>
      </div>
    </div>

    <div
      v-show="!showForm"
      class="add-address-btn"
      @click="showAddDialog"
    >
      <van-icon name="plus" size="24" />
      <span>新增</span>
    </div>

    <!-- 添加/编辑地址弹窗 -->
    <van-popup v-model:show="showForm" position="bottom" :style="{ height: '80%' }">
      <div class="address-form">
        <van-nav-bar :title="isEdit ? '编辑地址' : '添加地址'">
          <template #left>
            <van-icon name="cross" size="20" @click="closeForm" />
          </template>
        </van-nav-bar>

        <van-form @submit="handleSubmit">
          <van-cell-group inset>
            <van-field
              v-model="form.receiver"
              name="receiver"
              label="收货人"
              placeholder="请输入收货人姓名"
              :rules="[{ required: true, message: '请输入收货人姓名' }]"
            />
            <van-field
              v-model="form.phone"
              name="phone"
              label="手机号"
              placeholder="请输入手机号"
              type="tel"
              :rules="[
                { required: true, message: '请输入手机号' },
                { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' },
              ]"
            />
            <van-field
              v-model="form.province"
              name="province"
              label="省份"
              placeholder="请输入省份"
              :rules="[{ required: true, message: '请输入省份' }]"
            />
            <van-field
              v-model="form.city"
              name="city"
              label="城市"
              placeholder="请输入城市"
              :rules="[{ required: true, message: '请输入城市' }]"
            />
            <van-field
              v-model="form.district"
              name="district"
              label="区县"
              placeholder="请输入区县"
              :rules="[{ required: true, message: '请输入区县' }]"
            />
            <van-field
              v-model="form.detail_address"
              name="detail_address"
              label="详细地址"
              placeholder="请输入详细地址"
              rows="2"
              type="textarea"
              :rules="[{ required: true, message: '请输入详细地址' }]"
            />
            <van-field name="is_default" label="设为默认">
              <template #input>
                <van-switch v-model="form.is_default" size="24" />
              </template>
            </van-field>
          </van-cell-group>

          <div class="submit-btn">
            <van-button round block type="primary" native-type="submit" :loading="submitting">
              {{ isEdit ? '保存' : '添加' }}
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getUserAddresses,
  createUserAddress,
  updateUserAddress,
  deleteUserAddress,
  setDefaultAddress,
} from '@/api/users'
import { showConfirmDialog, showToast } from 'vant'

const router = useRouter()
const addresses = ref([])
const loading = ref(true)
const showForm = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const submitting = ref(false)

const form = ref({
  receiver: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detail_address: '',
  is_default: false,
})

function resetForm() {
  form.value = {
    receiver: '',
    phone: '',
    province: '',
    city: '',
    district: '',
    detail_address: '',
    is_default: false,
  }
  isEdit.value = false
  editingId.value = null
}

async function fetchAddresses() {
  try {
    loading.value = true
    const result = await getUserAddresses()
    addresses.value = Array.isArray(result) ? result : []
  } catch (error) {
    console.error('获取地址列表失败:', error)
    addresses.value = []
    showToast('获取地址列表失败')
  } finally {
    loading.value = false
  }
}

function showAddDialog() {
  resetForm()
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  resetForm()
}

function handleEdit(address) {
  isEdit.value = true
  editingId.value = address.id
  form.value = {
    receiver: address.receiver,
    phone: address.phone,
    province: address.province,
    city: address.city,
    district: address.district,
    detail_address: address.detail_address,
    is_default: address.is_default,
  }
  showForm.value = true
}

async function handleSubmit() {
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateUserAddress(editingId.value, form.value)
      showToast('更新成功')
    } else {
      await createUserAddress(form.value)
      showToast('添加成功')
    }
    closeForm()
    await fetchAddresses()
  } catch (error) {
    console.error('保存地址失败:', error)
  } finally {
    submitting.value = false
  }
}

async function handleDelete(address) {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: '确定要删除此地址吗？',
    })
    await deleteUserAddress(address.id)
    showToast('删除成功')
    await fetchAddresses()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除地址失败:', error)
    }
  }
}

async function handleSetDefault(address) {
  try {
    await setDefaultAddress(address.id)
    showToast('已设为默认地址')
    await fetchAddresses()
  } catch (error) {
    console.error('设置默认地址失败:', error)
  }
}

function handleSelect(address) {
  // 如果从购物车页面进入，可以传递选中的地址
  const from = router.currentRoute.value.query.from
  if (from === 'cart') {
    router.push({ path: '/cart', query: { address_id: address.id } })
  }
}

onMounted(() => {
  fetchAddresses()
})
</script>

<style scoped>
.addresses {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 100px;
}

.address-list {
  padding: 8px;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}

.add-address-btn {
  position: fixed;
  right: 16px;
  bottom: 80px;
  background-color: #1989fa;
  color: #fff;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  gap: 2px;
}

.add-address-btn span {
  font-size: 10px;
}

.address-card {
  margin-bottom: 8px;
  cursor: pointer;
}

.address-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  font-weight: bold;
  font-size: 16px;
}

.phone {
  font-size: 14px;
  color: #646566;
}

.default-tag {
  margin-left: 4px;
}

.address-detail {
  margin-top: 4px;
  font-size: 14px;
  color: #323233;
  line-height: 1.5;
}

.address-actions {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
  justify-content: flex-end;
  border-top: 1px solid #f7f8fa;
}

.address-form {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.submit-btn {
  padding: 16px;
}
</style>
