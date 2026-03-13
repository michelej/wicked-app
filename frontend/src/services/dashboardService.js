import apiClient from './api'

export default {
  // Get daily progress for a budget
  getDailyProgress(budgetId) {
    return apiClient.get(`/api/dashboard/daily-progress/${budgetId}`)
  },

  // Get category summary
  getCategorySummary(budgetId) {
    return apiClient.get(`/api/dashboard/category-summary/${budgetId}`)
  },

  // Get payment method summary
  getPaymentMethodSummary(budgetId) {
    return apiClient.get(`/api/dashboard/payment-method-summary/${budgetId}`)
  },

  // Get upcoming expenses
  getUpcomingExpenses(daysAhead = 30) {
    return apiClient.get('/api/dashboard/upcoming-expenses', {
      params: { days_ahead: daysAhead }
    })
  },

  // Compare budgets
  compareBudgets(budgetIds) {
    return apiClient.get('/api/dashboard/budget-comparison', {
      params: { budget_ids: budgetIds }
    })
  }
}
