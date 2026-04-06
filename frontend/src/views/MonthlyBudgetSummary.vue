<template>
  <div class="monthly-budget-summary">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Resumen Mensual de Presupuestos</h1>
          <p class="page-subtitle">Vista consolidada de gastos por mes, categoria y extractos de tarjeta de credito</p>
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
          <div class="summary-section">
            <div class="section-header">
              <div>
                <span class="section-kicker">Presupuesto</span>
                <h3>Movimientos del presupuesto</h3>
                <p>Este apartado conserva solo los gastos registrados directamente en las transacciones del presupuesto.</p>
              </div>
              <div class="section-stat">
                <span>Total gastado</span>
                <strong>{{ formatCurrency(monthSummary.total_spent) }}</strong>
              </div>
            </div>

            <div class="parent-category-summary">
              <h4>Resumen por Categoría Padre</h4>
              <div class="parent-category-cards">
                <Card
                  v-for="parent in getBudgetParentCategorySummary(monthSummary)"
                  :key="`budget-${parent.category}`"
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

            <div class="categories-summary">
              <h4>Gastos por Categoría</h4>
              <DataTable
                :value="getBudgetCategoriesForMonth(monthSummary)"
                class="categories-table"
                stripedRows
                showGridlines
              >
                <template #empty>
                  <div class="empty-state compact-empty-state">
                    <i class="pi pi-chart-bar"></i>
                    <p>No hay gastos registrados para este mes</p>
                  </div>
                </template>

                <Column field="category" header="Categoría" sortable>
                  <template #body="{ data }">
                    <button
                      type="button"
                      class="category-link-button"
                      :class="{ 'parent-category': data.isParent, 'subcategory': data.isSubcategory }"
                      @click="goToTransactionsForMonthCategory(monthSummary, data)"
                    >
                      <div class="category-cell">
                        <span v-if="data.isParent" class="parent-indicator">📁</span>
                        <span v-if="data.isSubcategory" class="subcategory-indicator">↳</span>
                        <Tag
                          :value="data.category"
                          :severity="data.isParent ? 'primary' : 'secondary'"
                          :class="{ 'parent-tag': data.isParent }"
                        />
                      </div>
                    </button>
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
          </div>

          <div v-if="hasCreditCardSummary(monthSummary)" class="summary-section credit-card-section">
            <div class="section-header">
              <div>
                <span class="section-kicker">Tarjeta de credito</span>
                <h3>Extracto asociado al presupuesto</h3>
                <p>Este apartado mantiene separado el gasto de tarjeta segun el presupuesto al que pertenece cada movimiento.</p>
              </div>
              <div class="section-stat">
                <span>Total extracto</span>
                <strong>{{ formatCurrency(monthSummary.credit_card_total_spent || 0) }}</strong>
              </div>
            </div>

            <div class="parent-category-summary">
              <h4>Resumen por Categoría Padre</h4>
              <div class="parent-category-cards">
                <Card
                  v-for="parent in getCreditCardParentCategorySummary(monthSummary)"
                  :key="`credit-${parent.category}`"
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

            <div class="categories-summary">
              <h4>Gastos por Categoría</h4>
              <DataTable
                :value="getCreditCardCategoriesForMonth(monthSummary)"
                class="categories-table"
                stripedRows
                showGridlines
              >
                <template #empty>
                  <div class="empty-state compact-empty-state">
                    <i class="pi pi-credit-card"></i>
                    <p>No hay gastos de tarjeta registrados para este mes</p>
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
import { useRouter } from 'vue-router'
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
const router = useRouter()

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

const buildCategoryToParentMap = () => {
  const categoryToParent = {}

  categoryStore.categories.forEach(cat => {
    if (cat.parent_id) {
      const parentCat = categoryStore.categories.find(parent => parent._id === cat.parent_id)
      if (parentCat) {
        categoryToParent[cat.name] = parentCat.name
      }
    }
  })

  return categoryToParent
}

const normalizeCategoryTotals = (data = {}) => ({
  spent: typeof data.spent === 'number' && !Number.isNaN(data.spent) ? data.spent : 0,
  transactions: typeof data.transactions === 'number' && !Number.isNaN(data.transactions) ? data.transactions : 0,
  planned: typeof data.planned === 'number' && !Number.isNaN(data.planned) ? data.planned : 0
})

const getCategoriesForSummary = (categoriesSummary = {}) => {
  const categories = []
  const categoryToParent = buildCategoryToParentMap()
  const parentGroups = {}

  const ensureParentGroup = (categoryName) => {
    if (!parentGroups[categoryName]) {
      parentGroups[categoryName] = {
        category: categoryName,
        ownSpent: null,
        ownTransactions: null,
        ownPlanned: null,
        fallbackSpent: 0,
        fallbackTransactions: 0,
        fallbackPlanned: 0,
        subcategories: []
      }
    }

    return parentGroups[categoryName]
  }

  Object.entries(categoriesSummary).forEach(([catName, rawData]) => {
    if (catName === 'Transferido Cuentas') {
      return
    }

    const data = normalizeCategoryTotals(rawData)
    const parentName = categoryToParent[catName]

    if (parentName) {
      const parentGroup = ensureParentGroup(parentName)

      parentGroup.fallbackSpent += data.spent
      parentGroup.fallbackTransactions += data.transactions
      parentGroup.fallbackPlanned += data.planned
      parentGroup.subcategories.push({
        category: catName,
        spent: data.spent,
        transactions: data.transactions,
        planned: data.planned,
        isSubcategory: true
      })

      return
    }

    const categoryGroup = ensureParentGroup(catName)
    categoryGroup.ownSpent = data.spent
    categoryGroup.ownTransactions = data.transactions
    categoryGroup.ownPlanned = data.planned
  })

  Object.values(parentGroups)
    .map(group => ({
      category: group.category,
      spent: group.ownSpent ?? group.fallbackSpent,
      transactions: group.ownTransactions ?? group.fallbackTransactions,
      planned: group.ownPlanned ?? group.fallbackPlanned,
      subcategories: group.subcategories
    }))
    .sort((a, b) => b.spent - a.spent)
    .forEach(parent => {
      parent.subcategories.sort((a, b) => b.spent - a.spent)

      categories.push({
        ...parent,
        isParent: parent.subcategories.length > 0
      })

      parent.subcategories.forEach(sub => {
        categories.push(sub)
      })
    })

  return categories
}

