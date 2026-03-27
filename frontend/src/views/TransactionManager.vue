<template>
  <div class="transaction-manager">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Gestión de Transacciones</h1>
          <p class="page-subtitle">Administra todas tus transacciones</p>
        </div>
        <Button 
          label="Nueva Transacción" 
          icon="pi pi-plus"
          @click="showCreateDialog = true"
          severity="success"
        />
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="stats-grid">
      <div class="stat-card stat-card-1">
        <div class="stat-icon">
          <i class="pi pi-list"></i>
        </div>
        <div class="stat-content">
          <h3 class="stat-value">{{ filteredTransactions.length }}</h3>
          <p class="stat-label">Total Transacciones</p>
        </div>
      </div>

      <div class="stat-card stat-card-2">
        <div class="stat-icon">
          <i class="pi pi-arrow-down"></i>
        </div>
        <div class="stat-content">
          <h3 class="stat-value">{{ formatCurrency(totalIncome) }}</h3>
          <p class="stat-label">Total Ingresos</p>
        </div>
      </div>

      <div class="stat-card stat-card-3">
        <div class="stat-icon">
          <i class="pi pi-arrow-up"></i>
        </div>
        <div class="stat-content">
          <h3 class="stat-value">{{ formatCurrency(totalExpense) }}</h3>
          <p class="stat-label">Total Gastos</p>
        </div>
      </div>

      <div class="stat-card stat-card-4">
        <div class="stat-icon">
          <i class="pi pi-wallet"></i>
        </div>
        <div class="stat-content">
          <h3 class="stat-value" :class="{ 'negative': balance < 0 }">
            {{ formatCurrency(balance) }}
          </h3>
          <p class="stat-label">Balance</p>
        </div>
      </div>
    </div>

    <!-- Filters Card -->
    <Card class="filters-card">
      <template #content>
        <div class="filters-grid">
          <div class="filter-field">
            <label>Buscar</label>
            <InputText 
              v-model="filters.search"
              placeholder="Categoría, banco, comentario..."
              class="w-full"
            >
              <template #prefix>
                <i class="pi pi-search"></i>
              </template>
            </InputText>
          </div>

          <div class="filter-field">
            <label>Presupuesto</label>
            <Select 
              v-model="filters.budgetId"
              :options="budgetOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Todos"
              class="w-full"
              showClear
            />
          </div>

          <div class="filter-field">
            <label>Tipo</label>
            <Select 
              v-model="filters.type"
              :options="typeOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Todos"
              class="w-full"
            />
          </div>

          <div class="filter-field">
            <label>Categoría</label>
            <Select 
              v-model="filters.category"
              :options="categoryOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Todas"
              class="w-full"
              filter
              showClear
            />
          </div>

          <div class="filter-field">
            <label>Estado</label>
            <Select 
              v-model="filters.status"
              :options="statusOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Todos"
              class="w-full"
            />
          </div>

          <div class="filter-field">
            <Button 
              label="Limpiar Filtros"
              icon="pi pi-times"
              text
              @click="clearFilters"
              class="clear-button"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Transactions Table -->
    <Card class="table-card">
      <template #content>
        <DataTable 
          :value="filteredTransactions"
          :loading="transactionStore.loading"
          stripedRows
          paginator
          :rows="20"
          :rowsPerPageOptions="[10, 20, 50, 100]"
          class="transactions-table"
          sortField="timestamp"
          :sortOrder="-1"
        >
          <template #empty>
            <div class="empty-state">
              <i class="pi pi-inbox"></i>
              <p>No hay transacciones</p>
              <Button 
                label="Crear Primera Transacción"
                icon="pi pi-plus"
                @click="showCreateDialog = true"
                text
              />
            </div>
          </template>

          <Column field="timestamp" header="Fecha" sortable>
            <template #body="{ data }">
              <span class="date-text">{{ formatDateTime(data.timestamp) }}</span>
            </template>
          </Column>

          <Column field="category" header="Categoría" sortable>
            <template #body="{ data }">
              <Tag :value="data.category" severity="secondary" />
            </template>
          </Column>

          <Column field="type" header="Tipo" sortable>
            <template #body="{ data }">
              <Tag 
                :value="formatTransactionType(data.type)"
                :severity="data.type === 'income' ? 'success' : 'danger'"
              />
            </template>
          </Column>

          <Column field="amount" header="Monto" sortable>
            <template #body="{ data }">
              <span 
                class="amount-text"
                :class="{ 'text-green': data.type === 'income', 'text-red': data.type === 'expense' }"
              >
                {{ data.type === 'income' ? '+' : '-' }}{{ formatCurrency(data.amount) }}
              </span>
            </template>
          </Column>

          <Column field="bank" header="Banco" sortable />

          <Column field="payment_method" header="Método" sortable>
            <template #body="{ data }">
              {{ formatPaymentMethod(data.payment_method) }}
            </template>
          </Column>

          <Column field="is_charged" header="Estado" sortable>
            <template #body="{ data }">
              <Tag 
                :value="data.is_charged ? 'Cobrado' : 'Pendiente'"
                :severity="data.is_charged ? 'success' : 'warning'"
              />
            </template>
          </Column>

          <Column header="Acciones" :exportable="false">
            <template #body="{ data }">
              <div class="action-buttons">
                <Button 
                  v-if="!data.is_charged"
                  icon="pi pi-check"
                  text
                  rounded
                  severity="success"
                  v-tooltip.top="'Marcar como cobrado'"
                  @click.stop="markAsCharged(data)"
                />
                <Button 
                  icon="pi pi-pencil"
                  text
                  rounded
                  severity="secondary"
                  v-tooltip.top="'Editar'"
                  @click.stop="editTransaction(data)"
                />
                <Button 
                  icon="pi pi-trash"
                  text
                  rounded
                  severity="danger"
                  v-tooltip.top="'Eliminar'"
                  @click.stop="confirmDelete(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Create/Edit Dialog -->
    <Dialog 
      v-model:visible="showCreateDialog"
      modal
      :header="editingTransaction ? 'Editar Transacción' : 'Nueva Transacción'"
      :style="{ width: '650px' }"
      class="transaction-dialog"
    >
      <div class="dialog-content">
        <div class="form-field">
          <label>Tipo *</label>
          <div class="button-group">
            <Button 
              label="Ingreso"
              icon="pi pi-arrow-down"
              :severity="transactionForm.type === 'income' ? 'success' : 'secondary'"
              :outlined="transactionForm.type !== 'income'"
              @click="transactionForm.type = 'income'"
            />
            <Button 
              label="Gasto"
              icon="pi pi-arrow-up"
              :severity="transactionForm.type === 'expense' ? 'danger' : 'secondary'"
              :outlined="transactionForm.type !== 'expense'"
              @click="transactionForm.type = 'expense'"
            />
          </div>
        </div>

        <div class="form-field">
          <label for="budget">Presupuesto *</label>
          <Select 
            id="budget"
            v-model="transactionForm.budget_id"
            :options="activeBudgetOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Selecciona presupuesto"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="amount">Monto *</label>
          <InputNumber 
            id="amount"
            v-model="transactionForm.amount"
            mode="currency"
            currency="EUR"
            locale="es-ES"
            :minFractionDigits="2"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="category">Categoría *</label>
          <Select 
            id="category"
            v-model="transactionForm.category"
            :options="availableCategories"
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
            <label for="bank">Banco *</label>
            <InputText 
              id="bank"
              v-model="transactionForm.bank"
              placeholder="ej. BBVA"
              class="w-full"
            />
          </div>
          <div class="form-field">
            <label for="paymentMethod">Método de Pago *</label>
            <Select 
              id="paymentMethod"
              v-model="transactionForm.payment_method"
              :options="paymentMethodOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecciona método"
              class="w-full"
            />
          </div>
        </div>

        <div class="form-field">
          <label for="timestamp">Fecha y Hora *</label>
          <Calendar 
            id="timestamp"
            v-model="transactionForm.timestamp"
            showTime
            hourFormat="24"
            dateFormat="dd/mm/yy"
            placeholder="Selecciona fecha y hora"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="comment">Comentario</label>
          <Textarea 
            id="comment"
            v-model="transactionForm.comment"
            rows="3"
            placeholder="Descripción opcional"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <div class="checkbox-field">
            <Checkbox 
              v-model="transactionForm.is_charged"
              :binary="true"
              inputId="isCharged"
            />
            <label for="isCharged">Marcar como cobrado</label>
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
          :label="editingTransaction ? 'Actualizar' : 'Crear'"
          icon="pi pi-check"
          @click="saveTransaction"
          :loading="transactionStore.loading"
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
      <p>¿Estás seguro de que deseas eliminar esta transacción?</p>
      <p v-if="transactionToDelete" class="transaction-details">
        <strong>{{ transactionToDelete.category }}</strong> - 
        {{ formatCurrency(transactionToDelete.amount) }}
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
          @click="deleteTransaction"
          :loading="transactionStore.loading"
          severity="danger"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTransactionStore } from '@/stores/transactions'
