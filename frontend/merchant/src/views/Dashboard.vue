<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409EFF">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_orders || 0 }}</div>
              <div class="stat-label">今日订单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #E6A23C">
              <el-icon :size="30"><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending_orders || 0 }}</div>
              <div class="stat-label">待处理订单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67C23A">
              <el-icon :size="30"><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ formatMoney(stats.today_revenue) }}</div>
              <div class="stat-label">今日收入</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #F56C6C">
              <el-icon :size="30"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_orders || 0 }}</div>
              <div class="stat-label">总订单数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #909399">
              <el-icon :size="30"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending_payment || 0 }}</div>
              <div class="stat-label">待付款</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #79BBFA">
              <el-icon :size="30"><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.preparing || 0 }}</div>
              <div class="stat-label">制作中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #52C41A">
              <el-icon :size="30"><Van /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.delivering || 0 }}</div>
              <div class="stat-label">配送中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #1890FF">
              <el-icon :size="30"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.completed_orders || 0 }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>近期订单趋势</span>
            </div>
          </template>
          <div ref="orderChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>订单状态分布</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="recent-orders">
      <template #header>
        <div class="card-header">
          <span>最近订单</span>
          <el-button text @click="goToOrders">查看更多</el-button>
        </div>
      </template>
      <el-table :data="recentOrders" v-loading="ordersLoading" stripe>
        <el-table-column prop="order_no" label="订单编号" width="180" />
        <el-table-column prop="receiver" label="收货人" width="120" />
        <el-table-column prop="pay_amount" label="实付金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ formatMoney(row.pay_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { getMyOrders } from '@/api/orders'
import * as echarts from 'echarts'
import {
  Document,
  Bell,
  Money,
  TrendCharts,
  Clock,
  Timer,
  Van,
  CircleCheck
} from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref({
  today_orders: 0,
  pending_orders: 0,
  today_revenue: 0,
  total_orders: 0,
  pending_payment: 0,
  preparing: 0,
  delivering: 0,
  completed_orders: 0,
})

const recentOrders = ref([])
const ordersLoading = ref(false)

const orderChartRef = ref(null)
const statusChartRef = ref(null)
let orderChart = null
let statusChart = null

function formatMoney(value) {
  if (!value && value !== 0) return '0.00'
  return Number(value).toFixed(2)
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

function getStatusType(status) {
  const typeMap = {
    pending: '',
    paid: 'primary',
    preparing: 'warning',
    delivering: 'info',
    completed: 'success',
    cancelled: 'danger',
    refunded: 'danger'
  }
  return typeMap[status] || ''
}

function getStatusText(status) {
  const textMap = {
    pending: '待付款',
    paid: '已付款',
    preparing: '制作中',
    delivering: '配送中',
    completed: '已完成',
    cancelled: '已取消',
    refunded: '已退款'
  }
  return textMap[status] || status
}

function goToOrders() {
  router.push('/orders')
}

function calculateStats(orders) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  let todayOrders = 0
  let todayRevenue = 0
  let pendingOrders = 0
  let pendingPayment = 0
  let preparing = 0
  let delivering = 0
  let completedOrders = 0

  orders.forEach((order) => {
    const orderDate = new Date(order.created_at)

    if (orderDate >= today) {
      todayOrders++
      todayRevenue += Number(order.pay_amount) || 0
    }

    switch (order.status) {
      case 'pending':
        pendingOrders++
        pendingPayment++
        break
      case 'paid':
        pendingOrders++
        break
      case 'preparing':
        preparing++
        break
      case 'delivering':
        delivering++
        break
      case 'completed':
        completedOrders++
        break
    }
  })

  stats.value = {
    today_orders: todayOrders,
    pending_orders: pendingOrders,
    today_revenue: todayRevenue,
    total_orders: orders.length,
    pending_payment: pendingPayment,
    preparing,
    delivering,
    completed_orders: completedOrders,
  }
}

function renderOrderChart(orders) {
  if (!orderChartRef.value) return

  if (!orderChart) {
    orderChart = echarts.init(orderChartRef.value)
  }

  const last7Days = []
  const orderCounts = []
  const revenues = []

  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    date.setHours(0, 0, 0, 0)
    const dateStr = date.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit'
    })
    last7Days.push(dateStr)

    let dayOrders = 0
    let dayRevenue = 0
    const nextDate = new Date(date)
    nextDate.setDate(nextDate.getDate() + 1)

    orders.forEach((order) => {
      const orderDate = new Date(order.created_at)
      if (orderDate >= date && orderDate < nextDate) {
        dayOrders++
        dayRevenue += Number(order.pay_amount) || 0
      }
    })

    orderCounts.push(dayOrders)
    revenues.push(dayRevenue.toFixed(2))
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['订单数', '收入']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: last7Days,
    },
    yAxis: [
      {
        type: 'value',
        name: '订单数',
        position: 'left',
      },
      {
        type: 'value',
        name: '收入(元)',
        position: 'right',
        axisLine: {
          show: true,
          lineStyle: {
            color: '#E6A23C'
          }
        },
        axisLabel: {
          formatter: '{value}'
        }
      }
    ],
    series: [
      {
        name: '订单数',
        type: 'bar',
        data: orderCounts,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '收入',
        type: 'line',
        yAxisIndex: 1,
        data: revenues,
        itemStyle: {
          color: '#E6A23C'
        }
      }
    ]
  }

  orderChart.setOption(option)
}

function renderStatusChart() {
  if (!statusChartRef.value) return

  if (!statusChart) {
    statusChart = echarts.init(statusChartRef.value)
  }

  const statusData = [
    { name: '待付款', value: stats.value.pending_payment || 0, itemStyle: { color: '#909399' } },
    { name: '已付款', value: (stats.value.pending_orders - stats.value.pending_payment) || 0, itemStyle: { color: '#409EFF' } },
    { name: '制作中', value: stats.value.preparing || 0, itemStyle: { color: '#E6A23C' } },
    { name: '配送中', value: stats.value.delivering || 0, itemStyle: { color: '#79BBFA' } },
    { name: '已完成', value: stats.value.completed_orders || 0, itemStyle: { color: '#67C23A' } },
  ]

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        fontSize: 12
      }
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        center: ['50%', '50%'],
        data: statusData,
        label: {
          show: true,
          formatter: '{b}\n{c}'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  statusChart.setOption(option)
}

async function fetchDashboardData() {
  ordersLoading.value = true
  try {
    const data = await getMyOrders({ page: 1, page_size: 100 })
    const allOrders = data.items || []

    calculateStats(allOrders)
    recentOrders.value = allOrders.slice(0, 10)
    renderOrderChart(allOrders)
    renderStatusChart()
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  } finally {
    ordersLoading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})

onBeforeUnmount(() => {
  if (orderChart) {
    orderChart.dispose()
    orderChart = null
  }
  if (statusChart) {
    statusChart.dispose()
    statusChart = null
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 350px;
  width: 100%;
}

.recent-orders {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount {
  color: #f56c6c;
  font-weight: 500;
}
</style>
