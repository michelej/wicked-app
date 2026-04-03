import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import creditCardTransactionService from '@/services/creditCardTransactionService'

export const useCreditCardTransactionStore = defineStore('credit-card-transactions', () => {
  const transactions = ref([])
  const loading = ref(false)
  const error = ref(null)

  const incomeTransactions = computed(() =>
    transactions.value.filter((transaction) => transaction.type === 'income')
  )

  const expenseTransactions = computed(() =>
    transactions.value.filter((transaction) => transaction.type === 'expense')
  )

  const chargedTransactions = computed(() =>
    transactions.value.filter((transaction) => transaction.is_charged)
  )

  const pendingTransactions = computed(() =>
    transactions.value.filter((transaction) => !transaction.is_charged)
  )

  const totalIncome = computed(() =>
    incomeTransactions.value.reduce((sum, transaction) => sum + parseFloat(transaction.amount), 0)
  )

  const totalExpense = computed(() =>
    expenseTransactions.value.reduce((sum, transaction) => sum + parseFloat(transaction.amount), 0)
  )

  const balance = computed(() => totalIncome.value - totalExpense.value)

  async function fetchTransactions(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await creditCardTransactionService.getTransactions(params)
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
      const response = await creditCardTransactionService.getTransaction(id)
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
      const response = await creditCardTransactionService.createTransaction(transaction)
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
      const response = await creditCardTransactionService.bulkCreateTransactions(transactionsList)
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
      const response = await creditCardTransactionService.updateTransaction(id, transaction)
      const index = transactions.value.findIndex((item) => item._id === id)
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
      const response = await creditCardTransactionService.markCharged(id, isCharged)
      const index = transactions.value.findIndex((item) => item._id === id)
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
      await creditCardTransactionService.deleteTransaction(id)
      transactions.value = transactions.value.filter((transaction) => transaction._id !== id)
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
    transactions,
    loading,
    error,
    incomeTransactions,
    expenseTransactions,
    chargedTransactions,
    pendingTransactions,
    totalIncome,
    totalExpense,
    balance,
    fetchTransactions,
    getTransaction,
    createTransaction,
    bulkCreateTransactions,
    updateTransaction,
    markCharged,
    deleteTransaction,
    clearTransactions
  }
})
