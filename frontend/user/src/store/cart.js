import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref(JSON.parse(localStorage.getItem('cart_items') || '[]'))

  const merchantIds = computed(() => {
    const ids = new Set(items.value.map((i) => i.merchant_id))
    return [...ids]
  })

  const merchantGroups = computed(() => {
    const groups = {}
    items.value.forEach((item) => {
      if (!groups[item.merchant_id]) {
        groups[item.merchant_id] = {
          merchant_id: item.merchant_id,
          merchant_name: item.merchant_name || '',
          items: [],
          totalQuantity: 0,
          totalPrice: 0,
        }
      }
      groups[item.merchant_id].items.push(item)
      groups[item.merchant_id].totalQuantity += item.quantity
      groups[item.merchant_id].totalPrice += parseFloat(item.price) * item.quantity
    })
    return Object.values(groups)
  })

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

  function removeItemsByMerchant(merchantId) {
    items.value = items.value.filter((i) => i.merchant_id !== merchantId)
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
    merchantIds,
    merchantGroups,
    totalQuantity,
    totalPrice,
    formattedTotalPrice,
    addItem,
    removeItem,
    removeItemsByMerchant,
    updateQuantity,
    increaseQuantity,
    decreaseQuantity,
    clearCart,
  }
})
