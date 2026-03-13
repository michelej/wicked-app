<template>
  <div class="recurring-manager">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Gastos Recurrentes</h1>
          <p class="page-subtitle">Administra tus gastos recurrentes mensuales, anuales y trimestrales</p>
        </div>
        <Button 
          label="Nuevo Gasto Recurrente" 
          icon="pi pi-plus"
          @click="showCreateDialog = true"
          severity="success"
        />
      </div>
    </div>

    <!-- Status Tabs -->
    <div class="status-tabs">
      <Button 
        :label="`Activos (${recurringStore.activeExpenses.length})`"
        :severity="showActive ? 'primary' : 'secondary'"
        :text="!showActive"
        @click="showActive = true"
      />
      <Button 
        :label="`Inactivos (${inactiveExpenses.length})`"
        :severity="!showActive ? 'primary' : 'secondary'"
        :text="showActive"
        @click="showActive = false"
      />
    </div>

    <!-- Loading State -->
    <div v-if="recurringStore.loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando gastos recurrentes...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="recurringStore.error" class="error-message">
      <i class="pi pi-exclamation-circle"></i>
      {{ recurringStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="displayedExpenses.length === 0" class="empty-state">
      <i class="pi pi-replay"></i>
      <h2>No hay gastos recurrentes {{ showActive ? 'activos' : 'inactivos' }}</h2>
      <p>{{ showActive ? 'Crea tu primer gasto recurrente para automatizar tus finanzas' : 'Todos tus gastos recurrentes están activos' }}</p>
      <Button 
        v-if="showActive"
        label="Crear Gasto Recurrente" 
        icon="pi pi-plus"
        @click="showCreateDialog = true"
        severity="success"
      />
    </div>

    <!-- Expenses List -->
    <div v-else class="expenses-list">
      <Card 
        v-for="expense in displayedExpenses" 
        :key="expense._id"
        class="expense-item"
      >
        <template #header>
          <div class="expense-header">
            <div class="expense-info">
              <h3>{{ expense.name }}</h3>
              <div class="expense-meta">
                <Tag :value="expense.category" severity="secondary" />
                <Tag 
                  :value="formatFrequency(expense.frequency)" 
                  :severity="getFrequencySeverity(expense.frequency)"
                />
                <Tag 
                  :value="expense.is_active ? 'Activo' : 'Inactivo'"
                  :severity="expense.is_active ? 'success' : 'danger'"
                />
              </div>
            </div>
          </div>
        </template>

        <template #content>
          <div class="expense-details">
            <div class="detail-row">
              <div class="detail-item">
                <span class="detail-label">Monto</span>
                <span class="detail-value amount-text">{{ formatCurrency(expense.amount) }}</span>
              </div>
              <div class="detail-item" v-if="expense.frequency !== 'one-time'">
                <span class="detail-label">Día del Mes</span>
                <span class="detail-value">{{ expense.day_of_month }}</span>
              </div>
              <div class="detail-item" v-else>
                <span class="detail-label">Fecha</span>
                <span class="detail-value">{{ formatDate(expense.specific_date) }}</span>
              </div>
            </div>
            <div class="detail-row">
              <div class="detail-item">
                <span class="detail-label">Banco</span>
                <span class="detail-value">{{ expense.bank }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Método de Pago</span>
                <span class="detail-value">{{ formatPaymentMethod(expense.payment_method) }}</span>
              </div>
            </div>
            <div v-if="expense.comment" class="detail-row">
              <div class="detail-item full-width">
                <span class="detail-label">Comentario</span>
                <span class="detail-value">{{ expense.comment }}</span>
              </div>
            </div>
          </div>
        </template>

        <template #footer>
          <div class="expense-actions">
            <Button 
              v-if="expense.is_active"
              label="Aplicar a Presupuesto"
              icon="pi pi-calendar-plus"
              text
              @click.stop="openApplyDialog(expense)"
            />
            <Button 
              label="Editar"
              icon="pi pi-pencil"
              text
              severity="secondary"
              @click.stop="editExpense(expense)"
            />
            <Button 
              :label="expense.is_active ? 'Desactivar' : 'Activar'"
              :icon="expense.is_active ? 'pi pi-times' : 'pi pi-check'"
              text
              :severity="expense.is_active ? 'warning' : 'success'"
              @click.stop="toggleActive(expense)"
            />
            <Button 
              label="Eliminar"
              icon="pi pi-trash"
              text
              severity="danger"
              @click.stop="confirmDelete(expense)"
            />
          </div>
        </template>
      </Card>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog 
      v-model:visible="showCreateDialog"
      modal
      :header="editingExpense ? 'Editar Gasto Recurrente' : 'Nuevo Gasto Recurrente'"
      :style="{ width: '650px' }"
      class="expense-dialog"
    >
      <div class="dialog-content">
        <div class="form-field">
          <label for="name">Nombre *</label>
          <InputText 
            id="name"
            v-model="expenseForm.name"
            placeholder="ej. Alquiler Casa"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="category">Categoría *</label>
          <Select 
            id="category"
            v-model="expenseForm.category"
            :options="categoryStore.sortedExpenseCategories"
            optionLabel="name"
            optionValue="name"
            placeholder="Selecciona categoría"
            filter
            class="w-full"
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

        <div class="form-row">
          <div class="form-field">
            <label for="amount">Monto *</label>
            <InputNumber 
              id="amount"
              v-model="expenseForm.amount"
              mode="currency"
              currency="EUR"
              locale="es-ES"
              :minFractionDigits="2"
              class="w-full"
            />
          </div>
          <div class="form-field" v-if="expenseForm.frequency !== 'one-time'">
            <label for="dayOfMonth">Día del Mes *</label>
            <InputNumber 
              id="dayOfMonth"
              v-model="expenseForm.day_of_month"
              :min="1"
              :max="31"
              placeholder="1-31"
              class="w-full"
            />
          </div>
          <div class="form-field" v-else>
            <label for="specificDate">Fecha Específica *</label>
            <Calendar 
              id="specificDate"
              v-model="expenseForm.specific_date"
              dateFormat="dd/mm/yy"
              placeholder="Selecciona fecha"
              :showIcon="true"
              class="w-full"
            />
          </div>
        </div>

        <div class="form-field">
          <label for="frequency">Frecuencia *</label>
          <Select 
            id="frequency"
            v-model="expenseForm.frequency"
            :options="frequencyOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Selecciona frecuencia"
            class="w-full"
          />
        </div>

        <div class="form-row">
          <div class="form-field">
            <label for="bank">Banco *</label>
            <InputText 
              id="bank"
              v-model="expenseForm.bank"
              placeholder="ej. BBVA"
              class="w-full"
            />
          </div>
          <div class="form-field">
            <label for="paymentMethod">Método de Pago *</label>
            <Select 
              id="paymentMethod"
              v-model="expenseForm.payment_method"
              :options="paymentMethodOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecciona método"
              class="w-full"
            />
          </div>
        </div>

        <div class="form-field">
          <label for="comment">Comentario</label>
          <Textarea 
            id="comment"
            v-model="expenseForm.comment"
            rows="3"
            placeholder="Descripción opcional"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <div class="checkbox-field">
            <Checkbox 
              v-model="expenseForm.is_active"
              :binary="true"
              inputId="isActive"
            />
            <label for="isActive">Activo</label>
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
          :label="editingExpense ? 'Actualizar' : 'Crear'"
          icon="pi pi-check"
          @click="saveExpense"
          :loading="recurringStore.loading"
          severity="success"
        />
      </template>
    </Dialog>

    <!-- Apply to Budget Dialog -->
    <Dialog 
      v-model:visible="showApplyDialog"
      modal
      header="Aplicar a Presupuesto"
      :style="{ width: '500px' }"
    >
      <div class="dialog-content">
        <p class="dialog-description">
          Selecciona el presupuesto al que deseas aplicar este gasto recurrente:
        </p>

        <div class="form-field">
          <label>Presupuesto *</label>
          <Select 
            v-model="selectedBudget"
            :options="budgetStore.activeBudgets"
            optionLabel="name"
            optionValue="_id"
            placeholder="Selecciona presupuesto"
            class="w-full"
          >
            <template #option="{ option }">
              <div class="budget-option">
                <span>{{ option.name }}</span>
                <small>{{ formatDate(option.start_date) }} - {{ formatDate(option.end_date) }}</small>
              </div>
            </template>
          </Select>
        </div>

        <div v-if="expenseToApply" class="expense-preview">
          <h4>Vista Previa</h4>
          <div class="preview-details">
            <div class="preview-item">
              <span class="preview-label">Nombre:</span>
              <span>{{ expenseToApply.name }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">Monto:</span>
              <span class="amount-text">{{ formatCurrency(expenseToApply.amount) }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">Frecuencia:</span>
              <span>{{ formatFrequency(expenseToApply.frequency) }}</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancelar"
          text
          @click="showApplyDialog = false"
        />
        <Button 
          label="Aplicar"
          icon="pi pi-check"
          @click="applyToBudget"
          :loading="recurringStore.loading"
          :disabled="!selectedBudget"
          severity="success"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation -->
    <Dialog 
      v-model:visible="showDeleteDialog"
      modal
      header="Confirmar Eliminación"
      :style="{ width: '450px' }"
    >
      <p>¿Estás seguro de que deseas eliminar el gasto recurrente "{{ expenseToDelete?.name }}"?</p>
      <p class="warning-text">
        <i class="pi pi-exclamation-triangle"></i>
        Esta acción no se puede deshacer.
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
          @click="deleteExpense"
          :loading="recurringStore.loading"
          severity="danger"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRecurringStore } from '@/stores/recurring'
import { useBudgetStore } from '@/stores/budgets'
import { useCategoryStore } from '@/stores/categories'
import { useFormatters } from '@/composables/useFormatters'
import { useToast } from 'primevue/usetoast'
import ProgressSpinner from 'primevue/progressspinner'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'

const recurringStore = useRecurringStore()
const budgetStore = useBudgetStore()
const categoryStore = useCategoryStore()
const toast = useToast()
const { 
  formatCurrency, 
  formatDate, 
  formatPaymentMethod, 
  formatFrequency 
} = useFormatters()

// Helper function for icon normalization
const normalizeIcon = (icon) => {
  if (!icon) return 'pi pi-tag'
  if (icon.startsWith('pi pi-')) return icon
  if (icon.startsWith('pi-')) return `pi ${icon}`
  return `pi pi-${icon}`
}

// State
const showActive = ref(true)
const showCreateDialog = ref(false)
const showApplyDialog = ref(false)
const showDeleteDialog = ref(false)
const editingExpense = ref(null)
const expenseToDelete = ref(null)
const expenseToApply = ref(null)
const selectedBudget = ref(null)

const expenseForm = ref({
  name: '',
  category: '',
  amount: 0,
  bank: '',
  payment_method: 'debit',
  frequency: 'monthly',
  day_of_month: 1,
  specific_date: null,
  comment: '',
  is_active: true
})

const frequencyOptions = [
  { label: 'Mensual', value: 'monthly' },
  { label: 'Anual', value: 'annual' },
  { label: 'Trimestral', value: 'quarterly' },
  { label: 'Único', value: 'one-time' }
]

const paymentMethodOptions = [
  { label: 'Efectivo', value: 'cash' },
  { label: 'Débito', value: 'debit' },
  { label: 'Crédito', value: 'credit' }
]

// Computed
const inactiveExpenses = computed(() => 
  recurringStore.recurringExpenses.filter(e => !e.is_active)
)

const displayedExpenses = computed(() => 
  showActive.value 
    ? recurringStore.activeExpenses 
    : inactiveExpenses.value
)

// Lifecycle
onMounted(async () => {
  await Promise.all([
    recurringStore.fetchRecurringExpenses(),
    budgetStore.fetchBudgets(),
    categoryStore.fetchCategories()
  ])
})

// Methods
const getFrequencySeverity = (frequency) => {
  switch (frequency) {
    case 'monthly': return 'info'
    case 'annual': return 'warning'
    case 'quarterly': return 'success'
    case 'one-time': return 'secondary'
    default: return 'secondary'
  }
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingExpense.value = null
  expenseForm.value = {
    name: '',
    category: '',
    amount: 0,
    bank: '',
    payment_method: 'debit',
    frequency: 'monthly',
    day_of_month: 1,
    specific_date: null,
    comment: '',
    is_active: true
  }
}

const saveExpense = async () => {
  // Validate required fields
  if (!expenseForm.value.name || !expenseForm.value.category || 
      !expenseForm.value.amount || !expenseForm.value.bank) {
    toast.add({
      severity: 'warn',
      summary: 'Campos requeridos',
      detail: 'Completa todos los campos obligatorios',
      life: 3000
    })
    return
  }

  // Validate frequency-specific fields
  if (expenseForm.value.frequency === 'one-time' && !expenseForm.value.specific_date) {
    toast.add({
      severity: 'warn',
      summary: 'Fecha requerida',
      detail: 'Debes especificar una fecha para gastos únicos',
      life: 3000
    })
    return
  }

  if (expenseForm.value.frequency !== 'one-time' && !expenseForm.value.day_of_month) {
    toast.add({
      severity: 'warn',
      summary: 'Día del mes requerido',
      detail: 'Debes especificar un día del mes para gastos recurrentes',
      life: 3000
    })
    return
  }

  // Prepare data for submission
  const expenseData = { ...expenseForm.value }
  
  // Format specific_date if it's a Date object
  if (expenseData.specific_date && expenseData.specific_date instanceof Date) {
    const year = expenseData.specific_date.getFullYear()
    const month = String(expenseData.specific_date.getMonth() + 1).padStart(2, '0')
    const day = String(expenseData.specific_date.getDate()).padStart(2, '0')
    expenseData.specific_date = `${year}-${month}-${day}`
  }

  try {
    if (editingExpense.value) {
      await recurringStore.updateRecurringExpense(editingExpense.value._id, expenseData)
      toast.add({
        severity: 'success',
        summary: 'Gasto actualizado',
        detail: 'El gasto recurrente se actualizó correctamente',
        life: 3000
      })
    } else {
      await recurringStore.createRecurringExpense(expenseData)
      toast.add({
        severity: 'success',
        summary: 'Gasto creado',
        detail: 'El gasto recurrente se creó correctamente',
        life: 3000
      })
    }
    closeDialog()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: err.response?.data?.detail || 'No se pudo guardar el gasto recurrente',
      life: 3000
    })
  }
}

const editExpense = (expense) => {
  editingExpense.value = expense
  expenseForm.value = {
    name: expense.name,
    category: expense.category,
    amount: expense.amount,
    bank: expense.bank,
    payment_method: expense.payment_method,
    frequency: expense.frequency,
    day_of_month: expense.day_of_month,
    specific_date: expense.specific_date ? new Date(expense.specific_date) : null,
    comment: expense.comment || '',
    is_active: expense.is_active
  }
  showCreateDialog.value = true
}

const toggleActive = async (expense) => {
  try {
    await recurringStore.updateRecurringExpense(expense._id, {
      ...expense,
      is_active: !expense.is_active
    })
    toast.add({
      severity: 'success',
      summary: expense.is_active ? 'Gasto desactivado' : 'Gasto activado',
      detail: `El gasto se ${expense.is_active ? 'desactivó' : 'activó'} correctamente`,
      life: 3000
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo actualizar el gasto',
      life: 3000
    })
  }
}

const openApplyDialog = (expense) => {
  expenseToApply.value = expense
  selectedBudget.value = null
  showApplyDialog.value = true
}

const applyToBudget = async () => {
  try {
    await recurringStore.applyToBudget(selectedBudget.value, [expenseToApply.value._id])
    toast.add({
      severity: 'success',
      summary: 'Gasto aplicado',
      detail: 'El gasto recurrente se aplicó al presupuesto',
      life: 3000
    })
    showApplyDialog.value = false
    expenseToApply.value = null
    selectedBudget.value = null
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo aplicar el gasto al presupuesto',
      life: 3000
    })
  }
}

