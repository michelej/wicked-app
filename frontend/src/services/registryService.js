import apiClient from './api'

export default {
  getItems(params = {}) {
    return apiClient.get('/api/registry-items', { params })
  },

  getItem(id) {
    return apiClient.get(`/api/registry-items/${id}`)
  },

  createItem(payload) {
    return apiClient.post('/api/registry-items', payload)
  },

  updateItem(id, payload) {
    return apiClient.put(`/api/registry-items/${id}`, payload)
  },

  archiveItem(id) {
    return apiClient.post(`/api/registry-items/${id}/archive`)
  },

  duplicateItem(id) {
    return apiClient.post(`/api/registry-items/${id}/duplicate`)
  },

  deleteItem(id) {
    return apiClient.delete(`/api/registry-items/${id}`)
  }
}
