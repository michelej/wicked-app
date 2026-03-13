<template>
  <div class="budget-manager">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Gestión de Presupuestos</h1>
          <p class="page-subtitle">Administra todos tus presupuestos</p>
        </div>
        <Button 
          label="Nuevo Presupuesto" 
          icon="pi pi-plus"
          @click="showCreateDialog = true"
          severity="success"
        />
      </div>
    </div>

    <!-- Status Tabs -->
    <div class="status-tabs">
      <Button 
        :label="`Activos (${budgetStore.activeBudgets.length})`"
        :severity="currentTab === 'active' ? 'primary' : 'secondary'"
        :text="currentTab !== 'active'"
        @click="currentTab = 'active'"
      />
      <Button 
        :label="`Cerrados (${budgetStore.closedBudgets.length})`"
        :severity="currentTab === 'closed' ? 'primary' : 'secondary'"
        :text="currentTab !== 'closed'"
        @click="currentTab = 'closed'"
      />
      <Button 
        :label="`Borradores (${budgetStore.draftBudgets.length})`"
        :severity="currentTab === 'draft' ? 'primary' : 'secondary'"
        :text="currentTab !== 'draft'"
        @click="currentTab = 'draft'"
      />
    </div>

    <!-- Loading State -->
    <div v-if="budgetStore.loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando presupuestos...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="budgetStore.error" class="error-message">
      <i class="pi pi-exclamation-circle"></i>
      {{ budgetStore.error }}
    </div>

    <!-- Empty State -->
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

    <!-- Budgets List -->
    <div v-else class="budgets-list">
      <Card 
        v-for="budget in filteredBudgets" 
        :key="budget._id"
        class="budget-item"
      >
        <template #header>
          <div class="budget-header">
            <div class="budget-info">
              <h3>{{ budget.name }}</h3>
              <div class="budget-meta">
                <span class="budget-period">
                  <i class="pi pi-calendar"></i>
                  {{ formatDate(budget.start_date) }} - {{ formatDate(budget.end_date) }}
                </span>
                <Tag 
                  :value="formatBudgetStatus(budget.status).label" 
                  :severity="formatBudgetStatus(budget.status).severity"
                />
              </div>
            </div>
          </div>
        </template>

        <template #content>
          <div class="budget-summary">
            <div class="summary-row">
              <div class="summary-item">
                <span class="summary-label">Balance</span>
                <span 
                  class="summary-value"
                  :class="{
                    'text-green': (budget.summary?.balance || 0) >= 0,
                    'text-red': (budget.summary?.balance || 0) < 0
                  }"
                >
                  {{ formatCurrency(budget.summary?.balance || 0) }}
                </span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Transacciones</span>
                <span class="summary-value">{{ budget.summary?.transactions_count || 0 }}</span>
              </div>
            </div>
            <div class="summary-row">
              <div class="summary-item">
                <span class="summary-label text-green">
                  <i class="pi pi-arrow-down"></i> Ingresos
                </span>
                <span class="summary-value text-green">
                  {{ formatCurrency(budget.summary?.total_income || 0) }}
                </span>
              </div>
              <div class="summary-item">
                <span class="summary-label text-red">
                  <i class="pi pi-arrow-up"></i> Gastos
                </span>
                <span class="summary-value text-red">
                  {{ formatCurrency(budget.summary?.total_expense || 0) }}
                </span>
              </div>
            </div>
            <div v-if="budget.budget_items && budget.budget_items.length > 0" class="summary-row budget-items-info">
              <div class="summary-item">
                <span class="summary-label">
                  <i class="pi pi-list"></i> Categorías Planificadas
                </span>
                <span class="summary-value">{{ budget.budget_items.length }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">
                  <i class="pi pi-money-bill"></i> Total Planificado
                </span>
                <span class="summary-value">
                  {{ formatCurrency(calculateTotalPlanned(budget.budget_items)) }}
                </span>
              </div>
            </div>
          </div>
        </template>

        <template #footer>
          <div class="budget-actions">
            <Button 
              label="Ver Detalles"
              icon="pi pi-eye"
              text
              @click.stop="viewBudget(budget._id)"
            />
            <Button 
              label="Editar"
              icon="pi pi-pencil"
              text
              severity="secondary"
              @click.stop="editBudget(budget)"
              v-tooltip.top="'Editar presupuesto y categorías'"
            />
            <Button 
              label="Categorías"
              icon="pi pi-tags"
              text
              severity="info"
              @click.stop="editBudget(budget)"
              v-tooltip.top="'Editar categorías y montos planificados'"
            />
            <Button 
              v-if="budget.status === 'active'"
              label="Cerrar"
              icon="pi pi-lock"
              text
              severity="warning"
              @click.stop="confirmCloseBudget(budget)"
            />
            <Button 
              label="Eliminar"
              icon="pi pi-trash"
              text
              severity="danger"
              @click.stop="confirmDeleteBudget(budget)"
            />
          </div>
        </template>
      </Card>
    </div>

    <!-- Create/Edit Dialog -->
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

        <!-- Budget Items Section -->
        <div class="budget-items-section">
          <div class="section-header">
            <h4>Items del Presupuesto</h4>
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
                  <div class="form-row">
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

    <!-- Delete Confirmation Dialog -->
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

// Helper function for icon normalization
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

// State
const currentTab = ref('active')
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const editingBudget = ref(null)
const budgetToDelete = ref(null)

const budgetForm = ref({
  name: '',
  start_date: null,
  end_date: null,
  budget_items: [],
  status: 'active'
})

const statusOptions = [
  { label: 'Activo', value: 'active' },
  { label: 'Cerrado', value: 'closed' },
  { label: 'Borrador', value: 'draft' }
]

// Computed
const filteredBudgets = computed(() => {
  const budgets = currentTab.value === 'active' 
    ? budgetStore.activeBudgets 
    : currentTab.value === 'closed'
    ? budgetStore.closedBudgets
    : budgetStore.draftBudgets
  
  return budgets.map(budget => ({
    ...budget,
    summary: budgetStore.budgetSummaries[budget._id]
  }))
})

const totalPlanned = computed(() => {
  return budgetForm.value.budget_items.reduce((sum, item) => {
    return sum + (parseFloat(item.planned_amount) || 0)
  }, 0)
})

// Lifecycle
onMounted(async () => {
  await Promise.all([
    budgetStore.fetchBudgets(),
    categoryStore.fetchCategories()
  ])
  // Load summaries for all budgets
  for (const budget of budgetStore.budgets) {
    await budgetStore.getBudgetSummary(budget._id)
  }
})

// Methods
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
    start_date: new Date(budget.start_date),
    end_date: new Date(budget.end_date),
    budget_items: budget.budget_items || [],
    status: budget.status
  }
  showCreateDialog.value = true
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingBudget.value = null
  budgetForm.value = {
    name: '',
    start_date: null,
    end_date: null,
    budget_items: [],
    status: 'active'
  }
}

