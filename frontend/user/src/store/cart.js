import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref(JSON.parse(localStorage.getItem('cart_items') || '[]'))

  const totalQuantity = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  const totalPrice = computed(() => {
    return items.value.reduce((sum, item) => {
      const price = parseFloat(item.price) || 0
      return sum + price * item.quantity
    }, 0)
  })

  const formattedTotalPrice = computed(() => {
    return totalPrice.value.toFixed(2)
  })

  function addItem(item) {
    const existingItem = items.value.find(
      (i) => i.product_id === item.product_id && i.merchant_id === item.merchant_id
    )
    if (existingItem) {
      existingItem.quantity += item.quantity
    } else {
      items.value.push({ ...item })
    }
    saveCart()
  }

  function removeItem(productId) {
    items.value = items.value.filter((i) => i.product_id !== productId)
    saveCart()
  }

  function updateQuantity(productId, quantity) {
    const item = items.value.find((i) => i.product_id === productId)
    if (item) {
      if (quantity <= 0) {
        removeItem(productId)
      } else {
        item.quantity = quantity
        saveCart()
      }
    }
  }

  function increaseQuantity(productId) {
    const item = items.value.find((i) => i.product_id === productId)
    if (item) {
      item.quantity += 1
      saveCart()
    }
  }

  function decreaseQuantity(productId) {
    const item = items.value.find((i) => i.product_id === productId)
    if (item) {
      if (item.quantity <= 1) {
        removeItem(productId)
      } else {
        item.quantity -= 1
        saveCart()
      }
    }
  }

  function clearCart() {
    items.value = []
    saveCart()
  }

  function saveCart() {
    localStorage.setItem('cart_items', JSON.stringify(items.value))
  }

  return {
    items,
    totalQuantity,
    totalPrice,
    formattedTotalPrice,
    addItem,
    removeItem,
    updateQuantity,
    increaseQuantity,
    decreaseQuantity,
    clearCart,
  }
})
