import apiClient from './api'

export default {
  getTransactions(params = {}) {
    return apiClient.get('/api/credit-card-transactions', { params })
  },

  getTransaction(id) {
    return apiClient.get(`/api/credit-card-transactions/${id}`)
  },

  createTransaction(transaction) {
    return apiClient.post('/api/credit-card-transactions', transaction)
  },

  bulkCreateTransactions(transactions) {
    return apiClient.post('/api/credit-card-transactions/bulk', transactions)
  },

  updateTransaction(id, transaction) {
    return apiClient.put(`/api/credit-card-transactions/${id}`, transaction)
  },

  markCharged(id, isCharged = true) {
    return apiClient.patch(`/api/credit-card-transactions/${id}/charge`, null, {
      params: { is_charged: isCharged }
    })
  },

  deleteTransaction(id) {
    return apiClient.delete(`/api/credit-card-transactions/${id}`)
  }
}
