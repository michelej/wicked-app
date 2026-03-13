import apiClient from './api'

export default {
  // Get all recurring expenses
  getRecurringExpenses(params = {}) {
    return apiClient.get('/api/recurring-expenses', { params })
  },

  // Get active recurring expenses
  getActiveRecurringExpenses() {
    return apiClient.get('/api/recurring-expenses/active')
  },

  // Get recurring expense by ID
  getRecurringExpense(id) {
    return apiClient.get(`/api/recurring-expenses/${id}`)
  },

  // Create recurring expense
  createRecurringExpense(expense) {
    return apiClient.post('/api/recurring-expenses', expense)
  },

  // Update recurring expense
  updateRecurringExpense(id, expense) {
    return apiClient.put(`/api/recurring-expenses/${id}`, expense)
  },

  // Delete recurring expense
  deleteRecurringExpense(id) {
    return apiClient.delete(`/api/recurring-expenses/${id}`)
  },

  // Apply recurring expenses to budget
  applyToBudget(budgetId, recurringExpenseIds) {
    return apiClient.post('/api/recurring-expenses/apply-to-budget', {
      budget_id: budgetId,
      recurring_expense_ids: recurringExpenseIds
    })
  }
}
