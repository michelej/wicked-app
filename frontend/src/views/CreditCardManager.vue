<template>
  <div class="credit-card-manager" :style="themeStyleVars">
    <section class="hero-panel">
      <div class="hero-copy">
        <span class="hero-kicker">Tarjeta de Credito</span>
        <h1 class="page-title">Controla cada gasto de tu tarjeta sin mezclarlo con el resto de movimientos.</h1>
        <p class="page-subtitle">
          Trabaja por tarjeta, conserva categorias y presupuestos, y registra cada cargo con metodo de pago fijo en credito.
        </p>

        <div class="hero-actions">
          <Button
            label="Nueva Transacción"
            icon="pi pi-plus"
            severity="contrast"
            class="hero-primary-action"
            @click="openCreateDialog"
          />
          <div class="hero-tag-card">
            <span>Tarjeta activa</span>
            <strong>{{ selectedCardBrand.displayName }}</strong>
          </div>
        </div>
      </div>

      <div class="hero-card-preview">
        <div class="card-preview-shell">
          <span class="card-chip"></span>
          <div class="card-preview-header">
            <span class="card-logo">{{ selectedCardBrand.logoText }}</span>
            <Tag value="Credit" severity="warn" />
          </div>
          <div class="card-preview-copy">
            <strong>{{ selectedCardBrand.displayName }}</strong>
            <span>{{ selectedCardBrand.maskedNumber }}</span>
            <small>{{ selectedCardBrand.description }}</small>
          </div>
        </div>
      </div>
    </section>

    <section class="card-selector-panel">
      <div class="section-heading">
        <div>
          <span class="section-kicker">Selector</span>
          <h2>Elige la tarjeta con la que quieres trabajar.</h2>
        </div>
        <div class="selector-badge">
          <span>Disponibles</span>
          <strong>{{ creditCardOptions.length }}</strong>
        </div>
      </div>

      <div class="card-selector-grid">
        <button
          v-for="card in creditCardOptions"
          :key="card.value"
          type="button"
          class="credit-card-option"
          :class="{ selected: selectedCard === card.value }"
          :style="getCardOptionStyle(card)"
          @click="selectedCard = card.value"
        >
          <div class="credit-card-option__top">
            <span class="credit-card-option__logo">{{ card.logoText }}</span>
            <i v-if="selectedCard === card.value" class="pi pi-check-circle"></i>
          </div>
          <strong>{{ card.displayName }}</strong>
          <span>{{ card.maskedNumber }}</span>
          <small>{{ card.description }}</small>
        </button>
      </div>
    </section>

    <div class="stats-grid">
      <div class="stat-card">
        <span>Total transacciones</span>
        <strong>{{ filteredTransactions.length }}</strong>
      </div>
      <div class="stat-card">
        <span>Total ingresos</span>
        <strong>{{ formatCurrency(totalIncome) }}</strong>
      </div>
      <div class="stat-card">
        <span>Total gastos</span>
        <strong>{{ formatCurrency(totalExpense) }}</strong>
      </div>
      <div class="stat-card">
        <span>Pendientes</span>
        <strong>{{ pendingTransactionsCount }}</strong>
      </div>
    </div>

    <Card class="filters-card">
      <template #content>
        <div class="section-heading compact">
          <div>
            <span class="section-kicker">Filtrado</span>
            <h2>Ajusta la vista por presupuesto, tipo, categoria o estado.</h2>
          </div>
          <Button
            label="Limpiar"
            icon="pi pi-times"
            text
            @click="clearFilters"
          />
        </div>

        <div class="filters-grid">
          <div class="filter-field search-field">
            <label>Buscar</label>
            <InputText
              v-model="filters.search"
              placeholder="Categoria, comentario o presupuesto..."
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
              class="w-full"
            />
          </div>

          <div class="filter-field">
            <label>Categoria</label>
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
              class="w-full"
            />
          </div>
        </div>
      </template>
    </Card>

    <Card class="table-card">
      <template #content>
        <div class="section-heading compact">
          <div>
            <span class="section-kicker">Movimientos</span>
            <h2>{{ filteredTransactions.length }} transacciones visibles</h2>
          </div>
          <div class="table-summary-pill">
            <span>Metodo</span>
            <strong>Credit</strong>
          </div>
        </div>

        <DataTable
          :value="filteredTransactions"
          :loading="creditCardTransactionStore.loading"
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
              <i class="pi pi-credit-card"></i>
              <p>No hay transacciones registradas para esta tarjeta.</p>
              <Button
                label="Crear Primera Transacción"
                icon="pi pi-plus"
                text
                @click="openCreateDialog"
              />
            </div>
          </template>

          <Column field="timestamp" header="Fecha" sortable>
            <template #body="{ data }">
              <span class="date-text">{{ formatDateTime(data.timestamp) }}</span>
            </template>
          </Column>

          <Column field="category" header="Categoria" sortable>
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
              <span class="amount-text" :class="{ positive: data.type === 'income', negative: data.type === 'expense' }">
                {{ data.type === 'income' ? '+' : '-' }}{{ formatCurrency(data.amount) }}
              </span>
            </template>
          </Column>

          <Column field="budget_id" header="Presupuesto">
            <template #body="{ data }">
              <span>{{ budgetNameMap[data.budget_id] || 'Sin presupuesto' }}</span>
            </template>
          </Column>

          <Column field="payment_method" header="Metodo">
            <template #body>
              <Tag value="Credit" severity="warn" />
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
      :header="editingTransaction ? 'Editar Transacción de Tarjeta' : 'Nueva Transacción de Tarjeta'"
      :style="{ width: '640px' }"
      class="transaction-dialog"
    >
      <div class="dialog-content">
        <div class="form-field">
          <label>Tarjeta activa</label>
          <div class="selected-card-banner">
            <span class="selected-card-banner__logo">{{ selectedCardBrand.logoText }}</span>
            <div>
              <strong>{{ selectedCardBrand.displayName }}</strong>
              <small>{{ selectedCardBrand.maskedNumber }} · Metodo fijo en Credit</small>
            </div>
          </div>
        </div>

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
          <label for="category">Categoria *</label>
          <Select
            id="category"
            v-model="transactionForm.category_id"
            :options="availableCategories"
            optionLabel="displayName"
            optionValue="_id"
            placeholder="Selecciona categoria"
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

        <div class="form-field">
          <label for="timestamp">Fecha y hora *</label>
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
            placeholder="Descripcion opcional"
            class="w-full"
          />
        </div>

        <div class="form-field checkbox-field">
          <Checkbox
            v-model="transactionForm.is_charged"
            :binary="true"
            inputId="isCharged"
          />
          <label for="isCharged">Marcar como cobrado</label>
        </div>
      </div>

      <template #footer>
        <Button label="Cancelar" text @click="closeDialog" />
        <Button
          :label="editingTransaction ? 'Actualizar' : 'Crear'"
          icon="pi pi-check"
          :loading="creditCardTransactionStore.loading"
          @click="saveTransaction"
        />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="showDeleteDialog"
      modal
      header="Confirmar Eliminación"
      :style="{ width: '450px' }"
    >
      <p>¿Estas seguro de que deseas eliminar esta transacción de tarjeta?</p>

      <template #footer>
        <Button label="Cancelar" text @click="showDeleteDialog = false" />
        <Button label="Eliminar" severity="danger" icon="pi pi-trash" @click="deleteTransaction" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useBudgetStore } from '@/stores/budgets'
