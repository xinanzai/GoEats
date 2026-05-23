<template>
  <div class="merchant-detail">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      :title="merchant?.business_name || '商家详情'"
      left-arrow
      @click-left="$router.back()"
      fixed
      placeholder
    />

    <!-- 商家信息头部 -->
    <div class="merchant-header" v-if="merchant">
      <div class="merchant-banner">
        <div class="merchant-logo-wrapper">
          <van-image
            v-if="merchant.logo"
            :src="merchant.logo"
            class="merchant-logo"
            round
            fit="cover"
          />
          <div v-else class="merchant-logo-default">
            {{ merchant.business_name?.charAt(0) || '商' }}
          </div>
        </div>
        <div class="merchant-basic-info">
          <h2 class="merchant-title">{{ merchant.business_name }}</h2>
          <div class="merchant-tags">
            <van-tag v-if="merchant.status === 'approved'" type="success" size="small" round>
              营业中
            </van-tag>
          </div>
        </div>
      </div>
      <div class="merchant-address-bar">
        <van-icon name="location" />
        <span>{{ merchant.address || '暂无地址信息' }}</span>
      </div>
      <div class="merchant-desc-bar" v-if="merchant.description">
        <van-icon name="label" />
        <span>{{ merchant.description }}</span>
      </div>
    </div>

    <!-- 商家信息加载中 -->
    <div v-else class="merchant-header skeleton-header">
      <van-loading type="spinner" size="20" color="#1989fa" />
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧分类导航 -->
      <div class="category-sidebar">
        <div class="category-list">
          <div
            class="category-item"
            :class="{ active: activeCategoryId === null }"
            @click="selectCategory(null)"
          >
            全部
          </div>
          <div
            v-for="category in categories"
            :key="category.id"
            class="category-item"
            :class="{ active: activeCategoryId === category.id }"
            @click="selectCategory(category.id)"
          >
            <div class="category-name">{{ category.name }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧商品列表 -->
      <div class="product-area">
        <!-- 分类标题 -->
        <div class="category-title" v-if="activeCategoryId !== null && currentCategory">
          <van-divider :content-position="left">{{ currentCategory.name }}</van-divider>
        </div>

        <!-- 商品列表 -->
        <van-list
          v-model:loading="productsLoading"
          :finished="productsFinished"
          finished-text="没有更多商品了"
          @load="loadMoreProducts"
        >
          <div class="product-list">
            <div
              v-for="product in displayProducts"
              :key="product.id"
              class="product-item"
            >
              <!-- 商品图片 -->
              <div class="product-image-wrapper">
                <van-image
                  v-if="product.image_url"
                  :src="product.image_url"
                  width="80"
                  height="80"
                  fit="cover"
                  radius="4"
                />
                <div v-else class="product-image-default">
                  <van-icon name="orders-o" size="30" />
                </div>
              </div>

              <!-- 商品信息 -->
              <div class="product-info">
                <div class="product-name">{{ product.name }}</div>
                <div class="product-desc" v-if="product.description">
                  {{ product.description }}
                </div>
                <div class="product-stats">
                  <span class="sales-count">月售 100+</span>
                  <span v-if="!product.is_available" class="unavailable-tag">已售罄</span>
                </div>
                <div class="product-bottom">
                  <div class="product-price">
                    <span class="price-symbol">¥</span>
                    <span class="price-value">{{ formatPrice(product.price) }}</span>
                    <span v-if="product.original_price" class="original-price">
                      ¥{{ formatPrice(product.original_price) }}
                    </span>
                  </div>
                  <div class="product-add-cart">
                    <van-stepper
                      v-model="productCartQuantity[product.id]"
                      :min="0"
                      :max="product.stock || 99"
                      :disabled="!product.is_available"
                      @change="onCartQuantityChange(product, $event)"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <van-empty
            v-if="!productsLoading && displayProducts.length === 0"
            description="暂无商品"
            image="search"
          />
        </van-list>
      </div>
    </div>

    <!-- 购物车浮窗 -->
    <div class="cart-float-bar" v-if="currentMerchantTotalQuantity > 0">
      <div class="cart-icon-wrapper" @click="goToCart">
        <div class="cart-icon-badge">
          <van-icon name="cart-o" size="24" color="#fff" />
          <van-badge :content="currentMerchantTotalQuantity" :max="99" class="cart-badge" />
        </div>
      </div>
      <div class="cart-total-info" @click="goToCart">
        <div class="cart-total-price">
          <span class="price-symbol">¥</span>
          <span class="price-value">{{ currentMerchantFormattedTotalPrice }}</span>
        </div>
        <div class="cart-tip">不含配送费</div>
      </div>
      <div class="cart-checkout-btn" @click="goToCart">
        去结算
      </div>
    </div>

    <!-- 底部占位（购物车浮窗高度） -->
    <div class="bottom-spacer" v-if="currentMerchantTotalQuantity > 0"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { getMerchantDetail, getMerchantCategories } from '@/api/merchants'
import { getProductList } from '@/api/products'
import { useCartStore } from '@/store/cart'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const merchantId = computed(() => parseInt(route.params.id))
const merchant = ref(null)
const categories = ref([])
const activeCategoryId = ref(null)
const products = ref([])
const productsLoading = ref(false)
const productsFinished = ref(false)
const productsPage = ref(1)
const productsPageSize = 20

const productCartQuantity = ref({})

const currentMerchantCartItems = computed(() => {
  return cartStore.items.filter((i) => i.merchant_id === merchantId.value)
})

const currentMerchantTotalQuantity = computed(() => {
  return currentMerchantCartItems.value.reduce((sum, item) => sum + item.quantity, 0)
})

const currentMerchantTotalPrice = computed(() => {
  return currentMerchantCartItems.value.reduce((sum, item) => {
    return sum + parseFloat(item.price) * item.quantity
  }, 0)
})

const currentMerchantFormattedTotalPrice = computed(() => {
  return currentMerchantTotalPrice.value.toFixed(2)
})

const currentCategory = computed(() => {
  if (activeCategoryId.value === null) return null
  return categories.value.find((c) => c.id === activeCategoryId.value)
})

const displayProducts = computed(() => {
  return products.value
})

function formatPrice(price) {
  return parseFloat(price).toFixed(2)
}

async function fetchMerchantDetail() {
  try {
    const data = await getMerchantDetail(merchantId.value)
    merchant.value = data
  } catch (error) {
    console.error('获取商家详情失败:', error)
    showFailToast('获取商家信息失败')
    router.back()
  }
}

async function fetchCategories() {
  try {
    const data = await getMerchantCategories(merchantId.value)
    categories.value = data
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

async function fetchProducts() {
  if (productsLoading.value || productsFinished.value) return

  productsLoading.value = true
  try {
    const params = {
      page: productsPage.value,
      page_size: productsPageSize,
      merchant_id: merchantId.value,
    }

    if (activeCategoryId.value !== null) {
      params.category_id = activeCategoryId.value
    }

    const res = await getProductList(params)
    const items = res.items || []

    items.forEach((product) => {
      if (!(product.id in productCartQuantity.value)) {
        const cartItem = cartStore.items.find((i) => i.product_id === product.id)
        productCartQuantity.value[product.id] = cartItem ? cartItem.quantity : 0
      }
    })

    if (productsPage.value === 1) {
      products.value = items
    } else {
      products.value = [...products.value, ...items]
    }

    productsFinished.value = items.length < productsPageSize
    productsPage.value++
  } catch (error) {
    console.error('获取商品列表失败:', error)
  } finally {
    productsLoading.value = false
  }
}

function selectCategory(categoryId) {
  activeCategoryId.value = categoryId
  products.value = []
  productsPage.value = 1
  productsFinished.value = false
  productsLoading.value = false
  fetchProducts()
}

function loadMoreProducts() {
  if (!productsFinished.value) {
    fetchProducts()
  }
}

function onCartQuantityChange(product, newQuantity) {
  const quantity = parseInt(newQuantity) || 0

  if (quantity === 0) {
    cartStore.removeItem(product.id)
  } else {
    const existingItem = cartStore.items.find((i) => i.product_id === product.id)
    if (existingItem) {
      cartStore.updateQuantity(product.id, quantity)
    } else {
      cartStore.addItem({
        product_id: product.id,
        merchant_id: product.merchant_id,
        merchant_name: merchant.value?.business_name || '',
        name: product.name,
        price: product.price,
        image_url: product.image_url,
        quantity,
      })
      showToast(`已添加 ${product.name}`)
    }
  }
}

function goToCart() {
  router.push('/cart')
}

watch(
    () => route.params.id,
    (newId) => {
      if (newId) {
        merchant.value = null
        categories.value = []
        products.value = []
        productCartQuantity.value = {}
        activeCategoryId.value = null
        productsPage.value = 1
        productsFinished.value = false
        fetchMerchantDetail()
        fetchCategories()
        fetchProducts()
      }
    }
  )

onMounted(() => {
  fetchMerchantDetail()
  fetchCategories()
  fetchProducts()
})
</script>

<style scoped>
.merchant-detail {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 20px;
}

.merchant-header {
  background-color: #fff;
  padding: 12px;
  margin-bottom: 8px;
}

.skeleton-header {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}

.merchant-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.merchant-logo-wrapper {
  flex-shrink: 0;
}

.merchant-logo {
  width: 70px;
  height: 70px;
}

.merchant-logo-default {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1989fa 0%, #409eff 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
}

.merchant-basic-info {
  flex: 1;
  min-width: 0;
}

.merchant-title {
  margin: 0 0 6px 0;
  font-size: 18px;
  font-weight: bold;
  color: #323233;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.merchant-tags {
  display: flex;
  gap: 6px;
}

.merchant-address-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 0;
  font-size: 13px;
  color: #969799;
  border-top: 1px solid #f7f8fa;
}

.merchant-desc-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 0;
  font-size: 13px;
  color: #969799;
  border-top: 1px solid #f7f8fa;
}

.main-content {
  display: flex;
  min-height: calc(100vh - 200px);
}

.category-sidebar {
  width: 85px;
  background-color: #f6f6f6;
  flex-shrink: 0;
  overflow-y: auto;
  max-height: calc(100vh - 200px);
  position: sticky;
  top: 46px;
}

.category-list {
  padding-top: 8px;
}

.category-item {
  padding: 12px 8px;
  text-align: center;
  font-size: 13px;
  color: #646566;
  cursor: pointer;
  position: relative;
  background-color: #f6f6f6;
  transition: all 0.2s;
}

.category-item.active {
  background-color: #fff;
  color: #1989fa;
  font-weight: bold;
}

.category-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background-color: #1989fa;
  border-radius: 0 2px 2px 0;
}

