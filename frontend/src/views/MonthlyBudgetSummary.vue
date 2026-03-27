<template>
  <div class="monthly-budget-summary">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Resumen Mensual de Presupuestos</h1>
          <p class="page-subtitle">Vista consolidada de gastos por mes y categoría</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando resumen mensual...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-message">
      <i class="pi pi-exclamation-circle"></i>
      {{ error }}
    </div>

    <!-- Monthly Summary -->
    <div v-else-if="monthlySummaries.length > 0" class="monthly-summaries">
      <Card
        v-for="monthSummary in monthlySummaries"
        :key="monthSummary.budget_month"
        class="month-card"
      >
        <template #header>
          <div class="month-header">
            <h2>{{ monthSummary.budget_month }}</h2>
            <div class="month-stats">
              <span class="stat-item">
                <strong>Presupuestos:</strong> {{ monthSummary.budget_count }}
              </span>
              <span class="stat-item">
                <strong>Total Gastado:</strong> {{ formatCurrency(monthSummary.total_spent) }}
              </span>
            </div>
          </div>
        </template>

        <template #content>
          <!-- Parent Category Total Cards -->
          <div class="parent-category-summary">
            <h3>Resumen por Categoría Padre</h3>
            <div class="parent-category-cards">
              <Card
                v-for="parent in getParentCategorySummary(monthSummary)"
                :key="parent.category"
                class="parent-summary-card"
              >
                <template #content>
                  <div class="card-title">{{ parent.category }}</div>
                  <div class="card-stats-single">
                    <span class="amount-text text-red">{{ formatCurrency(parent.spent) }}</span>
                    <small class="amount-label">Gastado</small>
                  </div>
                </template>
              </Card>
            </div>
          </div>

          <!-- Categories Summary -->
          <div class="categories-summary">
            <h3>Gastos por Categoría</h3>
            <DataTable
              :value="getCategoriesForMonth(monthSummary)"
              class="categories-table"
              stripedRows
              showGridlines
              paginator
              :rows="10"
              :rowsPerPageOptions="[10, 20, 50]"
            >
              <template #empty>
                <div class="empty-state">
                  <i class="pi pi-chart-bar"></i>
                  <p>No hay gastos registrados para este mes</p>
                </div>
              </template>

              <Column field="category" header="Categoría" sortable>
                <template #body="{ data }">
                  <div class="category-cell" :class="{ 'parent-category': data.isParent, 'subcategory': data.isSubcategory }">
                    <span v-if="data.isParent" class="parent-indicator">📁</span>
                    <span v-if="data.isSubcategory" class="subcategory-indicator">↳</span>
                    <Tag
                      :value="data.category"
                      :severity="data.isParent ? 'primary' : 'secondary'"
                      :class="{ 'parent-tag': data.isParent }"
                    />
                  </div>
                </template>
              </Column>

              <Column field="spent" header="Gastado" sortable>
                <template #body="{ data }">
                  <span class="amount-text text-red">
                    {{ formatCurrency(data.spent) }}
                  </span>
                </template>
              </Column>

              <Column field="transactions" header="Transacciones" sortable>
                <template #body="{ data }">
                  <span class="transaction-count">{{ data.transactions }}</span>
                </template>
              </Column>

              <Column field="planned" header="Planificado" sortable>
                <template #body="{ data }">
                  <span class="amount-text">
                    {{ data.planned > 0 ? formatCurrency(data.planned) : '-' }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </div>
        </template>
      </Card>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <i class="pi pi-calendar"></i>
      <h2>No hay resúmenes mensuales</h2>
      <p>Crea presupuestos con meses asignados para ver el resumen aquí</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFormatters } from '@/composables/useFormatters'
import { useCategoryStore } from '@/stores/categories'
import budgetService from '@/services/budgetService'
import ProgressSpinner from 'primevue/progressspinner'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'

const { formatCurrency } = useFormatters()
const categoryStore = useCategoryStore()

// State
const monthlySummaries = ref([])
const loading = ref(true)
const error = ref(null)

