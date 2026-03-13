import { defineStore } from 'pinia'
import { ref } from 'vue'
import dashboardService from '@/services/dashboardService'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const dailyProgress = ref([])
  const categorySummary = ref([])
  const paymentMethodSummary = ref([])
  const upcomingExpenses = ref([])
  const budgetComparison = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchDailyProgress(budgetId) {
    loading.value = true
    error.value = null
    try {
      const response = await dashboardService.getDailyProgress(budgetId)
      dailyProgress.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCategorySummary(budgetId) {
    loading.value = true
    error.value = null
    try {
      const response = await dashboardService.getCategorySummary(budgetId)
      categorySummary.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchPaymentMethodSummary(budgetId) {
    loading.value = true
    error.value = null
    try {
      const response = await dashboardService.getPaymentMethodSummary(budgetId)
      paymentMethodSummary.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchUpcomingExpenses(daysAhead = 30) {
    loading.value = true
    error.value = null
    try {
      const response = await dashboardService.getUpcomingExpenses(daysAhead)
      upcomingExpenses.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchBudgetComparison(budgetIds) {
    loading.value = true
    error.value = null
    try {
      const response = await dashboardService.compareBudgets(budgetIds)
      budgetComparison.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearDashboardData() {
    dailyProgress.value = []
    categorySummary.value = []
    paymentMethodSummary.value = []
    upcomingExpenses.value = []
    budgetComparison.value = []
  }

  return {
    // State
    dailyProgress,
    categorySummary,
    paymentMethodSummary,
    upcomingExpenses,
    budgetComparison,
    loading,
    error,
    // Actions
    fetchDailyProgress,
    fetchCategorySummary,
    fetchPaymentMethodSummary,
    fetchUpcomingExpenses,
    fetchBudgetComparison,
    clearDashboardData
  }
})
