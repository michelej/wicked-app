<template>
  <div class="import-review-view">
    <section class="hero-panel">
      <div class="hero-copy">
        <span class="hero-kicker">Validacion</span>
        <h1 class="page-title">Revisa cada movimiento antes de convertirlo en transaccion real.</h1>
        <p class="page-subtitle">
          Asigna presupuesto, categoria y metadatos finales. Tambien puedes marcar movimientos como procesados sin incorporarlos al sistema.
        </p>
      </div>

      <div class="hero-metrics-grid">
        <div class="hero-metric-tile">
          <span>Pendientes</span>
          <strong>{{ pendingCount }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>Importadas</span>
          <strong>{{ importedCount }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>Descartadas</span>
          <strong>{{ skippedCount }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>Monto pendiente</span>
          <strong>{{ formatCurrency(pendingAmount) }}</strong>
        </div>
      </div>
    </section>

    <Card class="filters-card">
      <template #content>
        <div class="filters-header">
          <div>
            <span class="section-kicker">Filtro</span>
            <h2>Bandeja de transacciones importadas</h2>
          </div>
          <Button label="Importar otro fichero" icon="pi pi-upload" text @click="router.push('/imports/upload')" />
        </div>

        <div class="filters-grid">
          <div class="filter-field">
            <label>Buscar</label>
            <InputText v-model="searchQuery" placeholder="Concepto, comentario o movimiento" class="w-full" />
          </div>
          <div class="filter-field">
            <label>Estado</label>
            <Select v-model="statusFilter" :options="statusOptions" optionLabel="label" optionValue="value" class="w-full" />
          </div>
          <div class="filter-field">
            <label>Banco</label>
            <Select v-model="bankFilter" :options="bankOptions" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>
      </template>
    </Card>

    <Card class="table-card">
      <template #content>
        <DataTable :value="filteredItems" :loading="importedTransactionStore.loading" paginator :rows="15" stripedRows>
          <template #empty>
            <div class="empty-state">
              <i class="pi pi-inbox"></i>
              <p>No hay movimientos importados para este filtro.</p>
            </div>
          </template>

          <Column field="suggested_timestamp" header="Fecha" sortable>
            <template #body="{ data }">
              {{ formatDateTime(data.suggested_timestamp || data.booking_date || data.value_date) }}
            </template>
          </Column>

          <Column field="source_bank" header="Banco" sortable>
            <template #body="{ data }">
              <Tag :value="bankLabel(data.source_bank)" severity="secondary" />
            </template>
          </Column>

          <Column field="type" header="Tipo" sortable>
            <template #body="{ data }">
              <Tag :value="data.type === 'income' ? 'Ingreso' : 'Gasto'" :severity="data.type === 'income' ? 'success' : 'danger'" />
            </template>
          </Column>

          <Column field="amount" header="Importe" sortable>
            <template #body="{ data }">
              <span :class="data.type === 'income' ? 'text-green' : 'text-red'">{{ formatCurrency(data.amount) }}</span>
            </template>
          </Column>

          <Column field="raw_movement" header="Movimiento">
            <template #body="{ data }">
              <span class="truncate-text">{{ data.raw_movement || '-' }}</span>
            </template>
          </Column>

          <Column field="comment_suggestion" header="Comentario sugerido">
            <template #body="{ data }">
              <span class="truncate-text">{{ data.comment_suggestion || '-' }}</span>
            </template>
          </Column>

          <Column field="status" header="Estado" sortable>
            <template #body="{ data }">
              <Tag :value="statusLabel(data.status)" :severity="statusSeverity(data.status)" />
            </template>
          </Column>

          <Column header="Acciones">
            <template #body="{ data }">
              <Button
                v-if="data.status === 'pending'"
                icon="pi pi-pencil"
                text
                rounded
                severity="secondary"
                @click="openProcessDialog(data)"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="showProcessDialog" modal header="Validar transaccion importada" :style="{ width: '720px' }">
      <div v-if="selectedItem" class="dialog-content">
        <div class="raw-preview">
          <div class="preview-item">
            <span>Banco origen</span>
            <strong>{{ bankLabel(selectedItem.source_bank) }}</strong>
          </div>
          <div class="preview-item">
            <span>Concepto</span>
            <strong>{{ selectedItem.raw_concept || '-' }}</strong>
          </div>
          <div class="preview-item">
            <span>Movimiento</span>
            <strong>{{ selectedItem.raw_movement || '-' }}</strong>
          </div>
          <div class="preview-item">
            <span>Importe detectado</span>
            <strong>{{ formatCurrency(selectedItem.amount) }}</strong>
          </div>
        </div>

        <div class="form-row">
          <div class="form-field">
            <label>Tipo</label>
            <Select v-model="processForm.type" :options="transactionTypeOptions" optionLabel="label" optionValue="value" class="w-full" />
          </div>
          <div class="form-field">
            <label>Presupuesto</label>
            <Select v-model="processForm.budget_id" :options="budgetOptions" optionLabel="label" optionValue="value" class="w-full" filter />
          </div>
        </div>

        <div class="form-row">
          <div class="form-field">
            <label>Categoria</label>
            <Select v-model="processForm.category" :options="availableCategories" optionLabel="name" optionValue="name" class="w-full" filter />
          </div>
          <div class="form-field">
            <label>Banco</label>
            <Select v-model="processForm.bank" :options="processingBankOptions" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-field">
            <label>Metodo de pago</label>
            <Select v-model="processForm.payment_method" :options="paymentMethodOptions" optionLabel="label" optionValue="value" class="w-full" />
          </div>
          <div class="form-field">
            <label>Fecha y hora</label>
            <Calendar v-model="processForm.timestamp" showTime hourFormat="24" dateFormat="dd/mm/yy" class="w-full" />
          </div>
        </div>

        <div class="form-field">
          <label>Comentario</label>
          <Textarea v-model="processForm.comment" rows="4" class="w-full" />
        </div>

        <div class="form-field checkbox-field">
          <Checkbox v-model="processForm.is_charged" :binary="true" inputId="processCharged" />
          <label for="processCharged">Crear la transaccion como cobrada</label>
        </div>
      </div>

      <template #footer>
        <Button label="Cancelar" text @click="showProcessDialog = false" />
        <Button label="Marcar procesada sin importar" severity="secondary" outlined @click="processSelected(false)" :loading="importedTransactionStore.loading" />
        <Button label="Procesar e incorporar" severity="success" @click="processSelected(true)" :loading="importedTransactionStore.loading" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useImportedTransactionStore } from '@/stores/importedTransactions'
import { useBudgetStore } from '@/stores/budgets'
import { useCategoryStore } from '@/stores/categories'
import { useFormatters } from '@/composables/useFormatters'
import { BUDGET_BANK_OPTIONS, formatBudgetOptionLabel } from '@/constants/banks'

const router = useRouter()
const toast = useToast()
const importedTransactionStore = useImportedTransactionStore()
const budgetStore = useBudgetStore()
const categoryStore = useCategoryStore()
const { formatCurrency, formatDateTime } = useFormatters()

const showProcessDialog = ref(false)
const selectedItem = ref(null)
const searchQuery = ref('')
const statusFilter = ref('pending')
const bankFilter = ref('all')

const processForm = ref({
  type: 'expense',
  budget_id: null,
  category: null,
  bank: 'BBVA',
  payment_method: 'debit',
  timestamp: new Date(),
  comment: '',
  is_charged: false
})

const statusOptions = [
  { label: 'Pendientes', value: 'pending' },
  { label: 'Importadas', value: 'processed_imported' },
  { label: 'Descartadas', value: 'processed_skipped' },
  { label: 'Todas', value: 'all' }
]

const bankOptions = [
  { label: 'Todos', value: 'all' },
  { label: 'BBVA', value: 'bbva' },
  { label: 'ING Direct', value: 'ing_direct' }
]

const processingBankOptions = BUDGET_BANK_OPTIONS

const paymentMethodOptions = [
  { label: 'Debito', value: 'debit' },
  { label: 'Credito', value: 'credit' },
  { label: 'Efectivo', value: 'cash' }
]

const transactionTypeOptions = [
  { label: 'Gasto', value: 'expense' },
  { label: 'Ingreso', value: 'income' }
]

const budgetOptions = computed(() => {
  const selectedBank = selectedItem.value ? bankLabel(selectedItem.value.source_bank) : null

  return budgetStore.budgets
    .filter((budget) => !selectedBank || !budget.bank || budget.bank === selectedBank)
    .map((budget) => ({
      label: formatBudgetOptionLabel(budget),
      value: budget._id
    }))
})

const availableCategories = computed(() => {
  return processForm.value.type === 'income' ? categoryStore.sortedIncomeCategories : categoryStore.sortedExpenseCategories
})

const filteredItems = computed(() => {
  let items = [...importedTransactionStore.importedTransactions]

  if (statusFilter.value !== 'all') {
    items = items.filter((item) => item.status === statusFilter.value)
  }

  if (bankFilter.value !== 'all') {
    items = items.filter((item) => item.source_bank === bankFilter.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    items = items.filter((item) => {
      return [item.raw_concept, item.raw_movement, item.raw_observations, item.comment_suggestion]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(query))
    })
  }

  return items
})

const pendingCount = computed(() => {
  return importedTransactionStore.importedTransactions.filter((item) => item.status === 'pending').length
})

const importedCount = computed(() => {
  return importedTransactionStore.importedTransactions.filter((item) => item.status === 'processed_imported').length
})

const skippedCount = computed(() => {
  return importedTransactionStore.importedTransactions.filter((item) => item.status === 'processed_skipped').length
})

const pendingAmount = computed(() => {
  return importedTransactionStore.importedTransactions
    .filter((item) => item.status === 'pending')
    .reduce((sum, item) => sum + Number(item.amount || 0), 0)
})

onMounted(async () => {
  await Promise.all([
    importedTransactionStore.fetchImportedTransactions({ limit: 1000 }),
    budgetStore.fetchBudgets(),
    categoryStore.fetchCategories()
  ])
})

const bankLabel = (value) => {
  return value === 'bbva' ? 'BBVA' : 'ING Direct'
}

const statusLabel = (value) => {
  if (value === 'processed_imported') return 'Importada'
  if (value === 'processed_skipped') return 'Procesada sin importar'
  return 'Pendiente'
}

const statusSeverity = (value) => {
  if (value === 'processed_imported') return 'success'
  if (value === 'processed_skipped') return 'secondary'
  return 'warning'
}

const openProcessDialog = (item) => {
  selectedItem.value = item
  processForm.value = {
    type: item.type,
    budget_id: null,
    category: null,
    bank: bankLabel(item.source_bank),
    payment_method: item.payment_method_suggestion || 'debit',
    timestamp: item.suggested_timestamp ? new Date(item.suggested_timestamp) : new Date(),
    comment: item.comment_suggestion || '',
    is_charged: false
  }
  showProcessDialog.value = true
}

const processSelected = async (importToSystem) => {
  if (!selectedItem.value) {
    return
  }

  if (importToSystem && (!processForm.value.budget_id || !processForm.value.category || !processForm.value.payment_method)) {
    toast.add({
      severity: 'warn',
      summary: 'Campos requeridos',
      detail: 'Selecciona presupuesto, categoria y metodo de pago para importar al sistema.',
      life: 4000
    })
    return
  }

  try {
    await importedTransactionStore.processImportedTransaction(selectedItem.value._id, {
      import_to_system: importToSystem,
      type: processForm.value.type,
      budget_id: processForm.value.budget_id,
      category: processForm.value.category,
      bank: processForm.value.bank,
      payment_method: processForm.value.payment_method,
      comment: processForm.value.comment,
      timestamp: processForm.value.timestamp?.toISOString(),
      is_charged: processForm.value.is_charged
    })

    toast.add({
      severity: 'success',
      summary: importToSystem ? 'Transaccion incorporada' : 'Movimiento procesado',
      detail: importToSystem ? 'La transaccion se incorporo al sistema correctamente.' : 'El movimiento se marco como procesado sin importar.',
      life: 4000
    })

    showProcessDialog.value = false
    selectedItem.value = null
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'No se pudo procesar el movimiento importado.',
      life: 5000
    })
  }
}
</script>

