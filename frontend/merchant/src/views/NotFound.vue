<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1 class="not-found-code">404</h1>
      <p class="not-found-title">页面不存在</p>
      <p class="not-found-desc">抱歉，您访问的页面不存在或已被删除</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push('/dashboard')
}
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f7fa;
}

.not-found-content {
  text-align: center;
}

.not-found-code {
  font-size: 120px;
  font-weight: 700;
  color: #409eff;
  margin: 0;
  line-height: 1;
}

.not-found-title {
  font-size: 24px;
  color: #303133;
  margin: 20px 0 10px;
}

.not-found-desc {
  font-size: 14px;
  color: #909399;
  margin: 0 0 30px;
}
</style>
