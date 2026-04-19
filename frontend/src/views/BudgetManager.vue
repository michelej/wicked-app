<template>
  <div class="budget-manager">
    <section class="budget-toolbar">
      <div class="toolbar-row">
        <div class="toolbar-copy">
          <span class="section-kicker">Presupuestos</span>
          <h1 class="page-title">Presupuestos</h1>
        </div>

        <Button
          label="Planificar mes siguiente"
          icon="pi pi-calendar"
          severity="secondary"
          outlined
          class="toolbar-secondary-action"
          @click="router.push({ name: 'next-month-planner-setup' })"
        />

        <Button
          label="Nuevo Presupuesto"
          icon="pi pi-plus"
          severity="success"
          class="toolbar-primary-action"
          @click="showCreateDialog = true"
        />
      </div>

      <div class="toolbar-row toolbar-row-secondary">
        <div class="status-tabs">
          <Button
            :label="`Activos (${budgetStore.activeBudgets.length})`"
            :severity="currentTab === 'active' ? 'primary' : 'secondary'"
            :outlined="currentTab !== 'active'"
            @click="currentTab = 'active'"
          />
          <Button
            :label="`Cerrados (${budgetStore.closedBudgets.length})`"
            :severity="currentTab === 'closed' ? 'primary' : 'secondary'"
            :outlined="currentTab !== 'closed'"
            @click="currentTab = 'closed'"
          />
          <Button
            :label="`Borradores (${budgetStore.draftBudgets.length})`"
            :severity="currentTab === 'draft' ? 'primary' : 'secondary'"
            :outlined="currentTab !== 'draft'"
            @click="currentTab = 'draft'"
          />
        </div>

        <div class="toolbar-metrics">
          <div class="toolbar-metric">
            <span>Visibles</span>
            <strong>{{ filteredBudgets.length }}</strong>
          </div>
          <div class="toolbar-metric">
            <span>Balance</span>
            <strong :class="{ negative: visibleBalanceTotal < 0 }">{{ formatCurrency(visibleBalanceTotal) }}</strong>
          </div>
          <div class="toolbar-metric">
            <span>Planificado</span>
            <strong>{{ formatCurrency(visiblePlannedTotal) }}</strong>
          </div>
          <div class="toolbar-metric">
            <span>Categorias</span>
            <strong>{{ plannedCategoriesCount }}</strong>
          </div>
        </div>
      </div>
    </section>

    <div v-if="budgetStore.loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando presupuestos...</p>
    </div>

    <div v-else-if="budgetStore.error" class="error-message">
      <i class="pi pi-exclamation-circle"></i>
      {{ budgetStore.error }}
    </div>

    <div v-else-if="filteredBudgets.length === 0" class="empty-state">
      <i class="pi pi-wallet"></i>
      <h2>No hay presupuestos {{ currentTab === 'active' ? 'activos' : currentTab === 'closed' ? 'cerrados' : 'en borrador' }}</h2>
      <p>{{ currentTab === 'active' ? 'Crea tu primer presupuesto activo' : 'No tienes presupuestos en esta categoría' }}</p>
      <Button
        v-if="currentTab === 'active'"
        label="Crear Presupuesto"
        icon="pi pi-plus"
        @click="showCreateDialog = true"
        severity="success"
      />
    </div>

    <div v-else class="budgets-list">
      <Card
        v-for="budget in filteredBudgets"
        :key="budget._id"
        class="budget-item"
        :style="getBudgetBankStyle(budget)"
      >
        <template #header>
          <div class="budget-header">
            <div class="budget-heading">
              <div class="budget-avatar">{{ getBudgetBankBrand(budget).logoText }}</div>

              <div class="budget-info">
                <div class="budget-meta-top">
                  <span class="budget-bank-pill">
                    <span class="budget-bank-dot"></span>
                    {{ getBudgetBankBrand(budget).label }}
                  </span>
                  <Tag
                    :value="formatBudgetStatus(budget.status).label"
                    :severity="formatBudgetStatus(budget.status).severity"
                  />
                  <span class="budget-health" :class="`is-${getBudgetHealth(budget).tone}`">
                    {{ getBudgetHealth(budget).label }}
                  </span>
                </div>

                <h3>{{ budget.name }}</h3>

                <div class="budget-meta">
                  <span class="budget-period">
                    <i class="pi pi-calendar"></i>
                    {{ formatDate(budget.start_date) }} - {{ formatDate(budget.end_date) }}
                  </span>
                  <span class="budget-period">
                    <i class="pi pi-bookmark"></i>
                    {{ budget.budget_month || 'Sin mes asignado' }}
                  </span>
                </div>
              </div>
            </div>

            <div class="budget-balance-panel">
              <span>Balance</span>
              <strong :class="{ 'text-green': (budget.summary?.balance || 0) >= 0, 'text-red': (budget.summary?.balance || 0) < 0 }">
                {{ formatCurrency(budget.summary?.balance || 0) }}
              </strong>
              <small>{{ getBudgetHealth(budget).description }}</small>
            </div>
          </div>
        </template>

        <template #content>
          <div class="budget-summary">
            <div class="summary-grid">
              <div class="summary-item emphasis-item">
                <span class="summary-label">Transacciones</span>
                <span class="summary-value">{{ budget.summary?.transactions_count || 0 }}</span>
              </div>

              <div class="summary-item">
                <span class="summary-label text-green">
                  <i class="pi pi-arrow-down"></i>
                  Ingresos
                </span>
                <span class="summary-value text-green">{{ formatCurrency(budget.summary?.total_income || 0) }}</span>
              </div>

              <div class="summary-item">
                <span class="summary-label text-red">
                  <i class="pi pi-arrow-up"></i>
                  Gastos
                </span>
                <span class="summary-value text-red">{{ formatCurrency(budget.summary?.total_expense || 0) }}</span>
              </div>

              <div class="summary-item" v-if="budget.budget_items && budget.budget_items.length > 0">
                <span class="summary-label">
                  <i class="pi pi-money-bill"></i>
                  Total planificado
                </span>
                <span class="summary-value">{{ formatCurrency(calculateTotalPlanned(budget.budget_items)) }}</span>
              </div>

              <div class="summary-item" v-if="budget.budget_items && budget.budget_items.length > 0">
                <span class="summary-label">
                  <i class="pi pi-list"></i>
                  Categorias planificadas
                </span>
                <span class="summary-value">{{ budget.budget_items.length }}</span>
              </div>

              <div class="summary-item empty-plan-item" v-else>
                <span class="summary-label">
                  <i class="pi pi-folder-open"></i>
                  Planificacion
                </span>
                <span class="summary-value">Sin categorias definidas</span>
              </div>
            </div>
          </div>
        </template>

        <template #footer>
          <div class="budget-actions">
            <Button
              label="Ver Detalles"
              icon="pi pi-eye"
              size="small"
              class="budget-detail-button"
              @click.stop="viewBudget(budget._id)"
            />

            <div class="budget-actions-grid">
              <Button
                label="Editar"
                icon="pi pi-pencil"
                size="small"
                severity="secondary"
                outlined
                @click.stop="editBudget(budget)"
                v-tooltip.top="'Editar presupuesto y categorías'"
              />
              <Button
                label="Categorías"
                icon="pi pi-tags"
                size="small"
                severity="info"
                outlined
                @click.stop="editBudget(budget)"
                v-tooltip.top="'Editar categorías y montos planificados'"
              />
              <Button
                v-if="budget.status === 'active' || budget.status === 'closed'"
                :label="budget.status === 'active' ? 'Cerrar' : 'Abrir'"
                :icon="budget.status === 'active' ? 'pi pi-lock' : 'pi pi-lock-open'"
                size="small"
                :severity="budget.status === 'active' ? 'warning' : 'success'"
                outlined
                @click.stop="toggleBudgetStatus(budget)"
              />
              <Button
                label="Eliminar"
                icon="pi pi-trash"
                size="small"
                severity="danger"
                text
                @click.stop="confirmDeleteBudget(budget)"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>

    <Dialog
      v-model:visible="showCreateDialog"
      modal
      :header="editingBudget ? 'Editar Presupuesto' : 'Crear Presupuesto'"
      :style="{ width: '600px' }"
      class="budget-dialog"
    >
      <div class="dialog-content">
        <div class="form-field">
          <label for="budgetName">Nombre del Presupuesto *</label>
          <InputText
            id="budgetName"
            v-model="budgetForm.name"
            placeholder="ej. Presupuesto Marzo 2026"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="budgetBank">Banco *</label>
          <Select
            id="budgetBank"
            v-model="budgetForm.bank"
            :options="budgetBankOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Selecciona banco"
            class="w-full"
          >
            <template #option="{ option }">
              <div class="bank-option-row">
                <span class="bank-option-logo">{{ option.shortLabel }}</span>
                <span>{{ option.label }}</span>
              </div>
            </template>
          </Select>
        </div>

        <div class="form-row">
          <div class="form-field">
            <label for="startDate">Fecha Inicio *</label>
            <Calendar
              id="startDate"
              v-model="budgetForm.start_date"
              dateFormat="dd/mm/yy"
              placeholder="Selecciona fecha"
              class="w-full"
            />
          </div>
          <div class="form-field">
            <label for="endDate">Fecha Fin *</label>
            <Calendar
              id="endDate"
              v-model="budgetForm.end_date"
              dateFormat="dd/mm/yy"
              placeholder="Selecciona fecha"
              class="w-full"
            />
          </div>
        </div>

        <div class="form-field">
          <label for="status">Estado *</label>
          <Select
            id="status"
            v-model="budgetForm.status"
            :options="statusOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Selecciona estado"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="budgetMonth">Mes del Presupuesto *</label>
          <InputText
            id="budgetMonth"
            v-model="budgetForm.budget_month"
            placeholder="ej. Marzo-2026"
            class="w-full"
          />
          <small class="form-help">Formato: Mes-Año (ej. Marzo-2026)</small>
        </div>

        <div class="budget-items-section">
          <div class="section-header">
            <div>
              <span class="section-kicker">Planificacion</span>
              <h4>Items del Presupuesto</h4>
            </div>
            <Button
              label="Agregar Categoría"
              icon="pi pi-plus"
              size="small"
              text
              @click="addBudgetItem"
            />
          </div>

          <div v-if="budgetForm.budget_items.length === 0" class="empty-items">
            <p>No hay categorías agregadas. Agrega categorías con sus montos planificados.</p>
          </div>

          <div v-else class="budget-items-list">
            <Card
              v-for="(item, index) in budgetForm.budget_items"
              :key="index"
              class="budget-item-card"
            >
              <template #content>
                <div class="item-form">
                  <div class="form-row item-row">
                    <div class="form-group flex-2">
                      <label>Categoría *</label>
                      <Select
                        v-model="item.category"
                        :options="categoryStore.sortedExpenseCategories"
                        optionLabel="name"
                        optionValue="name"
                        placeholder="Seleccionar categoría"
                        filter
                      >
                        <template #option="{ option }">
                          <div class="category-option">
                            <span v-if="option.parent_id" class="subcategory-indicator">↳</span>
                            <i :class="normalizeIcon(option.icon)" :style="{ color: option.color }"></i>
                            <span>{{ option.name }}</span>
                          </div>
                        </template>
                      </Select>
                    </div>

                    <div class="form-group">
                      <label>Monto Planificado *</label>
                      <InputNumber
                        v-model="item.planned_amount"
                        mode="currency"
                        currency="EUR"
                        locale="es-ES"
                        :minFractionDigits="2"
                        :maxFractionDigits="2"
                        placeholder="0,00 €"
                      />
                    </div>

                    <div class="form-group-actions">
                      <Button
                        icon="pi pi-trash"
                        severity="danger"
                        text
                        @click="removeBudgetItem(index)"
                      />
                    </div>
                  </div>
                </div>
              </template>
            </Card>
          </div>

          <div v-if="budgetForm.budget_items.length > 0" class="total-planned">
            <span class="label">Total Planificado:</span>
            <span class="value">{{ formatCurrency(totalPlanned) }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          label="Cancelar"
          text
          @click="closeDialog"
        />
        <Button
          :label="editingBudget ? 'Actualizar' : 'Crear'"
          icon="pi pi-check"
          @click="saveBudget"
          :loading="budgetStore.loading"
          severity="success"
        />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="showDeleteDialog"
      modal
      header="Confirmar Eliminación"
      :style="{ width: '450px' }"
    >
      <p>¿Estás seguro de que deseas eliminar el presupuesto "{{ budgetToDelete?.name }}"?</p>
      <p v-if="budgetToDelete?.summary?.transactions_count > 0" class="warning-text">
        <i class="pi pi-exclamation-triangle"></i>
        Este presupuesto tiene {{ budgetToDelete.summary.transactions_count }} transacciones asociadas.
      </p>

      <template #footer>
        <Button
          label="Cancelar"
          text
          @click="showDeleteDialog = false"
        />
        <Button
          label="Eliminar"
          icon="pi pi-trash"
          @click="deleteBudget"
          :loading="budgetStore.loading"
          severity="danger"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBudgetStore } from '@/stores/budgets'
