<template>
  <div class="dashboard">
    <section class="hero-panel">
      <div class="hero-copy">
        <span class="hero-kicker">Vision general</span>
        <h1 class="dashboard-title">Tu operacion financiera, mas clara y accionable.</h1>
        <p class="dashboard-subtitle">
          Supervisa liquidez, presupuestos activos y gastos pendientes desde un panel pensado para tomar decisiones con rapidez.
        </p>
        <div class="hero-actions">
          <Button
            label="Nuevo Presupuesto"
            icon="pi pi-plus"
            class="hero-primary-action"
            @click="navigateToBudgets"
            severity="success"
          />
          <Button
            label="Ver Presupuestos"
            icon="pi pi-arrow-right"
            text
            class="hero-secondary-action"
            @click="navigateToBudgets"
          />
        </div>
      </div>

      <div class="hero-summary-panel">
        <div class="hero-balance-card">
          <span class="panel-label">Balance consolidado</span>
          <strong :class="['hero-balance-value', { negative: totalBalance < 0 }]">
            {{ formatCurrency(totalBalance) }}
          </strong>
          <p>
            {{ healthyBudgetsCount }} de {{ activeBudgets.length || 0 }} presupuestos mantienen un margen saludable.
          </p>
        </div>

        <div class="hero-metric-grid">
          <div class="hero-metric-tile">
            <span>Gasto pendiente</span>
            <strong>{{ formatCurrency(totalPendingExpense) }}</strong>
          </div>
          <div class="hero-metric-tile">
            <span>Presupuestos en riesgo</span>
            <strong>{{ budgetsNeedingAttention }}</strong>
          </div>
          <div class="hero-metric-tile">
            <span>Movimientos registrados</span>
            <strong>{{ totalTransactions }}</strong>
          </div>
          <div class="hero-metric-tile">
            <span>Ritmo de gasto</span>
            <strong>{{ spendingPulse }}</strong>
          </div>
        </div>
      </div>
    </section>

    <div v-if="budgetStore.loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando datos...</p>
    </div>

    <div v-else-if="budgetStore.error" class="error-message">
      <i class="pi pi-exclamation-circle"></i>
      {{ budgetStore.error }}
    </div>

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

    <div v-else class="budgets-container">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="pi pi-wallet"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ activeBudgets.length }}</h3>
            <p class="stat-label">Presupuestos Activos</p>
            <small class="stat-note">Portafolio en seguimiento</small>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <i class="pi pi-arrow-down"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ formatCurrency(totalIncome) }}</h3>
            <p class="stat-label">Ingresos Totales</p>
            <small class="stat-note">Entrada consolidada del periodo</small>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <i class="pi pi-arrow-up"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ formatCurrency(totalExpense) }}</h3>
            <p class="stat-label">Gastos Totales</p>
            <small class="stat-note">Ejecucion actual del portafolio</small>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <i class="pi pi-clock"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ formatCurrency(totalPendingExpense) }}</h3>
            <p class="stat-label">Pendiente por Cobrar</p>
            <small class="stat-note">Gastos aun no cobrados</small>
          </div>
        </div>
      </div>

      <div class="insight-strip">
        <div class="insight-item">
          <span class="insight-label">Atencion</span>
          <strong>{{ budgetsNeedingAttention }}</strong>
          <p>presupuestos requieren seguimiento cercano.</p>
        </div>
        <div class="insight-item">
          <span class="insight-label">Liquidez</span>
          <strong>{{ formatCurrency(totalBalance - totalPendingExpense) }}</strong>
          <p>margen estimado despues de pendientes.</p>
        </div>
        <div class="insight-item">
          <span class="insight-label">Ritmo</span>
          <strong>{{ expenseRatioLabel }}</strong>
          <p>relacion entre gasto ejecutado e ingresos.</p>
        </div>
      </div>

      <div class="budget-cards-grid">
        <Card
          v-for="budget in activeBudgets"
          :key="budget._id"
          class="budget-card"
        >
          <template #header>
            <div class="budget-card-header">
              <div class="budget-heading">
                <div class="budget-avatar">{{ getBudgetInitial(budget) }}</div>
                <div class="budget-info">
                  <Tag :value="getBudgetHealth(budget).label" :severity="getBudgetHealth(budget).severity" class="budget-status" />
                  <h3>{{ budget.name }}</h3>
                  <p class="budget-period">
                    <i class="pi pi-calendar"></i>
                    {{ formatDate(budget.start_date) }} - {{ formatDate(budget.end_date) }}
                  </p>
                </div>
              </div>
              <Button
                icon="pi pi-arrow-up-right"
                text
                rounded
                severity="secondary"
                class="budget-open-button"
                @click="navigateToBudgetDetail(budget._id)"
              />
            </div>
          </template>

          <template #content>
            <div class="budget-summary">
              <div class="budget-balance-panel">
                <span class="panel-label">Balance disponible</span>
                <strong :class="['budget-balance-value', { negative: (budget.summary?.balance || 0) < 0 }]">
                  {{ formatCurrency(budget.summary?.balance || 0) }}
                </strong>
                <p>{{ getBudgetHealth(budget).description }}</p>
              </div>

              <div class="budget-progress-block">
                <div class="progress-meta">
                  <span>Consumo frente a ingresos</span>
                  <strong>{{ getBudgetProgressLabel(budget) }}</strong>
                </div>
                <div class="progress-track">
                  <span
                    class="progress-fill"
                    :class="getProgressTone(budget)"
                    :style="{ width: `${getBudgetProgress(budget)}%` }"
                  ></span>
                </div>
              </div>

              <div class="budget-metrics-grid">
                <div class="budget-metric">
                  <span>Ingresos</span>
                  <strong class="text-green">{{ formatCurrency(budget.summary?.total_income || 0) }}</strong>
                </div>
                <div class="budget-metric">
                  <span>Gastos</span>
                  <strong class="text-red">{{ formatCurrency(budget.summary?.total_expense || 0) }}</strong>
                </div>
                <div class="budget-metric">
                  <span>Pendiente</span>
                  <strong class="text-orange">{{ formatCurrency(budget.summary?.pending_expense || 0) }}</strong>
                </div>
                <div class="budget-metric">
                  <span>Transacciones</span>
                  <strong>{{ budget.summary?.transactions_count || 0 }}</strong>
                </div>
              </div>

              <div class="budget-inline-footer">
                <div class="summary-chip">
                  <i class="pi pi-chart-line"></i>
                  <span>{{ getBudgetFooterHint(budget) }}</span>
                </div>
                <div class="summary-chip muted-chip">
                  <i class="pi pi-wallet"></i>
                  {{ formatDate(budget.start_date) }} - {{ formatDate(budget.end_date) }}
                </div>
              </div>
            </div>
          </template>

          <template #footer>
            <Button
              label="Ver Detalles"
              icon="pi pi-arrow-right"
              class="w-full budget-detail-button"
              @click="navigateToBudgetDetail(budget._id)"
            />
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBudgetStore } from '@/stores/budgets'
import { useFormatters } from '@/composables/useFormatters'
import ProgressSpinner from 'primevue/progressspinner'

