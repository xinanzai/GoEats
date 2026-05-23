<template>
  <div class="register">
    <van-nav-bar title="注册" left-arrow @click-left="$router.back()" />

    <div class="register-header">
      <div class="logo">🍜</div>
      <h2>注册新账号</h2>
      <p>填写以下信息完成注册</p>
    </div>

    <div class="form-wrapper">
      <van-form @submit="handleRegister">
        <van-cell-group inset>
          <van-field
            v-model="formData.username"
            name="username"
            label="用户名"
            placeholder="请输入用户名"
            :rules="[
              { required: true, message: '请输入用户名' },
              { min: 2, max: 50, message: '用户名长度为2-50个字符' },
            ]"
          >
            <template #button>
              <van-icon name="user-o" />
            </template>
          </van-field>
          <van-field
            v-model="formData.phone"
            name="phone"
            label="手机号"
            placeholder="请输入手机号"
            type="tel"
            :rules="[
              { required: true, message: '请输入手机号' },
              { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' },
            ]"
            :formatter="(value) => value.replace(/\s/g, '')"
          >
            <template #button>
              <van-icon name="phone-o" />
            </template>
          </van-field>
          <van-field
            v-model="formData.password"
            type="password"
            name="password"
            label="密码"
            placeholder="请输入密码（至少6位）"
            :rules="[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码长度至少为6位' },
            ]"
          >
            <template #button>
              <van-icon name="lock" />
            </template>
          </van-field>
          <van-field
            v-model="formData.confirmPassword"
            type="password"
            name="confirmPassword"
            label="确认密码"
            placeholder="请再次输入密码"
            :rules="[
              { required: true, message: '请再次输入密码' },
              {
                validator: (value) => value === formData.password,
                message: '两次输入的密码不一致',
              },
            ]"
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
            class="register-btn"
          >
            注册
          </van-button>
          <div class="login-link">
            已有账号？
            <span class="link" @click="$router.push('/login')">立即登录</span>
          </div>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { showToast } from 'vant'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const formData = reactive({
  username: '',
  phone: '',
  password: '',
  confirmPassword: '',
})

async function handleRegister() {
  if (formData.password !== formData.confirmPassword) {
    showToast('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    await authStore.register({
      username: formData.username,
      phone: formData.phone,
      password: formData.password,
    })
    formData.username = ''
    formData.phone = ''
    formData.password = ''
    formData.confirmPassword = ''
    showToast('注册成功，即将跳转到登录页面...')
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error) {
    console.error('注册失败:', error)
    const message = error.response?.data?.detail || '注册失败，请稍后重试'
    showToast(message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register {
  min-height: 100vh;
  background: linear-gradient(180deg, #1989fa 0%, #409eff 30%, #f7f8fa 30%);
}

.register-header {
  padding: 60px 20px 40px;
  text-align: center;
  color: #fff;
}

.logo {
  font-size: 60px;
  margin-bottom: 16px;
}

.register-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: bold;
}

.register-header p {
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

.register-btn {
  margin-bottom: 16px;
}

.login-link {
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
