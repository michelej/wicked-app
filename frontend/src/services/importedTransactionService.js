import apiClient from './api'

export default {
  getImportedTransactions(params = {}) {
    return apiClient.get('/api/imported-transactions', { params })
  },

  getImportedTransaction(id) {
    return apiClient.get(`/api/imported-transactions/${id}`)
  },

  uploadImportedTransactions(sourceBank, file) {
    const formData = new FormData()
    formData.append('source_bank', sourceBank)
    formData.append('file', file)

    return apiClient.post('/api/imported-transactions/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  processImportedTransaction(id, payload) {
    return apiClient.post(`/api/imported-transactions/${id}/process`, payload)
  }
}