const router = useRouter()
const budgetStore = useBudgetStore()
const { formatCurrency, formatDate } = useFormatters()

onMounted(async () => {
  await budgetStore.fetchBudgets()

  for (const budget of budgetStore.activeBudgets) {
    await budgetStore.getBudgetSummary(budget._id)
  }
})

const activeBudgets = computed(() => {
  return budgetStore.activeBudgets.map((budget) => ({
    ...budget,
    summary: budgetStore.budgetSummaries[budget._id]
  }))
})

const totalPendingExpense = computed(() => {
  return activeBudgets.value.reduce((sum, budget) => sum + (budget.summary?.pending_expense || 0), 0)
})

const totalIncome = computed(() => {
  return activeBudgets.value.reduce((sum, budget) => sum + (budget.summary?.total_income || 0), 0)
})

const totalExpense = computed(() => {
  return activeBudgets.value.reduce((sum, budget) => sum + (budget.summary?.total_expense || 0), 0)
})

const totalBalance = computed(() => {
  return activeBudgets.value.reduce((sum, budget) => sum + (budget.summary?.balance || 0), 0)
})

const totalTransactions = computed(() => {
  return activeBudgets.value.reduce((sum, budget) => sum + (budget.summary?.transactions_count || 0), 0)
})

const healthyBudgetsCount = computed(() => {
  return activeBudgets.value.filter((budget) => (budget.summary?.balance || 0) >= 0).length
})