import { useCategoryStore } from '@/stores/categories'
import { useFormatters } from '@/composables/useFormatters'
import { BUDGET_BANK_OPTIONS, getBankBrand } from '@/constants/banks'
import { useToast } from 'primevue/usetoast'
import ProgressSpinner from 'primevue/progressspinner'
import Calendar from 'primevue/calendar'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import InputNumber from 'primevue/inputnumber'

const router = useRouter()
const budgetStore = useBudgetStore()
const categoryStore = useCategoryStore()
const toast = useToast()
const { formatCurrency, formatDate, formatBudgetStatus } = useFormatters()
const budgetBankOptions = BUDGET_BANK_OPTIONS

const defaultBudgetForm = () => ({
  name: '',
  bank: null,
  start_date: null,
  end_date: null,
  budget_month: '',
  budget_items: [],
  status: 'active'
})

const normalizeIcon = (icon) => {
  if (!icon) return 'pi pi-tag'
  if (icon.startsWith('pi pi-')) return icon
  if (icon.startsWith('pi-')) return `pi ${icon}`
  return `pi pi-${icon}`
}

const calculateTotalPlanned = (budgetItems) => {
  if (!budgetItems || budgetItems.length === 0) return 0
  return budgetItems.reduce((sum, item) => {
    return sum + (parseFloat(item.planned_amount) || 0)
  }, 0)
}

