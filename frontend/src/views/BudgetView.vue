<template>
  <div class="budget-view">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando presupuesto...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-message">
      <i class="pi pi-exclamation-circle"></i>
      {{ error }}
    </div>

    <!-- Budget Details -->
    <div v-else-if="budget" class="budget-content">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <div class="header-left">
            <Button 
              icon="pi pi-arrow-left"
              text
              rounded
              @click="goBack"
              class="back-button"
            />
            <div class="header-text">
              <h1 class="page-title">{{ budget.name }}</h1>
              <div class="page-meta">
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
          <div class="header-actions">
            <Button 
              label="Aplicar Gastos Recurrentes"
              icon="pi pi-replay"
              @click="showRecurringDialog = true"
              severity="secondary"
            />
            <Button 
              label="Nueva Transacción" 
              icon="pi pi-plus"
              @click="showTransactionDialog = true"
              severity="success"
            />
          </div>
        </div>
      </div>

      <!-- Summary Cards -->
      <div class="stats-grid">
        <div class="stat-card stat-card-balance">
          <div class="stat-icon">
            <i class="pi pi-wallet"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value" :class="{ 'negative': summary.balance < 0 }">
              {{ formatCurrency(summary.balance) }}
            </h3>
            <p class="stat-label">Balance Total</p>
          </div>
        </div>

        <div class="stat-card stat-card-income">
          <div class="stat-icon">
            <i class="pi pi-arrow-down"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ formatCurrency(summary.total_income) }}</h3>
            <p class="stat-label">Ingresos Totales</p>
            <small class="stat-detail">Cobrados: {{ formatCurrency(summary.charged_income) }}</small>
          </div>
        </div>

        <div class="stat-card stat-card-expense">
          <div class="stat-icon">
            <i class="pi pi-arrow-up"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ formatCurrency(summary.total_expense) }}</h3>
            <p class="stat-label">Gastos Totales</p>
            <small class="stat-detail">Cobrados: {{ formatCurrency(summary.charged_expense) }}</small>
          </div>
        </div>

        <div class="stat-card stat-card-pending">
          <div class="stat-icon">
            <i class="pi pi-clock"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ formatCurrency(summary.pending_expense) }}</h3>
            <p class="stat-label">Gastos Pendientes</p>
            <small class="stat-detail">{{ summary.transactions_count }} transacciones</small>
          </div>
        </div>
      </div>

      <!-- Budget Items Progress -->
      <Card v-if="summary.budget_items && summary.budget_items.length > 0" class="budget-items-card">
        <template #header>
          <div class="card-header">
            <div class="header-title-section">
              <h2>Progreso por Categoría</h2>
              <div class="header-actions-section">
                <Button
                  v-if="!editingBudgetItems"
                  label="Editar Categorías"
                  icon="pi pi-pencil"
                  size="small"
                  text
                  @click="startEditingBudgetItems"
                />
                <template v-else>
                  <Button
                    label="Cancelar"
                    icon="pi pi-times"
                    size="small"
                    text
                    severity="secondary"
                    @click="cancelEditingBudgetItems"
                  />
                  <Button
                    label="Guardar"
                    icon="pi pi-check"
                    size="small"
                    severity="success"
                    @click="saveBudgetItems"
                    :loading="budgetStore.loading"
                  />
                </template>
              </div>
            </div>
            <div class="summary-stats">
              <span class="stat-item">
                <strong>Total Planificado:</strong> {{ formatCurrency(summary.total_planned) }}
              </span>
              <span class="stat-item">
                <strong>Total Gastado:</strong> {{ formatCurrency(summary.total_spent) }}
              </span>
              <span class="stat-item" :class="{ 'text-green': summary.total_remaining >= 0, 'text-red': summary.total_remaining < 0 }">
                <strong>Restante:</strong> {{ formatCurrency(summary.total_remaining) }}
              </span>
            </div>
          </div>
        </template>

        <template #content>
          <!-- Add Category Button (Edit Mode) -->
          <div v-if="editingBudgetItems" class="add-category-section">
            <Button
              label="Agregar Categoría"
              icon="pi pi-plus"
              size="small"
              @click="addNewBudgetItem"
            />
          </div>

          <DataTable
            :value="editingBudgetItems ? tempBudgetItems : enrichedBudgetItems"
            class="budget-items-table"
            stripedRows
            showGridlines
            :rowClass="rowClass"
          >
            <Column field="category" header="Categoría" :sortable="true">
              <template #body="{ data, index }">
                <div v-if="!editingBudgetItems" class="category-cell">
                  
                  <span>{{ data.category }}</span>
                </div>
                <Select
                  v-else
                  v-model="data.category"
                  :options="categoryStore.sortedExpenseCategories"
                  optionLabel="name"
                  optionValue="name"
                  placeholder="Seleccionar categoría"
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
              </template>
            </Column>

            <Column field="planned_amount" header="Monto Planificado" :sortable="true">
              <template #body="{ data }">
                <InputNumber
                  v-if="editingBudgetItems"
                  v-model="data.planned_amount"
                  mode="currency"
                  currency="EUR"
                  locale="es-ES"
                  :minFractionDigits="2"
                  :maxFractionDigits="2"
                  class="w-full"
                />
                <span v-else class="amount-value">{{ formatCurrency(data.planned_amount) }}</span>
              </template>
            </Column>

            <Column field="spent_amount" header="Gastado" :sortable="true">
              <template #body="{ data }">
                <span class="amount-value spent">{{ formatCurrency(data.spent_amount) }}</span>
              </template>
            </Column>

            <Column field="remaining" header="Restante" :sortable="true">
              <template #body="{ data }">
                <span 
                  class="amount-value"
                  :class="{ 'text-red': getRemainingAmount(data) < 0, 'text-green': getRemainingAmount(data) >= 0 }"
                >
                  {{ formatCurrency(getRemainingAmount(data)) }}
                </span>
              </template>
            </Column>

            <Column field="percentage" header="% Restante" :sortable="true">
              <template #body="{ data }">
                <div class="percentage-cell">
                  <span 
                    class="percentage-value"
                    :class="{ 'text-red': getRemainingPercentage(data) < 0, 'text-green': getRemainingPercentage(data) >= 0 }"
                  >
                    {{ getRemainingPercentage(data).toFixed(1) }}%
                  </span>
                  <div class="mini-progress-bar">
                    <div 
                      class="mini-progress-fill"
                      :class="getProgressClass(data)"
                      :style="{ width: Math.min(getProgressPercentage(data), 100) + '%' }"
                    ></div>
                  </div>
                </div>
              </template>
            </Column>

           

            <Column v-if="editingBudgetItems" header="Acciones" :exportable="false" style="width: 5rem">
              <template #body="{ index }">
                <Button
                  icon="pi pi-trash"
                  size="small"
                  text
                  severity="danger"
                  @click="removeBudgetItem(index)"
                />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>

      <!-- Transactions Section -->
      <Card class="transactions-card">
        <template #header>
          <div class="card-header">
            <h2>Transacciones</h2>
            <div class="header-filters">
              <InputText 
                v-model="searchQuery"
                placeholder="Buscar..."
                class="search-input"
              >
                <template #prefix>
                  <i class="pi pi-search"></i>
                </template>
              </InputText>
              <Select 
                v-model="filterType"
                :options="typeOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Tipo"
              />
            </div>
          </div>
        </template>

        <template #content>
          <!-- Transaction Summary -->
          <div class="transaction-summary">
            <div class="summary-item">
              <div class="summary-icon income-icon">
                <i class="pi pi-arrow-down"></i>
              </div>
              <div class="summary-content">
                <h4 class="summary-value">{{ formatCurrency(transactionSummary.totalIncome) }}</h4>
                <p class="summary-label">Total Ingresos</p>
              </div>
            </div>
            <div class="summary-item">
              <div class="summary-icon expense-icon">
                <i class="pi pi-arrow-up"></i>
              </div>
              <div class="summary-content">
                <h4 class="summary-value">{{ formatCurrency(transactionSummary.totalExpense) }}</h4>
                <p class="summary-label">Total Gastos</p>
              </div>
            </div>
            <div class="summary-item">
              <div class="summary-icon balance-icon">
                <i class="pi pi-wallet"></i>
              </div>
              <div class="summary-content">
                <h4 class="summary-value" :class="{ 'negative': transactionSummary.balance < 0 }">
                  {{ formatCurrency(transactionSummary.balance) }}
                </h4>
                <p class="summary-label">Balance</p>
              </div>
            </div>
          </div>

          <DataTable 
            :value="transactionsWithBalance"
            :loading="transactionStore.loading"
            stripedRows
            paginator
            :rows="10"
            :rowsPerPageOptions="[10, 20, 50]"
            class="transactions-table"
          >
            <template #empty>
              <div class="empty-state">
                <i class="pi pi-inbox"></i>
                <p>No hay transacciones</p>
                <Button 
                  label="Agregar Transacción"
                  icon="pi pi-plus"
                  @click="showTransactionDialog = true"
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

            <Column field="runningBalance" header="Saldo" sortable>
              <template #body="{ data }">
                <span 
                  class="balance-text"
                  :class="{ 'text-green': data.runningBalance >= 0, 'text-red': data.runningBalance < 0 }"
                >
                  {{ formatCurrency(data.runningBalance) }}
                </span>
              </template>
            </Column>

            <Column field="payment_method" header="Método">
              <template #body="{ data }">
                {{ formatPaymentMethod(data.payment_method) }}
              </template>
            </Column>

            <Column field="bank" header="Banco" sortable />

            <Column field="is_charged" header="Estado">
              <template #body="{ data }">
                <Tag 
                  :value="data.is_charged ? 'Cobrado' : 'Pendiente'"
                  :severity="data.is_charged ? 'success' : 'warning'"
                />
              </template>
            </Column>

            <Column header="Acciones">
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
                    @click.stop="confirmDeleteTransaction(data)"
                  />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>

      <!-- Expenses by Category Summary -->
      <Card class="expenses-summary-card">
        <template #header>
          <div class="card-header">
            <h2>Gastos Reales por Categoría</h2>
            <div class="summary-stats">
              <span class="stat-item">
                <strong>Total Gastado:</strong> {{ formatCurrency(expensesByCategory.filter(item => !item.isIndented).reduce((sum, cat) => sum + cat.totalSpent, 0)) }}
              </span>
              <span class="stat-item">
                <strong>Categorías:</strong> {{ expensesByCategory.filter(item => !item.isIndented).length }}
              </span>
            </div>
          </div>
        </template>

        <template #content>
          <DataTable
            :value="expensesByCategory"
            class="expenses-summary-table"
            stripedRows
            showGridlines
            paginator
            :rows="10"
            :rowsPerPageOptions="[10, 20, 50]"
          >
            <template #empty>
              <div class="empty-state">
                <i class="pi pi-chart-bar"></i>
                <p>No hay gastos registrados</p>
              </div>
            </template>

            <Column field="category" header="Categoría" sortable>
              <template #body="{ data }">
                <div class="category-cell" :class="{ 'parent-category': data.isParent, 'subcategory': data.isIndented }">
                  <span v-if="data.isParent" class="parent-indicator">📁</span>
                  <span v-if="data.isIndented" class="subcategory-indicator">↳</span>
                  <Tag 
                    :value="data.category" 
                    :severity="data.isParent ? 'primary' : 'secondary'"
                    :class="{ 'parent-tag': data.isParent }"
                  />
                  <span v-if="data.isParent" class="subcategory-count">
                    ({{ data.subcategories.length }} subcategorías)
                  </span>
                </div>
              </template>
            </Column>

            <Column field="totalSpent" header="Total Gastado" sortable>
              <template #body="{ data }">
                <span class="amount-text text-red">
                  {{ formatCurrency(data.totalSpent) }}
                </span>
              </template>
            </Column>

            <Column field="transactionCount" header="Transacciones" sortable>
              <template #body="{ data }">
                <span class="transaction-count">{{ data.transactionCount }}</span>
              </template>
            </Column>

            <Column field="banks" header="Bancos">
              <template #body="{ data }">
                <div class="banks-list">
                  <Tag 
                    v-for="bank in data.banks.slice(0, 2)" 
                    :key="bank"
                    :value="bank"
                    severity="info"
                    class="bank-tag"
                  />
                  <Tag 
                    v-if="data.banks.length > 2"
                    :value="`+${data.banks.length - 2} más`"
                    severity="secondary"
                    class="bank-tag"
                  />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <!-- Transaction Dialog -->
    <Dialog 
      v-model:visible="showTransactionDialog"
      modal
      :header="editingTransaction ? 'Editar Transacción' : 'Nueva Transacción'"
      :style="{ width: '600px' }"
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
          @click="closeTransactionDialog"
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

    <!-- Recurring Expenses Dialog -->
    <Dialog 
      v-model:visible="showRecurringDialog"
      modal
      header="Aplicar Gastos Recurrentes"
      :style="{ width: '600px' }"
    >
      <div class="dialog-content">
        <p class="dialog-description">
          Selecciona los gastos recurrentes que deseas agregar al presupuesto como montos planificados. Los gastos se sumarán a las categorías correspondientes del presupuesto.
        </p>

        <div v-if="recurringStore.loading" class="loading-state">
          <ProgressSpinner style="width: 50px; height: 50px" />
        </div>

        <div v-else-if="recurringStore.activeExpenses.length === 0" class="empty-state">
          <p>No hay gastos recurrentes activos</p>
        </div>

        <div v-else class="recurring-list">
          <div 
            v-for="expense in recurringStore.activeExpenses"
            :key="expense._id"
            class="recurring-item"
          >
            <Checkbox 
              v-model="selectedRecurring"
              :value="expense._id"
              :inputId="expense._id"
            />
            <label :for="expense._id" class="recurring-label">
              <div class="recurring-info">
                <span class="recurring-name">{{ expense.name }}</span>
                <span class="recurring-detail">
                  {{ formatCurrency(expense.amount) }} - {{ expense.category }} - {{ formatFrequency(expense.frequency) }}
                </span>
              </div>
            </label>
          </div>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancelar"
          text
          @click="showRecurringDialog = false"
        />
        <Button 
          label="Aplicar"
          icon="pi pi-check"
          @click="applyRecurringExpenses"
          :loading="recurringStore.loading"
          :disabled="selectedRecurring.length === 0"
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
import { useRoute, useRouter } from 'vue-router'
import { useBudgetStore } from '@/stores/budgets'
import { useTransactionStore } from '@/stores/transactions'
import { useCategoryStore } from '@/stores/categories'
import { useRecurringStore } from '@/stores/recurring'
import { useFormatters } from '@/composables/useFormatters'
import { useToast } from 'primevue/usetoast'
import ProgressSpinner from 'primevue/progressspinner'
import Calendar from 'primevue/calendar'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'

