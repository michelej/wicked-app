import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useItemsStore = defineStore('items', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchItems() {
    loading.value = true
    error.value = null
    try {
      const response = await api.getItems()
      items.value = response.data.items
    } catch (err) {
      error.value = err.message
      console.error('Error fetching items:', err)
    } finally {
      loading.value = false
    }
  }

  async function createItem(name) {
    loading.value = true
    error.value = null
    try {
      const response = await api.createItem(name)
      await fetchItems() // Refresh the list
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Error creating item:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    items,
    loading,
    error,
    fetchItems,
    createItem
  }
})