const getParentCategorySummary = (categoriesSummary = {}) => {
  const categories = getCategoriesForSummary(categoriesSummary)

  return categories
    .filter(item => item.isParent)
    .map(parent => ({
      category: parent.category,
      spent: parent.spent
    }))
    .sort((a, b) => b.spent - a.spent)
}

const getBudgetCategoriesForMonth = (monthSummary) => getCategoriesForSummary(monthSummary.categories_summary)

const getBudgetParentCategorySummary = (monthSummary) => getParentCategorySummary(monthSummary.categories_summary)

const getCreditCardCategoriesForMonth = (monthSummary) => getCategoriesForSummary(monthSummary.credit_card_categories_summary)

const getCreditCardParentCategorySummary = (monthSummary) => getParentCategorySummary(monthSummary.credit_card_categories_summary)

const hasCreditCardSummary = (monthSummary) => {
  return getCreditCardCategoriesForMonth(monthSummary).length > 0 || Number(monthSummary.credit_card_total_spent || 0) > 0
}

const goToTransactionsForMonthCategory = (monthSummary, categoryRow) => {
  const query = {
    budgetMonth: monthSummary.budget_month,
    type: 'expense'
  }

  if (categoryRow.isParent) {
    query.parentCategory = categoryRow.category
  } else {
    query.category = categoryRow.category
  }

  router.push({
    name: 'transactions',
    query
  })
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

.summary-section {
  margin-top: 1rem;
  padding: 1.25rem;
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.04) 0%, rgba(59, 130, 246, 0.01) 100%);
}

.credit-card-section {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(249, 115, 22, 0.03) 100%);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-kicker {
  display: inline-flex;
  margin-bottom: 0.4rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-color);
}

.section-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
}

.section-header p {
  margin: 0.4rem 0 0;
  color: var(--text-color-secondary);
  line-height: 1.5;
}

.section-stat {
  min-width: 180px;
  padding: 0.9rem 1rem;
  border-radius: 12px;
  border: 1px solid var(--surface-border);
  background: var(--surface-card);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.section-stat span {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-color-secondary);
}

.section-stat strong {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-color);
}

/* Categories Summary */
.parent-category-summary {
  margin-bottom: 1.25rem;
}

.parent-category-summary h4 {
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

.categories-summary h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
   margin-bottom: 0.8rem;
}

.compact-empty-state {
  padding: 2rem 1rem;
}

.categories-table :deep(.p-datatable-thead > tr > th) {
  background: var(--primary-color);
  color: white;
  font-weight: 600;
   padding: 0.28rem 0.45rem;
  border: 1px solid var(--surface-border);
  text-align: left;
   font-size: 0.78rem;
   line-height: 1.15;
}

.categories-table :deep(.p-datatable-tbody > tr > td) {
   padding: 0.26rem 0.45rem;
  border: 1px solid var(--surface-border);
  vertical-align: middle;
   font-size: 0.78rem;
   line-height: 1.15;
}

.categories-table :deep(.p-tag) {
  font-size: 0.72rem;
  padding: 0.2rem 0.42rem;
}

.categories-table :deep(.p-paginator) {
  padding: 0.4rem 0.55rem;
}

.categories-table :deep(.p-paginator .p-paginator-page),
.categories-table :deep(.p-paginator .p-paginator-prev),
.categories-table :deep(.p-paginator .p-paginator-next),
.categories-table :deep(.p-paginator .p-paginator-first),
.categories-table :deep(.p-paginator .p-paginator-last) {
  min-width: 1.9rem;
  height: 1.9rem;
}

.categories-table :deep(.p-paginator .p-dropdown-label) {
  font-size: 0.78rem;
}

/* Category Hierarchy */
.category-cell {
  display: flex;
  align-items: center;
  gap: 0.22rem;
}

.category-link-button {
  width: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
  border-radius: 10px;
}

.category-link-button:focus-visible {
  outline: 2px solid color-mix(in srgb, var(--primary-color) 75%, white);
  outline-offset: 2px;
}

.category-link-button:hover .category-cell,
.category-link-button:focus-visible .category-cell {
  transform: translateX(1px);
}

.category-link-button .category-cell {
  transition: transform 0.18s ease;
}

.parent-category {
  font-weight: 600;
  background: rgba(59, 130, 246, 0.05);
   padding: 0.35rem 0.45rem;
  border-radius: 8px;
   margin: 0.15rem 0;
}

.subcategory {
   margin-left: 1.2rem;
  opacity: 0.9;
}

.parent-indicator {
   font-size: 0.95rem;
}

.subcategory-indicator {
  color: var(--primary-color);
   font-size: 0.82rem;
  font-weight: bold;
  margin-right: 0.15rem;
}

.parent-tag {
  font-weight: 600;
   font-size: 0.76rem;
}

.amount-text {
  font-weight: 600;
   font-size: 0.84rem;
}

.text-red {
  color: #ef4444 !important;
}

.transaction-count {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.78rem;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
  }

  .section-stat {
    width: 100%;
    min-width: 0;
  }
}
</style>
