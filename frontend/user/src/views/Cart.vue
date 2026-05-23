<template>
  <div class="cart">
    <van-nav-bar title="购物车" />

    <div class="content">
      <van-empty v-if="cartStore.items.length === 0" description="购物车是空的">
        <van-button type="primary" @click="$router.push('/')">去逛逛</van-button>
      </van-empty>

      <div v-else class="cart-body">
        <div
          v-for="group in merchantGroups"
          :key="group.merchant_id"
          class="merchant-section"
        >
          <div class="merchant-header">
            <div class="merchant-name">
              {{ group.merchant_name || '商家' }}
            </div>
            <van-icon
              name="delete-o"
              class="merchant-delete-btn"
              @click="handleDeleteGroup(group.merchant_id)"
            />
          </div>

          <div class="cart-item-list">
            <div
              v-for="item in group.items"
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
                  :model-value="item.quantity"
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

          <div class="merchant-footer">
            <div class="merchant-total">
              <span class="price-label">小计：</span>
              <span class="price-symbol">¥</span>
              <span class="price-value">{{ formatPrice(group.totalPrice) }}</span>
            </div>
            <div class="merchant-checkout-btn" @click="handleCheckout(group)">
              去结算
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import { getMerchantDetail } from '@/api/merchants'
import { showConfirmDialog, showToast } from 'vant'

const router = useRouter()
const cartStore = useCartStore()

const merchantGroups = ref([])

function formatPrice(price) {
  return parseFloat(price).toFixed(2)
}

async function fetchMerchantNames() {
  const groups = cartStore.merchantGroups
  for (const group of groups) {
    if (!group.merchant_name) {
      try {
        const merchant = await getMerchantDetail(group.merchant_id)
        group.merchant_name = merchant.business_name
      } catch (error) {
        console.error('获取商家信息失败:', error)
        group.merchant_name = '商家'
      }
    }
  }
  merchantGroups.value = groups
}

function refreshCart() {
  merchantGroups.value = cartStore.merchantGroups
}

function onQuantityChange(productId, newQuantity) {
  cartStore.updateQuantity(productId, newQuantity)
  refreshCart()
}

async function handleDelete(productId) {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: '确定要从购物车中移除该商品吗？',
    })
    cartStore.removeItem(productId)
    showToast('已删除')
    refreshCart()
  } catch (error) {
  }
}

async function handleDeleteGroup(merchantId) {
  try {
    await showConfirmDialog({
      title: '确认清空',
      message: '确定要清空该商家的所有商品吗？',
    })
    cartStore.removeItemsByMerchant(merchantId)
    showToast('已清空')
    refreshCart()
  } catch (error) {
  }
}

function handleCheckout(group) {
  if (group.items.length === 0) {
    showToast('该商家没有商品')
    return
  }

  const items = group.items.map((item) => ({
    product_id: item.product_id,
    merchant_id: item.merchant_id,
    name: item.name,
    price: item.price,
    image_url: item.image_url,
    quantity: item.quantity,
  }))

  router.push({
    path: '/checkout',
    query: {
      items: JSON.stringify(items),
      merchant_id: group.merchant_id,
    },
  })
}

onMounted(() => {
  if (cartStore.items.length > 0) {
    fetchMerchantNames()
  }
})
</script>

<style scoped>
.cart {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 30px;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.merchant-name {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}

.merchant-delete-btn {
  color: #969799;
  font-size: 18px;
  cursor: pointer;
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

.merchant-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid #f7f8fa;
  background-color: #fafafa;
}

.merchant-total {
  display: flex;
  align-items: baseline;
}

.price-label {
  font-size: 14px;
  color: #323233;
}

.merchant-total .price-symbol {
  font-size: 12px;
  color: #ee0a24;
  margin-left: 4px;
}

.merchant-total .price-value {
  font-size: 18px;
  color: #ee0a24;
  font-weight: 500;
}

.merchant-checkout-btn {
  background: linear-gradient(135deg, #ee0a24 0%, #ff455a 100%);
  color: #fff;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}
</style>