const budgetsNeedingAttention = computed(() => {
  return activeBudgets.value.filter((budget) => {
    const balance = budget.summary?.balance || 0
    const pending = budget.summary?.pending_expense || 0

    return balance < 0 || pending > Math.max(balance, 0)
  }).length
})

const expenseRatio = computed(() => {
  if (!totalIncome.value && !totalExpense.value) {
    return 0
  }

  return Math.min(100, Math.round((totalExpense.value / Math.max(totalIncome.value, totalExpense.value, 1)) * 100))
})

const expenseRatioLabel = computed(() => {
  if (!totalIncome.value && !totalExpense.value) {
    return 'Sin actividad'
  }

  return `${expenseRatio.value}% ejecutado`
})

const spendingPulse = computed(() => {
  if (!totalIncome.value && !totalExpense.value) {
    return 'Sin actividad'
  }

  if (expenseRatio.value <= 60) {
    return 'Controlado'
  }

  if (expenseRatio.value <= 85) {
    return 'En objetivo'
  }

  return 'Ajustado'
})

const getBudgetInitial = (budget) => {
  return budget.name?.trim()?.charAt(0)?.toUpperCase() || 'B'
}

const getBudgetHealth = (budget) => {
  const income = budget.summary?.total_income || 0
  const expense = budget.summary?.total_expense || 0
  const balance = budget.summary?.balance || 0
  const pending = budget.summary?.pending_expense || 0

  if (!income && !expense && !pending) {
    return {
      label: 'Sin movimiento',
      severity: 'secondary',
      description: 'Aun no registra actividad relevante en el periodo.'
    }
  }

  if (balance < 0) {
    return {
      label: 'En riesgo',
      severity: 'danger',
      description: 'El gasto acumulado ya supera el ingreso disponible.'
    }
  }

  if (pending > Math.max(balance, income * 0.2)) {
    return {
      label: 'Vigilar',
      severity: 'warning',
      description: 'Los gastos pendientes pueden tensionar la liquidez.'
    }
  }

  return {
    label: 'Saludable',
    severity: 'success',
    description: 'Mantiene un margen estable y ejecucion controlada.'
  }
}

const getBudgetProgress = (budget) => {
  const income = budget.summary?.total_income || 0
  const expense = budget.summary?.total_expense || 0

  if (!income && !expense) {
    return 8
  }

  return Math.min(100, Math.max(8, Math.round((expense / Math.max(income, expense, 1)) * 100)))
}

const getBudgetProgressLabel = (budget) => {
  if (!budget.summary?.total_income && !budget.summary?.total_expense) {
    return 'Sin referencia'
  }

  return `${getBudgetProgress(budget)}%`
}

const getProgressTone = (budget) => {
  const tone = getBudgetHealth(budget).severity

  return {
    'is-danger': tone === 'danger',
    'is-warning': tone === 'warning',
    'is-success': tone === 'success'
  }
}

