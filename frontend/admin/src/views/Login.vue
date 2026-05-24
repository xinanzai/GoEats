<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>外卖点餐系统</h1>
        <p>平台管理端</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="phone">
          <el-input
            v-model="loginForm.phone"
            placeholder="请输入手机号或用户名"
            size="large"
            clearable
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>

        <div class="login-tips">
          <el-alert
            title="测试账号"
            type="info"
            :closable="false"
            show-icon
          >
            <div>手机号: 13800000000</div>
            <div>密码: admin123</div>
          </el-alert>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  phone: '',
  password: '',
})

const loginRules = {
  phone: [
    { required: true, message: '请输入手机号或用户名', trigger: 'blur' },
    {
      pattern: /^1[3-9]\d{9}$|^[a-zA-Z0-9_\u4e00-\u9fa5]{2,50}$/,
      message: '请输入正确的手机号或用户名',
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度6-50位', trigger: 'blur' },
  ],
}

onMounted(() => {
  if (authStore.isLoggedIn && authStore.isAdmin) {
    router.push(route.query.redirect || '/dashboard')
  }
})

async function handleLogin() {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await authStore.loginAction({
      phone: loginForm.phone,
      password: loginForm.password,
    })

    ElMessage.success('登录成功')
    router.push(route.query.redirect || '/dashboard')
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 28px;
  color: #303133;
  margin: 0 0 10px;
  font-weight: 600;
}

.login-header p {
  font-size: 16px;
  color: #909399;
  margin: 0;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  width: 100%;
  margin-top: 10px;
}

.login-tips {
  margin-top: 20px;
}

:deep(.el-alert--info) {
  background-color: #f4f4f5;
  border: 1px solid #e5e6e7;
}

:deep(.el-alert__content) {
  font-size: 13px;
}

:deep(.el-alert__title) {
  line-height: 20px;
}
</style>
