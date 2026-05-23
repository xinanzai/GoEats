import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia } from 'pinia'
import { useCartStore } from '@/store/cart'

describe('Cart Store', () => {
  let cartStore
  let pinia

  beforeEach(() => {
    localStorage.clear()
    pinia = createPinia()
    cartStore = useCartStore(pinia)
  })

  describe('initial state', () => {
    it('should initialize with empty items', () => {
      expect(cartStore.items).toEqual([])
    })

    it('should have zero total quantity', () => {
      expect(cartStore.totalQuantity).toBe(0)
    })

    it('should have zero total price', () => {
      expect(cartStore.totalPrice).toBe(0)
    })

    it('should have formatted total price as 0.00', () => {
      expect(cartStore.formattedTotalPrice).toBe('0.00')
    })
  })

  describe('addItem', () => {
    it('should add new item to cart', () => {
      const item = {
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 1,
      }
      cartStore.addItem(item)
      expect(cartStore.items).toHaveLength(1)
      expect(cartStore.items[0].name).toBe('Test Product')
    })

    it('should update quantity when adding existing item', () => {
      const item1 = {
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 1,
      }
      const item2 = {
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 2,
      }
      cartStore.addItem(item1)
      cartStore.addItem(item2)
      expect(cartStore.items).toHaveLength(1)
      expect(cartStore.items[0].quantity).toBe(3)
    })

    it('should not add items from different merchants', () => {
      const item1 = {
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product 1',
        price: 10,
        quantity: 1,
      }
      const item2 = {
        product_id: 1,
        merchant_id: 2,
        name: 'Test Product 2',
        price: 15,
        quantity: 1,
      }
      cartStore.addItem(item1)
      cartStore.addItem(item2)
      expect(cartStore.items).toHaveLength(2)
    })
  })

  describe('removeItem', () => {
    it('should remove item from cart', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 1,
      })
      cartStore.removeItem(1)
      expect(cartStore.items).toHaveLength(0)
    })
  })

  describe('updateQuantity', () => {
    it('should update item quantity', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 1,
      })
      cartStore.updateQuantity(1, 5)
      expect(cartStore.items[0].quantity).toBe(5)
    })

    it('should remove item when quantity is 0 or less', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 1,
      })
      cartStore.updateQuantity(1, 0)
      expect(cartStore.items).toHaveLength(0)
    })
  })

  describe('increaseQuantity', () => {
    it('should increase item quantity by 1', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 1,
      })
      cartStore.increaseQuantity(1)
      expect(cartStore.items[0].quantity).toBe(2)
    })
  })

  describe('decreaseQuantity', () => {
    it('should decrease item quantity by 1', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 5,
      })
      cartStore.decreaseQuantity(1)
      expect(cartStore.items[0].quantity).toBe(4)
    })

    it('should remove item when quantity is 1', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 1,
      })
      cartStore.decreaseQuantity(1)
      expect(cartStore.items).toHaveLength(0)
    })
  })

  describe('clearCart', () => {
    it('should clear all items', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 1,
      })
      cartStore.clearCart()
      expect(cartStore.items).toHaveLength(0)
    })
  })

  describe('computed properties', () => {
    it('should calculate total quantity correctly', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product 1',
        price: 10,
        quantity: 2,
      })
      cartStore.addItem({
        product_id: 2,
        merchant_id: 1,
        name: 'Test Product 2',
        price: 15,
        quantity: 3,
      })
      expect(cartStore.totalQuantity).toBe(5)
    })

    it('should calculate total price correctly', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product 1',
        price: 10,
        quantity: 2,
      })
      expect(cartStore.totalPrice).toBe(20)
    })

    it('should format total price correctly', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10.5,
        quantity: 1,
      })
      expect(cartStore.formattedTotalPrice).toBe('10.50')
    })
  })

  describe('localStorage persistence', () => {
    it('should save cart to localStorage', () => {
      cartStore.addItem({
        product_id: 1,
        merchant_id: 1,
        name: 'Test Product',
        price: 10,
        quantity: 1,
      })
      const saved = localStorage.getItem('cart_items')
      expect(saved).toBeDefined()
      expect(JSON.parse(saved)).toHaveLength(1)
    })

    it('should load cart from localStorage on init', () => {
      const cartItems = [
        {
          product_id: 1,
          merchant_id: 1,
          name: 'Test Product',
          price: 10,
          quantity: 2,
        },
      ]
      localStorage.setItem('cart_items', JSON.stringify(cartItems))
      const newPinia = createPinia()
      const newCartStore = useCartStore(newPinia)
      expect(newCartStore.items).toHaveLength(1)
    })
  })
})
