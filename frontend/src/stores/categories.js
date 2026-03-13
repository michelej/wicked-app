import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import categoryService from '@/services/categoryService'

export const useCategoryStore = defineStore('categories', () => {
  // State
  const categories = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  // Solo categorías padre (sin subcategorías)
  const expenseCategories = computed(() => 
    categories.value.filter(c => (c.type === 'expense' || c.type === 'both') && !c.parent_id)
  )
  
  const incomeCategories = computed(() => 
    categories.value.filter(c => (c.type === 'income' || c.type === 'both') && !c.parent_id)
  )
  
  const activeCategories = computed(() => 
    categories.value.filter(c => c.is_active)
  )

  const parentCategories = computed(() =>
    categories.value.filter(c => !c.parent_id)
  )

  // Incluye categorías padre y subcategorías
  const allExpenseCategories = computed(() => 
    categories.value.filter(c => (c.type === 'expense' || c.type === 'both') && c.is_active)
  )
  
  const allIncomeCategories = computed(() => 
    categories.value.filter(c => (c.type === 'income' || c.type === 'both') && c.is_active)
  )

  const allActiveCategories = computed(() => 
    categories.value.filter(c => c.is_active)
  )

  const getSubcategoriesByParent = (parentId) => {
    return categories.value.filter(c => c.parent_id === parentId)
  }

  // Helper function to sort categories hierarchically (parents followed by their children)
  const sortCategoriesHierarchically = (categoriesToSort) => {
    const result = []
    const parents = categoriesToSort.filter(c => !c.parent_id)
    
    parents.forEach(parent => {
      result.push(parent)
      const children = categoriesToSort.filter(c => c.parent_id === parent._id)
      result.push(...children)
    })
    
    return result
  }

  // Sorted hierarchical getters
  const sortedExpenseCategories = computed(() => 
    sortCategoriesHierarchically(allExpenseCategories.value)
  )
  
  const sortedIncomeCategories = computed(() => 
    sortCategoriesHierarchically(allIncomeCategories.value)
  )

  const sortedActiveCategories = computed(() => 
    sortCategoriesHierarchically(allActiveCategories.value)
  )

  // Actions
  async function fetchCategories(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await categoryService.getCategories(params)
      categories.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getCategory(id) {
    loading.value = true
    error.value = null
    try {
      const response = await categoryService.getCategory(id)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createCategory(category) {
    loading.value = true
    error.value = null
    try {
      const response = await categoryService.createCategory(category)
      categories.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateCategory(id, category) {
    loading.value = true
    error.value = null
    try {
      const response = await categoryService.updateCategory(id, category)
      const index = categories.value.findIndex(c => c._id === id)
      if (index !== -1) {
        categories.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteCategory(id, force = false) {
    loading.value = true
    error.value = null
    try {
      await categoryService.deleteCategory(id, force)
      categories.value = categories.value.filter(c => c._id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchParentCategories(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await categoryService.getParentCategories(params)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchSubcategories(parentId) {
    loading.value = true
    error.value = null
    try {
      const response = await categoryService.getSubcategories(parentId)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    categories,
    loading,
    error,
    // Getters
    expenseCategories,
    incomeCategories,
    activeCategories,
    parentCategories,
    allExpenseCategories,
    allIncomeCategories,
    allActiveCategories,
    sortedExpenseCategories,
    sortedIncomeCategories,
    sortedActiveCategories,
    getSubcategoriesByParent,
    // Actions
    fetchCategories,
    fetchParentCategories,
    fetchSubcategories,
    getCategory,
    createCategory,
    updateCategory,
    deleteCategory
  }
})
