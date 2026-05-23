<template>
  <div class="orders">
    <van-nav-bar title="我的订单" />

    <div class="tabs-container">
      <van-tabs v-model:active="activeTab" sticky offset-top="0" @change="onTabChange">
        <van-tab name="" title="全部" />
        <van-tab name="pending" title="待付款" />
        <van-tab name="paid" title="已付款" />
        <van-tab name="preparing" title="制作中" />
        <van-tab name="delivering" title="配送中" />
        <van-tab name="completed" title="已完成" />
        <van-tab name="cancelled" title="已取消" />
      </van-tabs>
    </div>

    <div class="content">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <van-empty
          v-if="!loading && orders.length === 0"
          :description="emptyText"
          image="search"
        />

        <div v-else class="order-list">
          <div
            v-for="order in orders"
            :key="order.id"
            class="order-card"
            @click="goToOrderDetail(order.id)"
          >
            <div class="order-header">
              <span class="merchant-name">{{ order.merchant_name || '商家' }}</span>
              <span class="order-status" :class="'status-' + order.status">
                {{ getStatusText(order.status) }}
              </span>
            </div>

            <div class="order-items">
              <div
                v-for="item in order.items"
                :key="item.id"
                class="order-item"
              >
                <span class="item-name">{{ item.product_name }}</span>
                <span class="item-qty">x{{ item.quantity }}</span>
              </div>
            </div>

            <div class="order-footer">
              <div class="order-amount">
                <span class="amount-label">合计：</span>
                <span class="currency">¥</span>
                <span class="amount-value">{{ formatPrice(order.pay_amount) }}</span>
              </div>

              <div class="order-actions" v-if="showActions(order.status)">
                <van-button
                  v-if="order.status === 'pending'"
                  size="small"
                  type="primary"
                  @click.stop="handlePay(order.id)"
                >
                  立即支付
                </van-button>
                <van-button
                  v-if="order.status === 'pending'"
                  size="small"
                  plain
                  type="danger"
                  class="cancel-btn"
                  @click.stop="handleCancel(order.id)"
                >
                  取消订单
                </van-button>
              </div>
            </div>
          </div>
        </div>
      </van-list>
    </div>

    <div class="action-sheet">
      <van-dialog v-model:show="showCancelDialog" title="取消订单" show-cancel-button @confirm="confirmCancel">
        <van-field
          v-model="cancelReason"
          rows="2"
          type="textarea"
          placeholder="请填写取消原因（选填）"
          maxlength="100"
          show-word-limit
        />
      </van-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUserOrders, cancelOrder, payOrder } from '@/api/orders'
import { getMerchantDetail } from '@/api/merchants'
import { showConfirmDialog, showToast } from 'vant'

const router = useRouter()
const activeTab = ref('')
const orders = ref([])
const loading = ref(false)
const finished = ref(false)
const currentPage = ref(1)
const pageSize = 10

const showCancelDialog = ref(false)
const cancelReason = ref('')
const cancellingOrderId = ref(null)

const statusMap = {
  pending: '待付款',
  paid: '已付款',
  preparing: '制作中',
  delivering: '配送中',
  completed: '已完成',
  cancelled: '已取消',
  refunded: '已退款',
}

const emptyTextMap = {
  '': '暂无订单',
  pending: '暂无待付款订单',
  paid: '暂无已付款订单',
  preparing: '暂无制作中订单',
  delivering: '暂无配送中订单',
  completed: '暂无已完成订单',
  cancelled: '暂无已取消订单',
}

const emptyText = computed(() => emptyTextMap[activeTab.value] || '暂无订单')

function getStatusText(status) {
  return statusMap[status] || '未知状态'
}

function formatPrice(price) {
  return parseFloat(price).toFixed(2)
}

function showActions(status) {
  return status === 'pending'
}

async function fetchMerchantName(order) {
  if (order.merchant_name) return
  try {
    const merchant = await getMerchantDetail(order.merchant_id)
    order.merchant_name = merchant.business_name
  } catch (error) {
    order.merchant_name = '商家'
  }
}

async function fetchOrders(isRefresh = false) {
  if (loading.value) return

  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
    }

    if (activeTab.value) {
      params.status = activeTab.value
    }

    const res = await getUserOrders(params)
    const items = res.items || []

    for (const order of items) {
      await fetchMerchantName(order)
    }

    if (isRefresh || currentPage.value === 1) {
      orders.value = items
    } else {
      orders.value = [...orders.value, ...items]
    }

    finished.value = items.length < pageSize
    currentPage.value++
  } catch (error) {
    console.error('获取订单列表失败:', error)
  } finally {
    loading.value = false
  }
}

function onTabChange() {
  orders.value = []
  currentPage.value = 1
  finished.value = false
  loading.value = false
  fetchOrders(true)
}

function onLoad() {
  if (!finished.value) {
    fetchOrders()
  }
}

function goToOrderDetail(orderId) {
  router.push(`/orders/${orderId}`)
}

async function handlePay(orderId) {
  try {
    await showConfirmDialog({
      title: '确认支付',
      message: '确认支付此订单？',
    })
    await payOrder(orderId)
    showToast('支付成功')
    fetchOrders(true)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('支付失败:', error)
    }
  }
}

function handleCancel(orderId) {
  cancellingOrderId.value = orderId
  cancelReason.value = ''
  showCancelDialog.value = true
}

async function confirmCancel() {
  try {
    await cancelOrder(cancellingOrderId.value, {
      reason: cancelReason.value || null,
    })
    showToast('订单已取消')
    showCancelDialog.value = false
    fetchOrders(true)
  } catch (error) {
    console.error('取消订单失败:', error)
  }
}

onMounted(() => {
  const statusQuery = router.currentRoute.value.query.status
  if (statusQuery && statusMap[statusQuery]) {
    activeTab.value = statusQuery
  }
  fetchOrders(true)
})
</script>

<style scoped>
.orders {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 80px;
}

.tabs-container {
  background-color: #fff;
}

.content {
  padding: 12px;
  min-height: calc(100vh - 120px);
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
}

.order-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f7f8fa;
}

.merchant-name {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}

.order-status {
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 4px;
}

.status-pending {
  background-color: #fff7ed;
  color: #ff9800;
}

.status-paid,
.status-preparing {
  background-color: #edf7ff;
  color: #1989fa;
}

.status-delivering {
  background-color: #f0f9eb;
  color: #67c23a;
}

.status-completed {
  background-color: #f0f9eb;
  color: #67c23a;
}

.status-cancelled {
  background-color: #f5f5f5;
  color: #909399;
}

.status-refunded {
  background-color: #f5f5f5;
  color: #909399;
}

.order-items {
  margin-bottom: 12px;
}

.order-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 0;
}

.item-name {
  font-size: 14px;
  color: #323233;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 8px;
}

.item-qty {
  font-size: 13px;
  color: #969799;
  flex-shrink: 0;
}

.order-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #f7f8fa;
}

.order-amount {
  display: flex;
  align-items: baseline;
}

.amount-label {
  font-size: 14px;
  color: #646566;
}

.currency {
  font-size: 12px;
  color: #ee0a24;
  margin-left: 4px;
}

.amount-value {
  font-size: 16px;
  color: #ee0a24;
  font-weight: 500;
}

.order-actions {
  display: flex;
  gap: 8px;
}

.cancel-btn {
  border-color: #ee0a24;
  color: #ee0a24;
}
</style>
