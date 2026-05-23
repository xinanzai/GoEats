<template>
  <div class="merchants-view">
    <el-card>
      <div class="page-header">
        <h2>商家管理</h2>
      </div>

      <div class="search-bar">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索商家名称"
          clearable
          style="width: 300px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="searchForm.status"
          placeholder="状态筛选"
          clearable
          style="width: 150px"
        >
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已拒绝" value="rejected" />
        </el-select>

        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
    </el-card>

    <el-card class="table-card">
      <el-table
        :data="merchantList"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="business_name" label="商家名称" width="200" />
        <el-table-column prop="contact_phone" label="联系电话" width="150" />
        <el-table-column prop="address" label="地址" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="{ row }">
            <el-button size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="handleApprove(row)">
                通过
              </el-button>
              <el-button size="small" type="danger" @click="handleReject(row)">
                拒绝
              </el-button>
            </template>
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
      title="商家详情"
      width="700px"
    >
      <el-descriptions :column="2" border v-if="currentMerchant">
        <el-descriptions-item label="ID">{{ currentMerchant.id }}</el-descriptions-item>
        <el-descriptions-item label="商家名称">{{ currentMerchant.business_name }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentMerchant.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentMerchant.status)" size="small">
            {{ getStatusText(currentMerchant.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">
          {{ currentMerchant.address }}
        </el-descriptions-item>
        <el-descriptions-item label="商家描述" :span="2">
          {{ currentMerchant.description || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="Logo" :span="2">
          <el-avatar :size="80" :src="currentMerchant.logo" v-if="currentMerchant.logo" />
          <span v-else>未上传</span>
        </el-descriptions-item>
        <el-descriptions-item label="申请时间">
          {{ formatDateTime(currentMerchant.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDateTime(currentMerchant.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="审核时间" v-if="currentMerchant.approved_at">
          {{ formatDateTime(currentMerchant.approved_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="审核人" v-if="currentMerchant.approved_by">
          管理员 ID: {{ currentMerchant.approved_by }}
        </el-descriptions-item>
        <el-descriptions-item label="拒绝原因" v-if="currentMerchant.rejection_reason" :span="2">
          <el-tag type="danger"> {{ currentMerchant.rejection_reason }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <el-dialog
      v-model="rejectDialogVisible"
      title="拒绝商家审核"
      width="500px"
    >
      <el-form
        ref="rejectFormRef"
        :model="rejectForm"
        :rules="rejectRules"
        label-width="100px"
      >
        <el-form-item label="拒绝原因" prop="reason">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="handleConfirmReject" :loading="submitting">
          确定拒绝
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getMerchantList, getMerchantDetail, approveMerchant, rejectMerchant } from '@/api/merchants'

const loading = ref(false)
const submitting = ref(false)
const merchantList = ref([])
const currentMerchant = ref(null)
const detailDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const rejectFormRef = ref(null)

const searchForm = reactive({
  search: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const rejectForm = reactive({
  id: null,
  reason: ''
})

const rejectRules = {
  reason: [
    { required: true, message: '请输入拒绝原因', trigger: 'blur' },
    { min: 5, max: 255, message: '拒绝原因长度在5到255个字符', trigger: 'blur' }
  ]
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
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || ''
}

function getStatusText(status) {
  const textMap = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return textMap[status] || status
}

async function fetchMerchantList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (searchForm.search) params.search = searchForm.search
    if (searchForm.status) params.status = searchForm.status

    const data = await getMerchantList(params)
    merchantList.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取商家列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchMerchantList()
}

function handleReset() {
  searchForm.search = ''
  searchForm.status = ''
  pagination.page = 1
  fetchMerchantList()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchMerchantList()
}

function handlePageChange(page) {
  pagination.page = page
  fetchMerchantList()
}

async function handleViewDetail(row) {
  try {
    const data = await getMerchantDetail(row.id)
    currentMerchant.value = data
    detailDialogVisible.value = true
  } catch (error) {
    console.error('获取商家详情失败:', error)
  }
}

async function handleApprove(row) {
  try {
    await ElMessageBox.confirm(
      `确定要通过审核商家 "${row.business_name}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await approveMerchant(row.id)
    ElMessage.success('商家审核已通过')
    fetchMerchantList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核通过失败:', error)
    }
  }
}

function handleReject(row) {
  rejectForm.id = row.id
  rejectForm.reason = ''
  rejectDialogVisible.value = true
}

async function handleConfirmReject() {
  try {
    await rejectFormRef.value.validate()
    submitting.value = true
    await rejectMerchant(rejectForm.id, { reason: rejectForm.reason })
    ElMessage.success('商家审核已拒绝')
    rejectDialogVisible.value = false
    fetchMerchantList()
  } catch (error) {
    if (error !== false) {
      console.error('拒绝商家审核失败:', error)
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchMerchantList()
})
</script>

<style scoped>
.merchants-view {
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
}

.table-card {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