import { useBudgetStore } from '@/stores/budgets'
import { useCategoryStore } from '@/stores/categories'
import { useFormatters } from '@/composables/useFormatters'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Select from 'primevue/select'
import MultiSelect from 'primevue/multiselect'
import Tag from 'primevue/tag'
import Calendar from 'primevue/calendar'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'

const transactionStore = useTransactionStore()
const budgetStore = useBudgetStore()
const categoryStore = useCategoryStore()
const toast = useToast()
const { 
  formatCurrency, 
  formatDateTime, 
  formatTransactionType,
  formatPaymentMethod
} = useFormatters()

// Helper function for icon normalization
const normalizeIcon = (icon) => {
  if (!icon) return 'pi pi-tag'
  if (icon.startsWith('pi pi-')) return icon
  if (icon.startsWith('pi-')) return `pi ${icon}`
  return `pi pi-${icon}`
}

// State
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const editingTransaction = ref(null)
const transactionToDelete = ref(null)

const filters = ref({
  search: '',
  budgetId: null,
  type: 'all',
  category: null,
  status: 'all'
})

const transactionForm = ref({
  budget_id: '',
  type: 'expense',
  amount: 0,
  category: '',
  bank: '',
  payment_method: 'debit',
  timestamp: new Date(),
  comment: '',
  is_charged: false
})