const route = useRoute()
const router = useRouter()
const budgetStore = useBudgetStore()
const transactionStore = useTransactionStore()
const categoryStore = useCategoryStore()
const recurringStore = useRecurringStore()
const toast = useToast()
const { 
  formatCurrency, 
  formatDate, 
  formatDateTime,
  formatBudgetStatus, 
  formatTransactionType,
  formatPaymentMethod,
  formatFrequency
} = useFormatters()

// State
const budgetId = ref(route.params.id)
const budget = ref(null)
const summary = ref({})
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const filterType = ref('all')
const showTransactionDialog = ref(false)
const showRecurringDialog = ref(false)
const showDeleteDialog = ref(false)
const editingTransaction = ref(null)
const transactionToDelete = ref(null)
const selectedRecurring = ref([])
const editingBudgetItems = ref(false)
const tempBudgetItems = ref([])

const transactionForm = ref({
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

const paymentMethodOptions = [
  { label: 'Efectivo', value: 'cash' },
  { label: 'Débito', value: 'debit' },
  { label: 'Crédito', value: 'credit' }
]

// Computed
const availableCategories = computed(() => {
  if (transactionForm.value.type === 'income') {
    return categoryStore.sortedIncomeCategories
  } else if (transactionForm.value.type === 'expense') {
    return categoryStore.sortedExpenseCategories
  }
  return categoryStore.sortedActiveCategories
})

const sortedBudgetItems = computed(() => {
  if (!summary.value.budget_items || summary.value.budget_items.length === 0) {
    return []
  }

  // Create a map of category names to their parent_id
  const categoryMap = {}
  categoryStore.categories.forEach(cat => {
    categoryMap[cat.name] = cat.parent_id
  })

  // Create hierarchical sorted list
  const result = []
  const items = [...summary.value.budget_items]

  // First, add items for parent categories
  const parentItems = items.filter(item => !categoryMap[item.category])
  result.push(...parentItems)

  // Then, add items for child categories after their parents
  const processedParents = new Set()
  parentItems.forEach(parentItem => {
    processedParents.add(parentItem.category)
    
    // Find the parent category ID
    const parentCategory = categoryStore.categories.find(c => c.name === parentItem.category)
    if (parentCategory) {
      // Add all child items of this parent
      const childItems = items.filter(item => {
        const itemCategory = categoryStore.categories.find(c => c.name === item.category)
        return itemCategory && itemCategory.parent_id === parentCategory._id
      })
      result.push(...childItems)
    }
  })

  // Add any remaining items that don't have a parent in the budget
  items.forEach(item => {
    if (!result.find(r => r.category === item.category)) {
      result.push(item)
    }
  })

  return result
})

const enrichedBudgetItems = computed(() => {
  // Add bank information to each budget item based on transactions
  return sortedBudgetItems.value.map(item => {
    // Find all transactions for this category in this budget
    const categoryTransactions = transactionStore.transactions.filter(t => 
      t.budget_id === budgetId.value && 
      t.category === item.category &&
      t.type === 'expense'
    )
    
    // Extract unique banks
    const banks = [...new Set(categoryTransactions.map(t => t.bank).filter(Boolean))]
    
    return {
      ...item,
      banks: banks
    }
  })
})

const filteredTransactions = computed(() => {
  let transactions = transactionStore.transactions.filter(t => 
    t.budget_id === budgetId.value
  )

  if (filterType.value !== 'all') {
    transactions = transactions.filter(t => t.type === filterType.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    transactions = transactions.filter(t =>
      t.category.toLowerCase().includes(query) ||
      t.bank.toLowerCase().includes(query) ||
      t.comment?.toLowerCase().includes(query)
    )
  }

  return transactions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const transactionsWithBalance = computed(() => {
  // Get filtered transactions and sort by date ascending (oldest first)
  const sortedTransactions = [...filteredTransactions.value].sort((a, b) => 
    new Date(a.timestamp) - new Date(b.timestamp)
  )
  
  // Calculate running balance
  let runningBalance = 0
  const transactionsWithBalance = sortedTransactions.map(transaction => {
    const amount = transaction.type === 'income' ? transaction.amount : -transaction.amount
    runningBalance += amount
    
    return {
      ...transaction,
      runningBalance
    }
  })
  
  // Return sorted by date descending (newest first) for display
  return transactionsWithBalance.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const transactionSummary = computed(() => {
  const transactions = filteredTransactions.value
  
  const totalIncome = transactions
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + t.amount, 0)
  
  const totalExpense = transactions
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0)
  
  const balance = totalIncome - totalExpense
  
  return {
    totalIncome,
    totalExpense,
    balance
  }
})

const expensesByCategory = computed(() => {
  const transactions = transactionStore.transactions.filter(t => 
    t.budget_id === budgetId.value && t.type === 'expense'
  )
  
  // Create a map of category names to their details
  const categoryMap = {}
  categoryStore.categories.forEach(cat => {
    categoryMap[cat.name] = {
      id: cat._id,
      name: cat.name,
      parent_id: cat.parent_id,
      icon: cat.icon,
      color: cat.color
    }
  })
  
  // Calculate totals per category
  const categoryTotals = {}
  
  transactions.forEach(transaction => {
    const category = transaction.category
    if (!categoryTotals[category]) {
      categoryTotals[category] = {
        category,
        totalSpent: 0,
        transactionCount: 0,
        banks: new Set(),
        categoryInfo: categoryMap[category] || null,
        isSubcategory: false,
        parentCategory: null
      }
    }
    
    categoryTotals[category].totalSpent += transaction.amount
    categoryTotals[category].transactionCount += 1
    if (transaction.bank) {
      categoryTotals[category].banks.add(transaction.bank)
    }
  })
  
  // Group subcategories under their parents
  const parentTotals = {}
  const standaloneCategories = []
  
  // First pass: identify subcategories and accumulate parent totals
  Object.values(categoryTotals).forEach(item => {
    const catInfo = item.categoryInfo
    if (catInfo && catInfo.parent_id) {
      // This is a subcategory
      item.isSubcategory = true
      
      // Find parent category
      const parentCat = categoryStore.categories.find(c => c._id === catInfo.parent_id)
      if (parentCat) {
        item.parentCategory = parentCat.name
        
        // Accumulate in parent total
        if (!parentTotals[parentCat.name]) {
          parentTotals[parentCat.name] = {
            category: parentCat.name,
            totalSpent: 0,
            transactionCount: 0,
            banks: new Set(),
            categoryInfo: {
              id: parentCat._id,
              name: parentCat.name,
              parent_id: null,
              icon: parentCat.icon,
              color: parentCat.color
            },
            isParent: true,
            subcategories: []
          }
        }
        
        parentTotals[parentCat.name].totalSpent += item.totalSpent
        parentTotals[parentCat.name].transactionCount += item.transactionCount
        item.banks.forEach(bank => parentTotals[parentCat.name].banks.add(bank))
        parentTotals[parentCat.name].subcategories.push(item)
      } else {
        // Parent not found, treat as regular category
        standaloneCategories.push({
          ...item,
          banks: Array.from(item.banks)
        })
      }
    } else {
      // This is a parent category or standalone category
      standaloneCategories.push({
        ...item,
        banks: Array.from(item.banks)
      })
    }
  })
  
  // Build final result maintaining hierarchy
  const finalResult = []
  
  // Sort parent categories by total spent descending
  const sortedParents = Object.values(parentTotals).sort((a, b) => b.totalSpent - a.totalSpent)
  
  // Add each parent with its sorted subcategories
  sortedParents.forEach(parent => {
    // Sort subcategories by amount descending
    parent.subcategories.sort((a, b) => b.totalSpent - a.totalSpent)
    parent.banks = Array.from(parent.banks)
    
    finalResult.push(parent)
    
    // Add subcategories indented
    parent.subcategories.forEach(sub => {
      finalResult.push({
        ...sub,
        banks: Array.from(sub.banks),
        isIndented: true
      })
    })
  })
  
  // Add remaining standalone categories (not parents and not subcategories)
  const remainingStandalone = standaloneCategories.filter(item => 
    !sortedParents.find(p => p.category === item.category)
  ).sort((a, b) => b.totalSpent - a.totalSpent)
  
  finalResult.push(...remainingStandalone)
  
  return finalResult
})

// Lifecycle
onMounted(async () => {
  try {
    loading.value = true
    
    // Load budget, summary, transactions, categories, and recurring expenses
    await Promise.all([
      loadBudget(),
      transactionStore.fetchTransactions(),
      categoryStore.fetchCategories(),
      recurringStore.fetchRecurringExpenses()
    ])
  } catch (err) {
    error.value = 'Error al cargar los datos del presupuesto'
    console.error(err)
  } finally {
    loading.value = false
  }
})

// Methods
const loadBudget = async () => {
  budget.value = await budgetStore.getBudget(budgetId.value)
  summary.value = await budgetStore.getBudgetSummary(budgetId.value)
}

const goBack = () => {
  router.push('/budgets')
}

// Budget Items Progress Helpers
const getProgressPercentage = (item) => {
  if (!item.planned_amount || item.planned_amount === 0) return 0
  return Math.min((item.spent_amount / item.planned_amount) * 100, 100)
}

const getRemainingAmount = (item) => {
  return item.planned_amount - item.spent_amount
}

const getRemainingPercentage = (item) => {
  if (!item.planned_amount || item.planned_amount === 0) return 0
  return ((item.planned_amount - item.spent_amount) / item.planned_amount) * 100
}

const getProgressClass = (item) => {
  const percentage = getProgressPercentage(item)
  if (percentage >= 100) return 'progress-over'
  if (percentage >= 80) return 'progress-high'
  if (percentage >= 50) return 'progress-medium'
  return 'progress-low'
}

const isSubcategory = (categoryName) => {
  const category = categoryStore.categories.find(c => c.name === categoryName)
  return category && category.parent_id
}

const normalizeIcon = (icon) => {
  if (!icon) return 'pi pi-tag'
  if (icon.startsWith('pi pi-')) return icon
  if (icon.startsWith('pi-')) return `pi ${icon}`
  return `pi pi-${icon}`
}

const rowClass = (data) => {
  if (editingBudgetItems.value) {
    return 'editing-row'
  }
  
  const remaining = getRemainingAmount(data)
  if (remaining < 0) {
    return 'over-budget-row'
  }
  return ''
}

const closeTransactionDialog = () => {
  showTransactionDialog.value = false
  editingTransaction.value = null
  transactionForm.value = {
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
  if (!transactionForm.value.amount || !transactionForm.value.category || !transactionForm.value.bank) {
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
      budget_id: budgetId.value,
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

    closeTransactionDialog()
    await loadBudget()
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
    type: transaction.type,
    amount: transaction.amount,
    category: transaction.category,
    bank: transaction.bank,
    payment_method: transaction.payment_method,
    timestamp: new Date(transaction.timestamp),
    comment: transaction.comment || '',
    is_charged: transaction.is_charged
  }
  showTransactionDialog.value = true
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
    await loadBudget()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo actualizar la transacción',
      life: 3000
    })
  }
}

const confirmDeleteTransaction = (transaction) => {
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
    await loadBudget()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo eliminar la transacción',
      life: 3000
    })
  }
}

