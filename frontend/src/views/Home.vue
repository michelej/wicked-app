<template>
  <div class="dashboard">
    <!-- Header Section -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="dashboard-title">Dashboard Financiero</h1>
          <p class="dashboard-subtitle">Resumen de tus presupuestos activos</p>
        </div>
        <Button 
          label="Nuevo Presupuesto" 
          icon="pi pi-plus"
          class="add-button"
          @click="navigateToBudgets"
          severity="success"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="budgetStore.loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando datos...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="budgetStore.error" class="error-message">
      <i class="pi pi-exclamation-circle"></i>
      {{ budgetStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="activeBudgets.length === 0" class="empty-state">
      <i class="pi pi-inbox"></i>
      <h2>No hay presupuestos activos</h2>
      <p>Crea tu primer presupuesto para comenzar a gestionar tus finanzas</p>
      <Button 
        label="Crear Presupuesto" 
        icon="pi pi-plus"
        @click="navigateToBudgets"
        severity="success"
      />
    </div>

    <!-- Active Budgets -->
    <div v-else class="budgets-container">
      <!-- Summary Statistics -->
      <div class="stats-grid">
        <div class="stat-card stat-card-1">
          <div class="stat-icon">
            <i class="pi pi-wallet"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ activeBudgets.length }}</h3>
            <p class="stat-label">Presupuestos Activos</p>
          </div>
        </div>

        <div class="stat-card stat-card-2">
          <div class="stat-icon">
            <i class="pi pi-arrow-down"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ formatCurrency(totalIncome) }}</h3>
            <p class="stat-label">Ingresos Totales</p>
          </div>
        </div>

        <div class="stat-card stat-card-3">
          <div class="stat-icon">
            <i class="pi pi-arrow-up"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ formatCurrency(totalExpense) }}</h3>
            <p class="stat-label">Gastos Totales</p>
          </div>
        </div>

        <div class="stat-card stat-card-4">
          <div class="stat-icon">
            <i class="pi pi-chart-line"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value" :class="{ 'negative': totalBalance < 0 }">
              {{ formatCurrency(totalBalance) }}
            </h3>
            <p class="stat-label">Balance Total</p>
          </div>
        </div>
      </div>

      <!-- Budget Cards -->
      <div class="budget-cards-grid">
        <Card 
          v-for="budget in activeBudgets" 
          :key="budget._id"
          class="budget-card"
        >
          <template #header>
            <div class="budget-card-header">
              <div class="budget-info">
                <h3>{{ budget.name }}</h3>
                <p class="budget-period">
                  {{ formatDate(budget.start_date) }} - {{ formatDate(budget.end_date) }}
                </p>
              </div>
              <Button 
                icon="pi pi-eye" 
                text 
                rounded
                severity="secondary"
                @click="navigateToBudgetDetail(budget._id)"
              />
            </div>
          </template>

          <template #content>
            <div class="budget-summary">
              <div class="summary-item">
                <div class="summary-label">
                  <i class="pi pi-arrow-down text-green"></i>
                  <span>Ingresos</span>
                </div>
                <div class="summary-value text-green">
                  {{ formatCurrency(budget.summary?.total_income || 0) }}
                </div>
              </div>

              <div class="summary-item">
                <div class="summary-label">
                  <i class="pi pi-arrow-up text-red"></i>
                  <span>Gastos</span>
                </div>
                <div class="summary-value text-red">
                  {{ formatCurrency(budget.summary?.total_expense || 0) }}
                </div>
              </div>

              <Divider />

              <div class="summary-item summary-total">
                <div class="summary-label">
                  <i class="pi pi-wallet"></i>
                  <span>Balance</span>
                </div>
                <div 
                  class="summary-value" 
                  :class="{ 
                    'text-green': budget.summary?.balance >= 0, 
                    'text-red': budget.summary?.balance < 0 
                  }"
                >
                  {{ formatCurrency(budget.summary?.balance || 0) }}
                </div>
              </div>

              <div class="summary-item">
                <div class="summary-label">
                  <i class="pi pi-list"></i>
                  <span>Transacciones</span>
                </div>
                <div class="summary-value">
                  {{ budget.summary?.transactions_count || 0 }}
                </div>
              </div>

              <div class="summary-item">
                <div class="summary-label">
                  <i class="pi pi-clock"></i>
                  <span>Pendientes</span>
                </div>
                <div class="summary-value text-orange">
                  {{ formatCurrency(budget.summary?.pending_expense || 0) }}
                </div>
              </div>
            </div>
          </template>

          <template #footer>
            <Button 
              label="Ver Detalles" 
              icon="pi pi-arrow-right"
              text
              class="w-full"
              @click="navigateToBudgetDetail(budget._id)"
            />
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBudgetStore } from '@/stores/budgets'
import { useFormatters } from '@/composables/useFormatters'
import ProgressSpinner from 'primevue/progressspinner'
import Divider from 'primevue/divider'

