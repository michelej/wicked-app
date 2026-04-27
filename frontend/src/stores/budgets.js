import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import budgetService from '@/services/budgetService'

export const useBudgetStore = defineStore('budgets', () => {
  // State
  const budgets = ref([])
  const currentBudget = ref(null)
  const currentSummary = ref(null)
  const budgetSummaries = ref({}) // Store summaries by budget ID
  const loading = ref(false)
  const summariesLoading = ref(false)
  const error = ref(null)

  const sortBudgetsByStartDate = (items = []) => {
    return [...items].sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
  }

  // Getters
  const activeBudgets = computed(() => 
    budgets.value.filter(b => b.status === 'active')
  )
  
  const closedBudgets = computed(() => 
    budgets.value.filter(b => b.status === 'closed')
  )
  
  const draftBudgets = computed(() => 
    budgets.value.filter(b => b.status === 'draft')
  )

  // Actions
  async function fetchBudgets(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await budgetService.getBudgets(params)
      budgets.value = sortBudgetsByStartDate(response.data)
      return budgets.value
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchActiveBudgets() {
    loading.value = true
    error.value = null
    try {
      const response = await budgetService.getActiveBudgets()
      return sortBudgetsByStartDate(response.data)
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getBudget(id) {
    loading.value = true
    error.value = null
    try {
      const response = await budgetService.getBudget(id)
      currentBudget.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getBudgetSummary(id) {
    loading.value = true
    error.value = null
    try {
      const response = await budgetService.getBudgetSummary(id)
      currentSummary.value = response.data
      budgetSummaries.value[id] = response.data // Store in summaries object
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getBudgetSummaries(ids = [], force = false) {
    const targetIds = [...new Set(ids.filter(Boolean))].filter((id) => force || !budgetSummaries.value[id])
    if (targetIds.length === 0) {
      return budgetSummaries.value
    }

    summariesLoading.value = true
    error.value = null

    try {
      const responses = await Promise.all(targetIds.map((id) => budgetService.getBudgetSummary(id)))

      responses.forEach((response, index) => {
        budgetSummaries.value[targetIds[index]] = response.data
      })

      return budgetSummaries.value
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      summariesLoading.value = false
    }
  }

  async function createBudget(budget) {
    loading.value = true
    error.value = null
    try {
      const response = await budgetService.createBudget(budget)
      budgets.value = sortBudgetsByStartDate([...budgets.value, response.data])
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateBudget(id, budget) {
    loading.value = true
    error.value = null
    try {
      const response = await budgetService.updateBudget(id, budget)
      const index = budgets.value.findIndex(b => b._id === id)
      if (index !== -1) {
        budgets.value[index] = response.data
      }
      budgets.value = sortBudgetsByStartDate(budgets.value)
      if (currentBudget.value && currentBudget.value._id === id) {
        currentBudget.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteBudget(id, force = false) {
    loading.value = true
    error.value = null
    try {
      await budgetService.deleteBudget(id, force)
      budgets.value = budgets.value.filter(b => b._id !== id)
      delete budgetSummaries.value[id]
      if (currentBudget.value && currentBudget.value._id === id) {
        currentBudget.value = null
      }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  function setCurrentBudget(budget) {
    currentBudget.value = budget
  }

  function clearCurrentBudget() {
    currentBudget.value = null
    currentSummary.value = null
  }

  return {
    // State
    budgets,
    currentBudget,
    currentSummary,
    budgetSummaries,
    loading,
    summariesLoading,
    error,
    // Getters
    activeBudgets,
    closedBudgets,
    draftBudgets,
    // Actions
    fetchBudgets,
    fetchActiveBudgets,
    getBudget,
    getBudgetSummary,
    getBudgetSummaries,
    createBudget,
    updateBudget,
    deleteBudget,
    setCurrentBudget,
    clearCurrentBudget
  }
})