const applyRecurringExpenses = async () => {
  try {
    await recurringStore.applyToBudget(budgetId.value, selectedRecurring.value)
    toast.add({
      severity: 'success',
      summary: 'Gastos agregados',
      detail: `Se agregaron ${selectedRecurring.value.length} gastos recurrentes al presupuesto como montos planificados`,
      life: 3000
    })
    showRecurringDialog.value = false
    selectedRecurring.value = []
    await loadBudget()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron aplicar los gastos recurrentes',
      life: 3000
    })
  }
}

// Budget Items Editing Functions
const startEditingBudgetItems = () => {
  editingBudgetItems.value = true
  tempBudgetItems.value = JSON.parse(JSON.stringify(budget.value.budget_items || []))
}

const cancelEditingBudgetItems = () => {
  editingBudgetItems.value = false
  tempBudgetItems.value = []
}

const addNewBudgetItem = () => {
  tempBudgetItems.value.push({
    category: '',
    planned_amount: 0,
    spent_amount: 0
  })
}

const removeBudgetItem = (index) => {
  tempBudgetItems.value.splice(index, 1)
}

const saveBudgetItems = async () => {
  try {
    // Validate that all items have a category and amount
    const invalidItems = tempBudgetItems.value.filter(item => !item.category || !item.planned_amount)
    if (invalidItems.length > 0) {
      toast.add({
        severity: 'warn',
        summary: 'Validación',
        detail: 'Todas las categorías deben tener un nombre y monto planificado',
        life: 3000
      })
      return
    }

    await budgetStore.updateBudget(budgetId.value, {
      budget_items: tempBudgetItems.value
    })

    toast.add({
      severity: 'success',
      summary: 'Categorías actualizadas',
      detail: 'Los items del presupuesto se actualizaron correctamente',
      life: 3000
    })

    editingBudgetItems.value = false
    tempBudgetItems.value = []
    await loadBudget()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron actualizar los items del presupuesto',
      life: 3000
    })
  }
}
</script>