const currentTab = ref('active')
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const editingBudget = ref(null)
const budgetToDelete = ref(null)

const budgetForm = ref(defaultBudgetForm())

const statusOptions = [
  { label: 'Activo', value: 'active' },
  { label: 'Cerrado', value: 'closed' },
  { label: 'Borrador', value: 'draft' }
]

const filteredBudgets = computed(() => {
  const budgets = currentTab.value === 'active'
    ? budgetStore.activeBudgets
    : currentTab.value === 'closed'
      ? budgetStore.closedBudgets
      : budgetStore.draftBudgets

  return budgets
    .map((budget) => ({
      ...budget,
      summary: budgetStore.budgetSummaries[budget._id]
    }))
    .sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
})

const totalPlanned = computed(() => {
  return budgetForm.value.budget_items.reduce((sum, item) => {
    return sum + (parseFloat(item.planned_amount) || 0)
  }, 0)
})

const visibleBalanceTotal = computed(() => {
  return filteredBudgets.value.reduce((sum, budget) => sum + (budget.summary?.balance || 0), 0)
})

const visiblePlannedTotal = computed(() => {
  return filteredBudgets.value.reduce((sum, budget) => sum + calculateTotalPlanned(budget.budget_items), 0)
})

const plannedCategoriesCount = computed(() => {
  return filteredBudgets.value.reduce((sum, budget) => sum + (budget.budget_items?.length || 0), 0)
})