const getBudgetFooterHint = (budget) => {
  const balance = budget.summary?.balance || 0
  const pending = budget.summary?.pending_expense || 0

  if (balance < 0) {
    return 'Requiere correccion inmediata del margen.'
  }

  if (pending > 0) {
    return `${formatCurrency(pending)} pendientes de impacto.`
  }

  return 'Sin alertas operativas relevantes.'
}

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
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  animation: fadeIn 0.45s ease-in;
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

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.95fr);
  gap: 1.25rem;
  padding: 1.5rem;
  border-radius: 32px;
  background: var(--hero-gradient);
  border: 1px solid var(--surface-border);
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.hero-panel::after {
  content: '';
  position: absolute;
  inset: auto -6rem -6rem auto;
  width: 15rem;
  height: 15rem;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(15, 139, 111, 0.16) 0%, rgba(15, 139, 111, 0) 72%);
}

.hero-copy,
.hero-summary-panel {
  position: relative;
  z-index: 1;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.25rem;
}

.hero-kicker {
  display: inline-flex;
  width: fit-content;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.65);
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 700;
}

.dashboard-title {
  max-width: 12ch;
  font-size: clamp(2.25rem, 4vw, 3.6rem);
  font-weight: 800;
  color: var(--heading-color);
  letter-spacing: -0.04em;
}

.dashboard-subtitle {
  max-width: 60ch;
  font-size: 1.02rem;
  color: var(--text-color-secondary);
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.hero-primary-action {
  box-shadow: 0 18px 30px rgba(15, 139, 111, 0.22);
}

.hero-secondary-action {
  color: var(--text-color);
}

.hero-summary-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.hero-balance-card,
.hero-metric-tile {
  border: 1px solid rgba(124, 97, 61, 0.12);
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(12px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

.hero-balance-card {
  padding: 1.25rem;
  border-radius: 24px;
}

.panel-label {
  display: block;
  margin-bottom: 0.55rem;
  color: var(--text-color-secondary);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 700;
}

.hero-balance-value {
  display: block;
  font-size: clamp(2rem, 3vw, 2.8rem);
  letter-spacing: -0.04em;
  color: var(--heading-color);
}

.hero-balance-value.negative {
  color: var(--danger-color);
}

.hero-balance-card p {
  margin-top: 0.65rem;
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.hero-metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.hero-metric-tile {
  padding: 1rem;
  border-radius: 20px;
}

.hero-metric-tile span {
  display: block;
  font-size: 0.82rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.35rem;
}

.hero-metric-tile strong {
  font-size: 1.2rem;
  color: var(--heading-color);
}

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
  background: color-mix(in srgb, var(--surface-card) 84%, transparent);
  border: 1px solid var(--surface-border);
  border-radius: 28px;
  box-shadow: var(--shadow-sm);
}

.empty-state i {
  font-size: 4rem;
  color: var(--text-color-secondary);
  opacity: 0.5;
  margin-bottom: 1.5rem;
}

.empty-state h2 {
  font-size: 1.5rem;
  color: var(--heading-color);
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
  background: rgba(214, 69, 69, 0.08);
  border: 1px solid rgba(214, 69, 69, 0.16);
  border-radius: 20px;
  color: var(--danger-color);
}

.error-message i {
  font-size: 1.5rem;
}

.budgets-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: color-mix(in srgb, var(--surface-card) 86%, transparent);
  border-radius: 24px;
  padding: 1.4rem;
  border: 1px solid var(--surface-border);
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: rgba(15, 139, 111, 0.18);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
  color: white;
  background: linear-gradient(145deg, #0f8b6f 0%, #d97706 100%);
  box-shadow: 0 12px 24px rgba(15, 139, 111, 0.2);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--heading-color);
  margin-bottom: 0.2rem;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  font-weight: 500;
  margin: 0;
}

.stat-note {
  display: inline-block;
  margin-top: 0.55rem;
  font-size: 0.78rem;
  color: var(--text-color-soft);
}

.insight-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.insight-item {
  padding: 1.1rem 1.2rem;
  border-radius: 22px;
  background: color-mix(in srgb, var(--surface-card) 82%, transparent);
  border: 1px solid var(--surface-border);
  box-shadow: var(--shadow-sm);
}

.insight-label {
  display: block;
  margin-bottom: 0.4rem;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--text-color-secondary);
}

.insight-item strong {
  display: block;
  font-size: 1.35rem;
  color: var(--heading-color);
  margin-bottom: 0.25rem;
}

.insight-item p {
  color: var(--text-color-secondary);
  line-height: 1.55;
}

.budget-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.25rem;
}

