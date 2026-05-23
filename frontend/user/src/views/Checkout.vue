<template>
  <div class="checkout">
    <van-nav-bar title="确认订单" left-arrow @click-left="$router.back()" />

    <div v-if="loading" class="loading-container">
      <van-loading type="spinner" size="24" color="#1989fa" />
    </div>

    <div v-else-if="items.length === 0" class="empty-container">
      <van-empty description="购物车是空的">
        <van-button type="primary" @click="$router.push('/cart')">返回购物车</van-button>
      </van-empty>
    </div>

    <div v-else class="checkout-body">
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">收货地址</span>
          <van-icon name="arrow" size="16" color="#1989fa" @click="goToAddresses" />
        </div>

        <div v-if="selectedAddress" class="address-info" @click="showAddressPicker">
          <div class="address-header">
            <span class="receiver-name">{{ selectedAddress.receiver }}</span>
            <span class="receiver-phone">{{ selectedAddress.phone }}</span>
            <van-tag v-if="selectedAddress.is_default" size="mini" type="primary">默认</van-tag>
          </div>
          <div class="address-detail">
            {{ selectedAddress.province }}{{ selectedAddress.city }}{{ selectedAddress.district }}{{ selectedAddress.detail_address }}
          </div>
        </div>

        <div v-else class="no-address" @click="goToAddresses">
          <van-icon name="location-o" size="20" color="#ee0a24" />
          <span class="no-address-text">请选择收货地址</span>
          <van-icon name="arrow" size="16" color="#969799" />
        </div>
      </div>

      <div class="section-card">
        <div class="section-header">
          <span class="section-title">商品清单</span>
        </div>

        <div class="product-list">
          <div v-for="item in items" :key="item.product_id" class="product-item">
            <div class="product-image-wrapper">
              <van-image
                v-if="item.image_url"
                :src="item.image_url"
                width="50"
                height="50"
                fit="cover"
                radius="4"
              />
              <div v-else class="product-image-default">
                <van-icon name="orders-o" size="20" />
              </div>
            </div>
            <div class="product-info">
              <div class="product-name">{{ item.name }}</div>
              <div class="product-price-qty">
                <span class="product-price">¥{{ formatPrice(item.price) }}</span>
                <span class="product-qty">x{{ item.quantity }}</span>
              </div>
            </div>
            <div class="product-subtotal">
              ¥{{ formatPrice(item.price * item.quantity) }}
            </div>
          </div>
        </div>
      </div>

      <div class="section-card">
        <div class="section-header">
          <span class="section-title">配送备注</span>
        </div>
        <van-field
          v-model="remark"
          rows="2"
          type="textarea"
          maxlength="200"
          placeholder="选填（也可在下单后联系客服）"
          show-word-limit
        />
      </div>

      <div class="section-card">
        <div class="section-header">
          <span class="section-title">金额明细</span>
        </div>
        <div class="amount-detail">
          <div class="amount-row">
            <span class="amount-label">商品总价</span>
            <span class="amount-value">{{ formatPrice(totalPrice) }}</span>
          </div>
          <div class="amount-row">
            <span class="amount-label">配送费</span>
            <span class="amount-value">0.00</span>
          </div>
          <div class="amount-row">
            <span class="amount-label">优惠金额</span>
            <span class="amount-value discount">-0.00</span>
          </div>
          <div class="amount-row total-row">
            <span class="amount-label">实付金额</span>
            <span class="amount-value total">
              <span class="currency">¥</span>
              <span class="total-price">{{ formatPrice(totalPrice) }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="checkout-footer" v-if="!loading && items.length > 0">
      <div class="footer-total">
        <span class="total-label">合计：</span>
        <span class="currency">¥</span>
        <span class="total-price">{{ formatPrice(totalPrice) }}</span>
      </div>
      <van-button
        type="primary"
        block
        class="submit-btn"
        :loading="submitting"
        :disabled="!selectedAddress"
        @click="handleSubmitOrder"
      >
        提交订单
      </van-button>
    </div>

    <van-popup v-model:show="showAddressList" position="bottom" :style="{ height: '70%' }">
      <div class="address-picker">
        <van-nav-bar title="选择收货地址" left-arrow @click-left="showAddressList = false" />
        <div v-if="addressesLoading" class="loading-wrapper">
          <van-loading type="spinner" size="20" color="#1989fa" />
        </div>
        <div v-else-if="addresses.length === 0" class="no-address-list">
          <van-empty description="暂无收货地址">
            <van-button type="primary" @click="showAddressList = false; goToAddresses()">
              添加地址
            </van-button>
          </van-empty>
        </div>
        <div v-else class="address-list">
          <div
            v-for="address in addresses"
            :key="address.id"
            class="address-item"
            :class="{ active: selectedAddress && selectedAddress.id === address.id }"
            @click="selectAddress(address)"
          >
            <div class="address-header">
              <span class="receiver-name">{{ address.receiver }}</span>
              <span class="receiver-phone">{{ address.phone }}</span>
              <van-tag v-if="address.is_default" size="mini" type="primary">默认</van-tag>
            </div>
            <div class="address-detail">
              {{ address.province }}{{ address.city }}{{ address.district }}{{ address.detail_address }}
            </div>
            <van-icon v-if="selectedAddress && selectedAddress.id === address.id" name="successful" size="20" color="#1989fa" />
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import { getUserAddresses } from '@/api/users'
import { createOrder } from '@/api/orders'
import { showConfirmDialog, showToast } from 'vant'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const loading = ref(true)
const submitting = ref(false)
const remark = ref('')
const items = ref([])
const merchantId = ref(null)

const selectedAddress = ref(null)
const showAddressList = ref(false)
const addresses = ref([])
const addressesLoading = ref(false)

const totalPrice = computed(() => {
  return items.value.reduce((sum, item) => {
    return sum + parseFloat(item.price) * item.quantity
  }, 0)
})

function formatPrice(price) {
  return parseFloat(price).toFixed(2)
}

function parseCheckoutItems() {
  const itemsQuery = route.query.items
  const merchantIdQuery = route.query.merchant_id

  if (!itemsQuery) {
    items.value = []
    return
  }

  try {
    const parsedItems = JSON.parse(itemsQuery)
    items.value = parsedItems
    merchantId.value = parseInt(merchantIdQuery)
  } catch (error) {
    console.error('解析购物车数据失败:', error)
    items.value = []
  }
}

async function fetchAddresses() {
  try {
    addressesLoading.value = true
    const result = await getUserAddresses()
    addresses.value = Array.isArray(result) ? result : []

    if (addresses.value.length > 0) {
      const defaultAddress = addresses.value.find((a) => a.is_default)
      selectedAddress.value = defaultAddress || addresses.value[0]
    }
  } catch (error) {
    console.error('获取地址列表失败:', error)
    addresses.value = []
  } finally {
    addressesLoading.value = false
    loading.value = false
  }
}

function showAddressPicker() {
  if (addresses.value.length === 0 && !addressesLoading.value) {
    goToAddresses()
    return
  }
  showAddressList.value = true
}

function selectAddress(address) {
  selectedAddress.value = { ...address }
  showAddressList.value = false
  showToast('地址已选择')
}

function goToAddresses() {
  showAddressList.value = false
  router.push({
    path: '/addresses',
    query: { from: 'checkout' },
  })
}

async function handleSubmitOrder() {
  if (!selectedAddress.value) {
    showToast('请选择收货地址')
    return
  }

  if (items.value.length === 0) {
    showToast('购物车是空的')
    return
  }

  try {
    await showConfirmDialog({
      title: '确认提交',
      message: `确认支付 ¥${formatPrice(totalPrice.value)}？`,
    })
  } catch (error) {
    return
  }

  submitting.value = true
  try {
    const orderData = {
      merchant_id: merchantId.value,
      address_id: selectedAddress.value.id,
      items: items.value.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
      })),
      remark: remark.value || null,
    }

    const order = await createOrder(orderData)

    cartStore.removeItemsByMerchant(merchantId.value)

    showToast('订单提交成功')
    router.push({
      path: `/orders/${order.id}`,
      query: { from: 'checkout' },
    })
  } catch (error) {
    console.error('提交订单失败:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  parseCheckoutItems()
  fetchAddresses()
})
</script>

