<template>
  <div class="profile">
    <div class="profile-header" @click="handleEditProfile">
      <div class="avatar-wrapper" @click.stop="handleAvatarClick">
        <input
          ref="avatarInput"
          type="file"
          accept="image/*"
          class="avatar-input"
          @change="onAvatarSelected"
        />
        <van-image
          v-if="authStore.userInfo?.avatar"
          :src="getImageUrl(authStore.userInfo.avatar)"
          class="avatar"
          round
          width="64"
          height="64"
        />
        <div v-else class="avatar-default">
          {{ authStore.userInfo?.username?.charAt(0) || '用' }}
        </div>
        <van-icon name="photograph" class="avatar-camera" />
      </div>
      <div class="user-info">
        <div class="username">{{ authStore.userInfo?.username || '加载中...' }}</div>
        <div class="phone">{{ authStore.userInfo?.phone || '' }}</div>
      </div>
      <van-icon name="arrow" class="arrow-icon" />
    </div>

    <!-- 订单统计 -->
    <div class="order-stats">
      <van-grid :column-num="4" :border="false">
        <van-grid-item @click="$router.push('/orders?status=')">
          <div class="stat-icon">📋</div>
          <div class="stat-label">全部</div>
        </van-grid-item>
        <van-grid-item @click="$router.push('/orders?status=pending')">
          <div class="stat-icon">⏰</div>
          <div class="stat-label">待付款</div>
        </van-grid-item>
        <van-grid-item @click="$router.push('/orders?status=preparing')">
          <div class="stat-icon">🍳</div>
          <div class="stat-label">制作中</div>
        </van-grid-item>
        <van-grid-item @click="$router.push('/orders?status=delivering')">
          <div class="stat-icon">🚚</div>
          <div class="stat-label">配送中</div>
        </van-grid-item>
      </van-grid>
    </div>

    <!-- 功能菜单 -->
    <van-cell-group class="menu-group">
      <van-cell
        title="我的订单"
        icon="cart-o"
        is-link
        @click="router.push('/orders')"
      />
      <van-cell
        title="收货地址"
        icon="location"
        is-link
        @click="router.push('/addresses')"
      />
      <van-cell
        title="修改密码"
        icon="lock"
        is-link
        @click="showPasswordDialog = true"
      />
    </van-cell-group>

    <van-cell-group class="menu-group">
      <van-cell
        title="关于我们"
        icon="info-o"
        is-link
        @click="showAboutDialog = true"
      />
    </van-cell-group>

    <!-- 退出登录 -->
    <div class="logout-section">
      <van-button block type="danger" plain @click="handleLogout">
        退出登录
      </van-button>
    </div>

    <!-- 修改密码弹窗 -->
    <van-dialog
      v-model:show="showPasswordDialog"
      title="修改密码"
      show-cancel-button
      @confirm="handleChangePassword"
    >
      <div class="password-form">
        <van-field
          v-model="passwordForm.oldPassword"
          type="password"
          placeholder="旧密码"
          class="password-field"
        />
        <van-field
          v-model="passwordForm.newPassword"
          type="password"
          placeholder="新密码"
          class="password-field"
        />
        <van-field
          v-model="passwordForm.confirmPassword"
          type="password"
          placeholder="确认新密码"
          class="password-field"
        />
      </div>
    </van-dialog>

    <!-- 关于我们弹窗 -->
    <van-dialog v-model:show="showAboutDialog" title="关于我们">
      <div class="about-content">
        <p>外卖点餐系统 v1.0.0</p>
        <p>为您提供便捷的外卖点餐服务</p>
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { changePassword, updateUserProfile } from '@/api/users'
import { uploadAvatar } from '@/api/upload'
import { showConfirmDialog, showToast, showLoadingToast, closeToast } from 'vant'

const router = useRouter()
const authStore = useAuthStore()
const showPasswordDialog = ref(false)
const showAboutDialog = ref(false)
const uploading = ref(false)
const avatarInput = ref(null)
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

function handleEditProfile() {
  showToast('编辑个人信息功能开发中')
}

function getImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  return url
}

function handleAvatarClick() {
  if (uploading.value) return
  if (avatarInput.value) {
    avatarInput.value.click()
  }
}

async function onAvatarSelected(event) {
  const file = event.target.files[0]
  if (!file) return

  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    showToast('只能上传图片文件!')
    event.target.value = ''
    return
  }
  if (!isLt10M) {
    showToast('图片大小不能超过 10MB!')
    event.target.value = ''
    return
  }

  try {
    uploading.value = true
    showLoadingToast({
      message: '上传中...',
      forbidClick: true,
      duration: 0
    })
    const result = await uploadAvatar(file)
    await updateUserProfile({ avatar: result.data.url })
    await authStore.fetchUserInfo()
    showToast('头像上传成功')
  } catch (error) {
    console.error('头像上传失败:', error)
    showToast('上传失败，请重试')
  } finally {
    uploading.value = false
    closeToast()
    event.target.value = ''
  }
}

async function handleChangePassword() {
  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword) {
    showToast('请填写完整信息')
    return false
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    showToast('两次输入的密码不一致')
    return false
  }

  if (passwordForm.value.newPassword.length < 6) {
    showToast('密码长度至少为6位')
    return false
  }

  try {
    await changePassword({
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword,
    })
    showToast('密码修改成功')
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: '',
    }
  } catch (error) {
    console.error('密码修改失败:', error)
    return false
  }
}

async function handleLogout() {
  try {
    await showConfirmDialog({
      title: '确认退出',
      message: '确定要退出登录吗？',
    })
    authStore.logout()
    router.push('/login')
  } catch (error) {
    // 用户取消
  }
}
</script>

<style scoped>
.profile {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 80px;
}

.profile-header {
  background: linear-gradient(135deg, #1989fa, #409eff);
  padding: 40px 20px 30px;
  display: flex;
  align-items: center;
  gap: 16px;
  color: #fff;
  cursor: pointer;
}

.avatar-wrapper {
  flex-shrink: 0;
  position: relative;
}

.avatar-input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

.avatar {
  border: 2px solid #fff;
}

.avatar-default {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.3);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
  border: 2px solid #fff;
  cursor: pointer;
}

.avatar-camera {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 22px;
  height: 22px;
  background-color: #1989fa;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  border: 2px solid #fff;
  cursor: pointer;
}

.user-info {
  flex: 1;
}

.username {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 4px;
}

.phone {
  font-size: 14px;
  opacity: 0.9;
}

.arrow-icon {
  font-size: 20px;
  color: #fff;
}

.order-stats {
  background-color: #fff;
  margin-bottom: 8px;
}

.stat-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #646566;
}

.menu-group {
  margin-bottom: 8px;
}

.logout-section {
  padding: 16px;
  margin-bottom: 20px;
}

.password-form {
  padding: 16px;
}

.password-field {
  margin-bottom: 12px;
}

.about-content {
  padding: 16px;
  text-align: center;
  color: #646566;
}

.about-content p {
  margin: 8px 0;
}
</style>