import { useCategoryStore } from '@/stores/categories'
import { useCreditCardTransactionStore } from '@/stores/creditCardTransactions'
import { useFormatters } from '@/composables/useFormatters'
import { CREDIT_CARD_OPTIONS, getCreditCardBrand } from '@/constants/creditCards'
import { formatBudgetOptionLabel } from '@/constants/banks'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Calendar from 'primevue/calendar'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'

const budgetStore = useBudgetStore()
const categoryStore = useCategoryStore()
const creditCardTransactionStore = useCreditCardTransactionStore()
const toast = useToast()
const { formatCurrency, formatDateTime, formatTransactionType } = useFormatters()

const creditCardOptions = CREDIT_CARD_OPTIONS
const selectedCard = ref(creditCardOptions[0]?.value || '')
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

const createEmptyTransactionForm = () => ({
  budget_id: '',
  credit_card: selectedCard.value,
  type: 'expense',
  amount: 0,
  category_id: '',
  bank: getCreditCardBrand(selectedCard.value).issuerBank,
  payment_method: 'credit',
  timestamp: new Date(),
  comment: '',
  is_charged: false
})

const transactionForm = ref(createEmptyTransactionForm())

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

const normalizeIcon = (icon) => {
  if (!icon) return 'pi pi-tag'
  if (icon.startsWith('pi pi-')) return icon
  if (icon.startsWith('pi-')) return `pi ${icon}`
  return `pi pi-${icon}`
}