<style scoped>
.import-review-view {
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
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 1fr);
  gap: 1.25rem;
  padding: 1.5rem;
  border-radius: 32px;
  background: var(--hero-gradient);
  border: 1px solid var(--surface-border);
  box-shadow: var(--shadow-lg);
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
  background: rgba(255, 255, 255, 0.68);
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 700;
}

.page-title {
  max-width: 13ch;
  font-size: clamp(2.1rem, 3.8vw, 3.3rem);
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--heading-color);
}

.page-subtitle {
  max-width: 62ch;
  color: var(--text-color-secondary);
  line-height: 1.7;
}

.hero-metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.hero-metric-tile,
.preview-item {
  padding: 1rem;
  border-radius: 20px;
  border: 1px solid rgba(124, 97, 61, 0.12);
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(12px);
}

.hero-metric-tile span,
.preview-item span {
  display: block;
  margin-bottom: 0.3rem;
  color: var(--text-color-secondary);
  font-size: 0.82rem;
}

.hero-metric-tile strong,
.preview-item strong {
  color: var(--heading-color);
  font-size: 1.18rem;
}

.filters-card,
.table-card {
  border-radius: 28px;
  border: 1px solid var(--surface-border);
  box-shadow: var(--shadow-sm);
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.filters-header h2 {
  margin-top: 0.6rem;
  font-size: 1.2rem;
}

.filters-grid,
.form-row,
.raw-preview {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.form-row {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.filter-field,
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-field label,
.form-field label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-color);
}

.truncate-text {
  display: inline-block;
  max-width: 240px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.checkbox-field {
  flex-direction: row;
  align-items: center;
}

.text-green {
  color: var(--success-color);
  font-weight: 700;
}

.text-red {
  color: var(--danger-color);
  font-weight: 700;
}

.w-full {
  width: 100%;
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

@media (max-width: 1100px) {
  .hero-panel,
  .filters-grid,
  .raw-preview {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-panel {
    padding: 1.1rem;
    border-radius: 24px;
  }

  .hero-metrics-grid,
  .form-row {
    grid-template-columns: 1fr;
  }

  .filters-header {
    flex-direction: column;
  }
}
</style>