onMounted(async () => {
  await Promise.all([
    budgetStore.fetchBudgets(),
    categoryStore.fetchCategories()
  ])

  for (const budget of budgetStore.budgets) {
    await budgetStore.getBudgetSummary(budget._id)
  }
})

const getBudgetBankBrand = (budget) => getBankBrand(budget?.bank)

const getBudgetBankStyle = (budget) => {
  const brand = getBudgetBankBrand(budget)

  return {
    '--budget-bank-accent': brand.accent,
    '--budget-bank-accent-soft': brand.accentSoft,
    '--budget-bank-surface': brand.surface,
    '--budget-bank-shadow': brand.shadow,
    '--budget-bank-glow': brand.glow,
    '--budget-bank-pill-bg': brand.pillBackground,
    '--budget-bank-pill-color': brand.pillColor
  }
}

const getBudgetHealth = (budget) => {
  const balance = budget.summary?.balance || 0
  const planned = calculateTotalPlanned(budget.budget_items)
  const transactions = budget.summary?.transactions_count || 0

  if (balance < 0) {
    return {
      tone: 'danger',
      label: 'En riesgo',
      description: 'El gasto ejecutado ya presiona el margen disponible.'
    }
  }

  if (transactions === 0 && planned === 0) {
    return {
      tone: 'muted',
      label: 'Sin movimiento',
      description: 'Aun no hay actividad ni planificacion cargada.'
    }
  }

  if (planned > 0 && Math.abs(balance) <= planned * 0.15) {
    return {
      tone: 'warning',
      label: 'Ajustado',
      description: 'Conviene vigilar el margen restante del presupuesto.'
    }
  }

  return {
    tone: 'success',
    label: 'Saludable',
    description: 'Mantiene un comportamiento estable y controlado.'
  }
}

