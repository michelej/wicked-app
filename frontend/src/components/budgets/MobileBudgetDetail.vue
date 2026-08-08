<template>
  <section class="mobile-budget-detail">
    <div class="mobile-budget-header">
      <Button
        label="Presupuestos"
        icon="pi pi-arrow-left"
        text
        size="small"
        class="mobile-back-button"
        @click="goBack"
      />

      <div class="mobile-budget-title-block">
        <h1>{{ budget.name }}</h1>
        <p>{{ formatDate(budget.start_date) }} - {{ formatDate(budget.end_date) }}</p>
      </div>
    </div>

    <section class="mobile-budget-summary">
      <div class="mobile-summary-grid">
        <div class="mobile-summary-item">
          <span>Planificado</span>
          <strong>{{ formatCurrency(summaryTotals.planned) }}</strong>
        </div>
        <div class="mobile-summary-item">
          <span>Gastado</span>
          <strong>{{ formatCurrency(summaryTotals.spent) }}</strong>
        </div>
        <div class="mobile-summary-item">
          <span>Restante</span>
          <strong :class="{ 'is-negative': summaryTotals.remaining < 0, 'is-positive': summaryTotals.remaining >= 0 }">
            {{ formatCurrency(summaryTotals.remaining) }}
          </strong>
        </div>
      </div>

      <div class="mobile-summary-progress">
        <div class="mobile-progress-meta">
          <span>Progreso global</span>
          <strong>{{ summaryProgressLabel }}</strong>
        </div>
        <div class="mobile-progress-bar">
          <div class="mobile-progress-fill" :class="`is-${summaryProgressTone}`" :style="{ width: `${summaryProgressWidth}%` }"></div>
        </div>
      </div>
    </section>

    <section class="mobile-categories-section">
      <div class="mobile-section-heading">
        <h2>Categorías</h2>
        <span>{{ budgetItems.length }}</span>
      </div>

      <div v-if="budgetItems.length === 0" class="mobile-empty-state">
        Este presupuesto todavía no tiene categorías.
      </div>

      <div v-else class="mobile-category-list">
        <article v-for="item in budgetItems" :key="item.key" class="mobile-category-row">
          <div class="mobile-category-top-row">
            <strong class="mobile-category-name">{{ item.category }}</strong>
            <div class="mobile-category-status" :class="`is-${item.stateTone}`">
              <span>{{ item.progressLabel }}</span>
              <small>{{ item.stateLabel }}</small>
            </div>
          </div>

          <div class="mobile-category-progress-bar">
            <div class="mobile-category-progress-fill" :class="`is-${item.stateTone}`" :style="{ width: `${item.progressWidth}%` }"></div>
          </div>

          <div class="mobile-category-metrics">
            <div class="mobile-category-metric">
              <strong>{{ formatCurrency(item.plannedAmount) }}</strong>
              <span>Plan</span>
            </div>
            <div class="mobile-category-metric">
              <strong>{{ formatCurrency(item.spentAmount) }}</strong>
              <span>Gastado</span>
            </div>
            <div class="mobile-category-metric">
              <strong :class="{ 'is-negative': item.remainingAmount < 0, 'is-positive': item.remainingAmount >= 0 }">
                {{ formatCurrency(item.remainingAmount) }}
              </strong>
              <span>Restante</span>
            </div>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useFormatters } from '@/composables/useFormatters'

const props = defineProps({
  budget: {
    type: Object,
    required: true
  },
  summaryTotals: {
    type: Object,
    required: true
  },
  budgetItems: {
    type: Array,
    default: () => []
  }
})

const router = useRouter()
const { formatCurrency, formatDate } = useFormatters()

const summaryProgressPercentage = computed(() => {
  const planned = Number(props.summaryTotals?.planned || 0)
  const spent = Number(props.summaryTotals?.spent || 0)

  if (planned <= 0) {
    return spent > 0 ? null : 0
  }

  return (spent / planned) * 100
})

const summaryProgressWidth = computed(() => {
  if (summaryProgressPercentage.value === null) {
    return props.summaryTotals?.spent > 0 ? 100 : 0
  }

  return Math.max(Math.min(summaryProgressPercentage.value, 100), 0)
})

const summaryProgressLabel = computed(() => {
  if (summaryProgressPercentage.value === null) {
    return props.summaryTotals?.spent > 0 ? 'Sin plan' : '0%'
  }

  return `${summaryProgressPercentage.value.toFixed(0)}%`
})

const summaryProgressTone = computed(() => {
  if (props.summaryTotals?.remaining < 0) {
    return 'danger'
  }

  if (summaryProgressPercentage.value === null) {
    return props.summaryTotals?.spent > 0 ? 'danger' : 'neutral'
  }

  if (summaryProgressPercentage.value >= 100) {
    return 'danger'
  }

  if (summaryProgressPercentage.value >= 80) {
    return 'warning'
  }

  return 'healthy'
})

