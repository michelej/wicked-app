import apiClient from './api'

export default {
  // Get all templates
  getTemplates(params = {}) {
    return apiClient.get('/api/templates', { params })
  },

  // Get template by ID
  getTemplate(id) {
    return apiClient.get(`/api/templates/${id}`)
  },

  // Create template
  createTemplate(template) {
    return apiClient.post('/api/templates', template)
  },

  // Update template
  updateTemplate(id, template) {
    return apiClient.put(`/api/templates/${id}`, template)
  },

  // Delete template
  deleteTemplate(id) {
    return apiClient.delete(`/api/templates/${id}`)
  }
}
