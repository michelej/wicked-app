import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import transactionService from '@/services/transactionService'

export const useTransactionStore = defineStore('transactions', () => {
  // State
  const transactions = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const incomeTransactions = computed(() => 
    transactions.value.filter(t => t.type === 'income')
  )
  
  const expenseTransactions = computed(() => 
    transactions.value.filter(t => t.type === 'expense')
  )
  
  const chargedTransactions = computed(() => 
    transactions.value.filter(t => t.is_charged)
  )
  
  const pendingTransactions = computed(() => 
    transactions.value.filter(t => !t.is_charged)
  )
  
  const totalIncome = computed(() => 
    incomeTransactions.value.reduce((sum, t) => sum + parseFloat(t.amount), 0)
  )
  
  const totalExpense = computed(() => 
    expenseTransactions.value.reduce((sum, t) => sum + parseFloat(t.amount), 0)
  )
  
  const balance = computed(() => totalIncome.value - totalExpense.value)

  // Actions
  async function fetchTransactions(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await transactionService.getTransactions(params)
      transactions.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTransactionsByBudget(budgetId) {
    loading.value = true
    error.value = null
    try {
      const response = await transactionService.getTransactionsByBudget(budgetId)
      transactions.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getTransaction(id) {
    loading.value = true
    error.value = null
    try {
      const response = await transactionService.getTransaction(id)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createTransaction(transaction) {
    loading.value = true
    error.value = null
    try {
      const response = await transactionService.createTransaction(transaction)
      transactions.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function bulkCreateTransactions(transactionsList) {
    loading.value = true
    error.value = null
    try {
      const response = await transactionService.bulkCreateTransactions(transactionsList)
      transactions.value = [...response.data, ...transactions.value]
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateTransaction(id, transaction) {
    loading.value = true
    error.value = null
    try {
      const response = await transactionService.updateTransaction(id, transaction)
      const index = transactions.value.findIndex(t => t._id === id)
      if (index !== -1) {
        transactions.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function markCharged(id, isCharged = true) {
    loading.value = true
    error.value = null
    try {
      const response = await transactionService.markCharged(id, isCharged)
      const index = transactions.value.findIndex(t => t._id === id)
      if (index !== -1) {
        transactions.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteTransaction(id) {
    loading.value = true
    error.value = null
    try {
      await transactionService.deleteTransaction(id)
      transactions.value = transactions.value.filter(t => t._id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearTransactions() {
    transactions.value = []
  }

  return {
    // State
    transactions,
    loading,
    error,
    // Getters
    incomeTransactions,
    expenseTransactions,
    chargedTransactions,
    pendingTransactions,
    totalIncome,
    totalExpense,
    balance,
    // Actions
    fetchTransactions,
    fetchTransactionsByBudget,
    getTransaction,
    createTransaction,
    bulkCreateTransactions,
    updateTransaction,
    markCharged,
    deleteTransaction,
    clearTransactions
  }
})