.budget-card {
  border: 1px solid var(--surface-border);
  border-radius: 26px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.budget-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: rgba(15, 139, 111, 0.18);
}

.budget-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem 1.5rem 0.25rem;
  gap: 1rem;
}

.budget-heading {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.budget-avatar {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, #0f8b6f 0%, #d97706 100%);
  color: white;
  font-weight: 800;
  font-size: 1.05rem;
  flex-shrink: 0;
  box-shadow: 0 14px 24px rgba(15, 139, 111, 0.22);
}

.budget-info h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--heading-color);
  margin: 0.55rem 0 0.45rem;
}

.budget-status {
  margin-bottom: 0.1rem;
}

.budget-period {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.budget-summary {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.budget-balance-panel {
  padding: 1.1rem;
  border-radius: 22px;
  background: color-mix(in srgb, var(--surface-ground) 72%, transparent);
  border: 1px solid rgba(124, 97, 61, 0.1);
}

.budget-balance-value {
  display: block;
  margin-top: 0.15rem;
  font-size: 2rem;
  letter-spacing: -0.04em;
  color: var(--heading-color);
}

.budget-balance-value.negative {
  color: var(--danger-color);
}

.budget-balance-panel p {
  margin-top: 0.45rem;
  color: var(--text-color-secondary);
  line-height: 1.55;
}

.budget-progress-block {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.progress-meta strong {
  color: var(--heading-color);
}

.progress-track {
  height: 10px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--surface-hover) 88%, transparent);
  overflow: hidden;
}

.progress-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #0f8b6f 0%, #42bb9c 100%);
}

.progress-fill.is-warning {
  background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%);
}

.progress-fill.is-danger {
  background: linear-gradient(90deg, #d64545 0%, #ef4444 100%);
}

.budget-metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.budget-metric {
  padding: 0.95rem 1rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.58);
  border: 1px solid rgba(124, 97, 61, 0.08);
}

.budget-metric span {
  display: block;
  font-size: 0.8rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.3rem;
}

.budget-metric strong {
  font-size: 1rem;
  color: var(--heading-color);
}

.budget-inline-footer {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.summary-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.6rem 0.85rem;
  border-radius: 999px;
  background: rgba(15, 139, 111, 0.08);
  color: var(--primary-color);
  font-size: 0.84rem;
  font-weight: 600;
}

.muted-chip {
  background: rgba(107, 114, 128, 0.08);
  color: var(--text-color-secondary);
}

.budget-detail-button {
  box-shadow: 0 16px 28px rgba(15, 139, 111, 0.18);
}

.text-green {
  color: var(--success-color) !important;
}

.text-red {
  color: var(--danger-color) !important;
}

.text-orange {
  color: var(--warning-color) !important;
}

.w-full {
  width: 100%;
}

@media (max-width: 1100px) {
  .hero-panel {
    grid-template-columns: 1fr;
  }

  .insight-strip {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard {
    gap: 1rem;
  }

  .hero-panel {
    padding: 1.1rem;
    border-radius: 24px;
  }

  .dashboard-title {
    font-size: 2rem;
  }

  .stats-grid,
  .hero-metric-grid,
  .budget-metrics-grid,
  .budget-cards-grid {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-primary-action,
  .hero-secondary-action,
  .budget-detail-button {
    width: 100%;
  }

  .budget-card-header {
    flex-direction: column;
  }

  .summary-chip {
    width: 100%;
    justify-content: center;
  }
}
</style>