.category-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-area {
  flex: 1;
  background-color: #fff;
  min-width: 0;
  overflow-y: auto;
}

.category-title {
  padding: 8px 12px;
  background-color: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.product-list {
  padding: 0 12px;
}

.product-item {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #f7f8fa;
}

.product-image-wrapper {
  flex-shrink: 0;
  margin-right: 12px;
}

.product-image-default {
  width: 80px;
  height: 80px;
  background-color: #f7f8fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c8c9cc;
}

.product-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: 15px;
  font-weight: bold;
  color: #323233;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-desc {
  font-size: 12px;
  color: #969799;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.sales-count {
  font-size: 12px;
  color: #969799;
}

.unavailable-tag {
  font-size: 12px;
  color: #ee0a24;
}

.product-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.product-price {
  display: flex;
  align-items: baseline;
}

.product-price .price-symbol {
  font-size: 12px;
  color: #ee0a24;
}

.product-price .price-value {
  font-size: 18px;
  font-weight: bold;
  color: #ee0a24;
  margin-left: 2px;
}

.original-price {
  font-size: 12px;
  color: #969799;
  text-decoration: line-through;
  margin-left: 8px;
}

.product-add-cart {
  display: flex;
  align-items: center;
}

.cart-float-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50px;
  background-color: #1a1a1a;
  display: flex;
  align-items: center;
  z-index: 100;
}

.cart-icon-wrapper {
  position: relative;
  width: 50px;
  height: 50px;
  cursor: pointer;
  margin-top: -20px;
}

.cart-icon-badge {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #1989fa;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  position: relative;
}

.cart-badge {
  position: absolute;
  top: -4px;
  right: -4px;
}

.cart-total-info {
  flex: 1;
  padding: 0 12px;
  cursor: pointer;
}

.cart-total-price {
  display: flex;
  align-items: baseline;
  color: #fff;
}

.cart-total-price .price-symbol {
  font-size: 12px;
}

.cart-total-price .price-value {
  font-size: 20px;
  font-weight: bold;
  margin-left: 2px;
}

.cart-tip {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
}

.cart-checkout-btn {
  background-color: #1989fa;
  color: #fff;
  height: 50px;
  line-height: 50px;
  padding: 0 20px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
}

.bottom-spacer {
  height: 50px;
}

:deep(.van-divider--left-line) {
  border-color: #ebedf0;
}

:deep(.van-divider__text) {
  font-size: 14px;
  color: #323233;
}
</style>