const selectedCardBrand = computed(() => getCreditCardBrand(selectedCard.value))

const themeStyleVars = computed(() => ({
  '--card-accent': selectedCardBrand.value.accent,
  '--card-accent-soft': selectedCardBrand.value.accentSoft,
  '--card-surface': selectedCardBrand.value.surface,
  '--card-shadow': selectedCardBrand.value.shadow,
  '--card-glow': selectedCardBrand.value.glow,
  '--card-pill-background': selectedCardBrand.value.pillBackground,
  '--card-pill-color': selectedCardBrand.value.pillColor
}))

const budgetOptions = computed(() => [
  { label: 'Todos los presupuestos', value: null },
  ...budgetStore.budgets.map((budget) => ({
    label: formatBudgetOptionLabel(budget),
    value: budget._id
  }))
])

const activeBudgetOptions = computed(() =>
  budgetStore.activeBudgets.map((budget) => ({
    label: formatBudgetOptionLabel(budget),
    value: budget._id
  }))
)

const budgetNameMap = computed(() =>
  budgetStore.budgets.reduce((acc, budget) => {
    acc[budget._id] = budget.name
    return acc
  }, {})
)

const categoryOptions = computed(() => [
  { label: 'Todas las categorias', value: null },
  ...categoryStore.activeCategories.map((category) => ({
    label: category.name,
    value: category.name
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

const buildTransactionParams = () => {
  const params = {
    credit_card: selectedCard.value
  }

  if (filters.value.budgetId) {
    params.budget_id = filters.value.budgetId
  }

  if (filters.value.type !== 'all') {
    params.type_filter = filters.value.type
  }

  if (filters.value.category) {
    params.category = filters.value.category
  }

  if (filters.value.status !== 'all') {
    params.is_charged = filters.value.status === 'charged'
  }

  return params
}

const loadTransactions = async () => {
  if (!selectedCard.value) {
    creditCardTransactionStore.clearTransactions()
    return
  }

  await creditCardTransactionStore.fetchTransactions(buildTransactionParams())
}

const filteredTransactions = computed(() => {
  let transactions = [...creditCardTransactionStore.transactions]

  if (filters.value.search) {
    const query = filters.value.search.toLowerCase()
    transactions = transactions.filter((transaction) => {
      const budgetName = budgetNameMap.value[transaction.budget_id] || ''
      return (
        transaction.category.toLowerCase().includes(query) ||
        budgetName.toLowerCase().includes(query) ||
        transaction.comment?.toLowerCase().includes(query)
      )
    })
  }

  return transactions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const totalIncome = computed(() =>
  filteredTransactions.value
    .filter((transaction) => transaction.type === 'income')
    .reduce((sum, transaction) => sum + transaction.amount, 0)
)

const totalExpense = computed(() =>
  filteredTransactions.value
    .filter((transaction) => transaction.type === 'expense')
    .reduce((sum, transaction) => sum + transaction.amount, 0)
)

const pendingTransactionsCount = computed(() =>
  filteredTransactions.value.filter((transaction) => !transaction.is_charged).length
)

onMounted(async () => {
  await Promise.all([
    loadTransactions(),
    budgetStore.fetchBudgets(),
    categoryStore.fetchCategories()
  ])
})

watch(
  [
    () => selectedCard.value,
    () => filters.value.budgetId,
    () => filters.value.type,
    () => filters.value.category,
    () => filters.value.status
  ],
  () => {
    loadTransactions()
  }
)

watch(
  () => selectedCard.value,
  (card) => {
    const cardBrand = getCreditCardBrand(card)
    filters.value.search = ''
    transactionForm.value.credit_card = cardBrand.value
    transactionForm.value.bank = cardBrand.issuerBank
  }
)

const openCreateDialog = () => {
  editingTransaction.value = null
  transactionForm.value = createEmptyTransactionForm()
  showCreateDialog.value = true
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingTransaction.value = null
  transactionForm.value = createEmptyTransactionForm()
}

const clearFilters = () => {
  filters.value = {
    search: '',
    budgetId: null,
    type: 'all',
    category: null,
    status: 'all'
  }
}

const saveTransaction = async () => {
  if (!transactionForm.value.budget_id || !transactionForm.value.amount || !transactionForm.value.category_id) {
    toast.add({
      severity: 'warn',
      summary: 'Campos requeridos',
      detail: 'Completa presupuesto, monto y categoria antes de guardar.',
      life: 3000
    })
    return
  }

  const payload = {
    budget_id: transactionForm.value.budget_id,
    credit_card: selectedCardBrand.value.value,
    type: transactionForm.value.type,
    amount: transactionForm.value.amount,
    category_id: transactionForm.value.category_id,
    category: resolveCategoryName(transactionForm.value.category_id),
    bank: selectedCardBrand.value.issuerBank,
    payment_method: 'credit',
    timestamp: transactionForm.value.timestamp.toISOString(),
    comment: transactionForm.value.comment,
    is_charged: transactionForm.value.is_charged
  }

  try {
    if (editingTransaction.value) {
      await creditCardTransactionStore.updateTransaction(editingTransaction.value._id, payload)
      toast.add({
        severity: 'success',
        summary: 'Transacción actualizada',
        detail: 'La transacción de tarjeta se actualizó correctamente.',
        life: 3000
      })
    } else {
      await creditCardTransactionStore.createTransaction(payload)
      toast.add({
        severity: 'success',
        summary: 'Transacción creada',
        detail: 'La transacción de tarjeta se registró correctamente.',
        life: 3000
      })
    }

    closeDialog()
    await loadTransactions()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo guardar la transacción de tarjeta.',
      life: 3000
    })
  }
}

const editTransaction = (transaction) => {
  editingTransaction.value = transaction
  transactionForm.value = {
    budget_id: transaction.budget_id,
    credit_card: transaction.credit_card,
    type: transaction.type,
    amount: transaction.amount,
    category_id: resolveCategoryId(transaction.category_id || transaction.category),
    bank: transaction.bank,
    payment_method: 'credit',
    timestamp: new Date(transaction.timestamp),
    comment: transaction.comment || '',
    is_charged: transaction.is_charged
  }
  showCreateDialog.value = true
}

const markAsCharged = async (transaction) => {
  try {
    await creditCardTransactionStore.markCharged(transaction._id)
    toast.add({
      severity: 'success',
      summary: 'Transacción actualizada',
      detail: 'La transacción se marcó como cobrada.',
      life: 3000
    })
    await loadTransactions()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo actualizar la transacción.',
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
    await creditCardTransactionStore.deleteTransaction(transactionToDelete.value._id)
    toast.add({
      severity: 'success',
      summary: 'Transacción eliminada',
      detail: 'La transacción de tarjeta se eliminó correctamente.',
      life: 3000
    })
    showDeleteDialog.value = false
    transactionToDelete.value = null
    await loadTransactions()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo eliminar la transacción.',
      life: 3000
    })
  }
}

const getCardOptionStyle = (card) => ({
  '--option-surface': card.surface,
  '--option-shadow': card.shadow,
  '--option-pill-background': card.pillBackground,
  '--option-pill-color': card.pillColor
})
</script>

<style scoped>
.credit-card-manager {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.hero-panel,
.card-selector-panel,
.filters-card,
.table-card,
.stat-card {
  border: 1px solid var(--surface-border);
  box-shadow: var(--shadow-sm);
}

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.9fr);
  gap: 1.25rem;
  padding: 1.5rem;
  border-radius: 32px;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.42), transparent 28%),
    linear-gradient(140deg, rgba(255, 247, 237, 0.95) 0%, rgba(255, 237, 213, 0.9) 100%);
  overflow: hidden;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.hero-kicker,
.section-kicker {
  display: inline-flex;
  width: fit-content;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  color: var(--card-pill-color);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.page-title {
  max-width: 15ch;
  font-size: clamp(2.1rem, 4vw, 3.35rem);
  line-height: 1.02;
  letter-spacing: -0.04em;
}

.page-subtitle {
  max-width: 58ch;
  color: var(--text-color-secondary);
  line-height: 1.65;
}

.hero-actions,
.section-heading,
.section-heading.compact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.hero-primary-action {
  background: var(--card-surface);
  border: none;
  box-shadow: 0 18px 32px var(--card-shadow);
}

.hero-tag-card,
.table-summary-pill,
.selector-badge {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.9rem 1rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(124, 97, 61, 0.12);
}

.hero-tag-card span,
.table-summary-pill span,
.selector-badge span {
  color: var(--text-color-secondary);
  font-size: 0.82rem;
}

.hero-card-preview {
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-preview-shell {
  width: min(100%, 340px);
  min-height: 212px;
  padding: 1.35rem;
  border-radius: 28px;
  background: var(--card-surface);
  color: #fff7ed;
  box-shadow: 0 26px 42px var(--card-shadow);
  position: relative;
  overflow: hidden;
}

.card-preview-shell::after {
  content: '';
  position: absolute;
  top: -2.5rem;
  right: -2rem;
  width: 9rem;
  height: 9rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
}

.card-chip {
  display: inline-flex;
  width: 3rem;
  height: 2.2rem;
  border-radius: 0.85rem;
  background: linear-gradient(145deg, rgba(255, 247, 237, 0.95), rgba(255, 213, 128, 0.7));
  margin-bottom: 1.4rem;
}

.card-preview-header,
.credit-card-option__top,
.selected-card-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.card-logo,
.credit-card-option__logo,
.selected-card-banner__logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 3.2rem;
  min-height: 3.2rem;
  padding: 0.55rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.16);
  font-weight: 800;
  letter-spacing: 0.12em;
}

.card-preview-copy,
.credit-card-option {
  display: flex;
  flex-direction: column;
}

.card-preview-copy {
  margin-top: 2.4rem;
  gap: 0.35rem;
}

.card-preview-copy strong {
  font-size: 1.25rem;
}

.card-preview-copy small {
  max-width: 24ch;
  color: rgba(255, 247, 237, 0.82);
  line-height: 1.5;
}

.card-selector-panel {
  padding: 1.4rem;
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(255, 247, 237, 0.84));
}

