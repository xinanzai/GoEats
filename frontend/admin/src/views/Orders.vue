<template>
  <div class="orders-view">
    <el-card>
      <div class="page-header">
        <h2>订单管理</h2>
      </div>

      <div class="search-bar">
        <el-input
          v-model="searchForm.order_no"
          placeholder="搜索订单编号"
          clearable
          style="width: 250px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="searchForm.status"
          placeholder="订单状态"
          clearable
          style="width: 150px"
        >
          <el-option label="待付款" value="pending" />
          <el-option label="已付款" value="paid" />
          <el-option label="制作中" value="preparing" />
          <el-option label="配送中" value="delivering" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
          <el-option label="已退款" value="refunded" />
        </el-select>

        <el-date-picker
          v-model="searchForm.dateRange"
          type="daterange"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 280px"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />

        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
    </el-card>

    <el-card class="table-card">
      <el-table
        :data="orderList"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="order_no" label="订单编号" width="180" />
        <el-table-column prop="receiver" label="收货人" width="120" />
        <el-table-column prop="receiver_phone" label="联系电话" width="140" />
        <el-table-column prop="receiver_address" label="收货地址" show-overflow-tooltip />
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
        <el-table-column prop="created_at" label="下单时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="120">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleViewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          :background="true"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="detailDialogVisible"
      title="订单详情"
      width="800px"
    >
      <div v-if="currentOrder">
        <el-descriptions :column="2" border class="order-info">
          <el-descriptions-item label="订单编号">{{ currentOrder.order_no }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getStatusType(currentOrder.status)" size="small">
              {{ getStatusText(currentOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="下单时间">
            {{ formatDateTime(currentOrder.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(currentOrder.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="收货人">{{ currentOrder.receiver }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentOrder.receiver_phone }}</el-descriptions-item>
          <el-descriptions-item label="收货地址" :span="2">
            {{ currentOrder.receiver_address }}
          </el-descriptions-item>
          <el-descriptions-item label="用户备注" :span="2">
            {{ currentOrder.remark || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="取消原因" v-if="currentOrder.cancel_reason" :span="2">
            <el-tag type="danger">{{ currentOrder.cancel_reason }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">商品清单</el-divider>

        <el-table :data="currentOrder.items" border stripe class="items-table">
          <el-table-column prop="product_name" label="商品名称" />
          <el-table-column prop="price" label="单价" width="120">
            <template #default="{ row }">
              ¥{{ formatMoney(row.price) }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="100" align="center" />
          <el-table-column prop="subtotal" label="小计" width="120">
            <template #default="{ row }">
              ¥{{ formatMoney(row.subtotal) }}
            </template>
          </el-table-column>
        </el-table>

        <el-divider content-position="left">金额明细</el-divider>

        <div class="amount-summary">
          <div class="amount-row">
            <span>商品总价：</span>
            <span>¥{{ formatMoney(currentOrder.total_price) }}</span>
          </div>
          <div class="amount-row" v-if="currentOrder.discount_amount > 0">
            <span>优惠金额：</span>
            <span class="discount">-¥{{ formatMoney(currentOrder.discount_amount) }}</span>
          </div>
          <div class="amount-row">
            <span>配送费用：</span>
            <span>¥{{ formatMoney(currentOrder.delivery_fee) }}</span>
          </div>
          <div class="amount-row total">
            <span>实付金额：</span>
            <span class="total-amount">¥{{ formatMoney(currentOrder.pay_amount) }}</span>
          </div>
        </div>

        <el-divider v-if="currentOrder.paid_at" content-position="left">支付信息</el-divider>
        <div v-if="currentOrder.paid_at" class="payment-info">
          <p>支付时间：{{ formatDateTime(currentOrder.paid_at) }}</p>
        </div>

        <el-divider v-if="currentOrder.completed_at" content-position="left">完成信息</el-divider>
        <div v-if="currentOrder.completed_at" class="completion-info">
          <p>完成时间：{{ formatDateTime(currentOrder.completed_at) }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getOrderList } from '@/api/orders'

const loading = ref(false)
const orderList = ref([])
const currentOrder = ref(null)
const detailDialogVisible = ref(false)

const searchForm = reactive({
  order_no: '',
  status: '',
  dateRange: null
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

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

async function fetchOrderList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (searchForm.order_no) params.order_no = searchForm.order_no
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = searchForm.dateRange[0]
      params.end_date = searchForm.dateRange[1]
    }

    const data = await getOrderList(params)
    orderList.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取订单列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchOrderList()
}

function handleReset() {
  searchForm.order_no = ''
  searchForm.status = ''
  searchForm.dateRange = null
  pagination.page = 1
  fetchOrderList()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchOrderList()
}

function handlePageChange(page) {
  pagination.page = page
  fetchOrderList()
}

function handleViewDetail(row) {
  currentOrder.value = row
  detailDialogVisible.value = true
}

onMounted(() => {
  fetchOrderList()
})
</script>

<style scoped>
.orders-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.table-card {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.amount {
  color: #f56c6c;
  font-weight: bold;
}

.order-info {
  margin-bottom: 20px;
}

.items-table {
  margin-bottom: 20px;
}

.amount-summary {
  padding: 15px 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.amount-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
}

.amount-row:last-child {
  margin-bottom: 0;
}

.amount-row.total {
  padding-top: 10px;
  border-top: 1px solid #dcdfe6;
  font-size: 16px;
  font-weight: bold;
}

.discount {
  color: #f56c6c;
}

.total-amount {
  color: #f56c6c;
  font-size: 20px;
}

.payment-info,
.completion-info {
  padding: 10px 20px;
}

.payment-info p,
.completion-info p {
  margin: 5px 0;
  color: #606266;
}
</style>
