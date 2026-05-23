<template>
  <div class="app-container">
    <router-view />
    <van-tabbar
      v-if="showTabbar"
      v-model="activeTab"
      active-color="#1989fa"
      inactive-color="#969799"
      @change="onTabChange"
    >
      <van-tabbar-item name="/" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item name="/cart">
        购物车
        <template #icon>
          <div class="cart-icon-wrapper">
            <van-icon name="cart-o" size="24" />
            <div v-if="cartStore.totalQuantity > 0" class="cart-badge">
              {{ cartStore.totalQuantity }}
            </div>
          </div>
        </template>
      </van-tabbar-item>
      <van-tabbar-item name="/orders" icon="orders-o">订单</van-tabbar-item>
      <van-tabbar-item name="/profile" icon="contact">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCartStore } from '@/store/cart'

const router = useRouter()
const route = useRoute()
const cartStore = useCartStore()

const activeTab = ref(route.path)

const showTabbar = computed(() => {
  const allowedPaths = ['/', '/cart', '/orders', '/profile']
  return allowedPaths.includes(route.path)
})

watch(
  () => route.path,
  (newPath) => {
    activeTab.value = newPath
  }
)

function onTabChange(name) {
  router.push(name)
}
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
  background-color: #f7f8fa;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.app-container {
  width: 100%;
  height: 100vh;
  overflow-y: auto;
}

.cart-icon-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.cart-badge {
  position: absolute;
  top: -4px;
  right: -8px;
  background-color: #ee0a24;
  color: #fff;
  font-size: 10px;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}
</style>
