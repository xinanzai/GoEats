<template>
  <div class="users-view">
    <el-card>
      <div class="page-header">
        <h2>用户管理</h2>
      </div>

      <div class="search-bar">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索用户名或手机号"
          clearable
          style="width: 300px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="searchForm.role"
          placeholder="角色筛选"
          clearable
          style="width: 150px"
        >
          <el-option label="普通用户" value="user" />
          <el-option label="商家" value="merchant" />
          <el-option label="管理员" value="admin" />
        </el-select>

        <el-select
          v-model="searchForm.status"
          placeholder="状态筛选"
          clearable
          style="width: 150px"
        >
          <el-option label="启用" value="active" />
          <el-option label="禁用" value="inactive" />
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
        :data="userList"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="phone" label="手机号" width="150" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)" size="small">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="300">
          <template #default="{ row }">
            <el-button size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button
              size="small"
              :type="row.is_active ? 'danger' : 'success'"
              @click="handleToggleStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
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
      title="用户详情"
      width="600px"
    >
      <el-descriptions :column="2" border v-if="currentUser">
        <el-descriptions-item label="ID">{{ currentUser.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ currentUser.phone }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag :type="getRoleType(currentUser.role)" size="small">
            {{ getRoleText(currentUser.role) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentUser.is_active ? 'success' : 'danger'" size="small">
            {{ currentUser.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">
          {{ formatDateTime(currentUser.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDateTime(currentUser.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="头像" :span="2">
          <el-avatar :size="80" :src="currentUser.avatar" v-if="currentUser.avatar" />
          <el-avatar :size="80" v-else>
            {{ currentUser.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户信息"
      width="500px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editForm.phone" />
        </el-form-item>
        <el-form-item label="头像">
          <el-input v-model="editForm.avatar" placeholder="头像URL" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEdit" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getUserList, getUserDetail, toggleUserStatus, updateUser } from '@/api/admin'

const loading = ref(false)
const saving = ref(false)
const userList = ref([])
const currentUser = ref(null)
const detailDialogVisible = ref(false)
const editDialogVisible = ref(false)
const editFormRef = ref(null)

const searchForm = reactive({
  search: '',
  role: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const editForm = reactive({
  id: null,
  username: '',
  phone: '',
  avatar: ''
})

const editRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在2到50个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
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

function getRoleType(role) {
  const typeMap = {
    user: '',
    merchant: 'warning',
    admin: 'danger'
  }
  return typeMap[role] || ''
}

function getRoleText(role) {
  const textMap = {
    user: '普通用户',
    merchant: '商家',
    admin: '管理员'
  }
  return textMap[role] || role
}

async function fetchUserList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (searchForm.search) params.search = searchForm.search
    if (searchForm.role) params.role = searchForm.role
    if (searchForm.status) params.status = searchForm.status

    const data = await getUserList(params)
    userList.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchUserList()
}

function handleReset() {
  searchForm.search = ''
  searchForm.role = ''
  searchForm.status = ''
  pagination.page = 1
  fetchUserList()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  fetchUserList()
}

function handlePageChange(page) {
  pagination.page = page
  fetchUserList()
}

async function handleViewDetail(row) {
  try {
    const data = await getUserDetail(row.id)
    currentUser.value = data
    detailDialogVisible.value = true
  } catch (error) {
    console.error('获取用户详情失败:', error)
  }
}

async function handleToggleStatus(row) {
  const action = row.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${row.username}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await toggleUserStatus(row.id, { is_active: !row.is_active })
    ElMessage.success(`用户已${action}`)
    fetchUserList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换用户状态失败:', error)
    }
  }
}

function handleEdit(row) {
  editForm.id = row.id
  editForm.username = row.username
  editForm.phone = row.phone
  editForm.avatar = row.avatar || ''
  editDialogVisible.value = true
}

async function handleSaveEdit() {
  try {
    await editFormRef.value.validate()
    saving.value = true
    const data = {}
    if (editForm.username) data.username = editForm.username
    if (editForm.phone) data.phone = editForm.phone
    if (editForm.avatar !== undefined) data.avatar = editForm.avatar

    await updateUser(editForm.id, data)
    ElMessage.success('用户信息更新成功')
    editDialogVisible.value = false
    fetchUserList()
  } catch (error) {
    if (error !== false) {
      console.error('更新用户信息失败:', error)
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchUserList()
})
</script>

<style scoped>
.users-view {
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
