<template>
  <div class="order-detail">
    <van-nav-bar :title="orderNo" left-arrow @click-left="$router.back()" />

    <van-loading v-if="loading" class="loading" />

    <div v-else-if="order" class="detail-container">
      <!-- 状态进度条 -->
      <div class="status-section">
        <van-steps :active="activeStep" direction="vertical" active-color="#1989fa">
          <van-step v-if="order.status === 'pending'">待付款</van-step>
          <van-step v-if="['paid', 'preparing', 'delivering', 'completed'].includes(order.status)">
            已付款
          </van-step>
          <van-step v-if="['preparing', 'delivering', 'completed'].includes(order.status)">
            制作中
          </van-step>
          <van-step v-if="['delivering', 'completed'].includes(order.status)">
            配送中
          </van-step>
          <van-step v-if="order.status === 'completed'">已完成</van-step>
          <van-step v-if="order.status === 'cancelled'">已取消</van-step>
        </van-steps>
        <div class="status-tag" :class="'status-' + order.status">
          {{ statusText }}
        </div>
      </div>

      <!-- 商家信息 -->
      <van-cell-group class="section-card">
        <van-cell title="商家信息">
          <template #default>
            <div class="merchant-info">
              <img v-if="merchantLogo" :src="merchantLogo" class="merchant-logo" />
              <div v-else class="merchant-logo-default">{{ merchantInitial }}</div>
              <div class="merchant-name">{{ merchantName }}</div>
            </div>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 收货地址 -->
      <van-cell-group class="section-card">
        <van-cell title="收货信息" />
        <van-cell :title="receiver" :label="receiverAddress" />
        <van-cell :title="receiverPhone" />
      </van-cell-group>

      <!-- 商品清单 -->
      <van-cell-group class="section-card">
        <van-cell title="商品清单" />
        <van-cell
          v-for="item in order.items"
          :key="item.id"
          :title="item.product_name"
          :label="`${formatPrice(item.price)} x ${item.quantity}`"
        >
          <template #right-icon>
            <span class="item-subtotal">¥{{ formatPrice(item.subtotal) }}</span>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 金额明细 -->
      <van-cell-group class="section-card">
        <van-cell title="金额明细" />
        <van-cell title="商品总价" :value="formatPrice(order.total_price)" />
        <van-cell v-if="order.discount_amount > 0" title="优惠金额" :value="`-${formatPrice(order.discount_amount)}`">
          <template #right-icon>
            <span class="discount">-{{ formatPrice(order.discount_amount) }}</span>
          </template>
        </van-cell>
        <van-cell v-if="order.delivery_fee > 0" title="配送费" :value="formatPrice(order.delivery_fee)" />
        <van-cell title="实付金额" :value="`¥${formatPrice(order.pay_amount)}`">
          <template #right-icon>
            <span class="pay-amount">¥{{ formatPrice(order.pay_amount) }}</span>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 备注 -->
      <van-cell-group v-if="order.remark" class="section-card">
        <van-cell title="用户备注" :label="order.remark" />
      </van-cell-group>

      <!-- 订单信息 -->
      <van-cell-group class="section-card">
        <van-cell title="订单信息" />
        <van-cell title="订单编号" :label="order.order_no" />
        <van-cell title="下单时间" :label="formatDateTime(order.created_at)" />
        <van-cell v-if="order.paid_at" title="支付时间" :label="formatDateTime(order.paid_at)" />
        <van-cell v-if="order.completed_at" title="完成时间" :label="formatDateTime(order.completed_at)" />
      </van-cell-group>

      <!-- 操作按钮 -->
      <div class="action-buttons" v-if="showActions">
        <van-button
          v-if="order.status === 'pending'"
          block
          type="primary"
          @click="handlePay"
        >
          立即支付
        </van-button>
        <van-button
          v-if="order.status === 'pending'"
          block
          plain
          type="danger"
          class="cancel-btn"
          @click="handleCancel"
        >
          取消订单
        </van-button>
      </div>
    </div>

    <van-empty v-else description="订单不存在" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrderDetail, payOrder, cancelOrder } from '@/api/orders'
import { getMerchantDetail } from '@/api/merchants'
import { showConfirmDialog, showToast } from 'vant'

const route = useRoute()
const router = useRouter()
const orderId = parseInt(route.params.id)

const loading = ref(true)
const order = ref(null)
const merchantName = ref('')
const merchantLogo = ref('')

const merchantInitial = computed(() => merchantName.value?.charAt(0) || '?')

const statusMap = {
  pending: '待付款',
  paid: '已付款',
  preparing: '制作中',
  delivering: '配送中',
  completed: '已完成',
  cancelled: '已取消',
  refunded: '已退款',
}

const statusText = computed(() => statusMap[order.value?.status] || '未知状态')

const activeStep = computed(() => {
  const status = order.value?.status
  if (status === 'cancelled') return 0
  if (status === 'pending') return 0
  if (status === 'paid') return 1
  if (status === 'preparing') return 2
  if (status === 'delivering') return 3
  if (status === 'completed') return 4
  return 0
})

const showActions = computed(() => order.value?.status === 'pending')

function formatPrice(price) {
  return (parseFloat(price) || 0).toFixed(2)
}

function formatDateTime(dateTime) {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN')
}

async function fetchOrderDetail() {
  try {
    loading.value = true
    order.value = await getOrderDetail(orderId)

    try {
      const merchant = await getMerchantDetail(order.value.merchant_id)
      merchantName.value = merchant.business_name
      merchantLogo.value = merchant.logo
    } catch (err) {
      console.error('获取商家信息失败:', err)
    }
  } catch (error) {
    console.error('获取订单详情失败:', error)
  } finally {
    loading.value = false
  }
}

async function handlePay() {
  try {
    await showConfirmDialog({
      title: '确认支付',
      message: `确认支付 ¥${formatPrice(order.value.pay_amount)}？`,
    })
    await payOrder(orderId)
    showToast('支付成功')
    await fetchOrderDetail()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('支付失败:', error)
    }
  }
}

async function handleCancel() {
  try {
    await showConfirmDialog({
      title: '确认取消',
      message: '确认取消此订单？',
    })
    await cancelOrder(orderId)
    showToast('订单已取消')
    await fetchOrderDetail()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
    }
  }
}

onMounted(() => {
  fetchOrderDetail()
})
</script>

<style scoped>
.order-detail {
  min-height: 100vh;
  background-color: #f7f8fa;
}

.loading {
  padding: 40px 0;
}

.detail-container {
  padding-bottom: 100px;
}

.status-section {
  background-color: #fff;
  padding: 16px;
  margin-bottom: 8px;
}

.status-tag {
  margin-top: 12px;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
  display: inline-block;
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

.section-card {
  margin-bottom: 8px;
}

.merchant-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.merchant-logo,
.merchant-logo-default {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.merchant-logo-default {
  background-color: #1989fa;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
}

.merchant-name {
  font-size: 14px;
  color: #323233;
}

.item-subtotal {
  color: #ee0a24;
  font-size: 14px;
}

.discount {
  color: #ee0a24;
  font-size: 14px;
}

.pay-amount {
  color: #ee0a24;
  font-size: 16px;
  font-weight: bold;
}

.action-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  background-color: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.cancel-btn {
  margin-top: 8px;
}
</style>