<style scoped>
.budget-view {
  width: 100%;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Loading and Error States */
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

.header-left {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  flex: 1;
}

.back-button {
  margin-top: 0.5rem;
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}

.page-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.budget-period {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  color: var(--text-color-secondary);
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
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

.stat-card-balance .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card-income .stat-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-card-expense .stat-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-card-pending .stat-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
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
  margin: 0 0 0.25rem 0;
}

.stat-detail {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

/* Transactions Card */
.transactions-card {
  border: 1px solid var(--surface-border);
  border-radius: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.card-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.header-filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  width: 250px;
}

/* Transaction Summary */
.transaction-summary {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--surface-ground);
  border-radius: 12px;
  border: 1px solid var(--surface-border);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.income-icon {
  background: #10b981;
}

.expense-icon {
  background: #ef4444;
}

.balance-icon {
  background: #3b82f6;
}

.summary-content {
  flex: 1;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
  line-height: 1;
}

.summary-value.negative {
  color: #ef4444;
}

.summary-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  font-weight: 500;
  margin: 0;
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

.balance-text {
  font-weight: 700;
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

.dialog-description {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
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

/* Recurring List */
.recurring-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.recurring-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  transition: all 0.2s;
}

.recurring-item:hover {
  background: var(--surface-hover);
}

.recurring-label {
  flex: 1;
  cursor: pointer;
}

.recurring-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.recurring-name {
  font-weight: 600;
  color: var(--text-color);
}

.recurring-detail {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

/* Budget Items Card */
.budget-items-card {
  margin-bottom: 2rem;
}

.budget-items-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1.5rem;
  border-bottom: 1px solid var(--surface-border);
}

.header-title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.header-actions-section {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.budget-items-card .summary-stats {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9375rem;
}

.budget-items-card .stat-item {
  color: var(--text-color-secondary);
}

.add-category-section {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--surface-border);
  background: var(--surface-50);
}

/* Excel-like Table Styles */
.budget-items-table {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.budget-items-table :deep(.p-datatable-thead > tr > th) {
  background: var(--primary-color);
  color: white;
  font-weight: 600;
  padding: 0.35rem 0.5rem;
  border: 1px solid var(--surface-border);
  text-align: left;
  font-size: 0.8125rem;
  line-height: 1.2;
}

.budget-items-table :deep(.p-datatable-tbody > tr > td) {
  padding: 0.35rem 0.5rem;
  border: 1px solid var(--surface-border);
  vertical-align: middle;
  font-size: 0.8125rem;
  line-height: 1.2;
}

.transactions-table :deep(.p-datatable-thead > tr > th) {
  padding: 0.35rem 0.5rem;
  font-size: 0.8125rem;
  line-height: 1.2;
}

.transactions-table :deep(.p-datatable-tbody > tr > td) {
  padding: 0.35rem 0.5rem;
  vertical-align: middle;
  font-size: 0.8125rem;
  line-height: 1.2;
}

/* Expenses Summary Card */
.expenses-summary-card {
  margin-top: 2rem;
  border: 1px solid var(--surface-border);
  border-radius: 16px;
}

.expenses-summary-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.expenses-summary-card .card-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.expenses-summary-card .summary-stats {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9375rem;
}

.expenses-summary-card .stat-item {
  color: var(--text-color-secondary);
}

.expenses-summary-table :deep(.p-datatable-thead > tr > th) {
  background: var(--primary-color);
  color: white;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--surface-border);
  text-align: left;
  font-size: 0.875rem;
}

.expenses-summary-table :deep(.p-datatable-tbody > tr > td) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--surface-border);
  vertical-align: middle;
}

.transaction-count {
  font-weight: 600;
  color: var(--text-color);
}

.banks-list {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.bank-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.budget-items-table :deep(.p-datatable-tbody > tr:hover) {
  background: var(--highlight-bg) !important;
}

.budget-items-table :deep(.p-datatable-tbody > tr.over-budget-row) {
  background: rgba(239, 68, 68, 0.05);
}

.budget-items-table :deep(.p-datatable-tbody > tr.editing-row) {
  background: var(--surface-100);
}

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

.subcategory-count {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.category-cell {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
}

.subcategory-indicator {
  color: var(--text-color-secondary);
  font-weight: 600;
  margin-right: 0.25rem;
}

.amount-value {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  font-size: 0.9375rem;
}

.amount-value.spent {
  color: var(--primary-color);
}

.percentage-cell {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.percentage-value {
  font-weight: 600;
  font-size: 0.9375rem;
}

.mini-progress-bar {
  width: 100%;
  height: 8px;
  background: var(--surface-200);
  border-radius: 4px;
  overflow: hidden;
}

.mini-progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.mini-progress-fill.progress-low {
  background: #10b981;
}

.mini-progress-fill.progress-medium {
  background: #3b82f6;
}

.mini-progress-fill.progress-high {
  background: #f59e0b;
}

.mini-progress-fill.progress-over {
  background: #ef4444;
}

.banks-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.bank-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.no-banks {
  color: var(--text-color-secondary);
  font-style: italic;
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

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.75rem;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .header-left {
    flex-direction: column;
  }

  .header-actions {
    flex-direction: column;
  }

  .header-actions :deep(.p-button) {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .header-filters {
    flex-direction: column;
    width: 100%;
  }

  .search-input {
    width: 100%;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
