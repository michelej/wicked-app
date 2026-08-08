<template>
  <section class="mobile-budget-list">
    <article
      v-for="item in items"
      :key="item.id"
      class="mobile-budget-item"
      tabindex="0"
      role="button"
      @click="selectBudget(item.id)"
      @keydown.enter.prevent="selectBudget(item.id)"
      @keydown.space.prevent="selectBudget(item.id)"
    >
      <div class="mobile-budget-main-row">
        <div class="mobile-budget-copy">
          <div class="mobile-budget-title-row">
            <strong>{{ item.name }}</strong>
            <span class="mobile-health-pill" :class="`is-${item.healthTone}`">{{ item.healthLabel }}</span>
          </div>

          <div class="mobile-budget-meta-row">
            <span>{{ item.period }}</span>
            <span>{{ item.bankLabel }}</span>
          </div>
        </div>

        <div class="mobile-budget-balance">
          <span>Restante</span>
          <strong :class="{ 'is-negative': item.remaining < 0, 'is-positive': item.remaining >= 0 }">
            {{ formatCurrency(item.remaining) }}
          </strong>
        </div>
      </div>

      <div class="mobile-budget-progress-meta">
        <span>Plan {{ formatCurrency(item.planned) }}</span>
        <strong :class="`is-${item.progressTone}`">{{ item.progressLabel }}</strong>
      </div>

      <div class="mobile-budget-progress-bar">
        <div class="mobile-budget-progress-fill" :class="`is-${item.progressTone}`" :style="{ width: `${item.progressWidth}%` }"></div>
      </div>

      <div class="mobile-budget-metrics-row">
        <div class="mobile-budget-metric">
          <strong>{{ formatCurrency(item.planned) }}</strong>
          <span>Planificado</span>
        </div>
        <div class="mobile-budget-metric">
          <strong>{{ formatCurrency(item.spent) }}</strong>
          <span>Gastado</span>
        </div>
        <div class="mobile-budget-metric">
          <strong>{{ item.categoriesCount }}</strong>
          <span>Categorías</span>
        </div>
      </div>

      <Button
        label="Ver detalles"
        icon="pi pi-eye"
        size="small"
        text
        class="mobile-budget-detail-button"
        @click.stop="selectBudget(item.id)"
      />
    </article>
  </section>
</template>

<script setup>
import { useFormatters } from '@/composables/useFormatters'

defineProps({
  items: {
    type: Array,
    default: () => []
  }
})

const { formatCurrency } = useFormatters()

const emit = defineEmits(['view-budget'])

const selectBudget = (budgetId) => {
  emit('view-budget', budgetId)
}
</script>

<style scoped>
.mobile-budget-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mobile-budget-item {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding: 0.85rem 0.95rem;
  border: 1px solid var(--surface-border);
  border-radius: 22px;
  background: color-mix(in srgb, var(--surface-card) 90%, transparent);
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.07);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.mobile-budget-item:focus-visible {
  outline: 2px solid color-mix(in srgb, var(--primary-color) 75%, white);
  outline-offset: 2px;
}

.mobile-budget-item:active {
  transform: scale(0.992);
}

.mobile-budget-item:hover,
.mobile-budget-item:focus-visible {
  border-color: color-mix(in srgb, var(--primary-color) 24%, var(--surface-border));
  box-shadow: 0 16px 30px rgba(15, 23, 42, 0.1);
}

.mobile-budget-main-row,
.mobile-budget-title-row,
.mobile-budget-progress-meta,
.mobile-budget-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.mobile-budget-copy {
  min-width: 0;
  flex: 1;
}

.mobile-budget-title-row strong,
.mobile-budget-balance strong,
.mobile-budget-metric strong {
  color: var(--heading-color);
}

.mobile-budget-title-row strong {
  display: block;
  min-width: 0;
  font-size: 1rem;
  line-height: 1.15;
}

.mobile-budget-meta-row,
.mobile-budget-progress-meta span,
.mobile-budget-balance span,
.mobile-budget-metric span {
  color: var(--text-color-secondary);
}

.mobile-budget-meta-row {
  margin-top: 0.24rem;
  font-size: 0.72rem;
}

.mobile-health-pill {
  flex-shrink: 0;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.66rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.mobile-health-pill.is-success {
  background: rgba(16, 185, 129, 0.12);
  color: #0f8b6f;
}

.mobile-health-pill.is-warning {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
}

.mobile-health-pill.is-danger {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

.mobile-health-pill.is-muted {
  background: rgba(148, 163, 184, 0.14);
  color: #64748b;
}

.mobile-budget-balance {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.1rem;
}

.mobile-budget-balance span,
.mobile-budget-metric span {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.mobile-budget-balance strong {
  font-size: 0.95rem;
  line-height: 1.1;
}

.mobile-budget-balance strong.is-positive {
  color: #0f8b6f;
}

.mobile-budget-balance strong.is-negative {
  color: #ef4444;
}

.mobile-budget-progress-meta {
  font-size: 0.74rem;
}

.mobile-budget-progress-meta strong.is-healthy {
  color: #0f8b6f;
}

.mobile-budget-progress-meta strong.is-warning {
  color: #d97706;
}

.mobile-budget-progress-meta strong.is-danger {
  color: #ef4444;
}

.mobile-budget-progress-meta strong.is-neutral {
  color: #64748b;
}

.mobile-budget-progress-bar {
  width: 100%;
  height: 0.42rem;
  background: rgba(148, 163, 184, 0.18);
  border-radius: 999px;
  overflow: hidden;
}

.mobile-budget-progress-fill {
  height: 100%;
}

.mobile-budget-progress-fill.is-healthy {
  background: #10b981;
}

.mobile-budget-progress-fill.is-warning {
  background: #f59e0b;
}

.mobile-budget-progress-fill.is-danger {
  background: #ef4444;
}

.mobile-budget-progress-fill.is-neutral {
  background: #94a3b8;
}

.mobile-budget-metrics-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
}

.mobile-budget-metric strong {
  display: block;
  font-size: 0.88rem;
  line-height: 1.1;
}

.mobile-budget-detail-button {
  justify-content: flex-start;
  padding-left: 0;
}
</style>