const addBudgetItem = () => {
  budgetForm.value.budget_items.push({
    category: '',
    planned_amount: 0
  })
}

const removeBudgetItem = (index) => {
  budgetForm.value.budget_items.splice(index, 1)
}

const viewBudget = (budgetId) => {
  router.push(`/budgets/${budgetId}`)
}

const editBudget = (budget) => {
  editingBudget.value = budget
  budgetForm.value = {
    name: budget.name,
    bank: budget.bank || null,
    start_date: new Date(budget.start_date),
    end_date: new Date(budget.end_date),
    budget_month: budget.budget_month || '',
    budget_items: budget.budget_items || [],
    status: budget.status
  }
  showCreateDialog.value = true
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingBudget.value = null
  budgetForm.value = defaultBudgetForm()
}

const saveBudget = async () => {
  if (!budgetForm.value.name || !budgetForm.value.bank || !budgetForm.value.start_date || !budgetForm.value.end_date || !budgetForm.value.budget_month) {
    toast.add({
      severity: 'warn',
      summary: 'Campos requeridos',
      detail: 'Por favor completa todos los campos',
      life: 3000
    })
    return
  }

  const monthPattern = /^[A-Za-z]+-\d{4}$/
  if (!monthPattern.test(budgetForm.value.budget_month)) {
    toast.add({
      severity: 'warn',
      summary: 'Formato inválido',
      detail: 'El mes del presupuesto debe tener formato "Mes-Año" (ej. Marzo-2026)',
      life: 3000
    })
    return
  }

  try {
    if (editingBudget.value) {
      await budgetStore.updateBudget(editingBudget.value._id, {
        name: budgetForm.value.name,
        bank: budgetForm.value.bank,
        start_date: budgetForm.value.start_date.toISOString(),
        end_date: budgetForm.value.end_date.toISOString(),
        budget_month: budgetForm.value.budget_month,
        status: budgetForm.value.status,
        budget_items: budgetForm.value.budget_items
      })
      toast.add({
        severity: 'success',
        summary: 'Presupuesto actualizado',
        detail: 'El presupuesto se ha actualizado correctamente',
        life: 3000
      })
    } else {
      await budgetStore.createBudget({
        name: budgetForm.value.name,
        bank: budgetForm.value.bank,
        start_date: budgetForm.value.start_date.toISOString(),
        end_date: budgetForm.value.end_date.toISOString(),
        budget_month: budgetForm.value.budget_month,
        status: budgetForm.value.status,
        budget_items: budgetForm.value.budget_items
      })
      toast.add({
        severity: 'success',
        summary: 'Presupuesto creado',
        detail: 'El presupuesto se ha creado correctamente',
        life: 3000
      })
    }
    closeDialog()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo guardar el presupuesto',
      life: 3000
    })
  }
}

