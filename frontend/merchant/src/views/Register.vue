<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h1>外卖点餐系统</h1>
        <p>商家入驻申请</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        label-position="top"
      >
        <el-divider content-position="center">
          <span class="divider-text">账号信息</span>
        </el-divider>

        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（2-50个字符）"
            prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入手机号"
            prefix-icon="Cellphone"
            size="large"
            clearable
            maxlength="11"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（6-50个字符）"
            prefix-icon="Lock"
            size="large"
            show-password
            maxlength="50"
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            maxlength="50"
          />
        </el-form-item>

        <el-divider content-position="center">
          <span class="divider-text">店铺信息</span>
        </el-divider>

        <el-form-item label="店铺名称" prop="business_name">
          <el-input
            v-model="registerForm.business_name"
            placeholder="请输入店铺名称（2-100个字符）"
            prefix-icon="Shop"
            size="large"
            clearable
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="联系电话" prop="contact_phone">
          <el-input
            v-model="registerForm.contact_phone"
            placeholder="请输入店铺联系电话"
            prefix-icon="Phone"
            size="large"
            clearable
            maxlength="20"
          />
          <span class="form-tip">此号码将用于接收订单通知</span>
        </el-form-item>

        <el-form-item label="店铺地址" prop="address">
          <el-input
            v-model="registerForm.address"
            type="textarea"
            :rows="3"
            placeholder="请输入店铺详细地址（用于配送员取餐）"
            size="large"
            clearable
            maxlength="255"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="店铺描述">
          <el-input
            v-model="registerForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入店铺描述（选填，500字以内）"
            size="large"
            clearable
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="submit-button"
            @click="handleRegister"
          >
            {{ loading ? '提交中...' : '提交申请' }}
          </el-button>
        </el-form-item>

        <div class="register-footer">
          <span>已有账号？</span>
          <router-link to="/login" class="login-link">立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Cellphone, Lock, Shop, Phone } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/auth'
import { merchantRegister } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  phone: '',
  password: '',
  confirmPassword: '',
  business_name: '',
  contact_phone: '',
  address: '',
  description: '',
})

const confirmPwdValidate = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在2到50个字符', trigger: 'blur' },
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '手机号格式不正确',
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度6-50位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: confirmPwdValidate, trigger: 'blur' },
  ],
  business_name: [
    { required: true, message: '请输入店铺名称', trigger: 'blur' },
    { min: 2, max: 100, message: '店铺名称长度在2到100个字符', trigger: 'blur' },
  ],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '手机号格式不正确',
      trigger: 'blur',
    },
  ],
  address: [
    { required: true, message: '请输入店铺地址', trigger: 'blur' },
    { min: 5, max: 255, message: '地址长度在5到255个字符', trigger: 'blur' },
  ],
}

onMounted(() => {
  if (authStore.isLoggedIn && authStore.isMerchant) {
    router.push('/dashboard')
  }
})

async function handleRegister() {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await merchantRegister({
      username: registerForm.username,
      phone: registerForm.phone,
      password: registerForm.password,
      business_name: registerForm.business_name,
      contact_phone: registerForm.contact_phone,
      address: registerForm.address,
      description: registerForm.description || null,
    })

    ElMessage.success('商家注册申请已提交，请等待管理员审核')
    setTimeout(() => {
      router.push('/waiting-approval')
    }, 1500)
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.register-card {
  width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 40px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.register-card::-webkit-scrollbar {
  width: 6px;
}

.register-card::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h1 {
  font-size: 28px;
  color: #303133;
  margin: 0 0 10px;
  font-weight: 600;
}

.register-header p {
  font-size: 16px;
  color: #909399;
  margin: 0;
}

.register-form {
  margin-top: 10px;
}

.divider-text {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.submit-button {
  width: 100%;
  margin-top: 10px;
}

.register-footer {
  text-align: center;
  margin-top: 20px;
  color: #909399;
  font-size: 14px;
}

.login-link {
  color: #409eff;
  margin-left: 5px;
  text-decoration: none;
}

.login-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.form-tip {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}
</style>
