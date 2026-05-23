<template>
  <div class="cart">
    <van-nav-bar title="购物车" />

    <div class="content">
      <van-empty v-if="cartItems.length === 0" description="购物车是空的">
        <van-button type="primary" @click="$router.push('/')">去逛逛</van-button>
      </van-empty>

      <div v-else class="cart-body">
        <div class="merchant-section">
          <div class="merchant-header">
            <div class="merchant-name">
              {{ merchantName }}
            </div>
          </div>

          <div class="cart-item-list">
            <div
              v-for="item in cartItems"
              :key="item.product_id"
              class="cart-item"
            >
              <div class="item-image-wrapper">
                <van-image
                  v-if="item.image_url"
                  :src="item.image_url"
                  width="64"
                  height="64"
                  fit="cover"
                  radius="4"
                />
                <div v-else class="item-image-default">
                  <van-icon name="orders-o" size="24" />
                </div>
              </div>

              <div class="item-info">
                <div class="item-name">{{ item.name }}</div>
                <div class="item-price">
                  <span class="price-symbol">¥</span>
                  <span class="price-value">{{ formatPrice(item.price) }}</span>
                </div>
              </div>

              <div class="item-actions">
                <van-stepper
                  v-model="item.quantity"
                  :min="1"
                  :max="99"
                  @change="onQuantityChange(item.product_id, $event)"
                />
                <van-icon
                  name="delete-o"
                  class="delete-btn"
                  @click="handleDelete(item.product_id)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="cart-footer" v-if="cartItems.length > 0">
      <div class="footer-left">
        <van-checkbox v-model="selectAll" @change="onSelectAll">全选</van-checkbox>
        <div class="total-price">
          <span class="price-label">合计：</span>
          <span class="price-symbol">¥</span>
          <span class="price-value">{{ formattedTotalPrice }}</span>
        </div>
      </div>
      <div class="footer-right" @click="handleCheckout">
        <span class="checkout-count">{{ totalQuantity }}</span>
        <span>结算</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import { getMerchantDetail } from '@/api/merchants'
import { showConfirmDialog, showToast } from 'vant'

const router = useRouter()
const cartStore = useCartStore()
const selectAll = ref(true)
const merchantName = ref('')

const cartItems = computed(() => cartStore.items)

const totalQuantity = computed(() => {
  return cartStore.totalQuantity
})

const totalPrice = computed(() => {
  return cartStore.totalPrice
})

const formattedTotalPrice = computed(() => {
  return cartStore.formattedTotalPrice
})

function formatPrice(price) {
  return parseFloat(price).toFixed(2)
}

async function fetchMerchantName() {
  if (cartItems.value.length > 0) {
    const firstItem = cartItems.value[0]
    try {
      const merchant = await getMerchantDetail(firstItem.merchant_id)
      merchantName.value = merchant.business_name
    } catch (error) {
      console.error('获取商家信息失败:', error)
      merchantName.value = '商家'
    }
  }
}

function onQuantityChange(productId, newQuantity) {
  cartStore.updateQuantity(productId, newQuantity)
}

async function handleDelete(productId) {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: '确定要从购物车中移除该商品吗？',
    })
    cartStore.removeItem(productId)
    showToast('已删除')
    if (cartItems.value.length === 0) {
      merchantName.value = ''
    }
  } catch (error) {
    // 用户取消
  }
}

function onSelectAll(value) {
  showToast(value ? '已全选' : '已取消全选')
}

function handleCheckout() {
  if (cartItems.value.length === 0) {
    showToast('购物车是空的')
    return
  }

  const checkoutData = {
    items: cartItems.value.map((item) => ({
      product_id: item.product_id,
      merchant_id: item.merchant_id,
      name: item.name,
      price: item.price,
      image_url: item.image_url,
      quantity: item.quantity,
    })),
    merchant_id: cartItems.value[0].merchant_id,
  }

  router.push({
    path: '/checkout',
    query: {
      items: JSON.stringify(checkoutData.items),
      merchant_id: checkoutData.merchant_id,
    },
  })
}

onMounted(() => {
  if (cartItems.value.length > 0) {
    fetchMerchantName()
  }
})
</script>

<style scoped>
.cart {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 100px;
}

.content {
  padding: 12px;
}

.cart-body {
  padding: 0;
}

.merchant-section {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
}

.merchant-header {
  padding: 12px 16px;
  border-bottom: 1px solid #f7f8fa;
}

.merchant-name {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}

.cart-item-list {
  padding: 0 16px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f7f8fa;
}

.cart-item:last-child {
  border-bottom: none;
}

.item-image-wrapper {
  flex-shrink: 0;
  margin-right: 12px;
}

.item-image-default {
  width: 64px;
  height: 64px;
  border-radius: 4px;
  background-color: #f7f8fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c8c9cc;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 14px;
  color: #323233;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-price {
  color: #ee0a24;
  font-size: 14px;
  font-weight: 500;
}

.price-symbol {
  font-size: 12px;
}

.price-value {
  font-size: 16px;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 12px;
}

.delete-btn {
  color: #ee0a24;
  font-size: 20px;
  cursor: pointer;
}

.cart-footer {
  position: fixed;
  bottom: 50px;
  left: 0;
  right: 0;
  height: 50px;
  background-color: #fff;
  border-top: 1px solid #ebedf0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  z-index: 99;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.total-price {
  margin-left: 8px;
}

.price-label {
  font-size: 14px;
  color: #323233;
}

.total-price .price-symbol {
  font-size: 12px;
  color: #ee0a24;
}

.total-price .price-value {
  font-size: 18px;
  color: #ee0a24;
  font-weight: 500;
}

.footer-right {
  background: linear-gradient(135deg, #ee0a24 0%, #ff455a 100%);
  color: #fff;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.checkout-count {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}
</style>