const toggleBudgetStatus = async (budget) => {
  const nextStatus = budget.status === 'closed' ? 'active' : 'closed'
  const actionLabel = nextStatus === 'closed' ? 'cerrado' : 'abierto'

  try {
    await budgetStore.updateBudget(budget._id, {
      status: nextStatus
    })

    toast.add({
      severity: 'success',
      summary: `Presupuesto ${actionLabel}`,
      detail: `"${budget.name}" ahora está ${actionLabel}.`,
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `No se pudo ${nextStatus === 'closed' ? 'cerrar' : 'abrir'} el presupuesto`,
      life: 3000
    })
  }
}

const confirmDeleteBudget = (budget) => {
  budgetToDelete.value = budget
  showDeleteDialog.value = true
}

const deleteBudget = async () => {
  try {
    await budgetStore.deleteBudget(budgetToDelete.value._id)
    toast.add({
      severity: 'success',
      summary: 'Presupuesto eliminado',
      detail: 'El presupuesto se ha eliminado correctamente',
      life: 3000
    })
    showDeleteDialog.value = false
    budgetToDelete.value = null
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo eliminar el presupuesto',
      life: 3000
    })
  }
}
</script>

<style scoped>
.budget-manager {
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

.budget-toolbar,
.empty-state,
.budget-item {
  border: 1px solid var(--surface-border);
  box-shadow: var(--shadow-sm);
}

.budget-toolbar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem 1.15rem;
  border-radius: 24px;
  background: color-mix(in srgb, var(--surface-card) 88%, transparent);
}

.toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.toolbar-row-secondary {
  align-items: flex-start;
}

.toolbar-copy {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.section-kicker {
  display: inline-flex;
  width: fit-content;
  padding: 0.28rem 0.65rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--surface-ground) 74%, transparent);
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 700;
}

.page-title {
  margin: 0;
  font-size: clamp(1.45rem, 2.4vw, 2rem);
  font-weight: 700;
  color: var(--heading-color);
  letter-spacing: -0.03em;
}

.status-tabs {
  display: flex;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.toolbar-primary-action {
  box-shadow: 0 14px 26px rgba(15, 139, 111, 0.16);
}

.toolbar-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(110px, 1fr));
  gap: 0.65rem;
  margin-left: auto;
}

.toolbar-metric,
.summary-item,
.empty-items,
.total-planned {
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(12px);
}

.toolbar-metric {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
  padding: 0.7rem 0.8rem;
  border-radius: 16px;
  border: 1px solid rgba(124, 97, 61, 0.12);
}

.toolbar-metric span {
  color: var(--text-color-secondary);
  font-size: 0.76rem;
}

.toolbar-metric strong {
  color: var(--heading-color);
  font-size: 0.98rem;
}