const saveBudget = async () => {
  if (!budgetForm.value.name || !budgetForm.value.start_date || !budgetForm.value.end_date) {
    toast.add({
      severity: 'warn',
      summary: 'Campos requeridos',
      detail: 'Por favor completa todos los campos',
      life: 3000
    })
    return
  }

  try {
    if (editingBudget.value) {
      await budgetStore.updateBudget(editingBudget.value._id, {
        name: budgetForm.value.name,
        start_date: budgetForm.value.start_date.toISOString(),
        end_date: budgetForm.value.end_date.toISOString(),
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
        start_date: budgetForm.value.start_date.toISOString(),
        end_date: budgetForm.value.end_date.toISOString(),
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

const confirmCloseBudget = (budget) => {
  toast.add({
    severity: 'info',
    summary: 'Cerrar Presupuesto',
    detail: `Funcionalidad próximamente para: ${budget.name}`,
    life: 3000
  })
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

/* Status Tabs */
.status-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
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

/* Budgets List */
.budgets-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.budget-item {
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.budget-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.budget-header {
  padding: 1.5rem;
}

.budget-info h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.75rem 0;
}

.budget-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.budget-period {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.budget-summary {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.summary-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.summary-row.budget-items-info {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--surface-border);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
}

.text-green {
  color: #10b981 !important;
}

.text-red {
  color: #ef4444 !important;
}

.budget-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Dialog */
.dialog-content {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-field label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9375rem;
}

.w-full {
  width: 100%;
}

.warning-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(251, 146, 60, 0.1);
  border-radius: 8px;
  color: #f59e0b;
  margin-top: 0.5rem;
}

/* Budget Items Section */
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
}

.section-header h4 {
  margin: 0;
  font-size: 1rem;
  color: var(--text-color);
}

.budget-items-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.budget-item-card {
  background: var(--surface-ground);
}

.item-form {
  width: 100%;
}

.item-form .form-row {
  display: flex;
  gap: 0.75rem;
  align-items: end;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.form-group.flex-2 {
  flex: 2;
}

.form-group label {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-color);
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
  background: var(--surface-ground);
  border-radius: 8px;
}

.empty-items p {
  margin: 0;
}

.total-planned {
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  background: var(--primary-50);
  border-radius: 8px;
  font-weight: 600;
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

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.75rem;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .summary-row {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .budget-actions {
    flex-direction: column;
  }

  .budget-actions :deep(.p-button) {
    width: 100%;
  }
}
</style>