const router = useRouter()
const budgetStore = useBudgetStore()
const { formatCurrency, formatDate } = useFormatters()

// Load budgets with summaries on mount
onMounted(async () => {
  await budgetStore.fetchBudgets()
  // Load summaries for all active budgets
  for (const budget of budgetStore.activeBudgets) {
    await budgetStore.getBudgetSummary(budget._id)
  }
})

// Computed properties
const activeBudgets = computed(() => {
  return budgetStore.activeBudgets.map(budget => ({
    ...budget,
    summary: budgetStore.budgetSummaries[budget._id]
  }))
})

const totalIncome = computed(() => {
  return activeBudgets.value.reduce((sum, budget) => {
    return sum + (budget.summary?.total_income || 0)
  }, 0)
})

const totalExpense = computed(() => {
  return activeBudgets.value.reduce((sum, budget) => {
    return sum + (budget.summary?.total_expense || 0)
  }, 0)
})

const totalBalance = computed(() => {
  return activeBudgets.value.reduce((sum, budget) => {
    return sum + (budget.summary?.balance || 0)
  }, 0)
})

// Navigation methods
const navigateToBudgets = () => {
  router.push('/budgets')
}

const navigateToBudgetDetail = (budgetId) => {
  router.push(`/budgets/${budgetId}`)
}
</script>

<style scoped>
.dashboard {
  width: 100%;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Header Section */
.dashboard-header {
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

.dashboard-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.dashboard-subtitle {
  font-size: 1rem;
  color: var(--text-color-secondary);
  font-weight: 400;
}

.add-button {
  font-weight: 600;
}

/* Loading and Empty States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  gap: 1rem;
  color: var(--text-color-secondary);
}

.empty-state {
  text-align: center;
  padding: 4rem 1rem;
  color: var(--text-color-secondary);
}

.empty-state i {
  font-size: 4rem;
  color: var(--text-color-secondary);
  opacity: 0.5;
  margin-bottom: 1.5rem;
}

.empty-state h2 {
  font-size: 1.5rem;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.empty-state p {
  font-size: 1rem;
  margin-bottom: 2rem;
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

.error-message i {
  font-size: 1.5rem;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--surface-card);
  border-radius: 16px;
  padding: 1.75rem;
  border: 1px solid var(--surface-border);
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease-out;
  animation-fill-mode: both;
}

.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
.stat-card:nth-child(4) { animation-delay: 0.4s; }

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.stat-card-1 .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card-2 .stat-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.stat-card-3 .stat-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.stat-card-4 .stat-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.25rem;
  line-height: 1;
}

.stat-value.negative {
  color: #ef4444;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  font-weight: 500;
  margin: 0;
}

/* Budget Cards Grid */
.budget-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
  animation: slideUp 0.5s ease-out 0.5s;
  animation-fill-mode: both;
}

.budget-card {
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.budget-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.budget-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  gap: 1rem;
}

.budget-info h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.budget-period {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.budget-summary {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9375rem;
  color: var(--text-color-secondary);
}

.summary-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
}

.summary-total .summary-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.text-green {
  color: #10b981 !important;
}

.text-red {
  color: #ef4444 !important;
}

.text-orange {
  color: #f59e0b !important;
}

.w-full {
  width: 100%;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-title {
    font-size: 1.75rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .budget-cards-grid {
    grid-template-columns: 1fr;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .add-button {
    width: 100%;
  }
}
</style>