const typeOptions = [
  { label: 'Todos', value: 'all' },
  { label: 'Ingresos', value: 'income' },
  { label: 'Gastos', value: 'expense' }
]

const statusOptions = [
  { label: 'Todos', value: 'all' },
  { label: 'Cobrados', value: 'charged' },
  { label: 'Pendientes', value: 'pending' }
]

const paymentMethodOptions = [
  { label: 'Efectivo', value: 'cash' },
  { label: 'Débito', value: 'debit' },
  { label: 'Crédito', value: 'credit' }
]

// Computed
const budgetOptions = computed(() => [
  { label: 'Todos los presupuestos', value: null },
  ...budgetStore.budgets.map(b => ({
    label: b.name,
    value: b._id
  }))
])

const activeBudgetOptions = computed(() => 
  budgetStore.activeBudgets.map(b => ({
    label: b.name,
    value: b._id
  }))
)

const categoryOptions = computed(() => [
  { label: 'Todas las categorías', value: null },
  ...categoryStore.activeCategories.map(c => ({
    label: c.name,
    value: c.name
  }))
])

const availableCategories = computed(() => {
  if (transactionForm.value.type === 'income') {
    return categoryStore.sortedIncomeCategories
  } else if (transactionForm.value.type === 'expense') {
    return categoryStore.sortedExpenseCategories
  }
  return categoryStore.sortedActiveCategories
})

