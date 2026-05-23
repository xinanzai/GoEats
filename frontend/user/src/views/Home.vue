<template>
  <div class="home">
    <!-- 顶部搜索栏 -->
    <div class="search-bar">
      <van-search
        v-model="searchQuery"
        placeholder="搜索商家或美食"
        shape="round"
        show-action
        @search="handleSearch"
        @input="handleInput"
        @clear="handleClear"
        @cancel="handleCancel"
      />
    </div>

    <!-- 排序选项 -->
    <div class="sort-bar">
      <div
        class="sort-item"
        :class="{ active: activeSort === 'default' }"
        @click="activeSort = 'default'"
      >
        默认
      </div>
      <div
        class="sort-item"
        :class="{ active: activeSort === 'distance' }"
        @click="activeSort = 'distance'"
      >
        距离
      </div>
      <div
        class="sort-item"
        :class="{ active: activeSort === 'sales' }"
        @click="activeSort = 'sales'"
      >
        销量
      </div>
      <div
        class="sort-item"
        :class="{ active: activeSort === 'rating' }"
        @click="activeSort = 'rating'"
      >
        评分
      </div>
    </div>

    <!-- 商家列表 -->
    <div class="merchant-list">
      <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
        <van-list
          v-model:loading="loading"
          :finished="finished"
          finished-text="没有更多了"
          @load="onLoad"
        >
          <div
            v-for="merchant in merchants"
            :key="merchant.id"
            class="merchant-card"
            @click="goToMerchant(merchant.id)"
          >
            <!-- 商家头部信息 -->
            <div class="merchant-header">
              <div class="merchant-logo-wrapper">
                <van-image
                  v-if="merchant.logo"
                  :src="merchant.logo"
                  class="merchant-logo"
                  round
                  fit="cover"
                />
                <div v-else class="merchant-logo-default">
                  {{ merchant.business_name.charAt(0) }}
                </div>
              </div>
              <div class="merchant-info">
                <div class="merchant-name">{{ merchant.business_name }}</div>
                <div class="merchant-meta">
                  <span class="meta-item">评分 4.8</span>
                  <span class="meta-item">月售 1000+</span>
                  <span class="meta-item">配送费 ¥3</span>
                </div>
              </div>
            </div>

            <!-- 商家描述 -->
            <div class="merchant-desc" v-if="merchant.description">
              {{ merchant.description }}
            </div>

            <!-- 商家地址 -->
            <div class="merchant-address">
              <van-icon name="location" />
              {{ merchant.address }}
            </div>

            <!-- 商家状态标签 -->
            <div class="merchant-status" v-if="merchant.status === 'approved'">
              <van-tag type="success" size="medium" round>营业中</van-tag>
            </div>
          </div>
        </van-list>

        <!-- 空状态 -->
        <van-empty
          v-if="!loading && merchants.length === 0"
          description="暂无商家"
          image="search"
        />
      </van-pull-refresh>
    </div>

    <!-- 底部导航栏已移至 App.vue -->
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getMerchantList } from '@/api/merchants'

const router = useRouter()

const searchQuery = ref('')
const activeSort = ref('default')
const merchants = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const currentPage = ref(1)
const pageSize = 20
const debounceTimer = ref(null)

watch(activeSort, () => {
  resetList()
})

// 防抖搜索
function handleInput(value) {
  clearTimeout(debounceTimer.value)
  debounceTimer.value = setTimeout(() => {
    if (value) {
      searchMerchants(value)
    } else {
      resetList()
    }
  }, 500)
}

function handleSearch() {
  clearTimeout(debounceTimer.value)
  if (searchQuery.value) {
    searchMerchants(searchQuery.value)
  } else {
    resetList()
  }
}

function handleClear() {
  clearTimeout(debounceTimer.value)
  searchQuery.value = ''
  resetList()
}

function handleCancel() {
  clearTimeout(debounceTimer.value)
  searchQuery.value = ''
  resetList()
}

async function searchMerchants(query) {
  try {
    loading.value = true
    currentPage.value = 1
    merchants.value = []
    finished.value = false

    const res = await getMerchantList({
      page: 1,
      page_size: pageSize,
      search: query,
    })

    merchants.value = res.items || []
    finished.value = merchants.value.length < pageSize
  } catch (error) {
    console.error('搜索商家失败:', error)
  } finally {
    loading.value = false
  }
}

function resetList() {
  currentPage.value = 1
  merchants.value = []
  finished.value = false
  fetchMerchants()
}

async function fetchMerchants() {
  try {
    loading.value = true

    const res = await getMerchantList({
      page: currentPage.value,
      page_size: pageSize,
      search: searchQuery.value || undefined,
    })

    if (currentPage.value === 1) {
      merchants.value = res.items || []
    } else {
      merchants.value = [...merchants.value, ...(res.items || [])]
    }

    finished.value = (res.items || []).length < pageSize
    currentPage.value++
  } catch (error) {
    console.error('获取商家列表失败:', error)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onLoad() {
  if (!finished.value) {
    fetchMerchants()
  }
}

function onRefresh() {
  refreshing.value = true
  currentPage.value = 1
  merchants.value = []
  finished.value = false
  fetchMerchants()
}

function goToMerchant(merchantId) {
  router.push(`/merchant/${merchantId}`)
}

onMounted(() => {
  fetchMerchants()
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 50px;
}

.search-bar {
  background-color: #1989fa;
  padding: 8px 12px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.sort-bar {
  display: flex;
  background-color: #fff;
  padding: 8px 0;
  position: sticky;
  top: 52px;
  z-index: 99;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.sort-item {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 14px;
  color: #646566;
  cursor: pointer;
  position: relative;
}

.sort-item.active {
  color: #1989fa;
  font-weight: bold;
}

.sort-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background-color: #1989fa;
  border-radius: 2px;
}

.merchant-list {
  padding: 8px;
}

.merchant-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s;
}

.merchant-card:active {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.merchant-header {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.merchant-logo-wrapper {
  flex-shrink: 0;
}

.merchant-logo {
  width: 60px;
  height: 60px;
}

.merchant-logo-default {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #1989fa;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.merchant-info {
  flex: 1;
  min-width: 0;
}

.merchant-name {
  font-size: 16px;
  font-weight: bold;
  color: #323233;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.merchant-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 12px;
  color: #969799;
}

.merchant-desc {
  font-size: 13px;
  color: #969799;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.merchant-address {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #969799;
}

.merchant-address .van-icon {
  font-size: 14px;
}

.merchant-status {
  margin-top: 8px;
}

.cart-badge {
  position: absolute;
  top: -4px;
  right: -8px;
  background-color: #ee0a24;
  color: #fff;
  font-size: 10px;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}
</style>
