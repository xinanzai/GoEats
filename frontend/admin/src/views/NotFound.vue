<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1>404</h1>
      <p>页面不存在</p>
      <el-button type="primary" @click="$router.push('/dashboard')">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.not-found-content {
  text-align: center;
}

.not-found-content h1 {
  font-size: 120px;
  color: #409eff;
  margin: 0;
  font-weight: bold;
}

.not-found-content p {
  font-size: 20px;
  color: #606266;
  margin: 20px 0 40px;
}
</style>
