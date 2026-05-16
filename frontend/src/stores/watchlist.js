import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import watchlistService from '@/services/watchlistService'

export const useWatchlistStore = defineStore('watchlist', () => {
  const items = ref([])
  const searchResults = ref([])
  const loading = ref(false)
  const searching = ref(false)
  const saving = ref(false)
  const error = ref(null)

  const toWatchItems = computed(() => items.value.filter((item) => item.status === 'to_watch'))
  const watchingItems = computed(() => items.value.filter((item) => item.status === 'watching'))
  const watchedItems = computed(() => items.value.filter((item) => item.status === 'watched'))

  async function fetchItems(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await watchlistService.getItems(params)
      items.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function searchCatalog(params = {}) {
    searching.value = true
    error.value = null
    try {
      const response = await watchlistService.searchCatalog(params)
      searchResults.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      searching.value = false
    }
  }

  async function createItem(payload) {
    saving.value = true
    error.value = null
    try {
      const response = await watchlistService.createItem(payload)
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
      const response = await watchlistService.updateItem(id, payload)
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

  async function deleteItem(id) {
    saving.value = true
    error.value = null
    try {
      await watchlistService.deleteItem(id)
      items.value = items.value.filter((item) => item._id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      saving.value = false
    }
  }

  function clearSearchResults() {
    searchResults.value = []
  }

  return {
    items,
    searchResults,
    loading,
    searching,
    saving,
    error,
    toWatchItems,
    watchingItems,
    watchedItems,
    fetchItems,
    searchCatalog,
    createItem,
    updateItem,
    deleteItem,
    clearSearchResults
  }
})
