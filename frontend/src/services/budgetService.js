import apiClient from './api'

export default {
  // Get all budgets
  getBudgets(params = {}) {
    return apiClient.get('/api/budgets', { params })
  },

  // Get active budgets
  getActiveBudgets() {
    return apiClient.get('/api/budgets/active')
  },

  // Get budget by ID
  getBudget(id) {
    return apiClient.get(`/api/budgets/${id}`)
  },

  // Get budget summary
  getBudgetSummary(id) {
    return apiClient.get(`/api/budgets/${id}/summary`)
  },

  // Get monthly budget summaries
  getMonthlyBudgetSummaries() {
    return apiClient.get('/api/budgets/monthly-summary')
  },

  // Create budget
  createBudget(budget) {
    return apiClient.post('/api/budgets', budget)
  },

  // Update budget
  updateBudget(id, budget) {
    return apiClient.put(`/api/budgets/${id}`, budget)
  },

  // Delete budget
  deleteBudget(id, force = false) {
    return apiClient.delete(`/api/budgets/${id}`, {
      params: { force }
    })
  }
}
