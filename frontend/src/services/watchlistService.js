import apiClient from './api'

export default {
  getItems(params = {}) {
    return apiClient.get('/api/watchlist', { params })
  },

  createItem(payload) {
    return apiClient.post('/api/watchlist', payload)
  },

  updateItem(id, payload) {
    return apiClient.put(`/api/watchlist/${id}`, payload)
  },

  deleteItem(id) {
    return apiClient.delete(`/api/watchlist/${id}`)
  },

  searchCatalog(params = {}) {
    return apiClient.get('/api/watchlist/search/tmdb', { params })
  }
}
