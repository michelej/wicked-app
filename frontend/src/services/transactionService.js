import apiClient from './api'

export default {
  // Get all transactions
  getTransactions(params = {}) {
    return apiClient.get('/api/transactions', { params })
  },

  // Get transactions by budget
  getTransactionsByBudget(budgetId) {
    return apiClient.get(`/api/transactions/budget/${budgetId}`)
  },

  // Get transaction by ID
  getTransaction(id) {
    return apiClient.get(`/api/transactions/${id}`)
  },

  // Create transaction
  createTransaction(transaction) {
    return apiClient.post('/api/transactions', transaction)
  },

  // Bulk create transactions
  bulkCreateTransactions(transactions) {
    return apiClient.post('/api/transactions/bulk', transactions)
  },

  // Update transaction
  updateTransaction(id, transaction) {
    return apiClient.put(`/api/transactions/${id}`, transaction)
  },

  // Mark transaction as charged/uncharged
  markCharged(id, isCharged = true) {
    return apiClient.patch(`/api/transactions/${id}/charge`, null, {
      params: { is_charged: isCharged }
    })
  },

  // Delete transaction
  deleteTransaction(id) {
    return apiClient.delete(`/api/transactions/${id}`)
  }
}