.card-selector-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-top: 1.15rem;
}

.credit-card-option {
  gap: 0.45rem;
  padding: 1.2rem;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: var(--option-surface);
  color: #fff7ed;
  box-shadow: 0 20px 34px var(--option-shadow);
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.credit-card-option:hover,
.credit-card-option.selected {
  transform: translateY(-2px);
  box-shadow: 0 24px 38px var(--option-shadow);
}

.credit-card-option i {
  font-size: 1.1rem;
}

.credit-card-option small {
  color: rgba(255, 247, 237, 0.82);
  line-height: 1.45;
}

.stats-grid,
.filters-grid {
  display: grid;
  gap: 1rem;
}

.stats-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 1.2rem;
  border-radius: 24px;
  background: #ffffff;
}

.stat-card span {
  color: var(--text-color-secondary);
  font-size: 0.88rem;
}

.stat-card strong {
  font-size: 1.45rem;
  color: var(--heading-color);
}

.filters-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  margin-top: 1rem;
}

.search-field {
  grid-column: span 2;
}

.filter-field,
.dialog-content,
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.dialog-content {
  gap: 1rem;
}

.selected-card-banner {
  padding: 1rem;
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(255, 247, 237, 0.9), rgba(255, 237, 213, 0.82));
  border: 1px solid rgba(249, 115, 22, 0.14);
}

.selected-card-banner__logo {
  background: var(--card-surface);
  color: #fff7ed;
}

.selected-card-banner small {
  display: block;
  color: var(--text-color-secondary);
  margin-top: 0.18rem;
}

.button-group,
.checkbox-field,
.action-buttons,
.comment-hover,
.category-option {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.checkbox-field {
  flex-direction: row;
}

.subcategory-indicator,
.comment-empty {
  color: var(--text-color-secondary);
}

.amount-text {
  font-weight: 700;
}

.amount-text.positive {
  color: #15803d;
}

.amount-text.negative {
  color: #b91c1c;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 1rem;
  text-align: center;
  color: var(--text-color-secondary);
}

.empty-state i {
  font-size: 2rem;
  color: var(--card-accent);
}

@media (max-width: 960px) {
  .hero-panel {
    grid-template-columns: 1fr;
  }

  .search-field {
    grid-column: span 1;
  }
}
</style>