const filteredTransactions = computed(() => {
  let transactions = [...transactionStore.transactions]

  // Filter by search
  if (filters.value.search) {
    const query = filters.value.search.toLowerCase()
    transactions = transactions.filter(t =>
      t.category.toLowerCase().includes(query) ||
      t.bank.toLowerCase().includes(query) ||
      t.comment?.toLowerCase().includes(query)
    )
  }

  // Filter by budget
  if (filters.value.budgetId) {
    transactions = transactions.filter(t => t.budget_id === filters.value.budgetId)
  }

  // Filter by type
  if (filters.value.type !== 'all') {
    transactions = transactions.filter(t => t.type === filters.value.type)
  }

  // Filter by category
  if (filters.value.category) {
    transactions = transactions.filter(t => t.category === filters.value.category)
  }

  // Filter by status
  if (filters.value.status !== 'all') {
    transactions = transactions.filter(t => 
      filters.value.status === 'charged' ? t.is_charged : !t.is_charged
    )
  }

  return transactions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const totalIncome = computed(() => 
  filteredTransactions.value
    .filter(t => t.type === 'income' && t.category !== 'Transferido Cuentas')
    .reduce((sum, t) => sum + t.amount, 0)
)

const totalExpense = computed(() => 
  filteredTransactions.value
    .filter(t => t.type === 'expense' && t.category !== 'Transferido Cuentas')
    .reduce((sum, t) => sum + t.amount, 0)
)

const balance = computed(() => totalIncome.value - totalExpense.value)

// Lifecycle
onMounted(async () => {
  await Promise.all([
    transactionStore.fetchTransactions(),
    budgetStore.fetchBudgets(),
    categoryStore.fetchCategories()
  ])
})

// Methods
const clearFilters = () => {
  filters.value = {
    search: '',
    budgetId: null,
    type: 'all',
    category: null,
    status: 'all'
  }
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingTransaction.value = null
  transactionForm.value = {
    budget_id: '',
    type: 'expense',
    amount: 0,
    category: '',
    bank: '',
    payment_method: 'debit',
    timestamp: new Date(),
    comment: '',
    is_charged: false
  }
}

const saveTransaction = async () => {
  if (!transactionForm.value.budget_id || !transactionForm.value.amount || 
      !transactionForm.value.category || !transactionForm.value.bank) {
    toast.add({
      severity: 'warn',
      summary: 'Campos requeridos',
      detail: 'Completa todos los campos obligatorios',
      life: 3000
    })
    return
  }

  try {
    const payload = {
      budget_id: transactionForm.value.budget_id,
      type: transactionForm.value.type,
      amount: transactionForm.value.amount,
      category: transactionForm.value.category,
      bank: transactionForm.value.bank,
      payment_method: transactionForm.value.payment_method,
      timestamp: transactionForm.value.timestamp.toISOString(),
      comment: transactionForm.value.comment,
      is_charged: transactionForm.value.is_charged
    }

    if (editingTransaction.value) {
      await transactionStore.updateTransaction(editingTransaction.value._id, payload)
      toast.add({
        severity: 'success',
        summary: 'Transacción actualizada',
        detail: 'La transacción se actualizó correctamente',
        life: 3000
      })
    } else {
      await transactionStore.createTransaction(payload)
      toast.add({
        severity: 'success',
        summary: 'Transacción creada',
        detail: 'La transacción se creó correctamente',
        life: 3000
      })
    }

    closeDialog()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo guardar la transacción',
      life: 3000
    })
  }
}

const editTransaction = (transaction) => {
  editingTransaction.value = transaction
  transactionForm.value = {
    budget_id: transaction.budget_id,
    type: transaction.type,
    amount: transaction.amount,
    category: transaction.category,
    bank: transaction.bank,
    payment_method: transaction.payment_method,
    timestamp: new Date(transaction.timestamp),
    comment: transaction.comment || '',
    is_charged: transaction.is_charged
  }
  showCreateDialog.value = true
}

const markAsCharged = async (transaction) => {
  try {
    await transactionStore.markCharged(transaction._id)
    toast.add({
      severity: 'success',
      summary: 'Transacción actualizada',
      detail: 'La transacción se marcó como cobrada',
      life: 3000
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo actualizar la transacción',
      life: 3000
    })
  }
}

const confirmDelete = (transaction) => {
  transactionToDelete.value = transaction
  showDeleteDialog.value = true
}

const deleteTransaction = async () => {
  try {
    await transactionStore.deleteTransaction(transactionToDelete.value._id)
    toast.add({
      severity: 'success',
      summary: 'Transacción eliminada',
      detail: 'La transacción se eliminó correctamente',
      life: 3000
    })
    showDeleteDialog.value = false
    transactionToDelete.value = null
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo eliminar la transacción',
      life: 3000
    })
  }
}
</script>

<style scoped>
.transaction-manager {
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

/* Stats Grid */
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
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
  color: white;
}

.stat-card-1 .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card-2 .stat-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-card-3 .stat-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-card-4 .stat-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
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

/* Filters Card */
.filters-card {
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  margin-bottom: 2rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-field label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
}

.clear-button {
  width: 100%;
}

/* Table Card */
.table-card {
  border: 1px solid var(--surface-border);
  border-radius: 16px;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-color-secondary);
}

.empty-state i {
  font-size: 3rem;
  opacity: 0.5;
  margin-bottom: 1rem;
}

.date-text {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.amount-text {
  font-weight: 600;
  font-size: 1rem;
}

.text-green {
  color: #10b981 !important;
}

.text-red {
  color: #ef4444 !important;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
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

.button-group {
  display: flex;
  gap: 0.5rem;
}

.button-group :deep(.p-button) {
  flex: 1;
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

.transaction-details {
  padding: 0.75rem;
  background: var(--surface-hover);
  border-radius: 8px;
  margin-top: 0.5rem;
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

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