const confirmDelete = (expense) => {
  expenseToDelete.value = expense
  showDeleteDialog.value = true
}

const deleteExpense = async () => {
  try {
    await recurringStore.deleteRecurringExpense(expenseToDelete.value._id)
    toast.add({
      severity: 'success',
      summary: 'Gasto eliminado',
      detail: 'El gasto recurrente se eliminó correctamente',
      life: 3000
    })
    showDeleteDialog.value = false
    expenseToDelete.value = null
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo eliminar el gasto recurrente',
      life: 3000
    })
  }
}
</script>

<style scoped>
.recurring-manager {
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

/* Expenses List */
.expenses-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.expense-item {
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.expense-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.expense-header {
  padding: 1.5rem;
}

.expense-info h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.75rem 0;
}

.expense-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.expense-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.detail-value {
  font-size: 1rem;
  color: var(--text-color);
}

.amount-text {
  font-weight: 600;
  color: #10b981;
}

.expense-actions {
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

.dialog-description {
  color: var(--text-color-secondary);
  margin-bottom: 0.5rem;
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

.checkbox-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-field label {
  font-weight: 500;
  margin: 0;
  cursor: pointer;
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

.budget-option {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.budget-option small {
  color: var(--text-color-secondary);
  font-size: 0.75rem;
}

.expense-preview {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--surface-hover);
  border-radius: 8px;
}

.expense-preview h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1rem;
}

.preview-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.9375rem;
}

.preview-label {
  color: var(--text-color-secondary);
  font-weight: 500;
}

/* Category Options Styling */
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

  .detail-row {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .expense-actions {
    flex-direction: column;
  }

  .expense-actions :deep(.p-button) {
    width: 100%;
  }
}
</style>