// Methods
const loadMonthlySummaries = async () => {
  try {
    loading.value = true
    const response = await budgetService.getMonthlyBudgetSummaries()
    monthlySummaries.value = response.data
  } catch (err) {
    error.value = 'Error al cargar los resúmenes mensuales'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const getCategoriesForMonth = (monthSummary) => {
  const categories = []
  const processedParents = new Set()

  // Build category to parent mapping from store
  const categoryToParent = {}
  categoryStore.categories.forEach(cat => {
    if (cat.parent_id) {
      const parentCat = categoryStore.categories.find(p => p._id === cat.parent_id)
      if (parentCat) {
        categoryToParent[cat.name] = parentCat.name
      }
    }
  })

  // First, collect all categories
  const allCategories = Object.keys(monthSummary.categories_summary)

  // Group by parent
  const parentGroups = {}

  allCategories.forEach(catName => {
    // Skip "Transferido Cuentas" category as it's a transfer
    if (catName === "Transferido Cuentas") {
      return
    }
    
    const data = monthSummary.categories_summary[catName]
    const parentName = categoryToParent[catName]

    // Ensure data values are valid numbers
    const spent = typeof data.spent === 'number' && !isNaN(data.spent) ? data.spent : 0
    const transactions = typeof data.transactions === 'number' && !isNaN(data.transactions) ? data.transactions : 0
    const planned = typeof data.planned === 'number' && !isNaN(data.planned) ? data.planned : 0

    if (parentName) {
      // This is a subcategory
      if (!parentGroups[parentName]) {
        parentGroups[parentName] = {
          category: parentName,
          spent: 0,
          transactions: 0,
          planned: 0,
          subcategories: []
        }
      }

      parentGroups[parentName].spent += spent
      parentGroups[parentName].transactions += transactions
      parentGroups[parentName].planned += planned
      parentGroups[parentName].subcategories.push({
        category: catName,
        spent: spent,
        transactions: transactions,
        planned: planned,
        isSubcategory: true
      })
    } else {
      // This is a parent or standalone category
      if (!parentGroups[catName]) {
        parentGroups[catName] = {
          category: catName,
          spent: spent,
          transactions: transactions,
          planned: planned,
          subcategories: []
        }
      }
    }
  })

  // Build final result
  Object.values(parentGroups).forEach(parent => {
    // Sort subcategories by spent amount
    parent.subcategories.sort((a, b) => b.spent - a.spent)

    // Add parent
    categories.push({
      ...parent,
      isParent: parent.subcategories.length > 0
    })

    // Add subcategories
    parent.subcategories.forEach(sub => {
      categories.push(sub)
    })
  })

  return categories
}

const getParentCategorySummary = (monthSummary) => {
  const categories = getCategoriesForMonth(monthSummary)

  return categories
    .filter(item => item.isParent)
    .map(parent => ({
      category: parent.category,
      spent: parent.spent
    }))
    .sort((a, b) => b.spent - a.spent)
}

// Lifecycle
onMounted(async () => {
  await categoryStore.fetchCategories()
  await loadMonthlySummaries()
})
</script>

<style scoped>
.monthly-budget-summary {
  width: 100%;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Header */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 1rem;
  color: var(--text-color-secondary);
  font-weight: 400;
}

/* States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  gap: 1rem;
  color: var(--text-color-secondary);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 12px;
  color: #dc2626;
}

.empty-state {
  text-align: center;
  padding: 4rem 1rem;
  color: var(--text-color-secondary);
}

.empty-state i {
  font-size: 4rem;
  opacity: 0.5;
  margin-bottom: 1.5rem;
}

.empty-state h2 {
  font-size: 1.5rem;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

/* Monthly Summaries */
.monthly-summaries {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.month-card {
  border: 1px solid var(--surface-border);
  border-radius: 16px;
}

.month-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.month-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.month-stats {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9375rem;
}

.month-stats .stat-item {
  color: var(--text-color-secondary);
}

/* Categories Summary */
.parent-category-summary {
  margin-top: 1rem;
  margin-bottom: 1.25rem;
}

.parent-category-summary h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.75rem;
}

.parent-category-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.parent-summary-card {
  border: 1px solid var(--surface-border);
  border-radius: 12px;
  background: var(--surface-card);
  transition: all 0.25s ease;
}

.parent-summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.09);
  border-color: var(--primary-color);
}

.parent-summary-card .card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.parent-summary-card .card-stats-single {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
}

.parent-summary-card .card-stats-single .amount-text {
  font-size: 1.25rem;
  font-weight: 700;
}

.parent-summary-card .card-stats-single .amount-label {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.parent-summary-card .card-value {
  font-size: 1rem;
  font-weight: 700;
  margin-top: 0.15rem;
}

.parent-summary-card .text-red {
  color: #dc2626;
}

.categories-summary {
  margin-top: 1rem;
}

.categories-summary h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 1rem;
}

.categories-table :deep(.p-datatable-thead > tr > th) {
  background: var(--primary-color);
  color: white;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--surface-border);
  text-align: left;
  font-size: 0.8125rem;
  line-height: 1.2;
}

.categories-table :deep(.p-datatable-tbody > tr > td) {
  padding: 0.35rem 0.5rem;
  border: 1px solid var(--surface-border);
  vertical-align: middle;
  font-size: 0.8125rem;
  line-height: 1.2;
}

/* Category Hierarchy */
.category-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.parent-category {
  font-weight: 600;
  background: rgba(59, 130, 246, 0.05);
  padding: 0.5rem;
  border-radius: 8px;
  margin: 0.25rem 0;
}

.subcategory {
  margin-left: 2rem;
  opacity: 0.9;
}

.parent-indicator {
  font-size: 1.1rem;
}

.subcategory-indicator {
  color: var(--primary-color);
  font-size: 1rem;
  font-weight: bold;
}

.parent-tag {
  font-weight: 600;
  font-size: 0.9rem;
}

.amount-text {
  font-weight: 600;
  font-size: 0.9rem;
}

.text-red {
  color: #ef4444 !important;
}

.transaction-count {
  font-weight: 600;
  color: var(--text-color);
}
</style>