const goBack = () => {
  router.push({ name: 'budgets' })
}
</script>

<style scoped>
.mobile-budget-detail {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.mobile-budget-header,
.mobile-budget-summary,
.mobile-categories-section {
  border: 1px solid var(--surface-border);
  border-radius: 24px;
  background: color-mix(in srgb, var(--surface-card) 90%, transparent);
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.08);
}

.mobile-budget-header {
  padding: 0.85rem 0.95rem 0.95rem;
  background:
    radial-gradient(circle at top right, rgba(214, 145, 65, 0.14), transparent 30%),
    radial-gradient(circle at left bottom, rgba(15, 139, 111, 0.12), transparent 24%),
    linear-gradient(145deg, rgba(255, 251, 244, 0.96) 0%, rgba(241, 247, 245, 0.96) 100%);
}

.mobile-back-button {
  margin: -0.25rem 0 0.25rem -0.5rem;
}

.mobile-budget-title-block h1 {
  margin: 0;
  font-size: 1.4rem;
  line-height: 1.05;
  letter-spacing: -0.03em;
  color: var(--heading-color);
}

.mobile-budget-title-block p {
  margin: 0.35rem 0 0;
  color: var(--text-color-secondary);
  font-size: 0.82rem;
}

.mobile-budget-summary {
  padding: 0.95rem;
}

.mobile-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
}

.mobile-summary-item {
  min-width: 0;
}

.mobile-summary-item span,
.mobile-category-metric span,
.mobile-progress-meta span,
.mobile-category-status small,
.mobile-budget-title-block p,
.mobile-section-heading span,
.mobile-empty-state {
  color: var(--text-color-secondary);
}

.mobile-summary-item span,
.mobile-category-metric span {
  display: block;
  margin-top: 0.15rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.mobile-summary-item strong,
.mobile-category-metric strong {
  display: block;
  font-size: 0.96rem;
  line-height: 1.1;
  color: var(--heading-color);
}

.mobile-summary-item strong.is-negative,
.mobile-category-metric strong.is-negative {
  color: #ef4444;
}

.mobile-summary-item strong.is-positive,
.mobile-category-metric strong.is-positive {
  color: #0f8b6f;
}

.mobile-summary-progress {
  margin-top: 0.9rem;
}

.mobile-progress-meta,
.mobile-category-top-row,
.mobile-section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.mobile-progress-meta strong,
.mobile-section-heading h2,
.mobile-category-name {
  color: var(--heading-color);
}

.mobile-progress-meta strong {
  font-size: 0.8rem;
}

.mobile-progress-bar,
.mobile-category-progress-bar {
  width: 100%;
  height: 0.42rem;
  margin-top: 0.45rem;
  background: rgba(148, 163, 184, 0.18);
  border-radius: 999px;
  overflow: hidden;
}

.mobile-progress-fill,
.mobile-category-progress-fill {
  height: 100%;
  border-radius: inherit;
}

.mobile-progress-fill.is-healthy,
.mobile-category-progress-fill.is-healthy {
  background: #10b981;
}

.mobile-progress-fill.is-warning,
.mobile-category-progress-fill.is-warning {
  background: #f59e0b;
}

.mobile-progress-fill.is-danger,
.mobile-category-progress-fill.is-danger {
  background: #ef4444;
}

.mobile-progress-fill.is-neutral,
.mobile-category-progress-fill.is-neutral {
  background: #94a3b8;
}

.mobile-categories-section {
  padding: 0.95rem;
}

.mobile-section-heading {
  margin-bottom: 0.35rem;
}

.mobile-section-heading h2 {
  margin: 0;
  font-size: 0.95rem;
}

.mobile-section-heading span {
  font-size: 0.78rem;
  font-weight: 700;
}

.mobile-empty-state {
  padding: 0.85rem 0 0.2rem;
  font-size: 0.88rem;
}

.mobile-category-list {
  display: flex;
  flex-direction: column;
}

.mobile-category-row {
  padding: 0.8rem 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
}

.mobile-category-row:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.mobile-category-row:first-child {
  padding-top: 0.65rem;
}

.mobile-category-name {
  font-size: 0.95rem;
  line-height: 1.2;
}

.mobile-category-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: fit-content;
}

.mobile-category-status span {
  font-size: 0.84rem;
  font-weight: 700;
}

.mobile-category-status small {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.mobile-category-status.is-healthy span,
.mobile-category-status.is-healthy small {
  color: #0f8b6f;
}

.mobile-category-status.is-warning span,
.mobile-category-status.is-warning small {
  color: #d97706;
}

.mobile-category-status.is-danger span,
.mobile-category-status.is-danger small {
  color: #ef4444;
}

.mobile-category-status.is-neutral span,
.mobile-category-status.is-neutral small {
  color: #64748b;
}

.mobile-category-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
  margin-top: 0.55rem;
}
</style>
