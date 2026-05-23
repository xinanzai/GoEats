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
        <el-table-column label="操作" fixed="right" width="400">
          <template #default="{ row }">
            <el-button size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button
              size="small"
              type="warning"
              @click="handleResetPassword(row)"
            >
              重置密码
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
      v-model="resetPasswordDialogVisible"
      title="重置用户密码"
      width="450px"
    >
      <el-alert
        title="注意：重置密码后将使用新密码登录，请妥善保存新密码。"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />
      <el-form
        ref="resetPasswordFormRef"
        :model="resetPasswordForm"
        :rules="resetPasswordRules"
        label-width="100px"
      >
        <el-form-item label="用户名">
          <el-input :value="resetPasswordForm.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="resetPasswordForm.new_password"
            type="password"
            show-password
            placeholder="请输入新密码（至少6位）"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="resetPasswordForm.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPasswordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveResetPassword" :loading="resetting">
          确认重置
        </el-button>
      </template>
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
          <div class="avatar-upload">
            <el-upload
              class="avatar-uploader"
              action=""
              :show-file-list="false"
              :on-change="handleAvatarChange"
              :before-upload="beforeAvatarUpload"
              :disabled="saving || uploading"
            >
              <el-avatar :size="80" :src="editForm.avatar" v-if="editForm.avatar">
                <img :src="getImageUrl(editForm.avatar)" alt="头像" />
              </el-avatar>
              <el-avatar :size="80" v-else class="avatar-placeholder">
                <el-icon :size="30"><UserFilled /></el-icon>
              </el-avatar>
            </el-upload>
            <div class="upload-info">
              <el-button
                v-if="editForm.avatar"
                type="danger"
                text
                size="small"
                @click="editForm.avatar = ''"
              >
                清除
              </el-button>
              <span class="upload-tip">点击上传头像，支持 jpg、png 格式，最大10MB</span>
            </div>
          </div>
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
import { Search, UserFilled } from '@element-plus/icons-vue'
import { getUserList, getUserDetail, toggleUserStatus, updateUser, resetUserPassword } from '@/api/admin'
import { uploadAvatar } from '@/api/upload'

const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const resetting = ref(false)
const userList = ref([])
const currentUser = ref(null)
const detailDialogVisible = ref(false)
const editDialogVisible = ref(false)
const resetPasswordDialogVisible = ref(false)
const editFormRef = ref(null)
const resetPasswordFormRef = ref(null)

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

const resetPasswordForm = reactive({
  id: null,
  username: '',
  new_password: '',
  confirm_password: ''
})

const resetPasswordRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在6到50个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== resetPasswordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

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

function handleResetPassword(row) {
  resetPasswordForm.id = row.id
  resetPasswordForm.username = row.username
  resetPasswordForm.new_password = ''
  resetPasswordForm.confirm_password = ''
  resetPasswordDialogVisible.value = true
}

async function handleSaveResetPassword() {
  try {
    await resetPasswordFormRef.value.validate()
    resetting.value = true
    await resetUserPassword(resetPasswordForm.id, {
      new_password: resetPasswordForm.new_password
    })
    ElMessage.success('密码重置成功')
    resetPasswordDialogVisible.value = false
  } catch (error) {
    if (error !== false) {
      console.error('重置密码失败:', error)
    }
  } finally {
    resetting.value = false
  }
}

function getImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  return url
}

function beforeAvatarUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }
  return false
}

async function handleAvatarChange(file) {
  if (uploading.value) return
  try {
    uploading.value = true
    const response = await uploadAvatar(file.raw)
    editForm.avatar = response.data.url
    ElMessage.success('头像上传成功')
  } catch (error) {
    console.error('头像上传失败:', error)
  } finally {
    uploading.value = false
  }
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

.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.avatar-uploader {
  cursor: pointer;
}

.avatar-uploader :deep(.el-avatar) {
  transition: all 0.3s;
}

.avatar-uploader:hover :deep(.el-avatar) {
  opacity: 0.8;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.avatar-placeholder {
  background-color: #f5f7fa;
  color: #909399;
}

.upload-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}
</style>
