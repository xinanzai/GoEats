<template>
  <div class="statistics-view">
    <el-card>
      <div class="page-header">
        <h2>数据统计</h2>
      </div>

      <div class="filter-bar">
        <el-select
          v-model="daysRange"
          placeholder="选择统计天数"
          style="width: 150px"
          @change="fetchStatistics"
        >
          <el-option label="近7天" :value="7" />
          <el-option label="近30天" :value="30" />
          <el-option label="近90天" :value="90" />
          <el-option label="近一年" :value="365" />
        </el-select>
      </div>
    </el-card>

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
              <span>收入趋势</span>
            </div>
          </template>
          <div ref="revenueChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>订单状态分布</span>
            </div>
          </template>
          <div ref="orderStatusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>热销商品排行</span>
            </div>
          </template>
          <div ref="popularProductsChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="summary-card">
      <template #header>
        <div class="chart-header">
          <span>统计汇总</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">统计周期内订单总数</div>
            <div class="summary-value">{{ statisticsSummary.totalOrders }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">统计周期内总收入</div>
            <div class="summary-value">¥{{ formatMoney(statisticsSummary.totalRevenue) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">平均每日订单数</div>
            <div class="summary-value">{{ statisticsSummary.avgDailyOrders }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">平均每日收入</div>
            <div class="summary-value">¥{{ formatMoney(statisticsSummary.avgDailyRevenue) }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="products-card">
      <template #header>
        <div class="chart-header">
          <span>热销商品明细</span>
        </div>
      </template>
      <el-table :data="popularProducts" v-loading="productsLoading" stripe border>
        <el-table-column prop="id" label="商品ID" width="100" />
        <el-table-column prop="name" label="商品名称" />
        <el-table-column prop="total_sold" label="销售数量" width="120" align="center">
          <template #default="{ row }">
            <el-tag type="success">{{ row.total_sold }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_revenue" label="销售收入" width="150">
          <template #default="{ row }">
            <span class="revenue">¥{{ formatMoney(row.total_revenue) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { getStatistics, getOrderList } from '@/api/orders'
import * as echarts from 'echarts'

const daysRange = ref(30)
const popularProducts = ref([])
const productsLoading = ref(false)

const orderChartRef = ref(null)
const revenueChartRef = ref(null)
const orderStatusChartRef = ref(null)
const popularProductsChartRef = ref(null)

let orderChart = null
let revenueChart = null
let orderStatusChart = null
let popularProductsChart = null

const statisticsSummary = reactive({
  totalOrders: 0,
  totalRevenue: 0,
  avgDailyOrders: 0,
  avgDailyRevenue: 0
})

function formatMoney(value) {
  if (!value && value !== 0) return '0.00'
  return Number(value).toFixed(2)
}

async function fetchStatistics() {
  productsLoading.value = true
  try {
    const data = await getStatistics({ days: daysRange.value })

    if (data.order_statistics && data.order_statistics.data) {
      renderOrderChart(data.order_statistics.data)
      renderRevenueChart(data.order_statistics.data)
      calculateSummary(data.order_statistics.data)
    }

    if (data.popular_products) {
      popularProducts.value = data.popular_products
      renderPopularProductsChart(data.popular_products)
    }

    await fetchOrderStatusDistribution()
  } catch (error) {
    console.error('获取统计数据失败:', error)
  } finally {
    productsLoading.value = false
  }
}

async function fetchOrderStatusDistribution() {
  try {
    const statusList = ['pending', 'paid', 'preparing', 'delivering', 'completed', 'cancelled', 'refunded']
    const statusCounts = {}

    for (const status of statusList) {
      const data = await getOrderList({ page: 1, page_size: 1, status })
      statusCounts[status] = data.total || 0
    }

    renderOrderStatusChart(statusCounts)
  } catch (error) {
    console.error('获取订单状态分布失败:', error)
  }
}

function calculateSummary(data) {
  const totalOrders = data.reduce((sum, item) => sum + item.order_count, 0)
  const totalRevenue = data.reduce((sum, item) => sum + Number(item.revenue), 0)
  const days = data.length || 1

  statisticsSummary.totalOrders = totalOrders
  statisticsSummary.totalRevenue = totalRevenue
  statisticsSummary.avgDailyOrders = Math.round(totalOrders / days)
  statisticsSummary.avgDailyRevenue = totalRevenue / days
}

function renderOrderChart(data) {
  if (!orderChartRef.value) return

  if (!orderChart) {
    orderChart = echarts.init(orderChartRef.value)
  }

  const dates = data.map((item) => item.date.substring(5))
  const orderCounts = data.map((item) => item.order_count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
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
    yAxis: {
      type: 'value',
      name: '订单数'
    },
    series: [
      {
        name: '订单数',
        type: 'bar',
        data: orderCounts,
        itemStyle: {
          color: '#409EFF'
        },
        emphasis: {
          itemStyle: {
            color: '#66b1ff'
          }
        }
      }
    ]
  }

  orderChart.setOption(option)
}

function renderRevenueChart(data) {
  if (!revenueChartRef.value) return

  if (!revenueChart) {
    revenueChart = echarts.init(revenueChartRef.value)
  }

  const dates = data.map((item) => item.date.substring(5))
  const revenues = data.map((item) => Number(item.revenue).toFixed(2))

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>收入: ¥{c}'
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
    yAxis: {
      type: 'value',
      name: '收入(元)',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '收入',
        type: 'line',
        data: revenues,
        smooth: true,
        itemStyle: {
          color: '#67C23A'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
            ]
          }
        }
      }
    ]
  }

  revenueChart.setOption(option)
}

function renderOrderStatusChart(statusCounts) {
  if (!orderStatusChartRef.value) return

  if (!orderStatusChart) {
    orderStatusChart = echarts.init(orderStatusChartRef.value)
  }

  const statusTextMap = {
    pending: '待付款',
    paid: '已付款',
    preparing: '制作中',
    delivering: '配送中',
    completed: '已完成',
    cancelled: '已取消',
    refunded: '已退款'
  }

  const colorMap = {
    pending: '#909399',
    paid: '#409EFF',
    preparing: '#E6A23C',
    delivering: '#909399',
    completed: '#67C23A',
    cancelled: '#F56C6C',
    refunded: '#F56C6C'
  }

  const pieData = Object.keys(statusCounts).map((key) => ({
    name: statusTextMap[key] || key,
    value: statusCounts[key],
    itemStyle: {
      color: colorMap[key] || '#409EFF'
    }
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center'
    },
    series: [
      {
        name: '订单状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: pieData
      }
    ]
  }

  orderStatusChart.setOption(option)
}

function renderPopularProductsChart(products) {
  if (!popularProductsChartRef.value) return

  if (!popularProductsChart) {
    popularProductsChart = echarts.init(popularProductsChartRef.value)
  }

  const top10 = products.slice(0, 10)
  const names = top10.map((item) => item.name)
  const sold = top10.map((item) => item.total_sold)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '销售数量'
    },
    yAxis: {
      type: 'category',
      data: names.reverse(),
      axisLabel: {
        formatter: (value) => {
          return value.length > 8 ? value.substring(0, 8) + '...' : value
        }
      }
    },
    series: [
      {
        name: '销售数量',
        type: 'bar',
        data: sold.reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }
    ]
  }

  popularProductsChart.setOption(option)
}

function handleResize() {
  if (orderChart) orderChart.resize()
  if (revenueChart) revenueChart.resize()
  if (orderStatusChart) orderStatusChart.resize()
  if (popularProductsChart) popularProductsChart.resize()
}

onMounted(() => {
  fetchStatistics()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (orderChart) orderChart.dispose()
  if (revenueChart) revenueChart.dispose()
  if (orderStatusChart) orderStatusChart.dispose()
  if (popularProductsChart) popularProductsChart.dispose()
})
</script>

<style scoped>
.statistics-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
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
  font-size: 16px;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.summary-card {
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
  padding: 20px;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.products-card {
  margin-top: 20px;
}

.revenue {
  color: #f56c6c;
  font-weight: bold;
}
</style>
