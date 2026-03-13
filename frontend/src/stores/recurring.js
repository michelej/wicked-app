import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import recurringService from '@/services/recurringService'

export const useRecurringStore = defineStore('recurring', () => {
  // State
  const recurringExpenses = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const activeExpenses = computed(() => 
    recurringExpenses.value.filter(e => e.is_active)
  )
  
  const monthlyExpenses = computed(() => 
    recurringExpenses.value.filter(e => e.frequency === 'monthly')
  )
  
  const annualExpenses = computed(() => 
    recurringExpenses.value.filter(e => e.frequency === 'annual')
  )
  
  const quarterlyExpenses = computed(() => 
    recurringExpenses.value.filter(e => e.frequency === 'quarterly')
  )

  // Actions
  async function fetchRecurringExpenses(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await recurringService.getRecurringExpenses(params)
      recurringExpenses.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchActiveExpenses() {
    loading.value = true
    error.value = null
    try {
      const response = await recurringService.getActiveRecurringExpenses()
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getRecurringExpense(id) {
    loading.value = true
    error.value = null
    try {
      const response = await recurringService.getRecurringExpense(id)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createRecurringExpense(expense) {
    loading.value = true
    error.value = null
    try {
      const response = await recurringService.createRecurringExpense(expense)
      recurringExpenses.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateRecurringExpense(id, expense) {
    loading.value = true
    error.value = null
    try {
      const response = await recurringService.updateRecurringExpense(id, expense)
      const index = recurringExpenses.value.findIndex(e => e._id === id)
      if (index !== -1) {
        recurringExpenses.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteRecurringExpense(id) {
    loading.value = true
    error.value = null
    try {
      await recurringService.deleteRecurringExpense(id)
      recurringExpenses.value = recurringExpenses.value.filter(e => e._id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function applyToBudget(budgetId, expenseIds) {
    loading.value = true
    error.value = null
    try {
      const response = await recurringService.applyToBudget(budgetId, expenseIds)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    recurringExpenses,
    loading,
    error,
    // Getters
    activeExpenses,
    monthlyExpenses,
    annualExpenses,
    quarterlyExpenses,
    // Actions
    fetchRecurringExpenses,
    fetchActiveExpenses,
    getRecurringExpense,
    createRecurringExpense,
    updateRecurringExpense,
    deleteRecurringExpense,
    applyToBudget
  }
})
