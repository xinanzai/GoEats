<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409EFF">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.user_count || 0 }}</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67C23A">
              <el-icon :size="30"><OfficeBuilding /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.merchant_count || 0 }}</div>
              <div class="stat-label">商家总数</div>
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
              <div class="stat-value">{{ stats.pending_merchant_count || 0 }}</div>
              <div class="stat-label">待审核商家</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #F56C6C">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.order_count || 0 }}</div>
              <div class="stat-label">订单总数</div>
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
              <el-icon :size="30"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today_order_count || 0 }}</div>
              <div class="stat-label">今日订单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #79BBFA">
              <el-icon :size="30"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.month_order_count || 0 }}</div>
              <div class="stat-label">本月订单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #52C41A">
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
            <div class="stat-icon" style="background: #1890FF">
              <el-icon :size="30"><Coin /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ formatMoney(stats.month_revenue) }}</div>
              <div class="stat-label">本月收入</div>
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
              <span>订单趋势</span>
            </div>
          </template>
          <div ref="orderChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>商家状态分布</span>
            </div>
          </template>
          <div ref="merchantChartRef" class="chart-container"></div>
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
import { getDashboardStats } from '@/api/admin'
import { getStatistics, getOrderList } from '@/api/orders'
import * as echarts from 'echarts'
import {
  User,
  OfficeBuilding,
  Bell,
  Document,
  Calendar,
  TrendCharts,
  Money,
  Coin
} from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref({})
const recentOrders = ref([])
const ordersLoading = ref(false)

const orderChartRef = ref(null)
const merchantChartRef = ref(null)
let orderChart = null
let merchantChart = null

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

async function fetchDashboardStats() {
  try {
    const data = await getDashboardStats()
    stats.value = data
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  }
}

async function fetchOrderStatistics() {
  try {
    const data = await getStatistics({ days: 30 })
    if (data.order_statistics && data.order_statistics.data) {
      renderOrderChart(data.order_statistics.data)
    }
  } catch (error) {
    console.error('获取订单统计失败:', error)
  }
}

async function fetchRecentOrders() {
  ordersLoading.value = true
  try {
    const data = await getOrderList({ page: 1, page_size: 5 })
    recentOrders.value = data.items || []
  } catch (error) {
    console.error('获取最近订单失败:', error)
  } finally {
    ordersLoading.value = false
  }
}

function renderOrderChart(data) {
  if (!orderChartRef.value) return

  if (!orderChart) {
    orderChart = echarts.init(orderChartRef.value)
  }

  const dates = data.map((item) => item.date)
  const orderCounts = data.map((item) => item.order_count)
  const revenues = data.map((item) => Number(item.revenue).toFixed(2))

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
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '订单数'
      },
      {
        type: 'value',
        name: '收入(元)'
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
          color: '#67C23A'
        }
      }
    ]
  }

  orderChart.setOption(option)
}

function renderMerchantChart() {
  if (!merchantChartRef.value) return

  if (!merchantChart) {
    merchantChart = echarts.init(merchantChartRef.value)
  }

  const total = stats.value.merchant_count || 0
  const pending = stats.value.pending_merchant_count || 0
  const approved = total - pending

  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: [
          { value: approved, name: '已通过' },
          { value: pending, name: '待审核' }
        ],
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

  merchantChart.setOption(option)
}

function handleResize() {
  orderChart && orderChart.resize()
  merchantChart && merchantChart.resize()
}

function goToOrders() {
  router.push('/orders')
}

onMounted(async () => {
  await Promise.all([
    fetchDashboardStats(),
    fetchOrderStatistics(),
    fetchRecentOrders()
  ])
  renderMerchantChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  orderChart && orderChart.dispose()
  merchantChart && merchantChart.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 400px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount {
  color: #F56C6C;
  font-weight: bold;
}

.recent-orders {
  margin-bottom: 20px;
}
</style>

