import apiClient from './api'

export default {
  // Get all categories
  getCategories(params = {}) {
    return apiClient.get('/api/categories', { params })
  },

  // Get parent categories only
  getParentCategories(params = {}) {
    return apiClient.get('/api/categories/parent/list', { params })
  },

  // Get subcategories of a parent
  getSubcategories(parentId) {
    return apiClient.get(`/api/categories/${parentId}/subcategories`)
  },

  // Get category by ID
  getCategory(id) {
    return apiClient.get(`/api/categories/${id}`)
  },

  // Create category
  createCategory(category) {
    return apiClient.post('/api/categories', category)
  },

  // Update category
  updateCategory(id, category) {
    return apiClient.put(`/api/categories/${id}`, category)
  },

  // Delete category
  deleteCategory(id, force = false) {
    return apiClient.delete(`/api/categories/${id}`, {
      params: { force }
    })
  }
}
