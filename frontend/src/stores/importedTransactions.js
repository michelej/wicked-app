import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import importedTransactionService from '@/services/importedTransactionService'

export const useImportedTransactionStore = defineStore('importedTransactions', () => {
  const importedTransactions = ref([])
  const loading = ref(false)
  const error = ref(null)
  const lastUploadResult = ref(null)

  const pendingTransactions = computed(() => {
    return importedTransactions.value.filter((item) => item.status === 'pending')
  })

  const processedTransactions = computed(() => {
    return importedTransactions.value.filter((item) => item.status !== 'pending')
  })

  async function fetchImportedTransactions(params = {}) {
    loading.value = true
    error.value = null

    try {
      const response = await importedTransactionService.getImportedTransactions(params)
      importedTransactions.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function uploadImportedTransactions(sourceBank, file) {
    loading.value = true
    error.value = null

    try {
      const response = await importedTransactionService.uploadImportedTransactions(sourceBank, file)
      lastUploadResult.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function processImportedTransaction(id, payload) {
    loading.value = true
    error.value = null

    try {
      const response = await importedTransactionService.processImportedTransaction(id, payload)
      const index = importedTransactions.value.findIndex((item) => item._id === id)
      if (index !== -1) {
        importedTransactions.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    importedTransactions,
    loading,
    error,
    lastUploadResult,
    pendingTransactions,
    processedTransactions,
    fetchImportedTransactions,
    uploadImportedTransactions,
    processImportedTransaction
  }
})
