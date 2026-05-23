<template>
  <div class="waiting-container">
    <div class="waiting-card">
      <div class="waiting-icon">
        <el-icon :size="80" color="#e6a23c"><Clock /></el-icon>
      </div>

      <h2 class="waiting-title">申请已提交</h2>
      <p class="waiting-subtitle">您的商家入驻申请已提交成功，请等待管理员审核</p>

      <div class="status-card">
        <div class="status-item">
          <span class="status-label">当前状态：</span>
          <el-tag :type="getStatusType(status)" size="large">
            {{ getStatusText(status) }}
          </el-tag>
        </div>

        <div v-if="status === 'rejected'" class="rejection-info">
          <el-alert
            title="审核未通过"
            :description="rejectionReason"
            type="error"
            :closable="false"
            show-icon
          />
        </div>

        <div v-if="status === 'approved'" class="approved-info">
          <el-alert
            title="审核已通过"
            description="恭喜！您的商家入驻申请已通过审核，现在可以登录使用系统了"
            type="success"
            :closable="false"
            show-icon
          />
        </div>
      </div>

      <div class="info-tips">
        <el-timeline>
          <el-timeline-item timestamp="已提交" placement="top" color="#67c23a">
            <el-card shadow="hover" class="tip-card">
              <p>您的商家入驻申请已提交</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="审核中" placement="top" :color="status === 'approved' || status === 'rejected' ? '#409eff' : '#e6a23c'">
            <el-card shadow="hover" class="tip-card">
              <p>管理员正在审核您的申请</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="审核完成" placement="top" :color="status === 'approved' || status === 'rejected' ? '#409eff' : '#dcdfe6'" disabled>
            <el-card shadow="hover" class="tip-card">
              <p>审核结果将在此显示</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>

      <div class="waiting-actions">
        <el-button
          v-if="status === 'pending'"
          type="primary"
          :loading="refreshing"
          @click="handleRefreshStatus"
        >
          <el-icon><Refresh /></el-icon>
          刷新状态
        </el-button>

        <el-button
          v-if="status === 'approved'"
          type="success"
          @click="handleGoToLogin"
        >
          <el-icon><Right /></el-icon>
          前往登录
        </el-button>

        <el-button
          v-if="status === 'rejected'"
          type="warning"
          @click="handleReRegister"
        >
          <el-icon><EditPen /></el-icon>
          重新申请
        </el-button>

        <el-button @click="handleGoToLogin">
          返回登录页
        </el-button>
      </div>

      <div class="contact-info">
        <el-divider />
        <p class="contact-text">
          <el-icon><Service /></el-icon>
          如有疑问，请联系平台客服
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Clock, Refresh, Right, EditPen, Service } from '@element-plus/icons-vue'
import { getMyMerchant } from '@/api/merchants'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const status = ref('pending')
const rejectionReason = ref('')
const refreshing = ref(false)

function getStatusType(status) {
  const typeMap = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
  }
  return typeMap[status] || ''
}

function getStatusText(status) {
  const textMap = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
  }
  return textMap[status] || status
}

async function fetchStatus() {
  try {
    const merchantInfo = await getMyMerchant()
    status.value = merchantInfo.status
    rejectionReason.value = merchantInfo.rejection_reason || '无具体原因'
  } catch (error) {
    console.error('获取审核状态失败:', error)
    if (error.response?.status === 401) {
      ElMessage.info('请先登录查看审核状态')
      router.push('/login')
    }
  }
}

async function handleRefreshStatus() {
  refreshing.value = true
  try {
    await fetchStatus()
    if (status.value === 'approved') {
      ElMessage.success('恭喜！您的申请已通过审核')
    } else if (status.value === 'rejected') {
      ElMessage.error('很遗憾，您的申请未通过审核')
    } else {
      ElMessage.info('您的申请仍在审核中，请耐心等待')
    }
  } catch (error) {
    console.error('刷新状态失败:', error)
  } finally {
    refreshing.value = false
  }
}

function handleGoToLogin() {
  router.push('/login')
}

function handleReRegister() {
  router.push('/register')
}

onMounted(() => {
  const token = localStorage.getItem('access_token')
  if (token) {
    fetchStatus()
  }
})
</script>

<style scoped>
.waiting-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.waiting-card {
  width: 600px;
  padding: 50px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.waiting-icon {
  margin-bottom: 20px;
}

.waiting-title {
  font-size: 28px;
  color: #303133;
  margin: 0 0 10px;
  font-weight: 600;
}

.waiting-subtitle {
  font-size: 16px;
  color: #909399;
  margin: 0 0 30px;
}

.status-card {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
}

.status-label {
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

.rejection-info,
.approved-info {
  margin-top: 15px;
  text-align: left;
}

.info-tips {
  margin-bottom: 30px;
  text-align: left;
}

.tip-card {
  padding: 10px 15px;
  background: #fafafa;
}

.tip-card p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.waiting-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.waiting-actions .el-button {
  min-width: 140px;
}

.contact-info {
  margin-top: 20px;
}

.contact-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
  margin: 0;
}
</style>
