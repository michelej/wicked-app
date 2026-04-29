import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import registryService from '@/services/registryService'

export const useRegistryStore = defineStore('registry', () => {
  const items = ref([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)

  const archivedItems = computed(() => items.value.filter((item) => item.status === 'archived'))
  const activeItems = computed(() => items.value.filter((item) => item.status !== 'archived'))

  async function fetchItems(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await registryService.getItems(params)
      items.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createItem(payload) {
    saving.value = true
    error.value = null
    try {
      const response = await registryService.createItem(payload)
      items.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      saving.value = false
    }
  }

  async function updateItem(id, payload) {
    saving.value = true
    error.value = null
    try {
      const response = await registryService.updateItem(id, payload)
      const index = items.value.findIndex((item) => item._id === id)
      if (index !== -1) {
        items.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      saving.value = false
    }
  }

  async function archiveItem(id) {
    saving.value = true
    error.value = null
    try {
      const response = await registryService.archiveItem(id)
      const index = items.value.findIndex((item) => item._id === id)
      if (index !== -1) {
        items.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      saving.value = false
    }
  }

  async function duplicateItem(id) {
    saving.value = true
    error.value = null
    try {
      const response = await registryService.duplicateItem(id)
      items.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      saving.value = false
    }
  }

  async function deleteItem(id) {
    saving.value = true
    error.value = null
    try {
      await registryService.deleteItem(id)
      items.value = items.value.filter((item) => item._id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      saving.value = false
    }
  }

  return {
    items,
    loading,
    saving,
    error,
    activeItems,
    archivedItems,
    fetchItems,
    createItem,
    updateItem,
    archiveItem,
    duplicateItem,
    deleteItem
  }
})
