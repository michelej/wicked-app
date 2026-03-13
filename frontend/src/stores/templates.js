import { defineStore } from 'pinia'
import { ref } from 'vue'
import templateService from '@/services/templateService'

export const useTemplateStore = defineStore('templates', () => {
  // State
  const templates = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchTemplates(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await templateService.getTemplates(params)
      templates.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getTemplate(id) {
    loading.value = true
    error.value = null
    try {
      const response = await templateService.getTemplate(id)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createTemplate(template) {
    loading.value = true
    error.value = null
    try {
      const response = await templateService.createTemplate(template)
      templates.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateTemplate(id, template) {
    loading.value = true
    error.value = null
    try {
      const response = await templateService.updateTemplate(id, template)
      const index = templates.value.findIndex(t => t._id === id)
      if (index !== -1) {
        templates.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteTemplate(id) {
    loading.value = true
    error.value = null
    try {
      await templateService.deleteTemplate(id)
      templates.value = templates.value.filter(t => t._id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    templates,
    loading,
    error,
    // Actions
    fetchTemplates,
    getTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate
  }
})