.toolbar-metric strong.negative {
  color: var(--danger-color);
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
  border-radius: 28px;
  background: color-mix(in srgb, var(--surface-card) 84%, transparent);
  color: var(--text-color-secondary);
}

.empty-state i {
  font-size: 4rem;
  opacity: 0.5;
  margin-bottom: 1.5rem;
}

.empty-state h2 {
  margin-bottom: 0.5rem;
}

.empty-state p {
  margin-bottom: 2rem;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  border-radius: 20px;
  background: rgba(214, 69, 69, 0.08);
  border: 1px solid rgba(214, 69, 69, 0.16);
  color: var(--danger-color);
}

.budgets-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.budget-item {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  background:
    radial-gradient(circle at top right, var(--budget-bank-glow) 0%, transparent 34%),
    color-mix(in srgb, var(--surface-card) 90%, transparent);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.budget-item::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 4px;
  background: var(--budget-bank-surface);
}

.budget-item :deep(.p-card-body) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.budget-item :deep(.p-card-content) {
  flex: 1;
  padding: 0.85rem 1.25rem 1.1rem;
}

.budget-item :deep(.p-card-footer) {
  margin-top: auto;
  padding: 0.9rem 1.25rem 1.2rem;
  border-top: 1px solid rgba(124, 97, 61, 0.08);
}

.budget-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: color-mix(in srgb, var(--budget-bank-accent) 24%, var(--surface-border));
}

.budget-header {
  display: flex;
  justify-content: space-between;
  gap: 0.85rem;
  align-items: flex-start;
  padding: 1.2rem 1.25rem 0.15rem;
}

.budget-heading {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
}

.budget-avatar {
  min-width: 42px;
  height: 42px;
  padding: 0 0.8rem;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--budget-bank-surface);
  color: white;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  box-shadow: 0 14px 24px var(--budget-bank-shadow);
}

.budget-bank-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.32rem 0.7rem;
  border-radius: 999px;
  background: var(--budget-bank-pill-bg);
  color: var(--budget-bank-pill-color);
  font-size: 0.75rem;
  font-weight: 700;
}

.budget-bank-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 999px;
  background: var(--budget-bank-accent);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--budget-bank-accent) 18%, transparent);
}

.budget-meta-top {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 0.55rem;
}

.budget-info h3 {
  margin: 0 0 0.45rem;
  font-size: 1.1rem;
  color: var(--heading-color);
}

.budget-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
}

.budget-period {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-color-secondary);
  font-size: 0.88rem;
}

.budget-health {
  display: inline-flex;
  align-items: center;
  padding: 0.32rem 0.7rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.budget-health.is-success {
  background: rgba(15, 139, 111, 0.1);
  color: var(--success-color);
}

.budget-health.is-warning {
  background: rgba(217, 119, 6, 0.12);
  color: var(--warning-color);
}

.budget-health.is-danger {
  background: rgba(214, 69, 69, 0.12);
  color: var(--danger-color);
}

.budget-health.is-muted {
  background: rgba(107, 114, 128, 0.12);
  color: var(--text-color-secondary);
}

.budget-balance-panel {
  min-width: 145px;
  padding: 0.85rem 0.9rem;
  border-radius: 18px;
  background: color-mix(in srgb, var(--budget-bank-accent-soft) 16%, var(--surface-ground));
  border: 1px solid color-mix(in srgb, var(--budget-bank-accent) 14%, transparent);
}

.budget-balance-panel span {
  display: block;
  color: var(--text-color-secondary);
  font-size: 0.8rem;
  margin-bottom: 0.3rem;
}

.budget-balance-panel strong {
  display: block;
  font-size: 1.2rem;
  letter-spacing: -0.03em;
  color: var(--heading-color);
}

.budget-balance-panel small {
  display: -webkit-box;
  margin-top: 0.4rem;
  color: var(--text-color-secondary);
  line-height: 1.35;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.budget-summary {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.65rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.8rem 0.85rem;
  border-radius: 16px;
  border: 1px solid rgba(124, 97, 61, 0.08);
}

.emphasis-item {
  background: linear-gradient(135deg, color-mix(in srgb, var(--budget-bank-accent) 10%, white) 0%, color-mix(in srgb, var(--budget-bank-accent-soft) 18%, white) 100%);
}

.summary-label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--text-color-secondary);
  font-size: 0.8rem;
}

