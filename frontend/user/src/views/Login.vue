<template>
  <div class="login">
    <van-nav-bar title="登录" left-arrow @click-left="$router.back()" />

    <div class="login-header">
      <div class="logo">🍜</div>
      <h2>外卖点餐系统</h2>
      <p>欢迎回来，请登录您的账号</p>
    </div>

    <div class="form-wrapper">
      <van-form @submit="handleLogin">
        <van-cell-group inset>
          <van-field
            v-model="loginData.phone"
            name="phone"
            label="账号"
            placeholder="请输入手机号或用户名"
            :rules="[
              { required: true, message: '请输入手机号或用户名' },
              { pattern: /^1[3-9]\d{9}$|^[a-zA-Z0-9_\u4e00-\u9fa5]{2,50}$/, message: '请输入正确的手机号或用户名' },
            ]"
          >
            <template #button>
              <van-icon name="user-o" />
            </template>
          </van-field>
          <van-field
            v-model="loginData.password"
            type="password"
            name="password"
            label="密码"
            placeholder="请输入密码"
            :rules="[{ required: true, message: '请输入密码' }]"
          >
            <template #button>
              <van-icon name="lock" />
            </template>
          </van-field>
        </van-cell-group>

        <div class="form-actions">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            class="login-btn"
          >
            登录
          </van-button>
          <div class="register-link">
            还没有账号？
            <span class="link" @click="$router.push('/register')">立即注册</span>
          </div>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { showToast } from 'vant'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(false)
const loginData = reactive({
  phone: '',
  password: '',
})

async function handleLogin() {
  if (!loginData.phone || !loginData.password) {
    showToast('请填写完整信息')
    return
  }

  loading.value = true
  try {
    await authStore.login(loginData)
    showToast('登录成功')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login {
  min-height: 100vh;
  background: linear-gradient(180deg, #1989fa 0%, #409eff 30%, #f7f8fa 30%);
}

.login-header {
  padding: 60px 20px 40px;
  text-align: center;
  color: #fff;
}

.logo {
  font-size: 60px;
  margin-bottom: 16px;
}

.login-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: bold;
}

.login-header p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.form-wrapper {
  margin: -20px 16px 0;
}

.form-actions {
  padding: 0 16px 20px;
}

.login-btn {
  margin-bottom: 16px;
}

.register-link {
  text-align: center;
  font-size: 14px;
  color: #646566;
}

.link {
  color: #1989fa;
  cursor: pointer;
  margin-left: 4px;
}
</style>
