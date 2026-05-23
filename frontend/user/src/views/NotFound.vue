<template>
  <div class="not-found">
    <van-empty image="error" description="页面不存在">
      <van-button type="primary" @click="$router.push('/')">返回首页</van-button>
    </van-empty>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  background-color: #f7f8fa;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
</style>