<style scoped>
.checkout {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 140px;
}

.loading-container,
.empty-container {
  padding: 60px 20px;
  text-align: center;
}

.checkout-body {
  padding: 12px;
}

.section-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f7f8fa;
}

.section-title {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}

.address-info {
  cursor: pointer;
}

.address-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.receiver-name {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}

.receiver-phone {
  font-size: 14px;
  color: #646566;
}

.address-detail {
  font-size: 13px;
  color: #646566;
  line-height: 1.5;
}

.no-address {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  cursor: pointer;
}

.no-address-text {
  flex: 1;
  font-size: 14px;
  color: #ee0a24;
}

.product-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.product-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-image-wrapper {
  flex-shrink: 0;
}

.product-image-default {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  background-color: #f7f8fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c8c9cc;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: 14px;
  color: #323233;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-price-qty {
  display: flex;
  align-items: center;
  gap: 8px;
}

.product-price {
  font-size: 13px;
  color: #ee0a24;
}

.product-qty {
  font-size: 13px;
  color: #969799;
}

.product-subtotal {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}

.amount-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.amount-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.amount-label {
  font-size: 14px;
  color: #646566;
}

.amount-value {
  font-size: 14px;
  color: #323233;
}

.amount-value.discount {
  color: #ee0a24;
}

.total-row {
  padding-top: 12px;
  border-top: 1px solid #f7f8fa;
}

.total-row .amount-label {
  color: #323233;
  font-weight: 500;
}

.total-row .amount-value.total {
  color: #ee0a24;
  font-size: 16px;
  font-weight: 500;
}

.currency {
  font-size: 12px;
}

.total-price {
  font-size: 18px;
}

.checkout-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #fff;
  border-top: 1px solid #ebedf0;
  padding: 12px 16px;
  z-index: 100;
}

.footer-total {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.total-label {
  font-size: 14px;
  color: #323233;
}

.footer-total .currency {
  font-size: 12px;
  color: #ee0a24;
  margin-left: 4px;
}

.footer-total .total-price {
  color: #ee0a24;
  font-size: 18px;
  font-weight: 500;
}

.submit-btn {
  height: 44px;
  font-size: 16px;
  background: linear-gradient(135deg, #ee0a24 0%, #ff455a 100%);
  border: none;
}

.address-picker {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.loading-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-address-list {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.address-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.address-item {
  padding: 16px;
  margin-bottom: 12px;
  border-radius: 8px;
  border: 1px solid #ebedf0;
  cursor: pointer;
  position: relative;
}

.address-item.active {
  border-color: #1989fa;
  background-color: #f0f9ff;
}
</style>
