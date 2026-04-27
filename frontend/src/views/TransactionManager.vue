<template>
  <div class="transaction-manager">
    <section class="hero-panel">
      <div class="hero-copy">
        <span class="hero-kicker">Transaction desk</span>
        <h1 class="page-title">Controla movimientos y detecta señales clave al instante.</h1>
        <p class="page-subtitle">
          Revisa ingresos, gastos y pendientes desde una vista mas ordenada, manteniendo intacto el detalle operativo de cada transaccion.
        </p>

        <div class="hero-actions">
          <Button
            label="Nueva Transacción"
            icon="pi pi-plus"
            severity="success"
            class="hero-primary-action"
            @click="showCreateDialog = true"
          />
          <div class="hero-tag-card">
            <span>Filtros activos</span>
            <strong>{{ activeFilterCount }}</strong>
          </div>
        </div>
      </div>

      <div class="hero-metrics-grid">
        <div class="hero-metric-tile">
          <span>Total transacciones</span>
          <strong>{{ filteredTransactions.length }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>Total ingresos</span>
          <strong>{{ formatCurrency(totalIncome) }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>Total gastos</span>
          <strong>{{ formatCurrency(totalExpense) }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>Balance</span>
          <strong :class="{ negative: balance < 0 }">{{ formatCurrency(balance) }}</strong>
        </div>
      </div>
    </section>

    <div class="insight-strip">
      <div class="insight-item">
        <span class="insight-label">Cobrado</span>
        <strong>{{ chargedTransactionsCount }}</strong>
        <p>movimientos ya conciliados.</p>
      </div>
      <div class="insight-item">
        <span class="insight-label">Pendiente</span>
        <strong>{{ pendingTransactionsCount }}</strong>
        <p>movimientos aun por confirmar.</p>
      </div>
      <div class="insight-item">
        <span class="insight-label">Ticket promedio</span>
        <strong>{{ averageTransactionAmount }}</strong>
        <p>promedio por transaccion filtrada.</p>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-list"></i>
        </div>
        <div class="stat-content">
          <h3 class="stat-value">{{ filteredTransactions.length }}</h3>
          <p class="stat-label">Total Transacciones</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-arrow-down"></i>
        </div>
        <div class="stat-content">
          <h3 class="stat-value">{{ formatCurrency(totalIncome) }}</h3>
          <p class="stat-label">Total Ingresos</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-arrow-up"></i>
        </div>
        <div class="stat-content">
          <h3 class="stat-value">{{ formatCurrency(totalExpense) }}</h3>
          <p class="stat-label">Total Gastos</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="pi pi-wallet"></i>
        </div>
        <div class="stat-content">
          <h3 class="stat-value" :class="{ negative: balance < 0 }">
            {{ formatCurrency(balance) }}
          </h3>
          <p class="stat-label">Balance</p>
        </div>
      </div>
    </div>

    <Card class="filters-card">
      <template #content>
        <div class="panel-header">
          <div>
            <span class="section-kicker">Filtrado</span>
            <h2>Encuentra movimientos por presupuesto, categoria o estado.</h2>
          </div>
          <Button
            label="Limpiar Filtros"
            icon="pi pi-times"
            text
            @click="clearFilters"
            class="clear-button"
          />
        </div>

        <div class="filters-grid">
          <div class="filter-field search-field">
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
        </div>

        <div v-if="filters.budgetMonth" class="parent-category-filter-banner">
          <span class="parent-category-filter-label">Mes activo</span>
          <Tag :value="filters.budgetMonth" severity="info" />
          <small>Mostrando transacciones asociadas a este mes de presupuesto.</small>
          <Button
            icon="pi pi-times"
            text
            rounded
            severity="secondary"
            aria-label="Quitar filtro de mes"
            @click="clearBudgetMonthFilter"
          />
        </div>

        <div v-if="filters.parentCategory" class="parent-category-filter-banner">
          <span class="parent-category-filter-label">Categoría padre activa</span>
          <Tag :value="filters.parentCategory" severity="info" />
          <small>Mostrando transacciones de esta categoría y sus subcategorías.</small>
          <Button
            icon="pi pi-times"
            text
            rounded
            severity="secondary"
            aria-label="Quitar filtro de categoría padre"
            @click="clearParentCategoryFilter"
          />
        </div>
      </template>
    </Card>

    <Card class="table-card">
      <template #content>
        <div class="panel-header table-header">
          <div>
            <span class="section-kicker">Resultado</span>
            <h2>{{ filteredTransactions.length }} movimientos visibles</h2>
          </div>
          <div class="table-summary-pill">
            <span>Pendientes</span>
            <strong>{{ pendingTransactionsCount }}</strong>
          </div>
        </div>

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

          <Column field="bank" header="Banco" sortable>
            <template #body="{ data }">
              <span class="bank-text">{{ data.bank }}</span>
            </template>
          </Column>

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

          <Column header="Comentario">
            <template #body="{ data }">
              <span
                v-if="data.comment"
                class="comment-hover"
                v-tooltip.top="data.comment"
              >
                <i class="pi pi-comment"></i>
                <span>Ver</span>
              </span>
              <span v-else class="comment-empty">-</span>
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
            v-model="transactionForm.category_id"
            :options="availableCategories"
            optionLabel="displayName"
            optionValue="_id"
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
            <div v-if="isSelectedBudgetBankLocked" class="locked-bank-field" :style="selectedBudgetBankStyle">
              <span class="locked-bank-logo">{{ selectedBudgetBankBrand.logoText }}</span>
              <div class="locked-bank-copy">
                <strong>{{ selectedBudgetForForm.bank }}</strong>
                <small>El presupuesto seleccionado pertenece a este banco.</small>
              </div>
            </div>
            <Select
              v-else
              id="bank"
              v-model="transactionForm.bank"
              :options="budgetBankOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecciona banco"
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTransactionStore } from '@/stores/transactions'
import { useBudgetStore } from '@/stores/budgets'
import { useCategoryStore } from '@/stores/categories'
import { useFormatters } from '@/composables/useFormatters'
import { BUDGET_BANK_OPTIONS, formatBudgetOptionLabel, getBankBrand } from '@/constants/banks'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Calendar from 'primevue/calendar'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'

const route = useRoute()
const router = useRouter()
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

const normalizeIcon = (icon) => {
  if (!icon) return 'pi pi-tag'
  if (icon.startsWith('pi pi-')) return icon
  if (icon.startsWith('pi-')) return `pi ${icon}`
  return `pi pi-${icon}`
}

const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const editingTransaction = ref(null)
const transactionToDelete = ref(null)
const budgetBankOptions = BUDGET_BANK_OPTIONS

const normalizeQueryValue = (value) => {
  if (Array.isArray(value)) {
    return normalizeQueryValue(value[0])
  }

  if (typeof value !== 'string') {
    return null
  }

  const trimmedValue = value.trim()
  return trimmedValue ? trimmedValue : null
}

const createFiltersFromQuery = (query = {}) => {
  const budgetId = normalizeQueryValue(query.budgetId)
  const budgetMonth = normalizeQueryValue(query.budgetMonth)
  const type = normalizeQueryValue(query.type)
  const category = normalizeQueryValue(query.category)
  const parentCategory = normalizeQueryValue(query.parentCategory)
  const status = normalizeQueryValue(query.status)

  return {
    search: '',
    budgetId,
    budgetMonth,
    type: ['all', 'income', 'expense'].includes(type) ? type : 'all',
    category: parentCategory ? null : category,
    parentCategory,
    status: ['all', 'charged', 'pending'].includes(status) ? status : 'all'
  }
}

const buildQueryFromFilters = (currentFilters) => {
  const query = {}

  if (currentFilters.budgetId) {
    query.budgetId = currentFilters.budgetId
  }

  if (currentFilters.budgetMonth) {
    query.budgetMonth = currentFilters.budgetMonth
  }

  if (currentFilters.type && currentFilters.type !== 'all') {
    query.type = currentFilters.type
  }

  if (currentFilters.parentCategory) {
    query.parentCategory = currentFilters.parentCategory
  } else if (currentFilters.category) {
    query.category = currentFilters.category
  }

  if (currentFilters.status && currentFilters.status !== 'all') {
    query.status = currentFilters.status
  }

  return query
}

const areFilterSetsEqual = (first, second) => {
  return first.budgetId === second.budgetId &&
    first.budgetMonth === second.budgetMonth &&
    first.type === second.type &&
    first.category === second.category &&
    first.parentCategory === second.parentCategory &&
    first.status === second.status
}

const areQueriesEqual = (first, second) => JSON.stringify(first) === JSON.stringify(second)

const isApplyingRouteFilters = ref(false)

const filters = ref(createFiltersFromQuery(route.query))

const transactionForm = ref({
  budget_id: '',
  type: 'expense',
  amount: 0,
  category_id: '',
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

const budgetOptions = computed(() => [
  { label: 'Todos los presupuestos', value: null },
  ...budgetStore.budgets.map((b) => ({
    label: formatBudgetOptionLabel(b),
    value: b._id
  }))
])

const activeBudgetOptions = computed(() =>
  budgetStore.activeBudgets.map((b) => ({
    label: formatBudgetOptionLabel(b),
    value: b._id
  }))
)

const selectedBudgetForForm = computed(() => {
  return budgetStore.budgets.find((budget) => budget._id === transactionForm.value.budget_id) || null
})

const selectedBudgetBankBrand = computed(() => getBankBrand(selectedBudgetForForm.value?.bank))

const selectedBudgetBankStyle = computed(() => ({
  '--budget-bank-accent': selectedBudgetBankBrand.value.accent,
  '--budget-bank-surface': selectedBudgetBankBrand.value.surface,
  '--budget-bank-pill-bg': selectedBudgetBankBrand.value.pillBackground,
  '--budget-bank-shadow': selectedBudgetBankBrand.value.shadow
}))

const isSelectedBudgetBankLocked = computed(() => Boolean(selectedBudgetForForm.value?.bank))

const categoryOptions = computed(() => [
  { label: 'Todas las categorías', value: null },
  ...categoryStore.activeCategories.map((c) => ({
    label: c.name,
    value: c.name
  }))
])

const availableCategories = computed(() => {
  const categories = transactionForm.value.type === 'income'
    ? categoryStore.sortedIncomeCategories
    : transactionForm.value.type === 'expense'
      ? categoryStore.sortedExpenseCategories
      : categoryStore.sortedActiveCategories

  return categories.map((category) => ({
    ...category,
    displayName: category.parent_id ? `↳ ${category.name}` : category.name
  }))
})

const resolveCategoryId = (categoryValue) => {
  if (!categoryValue) {
    return ''
  }

  const exactIdMatch = categoryStore.categories.find((category) => category._id === categoryValue)
  if (exactIdMatch) {
    return exactIdMatch._id
  }

  return categoryStore.categories.find((category) => category.name === categoryValue)?._id || ''
}

const resolveCategoryName = (categoryId) => {
  if (!categoryId) {
    return ''
  }

  return categoryStore.categories.find((category) => category._id === categoryId)?.name || ''
}

const categoryParentLookup = computed(() => {
  const categoryById = new Map(categoryStore.categories.map((category) => [category._id, category]))
  const lookup = {}

  categoryStore.categories.forEach((category) => {
    if (!category.parent_id) {
      return
    }

    const parentCategory = categoryById.get(category.parent_id)
    if (parentCategory) {
      lookup[category.name] = parentCategory.name
    }
  })

  return lookup
})

const budgetMonthLookup = computed(() => {
  const lookup = {}

  budgetStore.budgets.forEach((budget) => {
    lookup[budget._id] = budget.budget_month || null
  })

  return lookup
})

const buildTransactionParams = () => {
  const params = {}

  if (filters.value.budgetId) {
    params.budget_id = filters.value.budgetId
  }

  if (filters.value.type !== 'all') {
    params.type_filter = filters.value.type
  }

  if (filters.value.category && !filters.value.parentCategory) {
    params.category = filters.value.category
  }

  if (filters.value.status !== 'all') {
    params.is_charged = filters.value.status === 'charged'
  }

  return params
}

const loadTransactions = async () => {
  await transactionStore.fetchTransactions(buildTransactionParams())
}

const filteredTransactions = computed(() => {
  let transactions = [...transactionStore.transactions]

  if (filters.value.budgetMonth) {
    transactions = transactions.filter((transaction) => {
      return budgetMonthLookup.value[transaction.budget_id] === filters.value.budgetMonth
    })
  }

  if (filters.value.parentCategory) {
    transactions = transactions.filter((transaction) => {
      return transaction.category === filters.value.parentCategory ||
        categoryParentLookup.value[transaction.category] === filters.value.parentCategory
    })
  } else if (filters.value.category) {
    transactions = transactions.filter((transaction) => transaction.category === filters.value.category)
  }

  if (filters.value.search) {
    const query = filters.value.search.toLowerCase()
    transactions = transactions.filter((t) =>
      t.category.toLowerCase().includes(query) ||
      t.bank.toLowerCase().includes(query) ||
      t.comment?.toLowerCase().includes(query)
    )
  }

  return transactions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const totalIncome = computed(() =>
  filteredTransactions.value
    .filter((t) => t.type === 'income' && t.category !== 'Transferido Cuentas')
    .reduce((sum, t) => sum + t.amount, 0)
)

const totalExpense = computed(() =>
  filteredTransactions.value
    .filter((t) => t.type === 'expense' && t.category !== 'Transferido Cuentas')
    .reduce((sum, t) => sum + t.amount, 0)
)

const balance = computed(() => totalIncome.value - totalExpense.value)

const chargedTransactionsCount = computed(() => {
  return filteredTransactions.value.filter((transaction) => transaction.is_charged).length
})

const pendingTransactionsCount = computed(() => {
  return filteredTransactions.value.filter((transaction) => !transaction.is_charged).length
})

const averageTransactionAmount = computed(() => {
  if (!filteredTransactions.value.length) {
    return formatCurrency(0)
  }

  const total = filteredTransactions.value.reduce((sum, transaction) => sum + (transaction.amount || 0), 0)
  return formatCurrency(total / filteredTransactions.value.length)
})

const activeFilterCount = computed(() => {
  return [
    Boolean(filters.value.search),
    Boolean(filters.value.budgetId),
    Boolean(filters.value.budgetMonth),
    filters.value.type !== 'all',
    Boolean(filters.value.category || filters.value.parentCategory),
    filters.value.status !== 'all'
  ].filter(Boolean).length
})

onMounted(async () => {
  await Promise.all([
    loadTransactions(),
    budgetStore.fetchBudgets(),
    categoryStore.fetchCategories()
  ])
})

watch(
  [
    () => filters.value.budgetId,
    () => filters.value.budgetMonth,
    () => filters.value.type,
    () => filters.value.category,
    () => filters.value.parentCategory,
    () => filters.value.status
  ],
  () => {
    if (isApplyingRouteFilters.value) {
      return
    }

    const nextQuery = buildQueryFromFilters(filters.value)
    const currentQuery = buildQueryFromFilters(createFiltersFromQuery(route.query))

    if (!areQueriesEqual(nextQuery, currentQuery)) {
      router.replace({ name: 'transactions', query: nextQuery })
    }

    loadTransactions()
  }
)

watch(
  () => route.query,
  (query) => {
    const nextFilters = createFiltersFromQuery(query)

    if (areFilterSetsEqual(filters.value, nextFilters)) {
      return
    }

    isApplyingRouteFilters.value = true
    filters.value = {
      ...filters.value,
      ...nextFilters
    }
    isApplyingRouteFilters.value = false

    loadTransactions()
  }
)

watch(
  () => filters.value.budgetId,
  (newBudgetId, oldBudgetId) => {
    if (isApplyingRouteFilters.value || !filters.value.budgetMonth || newBudgetId === oldBudgetId) {
      return
    }

    filters.value.budgetMonth = null
  }
)

watch(
  () => filters.value.category,
  (newCategory, oldCategory) => {
    if (isApplyingRouteFilters.value || !filters.value.parentCategory || newCategory === oldCategory) {
      return
    }

    filters.value.parentCategory = null
  }
)

watch(
  () => transactionForm.value.budget_id,
  (budgetId) => {
    const selectedBudget = budgetStore.budgets.find((budget) => budget._id === budgetId)
    if (selectedBudget?.bank) {
      transactionForm.value.bank = selectedBudget.bank
    }
  }
)

const clearFilters = () => {
  filters.value = {
    search: '',
    budgetId: null,
    budgetMonth: null,
    type: 'all',
    category: null,
    parentCategory: null,
    status: 'all'
  }
}

const clearParentCategoryFilter = () => {
  filters.value.parentCategory = null
}

const clearBudgetMonthFilter = () => {
  filters.value.budgetMonth = null
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingTransaction.value = null
  transactionForm.value = {
    budget_id: '',
    type: 'expense',
    amount: 0,
    category_id: '',
    bank: '',
    payment_method: 'debit',
    timestamp: new Date(),
    comment: '',
    is_charged: false
  }
}

const saveTransaction = async () => {
  if (!transactionForm.value.budget_id || !transactionForm.value.amount || !transactionForm.value.category_id || !transactionForm.value.bank) {
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
      category_id: transactionForm.value.category_id,
      category: resolveCategoryName(transactionForm.value.category_id),
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
    await loadTransactions()
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
    category_id: resolveCategoryId(transaction.category_id || transaction.category),
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
    await loadTransactions()
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
    await loadTransactions()
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

.hero-panel,
.insight-item,
.stat-card,
.filters-card,
.table-card {
  border: 1px solid var(--surface-border);
  box-shadow: var(--shadow-sm);
}

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(300px, 1fr);
  gap: 1.25rem;
  padding: 1.5rem;
  border-radius: 32px;
  background: var(--hero-gradient);
  overflow: hidden;
  position: relative;
}

.hero-panel::after {
  content: '';
  position: absolute;
  right: -5rem;
  bottom: -5rem;
  width: 16rem;
  height: 16rem;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(217, 119, 6, 0.14) 0%, rgba(217, 119, 6, 0) 70%);
}

.hero-copy,
.hero-metrics-grid {
  position: relative;
  z-index: 1;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
}

.hero-kicker,
.section-kicker {
  display: inline-flex;
  width: fit-content;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.68);
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 700;
}

.page-title {
  max-width: 13ch;
  font-size: clamp(2.2rem, 3.8vw, 3.4rem);
  font-weight: 800;
  color: var(--heading-color);
  letter-spacing: -0.04em;
}

.page-subtitle {
  max-width: 62ch;
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
  box-shadow: 0 18px 30px rgba(15, 139, 111, 0.2);
}

.hero-tag-card,
.hero-metric-tile,
.table-summary-pill {
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(12px);
}

.hero-tag-card,
.table-summary-pill {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.85rem 1rem;
  border-radius: 20px;
  border: 1px solid rgba(124, 97, 61, 0.12);
}

.hero-tag-card span,
.table-summary-pill span {
  color: var(--text-color-secondary);
  font-size: 0.82rem;
}

.hero-tag-card strong,
.table-summary-pill strong {
  color: var(--heading-color);
  font-size: 1rem;
}

.hero-metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.hero-metric-tile {
  padding: 1rem;
  border-radius: 20px;
  border: 1px solid rgba(124, 97, 61, 0.12);
}

.hero-metric-tile span {
  display: block;
  margin-bottom: 0.35rem;
  color: var(--text-color-secondary);
  font-size: 0.82rem;
}

.hero-metric-tile strong {
  color: var(--heading-color);
  font-size: 1.2rem;
}

.hero-metric-tile strong.negative {
  color: var(--danger-color);
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
}

.insight-label {
  display: block;
  margin-bottom: 0.35rem;
  color: var(--text-color-secondary);
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

.insight-item strong {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--heading-color);
  font-size: 1.35rem;
}

.insight-item p {
  color: var(--text-color-secondary);
  line-height: 1.55;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.35rem;
  border-radius: 24px;
  background: color-mix(in srgb, var(--surface-card) 86%, transparent);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
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
  color: white;
  font-size: 1.5rem;
  background: linear-gradient(145deg, #0f8b6f 0%, #d97706 100%);
  box-shadow: 0 12px 24px rgba(15, 139, 111, 0.2);
}

.stat-content {
  flex: 1;
}

.stat-value {
  color: var(--heading-color);
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.2rem;
}

.stat-value.negative {
  color: var(--danger-color);
}

.stat-label {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.filters-card,
.table-card {
  border-radius: 28px;
  background: color-mix(in srgb, var(--surface-card) 84%, transparent);
}

.table-card :deep(.p-card-body) {
  padding: 0;
}

.table-card :deep(.p-card-content) {
  padding: 0.8rem 0.9rem 0.95rem;
}

.table-card .panel-header {
  gap: 0.75rem;
  margin-bottom: 0.8rem;
}

.table-card .panel-header h2 {
  margin-top: 0.45rem;
  font-size: 1.08rem;
}

.table-summary-pill {
  padding: 0.7rem 0.85rem;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.1rem;
}

.panel-header h2 {
  margin-top: 0.6rem;
  font-size: 1.2rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: 1.4fr repeat(4, minmax(0, 1fr));
  gap: 1rem;
  align-items: end;
}

.parent-category-filter-banner {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  margin-top: 0.85rem;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--surface-border);
  border-radius: 14px;
  background: color-mix(in srgb, var(--surface-hover) 80%, transparent);
  flex-wrap: wrap;
}

.parent-category-filter-label {
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-color-secondary);
}

.parent-category-filter-banner small {
  color: var(--text-color-secondary);
  font-size: 0.78rem;
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
  align-self: flex-start;
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

.date-text,
.bank-text {
  color: var(--text-color-secondary);
  font-size: 0.8rem;
}

.amount-text {
  font-weight: 700;
  font-size: 0.84rem;
}

.text-green {
  color: var(--success-color) !important;
}

.text-red {
  color: var(--danger-color) !important;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.action-buttons :deep(.p-button) {
  width: 1.9rem;
  height: 1.9rem;
}

.comment-hover {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.22rem 0.45rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--surface-ground) 72%, transparent);
  color: var(--text-color-secondary);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: help;
}

.comment-empty {
  color: var(--text-color-secondary);
}

.transactions-table :deep(.p-datatable-thead > tr > th) {
  padding: 0.28rem 0.45rem;
  font-size: 0.78rem;
  line-height: 1.15;
}

.transactions-table :deep(.p-datatable-tbody > tr > td) {
  padding: 0.26rem 0.45rem;
  vertical-align: middle;
  font-size: 0.78rem;
  line-height: 1.15;
}

.transactions-table :deep(.p-tag) {
  font-size: 0.72rem;
  padding: 0.2rem 0.42rem;
}

.transactions-table :deep(.p-paginator) {
  padding: 0.4rem 0.55rem;
}

.transactions-table :deep(.p-paginator .p-paginator-page),
.transactions-table :deep(.p-paginator .p-paginator-prev),
.transactions-table :deep(.p-paginator .p-paginator-next),
.transactions-table :deep(.p-paginator .p-paginator-first),
.transactions-table :deep(.p-paginator .p-paginator-last) {
  min-width: 1.9rem;
  height: 1.9rem;
}

.transactions-table :deep(.p-paginator .p-dropdown-label) {
  font-size: 0.78rem;
}

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

.locked-bank-field {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem 1rem;
  border-radius: 14px;
  border: 1px solid color-mix(in srgb, var(--budget-bank-accent) 18%, transparent);
  background: var(--budget-bank-pill-bg);
}

.locked-bank-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 3.2rem;
  padding: 0.4rem 0.55rem;
  border-radius: 999px;
  color: white;
  background: var(--budget-bank-surface);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  box-shadow: 0 12px 20px var(--budget-bank-shadow);
}

.locked-bank-copy {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.locked-bank-copy strong {
  color: var(--text-color);
}

.locked-bank-copy small {
  color: var(--text-color-secondary);
}

.transaction-details {
  padding: 0.85rem 1rem;
  background: color-mix(in srgb, var(--surface-hover) 84%, transparent);
  border-radius: 14px;
  margin-top: 0.5rem;
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
  .hero-panel,
  .insight-strip,
  .filters-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .transaction-manager {
    gap: 1rem;
  }

  .hero-panel,
  .filters-card,
  .table-card {
    border-radius: 24px;
  }

  .hero-panel {
    padding: 1.1rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .stats-grid,
  .hero-metrics-grid,
  .form-row {
    grid-template-columns: 1fr;
  }

  .hero-actions,
  .panel-header {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-primary-action,
  .clear-button {
    width: 100%;
  }

  .button-group {
    flex-direction: column;
  }
}
</style>