.summary-value {
  color: var(--heading-color);
  font-size: 1rem;
  font-weight: 700;
}

.empty-plan-item .summary-value {
  font-size: 0.92rem;
}

.text-green {
  color: var(--success-color) !important;
}

.text-red {
  color: var(--danger-color) !important;
}

.budget-actions {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.budget-detail-button {
  width: 100%;
  box-shadow: 0 14px 26px var(--budget-bank-shadow);
}

.bank-option-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.bank-option-logo {
  min-width: 3.2rem;
  padding: 0.3rem 0.55rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--surface-ground) 76%, transparent);
  color: var(--heading-color);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-align: center;
}

.budget-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.55rem;
}

.budget-actions-grid :deep(.p-button) {
  justify-content: center;
}

@media (max-width: 980px) {
  .budgets-list {
    grid-template-columns: 1fr;
  }
}

.dialog-content {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field,
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-field label,
.form-group label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9375rem;
}

.form-help {
  color: var(--text-color-secondary);
}

.w-full {
  width: 100%;
}

.warning-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(217, 119, 6, 0.1);
  border-radius: 12px;
  color: var(--warning-color);
  margin-top: 0.5rem;
}

.budget-items-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--surface-border);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.section-header h4 {
  margin: 0.55rem 0 0;
  font-size: 1rem;
}

.budget-items-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.budget-item-card {
  background: color-mix(in srgb, var(--surface-ground) 74%, transparent);
}

.item-form {
  width: 100%;
}

.item-row {
  align-items: end;
}

.form-group.flex-2 {
  flex: 2;
}

.form-group-actions {
  display: flex;
  align-items: end;
  padding-bottom: 0.25rem;
}

.empty-items {
  text-align: center;
  padding: 2rem;
  color: var(--text-color-secondary);
  border-radius: 16px;
  border: 1px dashed var(--surface-border);
}

.empty-items p {
  margin: 0;
}

.total-planned {
  display: flex;
  justify-content: space-between;
  padding: 1rem 1.1rem;
  border-radius: 18px;
  border: 1px solid rgba(15, 139, 111, 0.14);
  font-weight: 700;
}

.total-planned .label {
  color: var(--text-color);
}

.total-planned .value {
  color: var(--primary-color);
  font-size: 1.125rem;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
}

.category-option i {
  font-size: 1rem;
}

.subcategory-indicator {
  color: var(--text-color-secondary);
  margin-right: 0.25rem;
  font-weight: 600;
}

@media (max-width: 1100px) {
  .toolbar-row-secondary {
    flex-direction: column;
  }

  .toolbar-metrics {
    width: 100%;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .budget-manager {
    gap: 1rem;
  }

  .budget-toolbar {
    padding: 0.95rem;
    border-radius: 20px;
  }

  .page-title {
    font-size: 1.65rem;
  }

  .toolbar-row,
  .budget-header,
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-metrics,
  .summary-grid,
  .budgets-list,
  .form-row {
    grid-template-columns: 1fr;
  }

  .budget-actions {
    width: 100%;
  }

  .budget-actions-grid,
  .toolbar-primary-action {
    width: 100%;
  }

  .budget-actions-grid {
    grid-template-columns: 1fr;
  }

  .budget-actions :deep(.p-button) {
    width: 100%;
  }

  .status-tabs {
    width: 100%;
  }

  .toolbar-primary-action,
  .status-tabs :deep(.p-button) {
    width: 100%;
  }

  .budget-balance-panel {
    width: 100%;
    min-width: 0;
  }
}
</style>
