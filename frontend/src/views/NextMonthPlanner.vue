<template>
  <div class="next-month-planner-view">
    <section class="planner-hero">
      <div class="hero-copy">
        <span class="section-kicker">Planeacion mensual</span>
        <h1>{{ budgetMonth }}</h1>
        <p>Prepara ING y BBVA como borradores coordinados, ajusta ingresos temporales, reparte categorias y decide cuanto transferir al presupuesto operativo.</p>
      </div>

      <div class="hero-metrics">
        <div class="hero-metric-tile">
          <span>Ingresos previstos ING</span>
          <strong>{{ formatCurrency(ingIncomeTotal + ingTemporaryIncomeTotal) }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>Transferencia planificada</span>
          <strong>{{ formatCurrency(ingForm.transferAmount) }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>Gastos BBVA</span>
          <strong>{{ formatCurrency(bbvaExpenseTotal) }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>Margen ING</span>
          <strong :class="{ 'text-red': ingRemainingAfterTransfer < 0, 'text-green': ingRemainingAfterTransfer >= 0 }">{{ formatCurrency(ingRemainingAfterTransfer) }}</strong>
        </div>
      </div>
    </section>

    <div v-if="loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando planificacion...</p>
    </div>

    <div v-else-if="missingPair" class="empty-state planner-empty">
      <i class="pi pi-calendar"></i>
      <h2>No existe un par de borradores para {{ budgetMonth }}</h2>
      <p>Primero crea el presupuesto de ING y BBVA desde la configuracion inicial.</p>
      <Button label="Ir a configuracion inicial" icon="pi pi-arrow-right" @click="router.push({ name: 'next-month-planner-setup' })" />
    </div>

    <template v-else>
      <section class="planner-shell">
        <Card class="planner-bank-card planner-bank-card-ing">
          <template #content>
            <div class="bank-card-header">
              <div>
                <span class="bank-kicker">ING Direct</span>
                <InputText v-model="ingForm.name" class="bank-name-input" />
                <small>{{ formatDateRange(ingForm.start_date, ingForm.end_date) }}</small>
              </div>

              <div class="bank-card-actions">
                <Button label="Recurrentes" icon="pi pi-refresh" outlined size="small" @click="openRecurringDialog('ing')" />
                <Button label="Guardar ING" icon="pi pi-check" severity="warning" size="small" @click="savePlannerBudget('ing')" :loading="savingKey === 'ing'" />
              </div>
            </div>

            <div class="metric-strip">
              <div class="metric-chip success">
                <span>Ingresos</span>
                <strong>{{ formatCurrency(ingIncomeTotal) }}</strong>
              </div>
              <div class="metric-chip">
                <span>Temporales</span>
                <strong>{{ formatCurrency(ingTemporaryIncomeTotal) }}</strong>
              </div>
              <div class="metric-chip warning">
                <span>Salidas ING</span>
                <strong>{{ formatCurrency(ingExpenseTotal) }}</strong>
              </div>
            </div>

            <div class="planner-section">
              <div class="section-header">
                <div>
                  <span class="section-kicker subtle">Ingresos planificados</span>
                  <h3>Nomina e ingresos previstos</h3>
                </div>
                <Button label="Agregar ingreso" icon="pi pi-plus" text size="small" @click="addCategoryRow('ing', 'income')" />
              </div>

              <div v-if="ingForm.incomeItems.length === 0" class="empty-inline-state">Aun no hay ingresos planificados.</div>

              <div v-else class="line-items-list">
                <div v-for="row in ingForm.incomeItems" :key="row.id" class="line-item-row">
                  <Select v-model="row.category_id" :options="incomeCategoryOptions" optionLabel="displayName" optionValue="_id" class="flex-select" filter filterBy="name,displayName">
                    <template #option="{ option }">
                      <div class="category-option">
                        <span v-if="option.parent_id" class="subcategory-indicator">↳</span>
                        <i :class="normalizeIcon(option.icon)" :style="{ color: option.color }"></i>
                        <span>{{ option.displayName }}</span>
                      </div>
                    </template>
                  </Select>
                  <InputNumber v-model="row.planned_amount" mode="currency" currency="EUR" locale="es-ES" :minFractionDigits="2" class="amount-input" />
                  <Button icon="pi pi-trash" text severity="danger" @click="removeCategoryRow('ing', 'income', row.id)" />
                </div>
              </div>
            </div>

            <div class="planner-section temporary-income-section">
              <div class="section-header">
                <div>
                  <span class="section-kicker subtle">Ajustes temporales</span>
                  <h3>Ingresos temporales</h3>
                </div>
                <Button label="Agregar temporal" icon="pi pi-plus" text size="small" @click="addTemporaryIncome" />
              </div>

              <div v-if="ingForm.temporaryIncomes.length === 0" class="empty-inline-state">Usa esta zona para ingresos no reales que solo sirven para planear el mes.</div>

              <div v-else class="line-items-list">
                <div v-for="row in ingForm.temporaryIncomes" :key="row.id" class="line-item-row temp-row">
                  <InputText v-model="row.label" class="flex-select" placeholder="ej. Bonus estimado" />
                  <InputNumber v-model="row.amount" mode="currency" currency="EUR" locale="es-ES" :minFractionDigits="2" class="amount-input" />
                  <Button icon="pi pi-trash" text severity="danger" @click="removeTemporaryIncome(row.id)" />
                </div>
              </div>
            </div>

            <div class="planner-section">
              <div class="section-header">
                <div>
                  <span class="section-kicker subtle">Salidas ING</span>
                  <h3>Gastos o ajustes del presupuesto origen</h3>
                </div>
                <Button label="Agregar salida" icon="pi pi-plus" text size="small" @click="addCategoryRow('ing', 'expense')" />
              </div>

              <div v-if="ingForm.expenseItems.length === 0" class="empty-inline-state">No hay otras salidas planificadas en ING.</div>

              <div v-else class="line-items-list">
                <div v-for="row in ingForm.expenseItems" :key="row.id" class="line-item-row">
                  <Select v-model="row.category_id" :options="expenseCategoryOptions" optionLabel="displayName" optionValue="_id" class="flex-select" filter filterBy="name,displayName">
                    <template #option="{ option }">
                      <div class="category-option">
                        <span v-if="option.parent_id" class="subcategory-indicator">↳</span>
                        <i :class="normalizeIcon(option.icon)" :style="{ color: option.color }"></i>
                        <span>{{ option.displayName }}</span>
                      </div>
                    </template>
                  </Select>
                  <InputNumber v-model="row.planned_amount" mode="currency" currency="EUR" locale="es-ES" :minFractionDigits="2" class="amount-input" />
                  <Button icon="pi pi-trash" text severity="danger" @click="removeCategoryRow('ing', 'expense', row.id)" />
                </div>
              </div>
            </div>

            <div class="transfer-card">
              <div>
                <span class="section-kicker subtle">Transferencia</span>
                <h3>Traspaso previsto hacia BBVA</h3>
                <p>El importe sugerido se basa en los gastos planificados del presupuesto BBVA.</p>
              </div>

              <div class="transfer-controls">
                <InputNumber v-model="ingForm.transferAmount" mode="currency" currency="EUR" locale="es-ES" :minFractionDigits="2" class="amount-input transfer-input" />
                <Button label="Usar sugerido" icon="pi pi-sync" outlined size="small" @click="syncTransferToSuggestion" />
              </div>

              <div class="transfer-metrics">
                <div class="metric-chip info">
                  <span>Sugerido</span>
                  <strong>{{ formatCurrency(suggestedTransferAmount) }}</strong>
                </div>
                <div class="metric-chip" :class="ingRemainingAfterTransfer < 0 ? 'danger' : 'success'">
                  <span>Saldo ING tras transferir</span>
                  <strong>{{ formatCurrency(ingRemainingAfterTransfer) }}</strong>
                </div>
                <div class="metric-chip" :class="bbvaCoverageDelta < 0 ? 'danger' : 'info'">
                  <span>Cobertura BBVA</span>
                  <strong>{{ formatCurrency(bbvaCoverageDelta) }}</strong>
                </div>
              </div>
            </div>
          </template>
        </Card>

        <Card class="planner-bank-card planner-bank-card-bbva">
          <template #content>
            <div class="bank-card-header">
              <div>
                <span class="bank-kicker">BBVA</span>
                <InputText v-model="bbvaForm.name" class="bank-name-input" />
                <small>{{ formatDateRange(bbvaForm.start_date, bbvaForm.end_date) }}</small>
              </div>

              <div class="bank-card-actions">
                <Button label="Recurrentes" icon="pi pi-refresh" outlined size="small" @click="openRecurringDialog('bbva')" />
                <Button label="Guardar BBVA" icon="pi pi-check" severity="primary" size="small" @click="savePlannerBudget('bbva')" :loading="savingKey === 'bbva'" />
              </div>
            </div>

            <div class="metric-strip">
              <div class="metric-chip warning">
                <span>Gastos planificados</span>
                <strong>{{ formatCurrency(bbvaExpenseTotal) }}</strong>
              </div>
              <div class="metric-chip info">
                <span>Transferencia desde ING</span>
                <strong>{{ formatCurrency(ingForm.transferAmount) }}</strong>
              </div>
              <div class="metric-chip" :class="bbvaCoverageDelta < 0 ? 'danger' : 'success'">
                <span>Diferencia</span>
                <strong>{{ formatCurrency(bbvaCoverageDelta) }}</strong>
              </div>
            </div>

            <div class="planner-section">
              <div class="section-header">
                <div>
                  <span class="section-kicker subtle">Presupuesto operativo</span>
                  <h3>Gastos del mes en BBVA</h3>
                </div>
                <Button label="Agregar categoria" icon="pi pi-plus" text size="small" @click="addCategoryRow('bbva', 'expense')" />
              </div>

              <div v-if="bbvaForm.expenseItems.length === 0" class="empty-inline-state">No hay categorias de gasto en BBVA todavia.</div>

              <div v-else class="line-items-list">
                <div v-for="row in bbvaForm.expenseItems" :key="row.id" class="line-item-row">
                  <Select v-model="row.category_id" :options="expenseCategoryOptions" optionLabel="displayName" optionValue="_id" class="flex-select" filter filterBy="name,displayName">
                    <template #option="{ option }">
                      <div class="category-option">
                        <span v-if="option.parent_id" class="subcategory-indicator">↳</span>
                        <i :class="normalizeIcon(option.icon)" :style="{ color: option.color }"></i>
                        <span>{{ option.displayName }}</span>
                      </div>
                    </template>
                  </Select>
                  <InputNumber v-model="row.planned_amount" mode="currency" currency="EUR" locale="es-ES" :minFractionDigits="2" class="amount-input" />
                  <Button icon="pi pi-trash" text severity="danger" @click="removeCategoryRow('bbva', 'expense', row.id)" />
                </div>
              </div>
            </div>

            <div class="bbva-insight-card">
              <div>
                <span class="section-kicker subtle">Lectura rapida</span>
                <h3>Viabilidad del gasto BBVA</h3>
                <p>{{ bbvaCoverageDelta < 0 ? 'El traspaso actual no cubre todos los gastos planificados de BBVA.' : bbvaCoverageDelta > 0 ? 'La transferencia supera el gasto previsto y deja margen en BBVA.' : 'La transferencia coincide exactamente con el gasto previsto.' }}</p>
              </div>

              <div class="transfer-metrics">
                <div class="metric-chip warning">
                  <span>Total gastos</span>
                  <strong>{{ formatCurrency(bbvaExpenseTotal) }}</strong>
                </div>
                <div class="metric-chip info">
                  <span>Transferencia</span>
                  <strong>{{ formatCurrency(ingForm.transferAmount) }}</strong>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </section>

      <div class="planner-footer-actions">
        <Button label="Volver a configuracion" icon="pi pi-arrow-left" text @click="router.push({ name: 'next-month-planner-setup' })" />
        <Button label="Guardar ambos borradores" icon="pi pi-save" severity="success" @click="saveAllBudgets" :loading="savingKey === 'all'" />
      </div>
    </template>

    <Dialog v-model:visible="showRecurringDialog" modal header="Asignar gastos recurrentes" :style="{ width: '760px' }">
      <div class="recurring-dialog-content">
        <p class="recurring-dialog-copy">Selecciona los gastos recurrentes que quieres incorporar como planificados en <strong>{{ recurringDialogTargetLabel }}</strong>.</p>

        <div v-if="recurringStore.activeExpenses.length === 0" class="empty-inline-state">No hay gastos recurrentes activos disponibles.</div>

        <div v-else class="recurring-picker-list">
          <label v-for="expense in recurringStore.activeExpenses" :key="expense._id" class="recurring-picker-item">
            <Checkbox v-model="selectedRecurringIds" :value="expense._id" />
            <div class="recurring-picker-copy">
              <strong>{{ expense.name }}</strong>
              <small>{{ expense.category }} · {{ formatCurrency(expense.amount) }} · {{ formatFrequency(expense.frequency) }}</small>
            </div>
          </label>
        </div>
      </div>

      <template #footer>
        <Button label="Cancelar" text @click="showRecurringDialog = false" />
        <Button label="Aplicar al presupuesto" icon="pi pi-check" severity="success" @click="applyRecurringSelection" :loading="recurringStore.loading" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useBudgetStore } from '@/stores/budgets'
import { useCategoryStore } from '@/stores/categories'
import { useRecurringStore } from '@/stores/recurring'
import { useFormatters } from '@/composables/useFormatters'

const TRANSFER_CATEGORY = 'Transferido Cuentas'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const budgetStore = useBudgetStore()
const categoryStore = useCategoryStore()
const recurringStore = useRecurringStore()
const { formatCurrency, formatDateRange, formatFrequency } = useFormatters()

const budgetMonth = computed(() => String(route.params.budgetMonth || ''))
const loading = ref(true)
const savingKey = ref(null)
const showRecurringDialog = ref(false)
const recurringDialogTarget = ref(null)
const selectedRecurringIds = ref([])

const createRowId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`

const normalizeIcon = (icon) => {
  if (!icon) return 'pi pi-tag'
  if (icon.startsWith('pi pi-')) return icon
  if (icon.startsWith('pi-')) return `pi ${icon}`
  return `pi pi-${icon}`
}

const createCategoryRow = (categoryId = '', plannedAmount = null) => ({
  id: createRowId(),
  category_id: categoryId,
  planned_amount: plannedAmount
})

const createTemporaryIncomeRow = (label = '', amount = null) => ({
  id: createRowId(),
  label,
  amount
})

const ingForm = ref({
  id: null,
  name: '',
  start_date: null,
  end_date: null,
  incomeItems: [],
  expenseItems: [],
  transferAmount: null,
  temporaryIncomes: []
})

const bbvaForm = ref({
  id: null,
  name: '',
  start_date: null,
  end_date: null,
  expenseItems: []
})

const categoryByName = computed(() => {
  const lookup = {}
  categoryStore.categories.forEach((category) => {
    lookup[category.name] = category
  })
  return lookup
})

const categoryById = computed(() => {
  const lookup = {}
  categoryStore.categories.forEach((category) => {
    lookup[category._id] = category
  })
  return lookup
})

const incomeCategoryOptions = computed(() => {
  return categoryStore.sortedIncomeCategories.map((category) => ({
    ...category,
    displayName: category.parent_id ? `↳ ${category.name}` : category.name
  }))
})

const defaultIncomeCategoryId = computed(() => {
  const payrollCategory = incomeCategoryOptions.value.find((category) => /nomina/i.test(category.name))
  return payrollCategory?._id || incomeCategoryOptions.value[0]?._id || ''
})

const expenseCategoryOptions = computed(() => {
  return categoryStore.sortedExpenseCategories.map((category) => ({
    ...category,
    displayName: category.parent_id ? `↳ ${category.name}` : category.name
  }))
})

const draftsForMonth = computed(() => {
  return budgetStore.draftBudgets.filter((budget) => budget.budget_month === budgetMonth.value)
})

const ingBudget = computed(() => draftsForMonth.value.find((budget) => budget.bank === 'ING Direct') || null)
const bbvaBudget = computed(() => draftsForMonth.value.find((budget) => budget.bank === 'BBVA') || null)
const missingPair = computed(() => !ingBudget.value || !bbvaBudget.value)

const sumAmounts = (items = [], field = 'planned_amount') => {
  return items.reduce((sum, item) => sum + (Number(item?.[field] || 0)), 0)
}

const ingIncomeTotal = computed(() => sumAmounts(ingForm.value.incomeItems))
const ingTemporaryIncomeTotal = computed(() => sumAmounts(ingForm.value.temporaryIncomes, 'amount'))
const ingExpenseTotal = computed(() => sumAmounts(ingForm.value.expenseItems))
const bbvaExpenseTotal = computed(() => sumAmounts(bbvaForm.value.expenseItems))
const suggestedTransferAmount = computed(() => bbvaExpenseTotal.value)
const ingAvailableBeforeTransfer = computed(() => ingIncomeTotal.value + ingTemporaryIncomeTotal.value - ingExpenseTotal.value)
const ingRemainingAfterTransfer = computed(() => ingAvailableBeforeTransfer.value - Number(ingForm.value.transferAmount || 0))
const bbvaCoverageDelta = computed(() => Number(ingForm.value.transferAmount || 0) - bbvaExpenseTotal.value)

const recurringDialogTargetLabel = computed(() => {
  if (recurringDialogTarget.value === 'ing') return ingForm.value.name || 'ING Direct'
  if (recurringDialogTarget.value === 'bbva') return bbvaForm.value.name || 'BBVA'
  return 'presupuesto seleccionado'
})

const resolveCategoryId = (categoryValue) => {
  if (!categoryValue) {
    return ''
  }

  if (categoryById.value[categoryValue]) {
    return categoryValue
  }

  return categoryStore.categories.find((category) => category.name === categoryValue)?._id || ''
}

const resolveCategoryName = (categoryId) => {
  if (!categoryId) {
    return ''
  }

  return categoryById.value[categoryId]?.name || ''
}

const isIncomeCategory = (categoryValue) => {
  const category = categoryById.value[categoryValue] || categoryByName.value[categoryValue]
  return category ? category.type === 'income' || category.type === 'both' : /nomina|ingreso/i.test(categoryValue || '')
}

const mapBudgetToForm = (budget) => {
  const items = Array.isArray(budget?.budget_items) ? budget.budget_items : []
  const transferItem = items.find((item) => item.category === TRANSFER_CATEGORY)

  return {
    id: budget._id,
    name: budget.name,
    start_date: budget.start_date,
    end_date: budget.end_date,
    incomeItems: budget.bank === 'ING Direct'
      ? items
        .filter((item) => item.category !== TRANSFER_CATEGORY && isIncomeCategory(item.category_id || item.category))
        .map((item) => createCategoryRow(resolveCategoryId(item.category_id || item.category), Number(item.planned_amount)))
      : [],
    expenseItems: items
      .filter((item) => item.category !== TRANSFER_CATEGORY && (budget.bank === 'BBVA' || !isIncomeCategory(item.category_id || item.category)))
      .map((item) => createCategoryRow(resolveCategoryId(item.category_id || item.category), Number(item.planned_amount))),
    transferAmount: budget.bank === 'ING Direct' ? Number(transferItem?.planned_amount || 0) : null,
    temporaryIncomes: budget.bank === 'ING Direct'
      ? (budget.planning_metadata?.temporary_incomes || []).map((item) => createTemporaryIncomeRow(item.label, Number(item.amount)))
      : []
  }
}

const hydrateForms = () => {
  if (ingBudget.value) {
    ingForm.value = mapBudgetToForm(ingBudget.value)
    if (ingForm.value.incomeItems.length === 0) {
      ingForm.value.incomeItems.push(createCategoryRow(defaultIncomeCategoryId.value))
    }
  }

  if (bbvaBudget.value) {
    bbvaForm.value = mapBudgetToForm(bbvaBudget.value)
    if (bbvaForm.value.expenseItems.length === 0) {
      bbvaForm.value.expenseItems.push(createCategoryRow())
    }
  }
}

const loadPlanner = async () => {
  loading.value = true
  try {
    await Promise.all([
      budgetStore.fetchBudgets({ status: 'draft', limit: 1000 }),
      categoryStore.fetchCategories(),
      recurringStore.fetchRecurringExpenses({ is_active: true, limit: 1000 })
    ])
    hydrateForms()
  } finally {
    loading.value = false
  }
}

onMounted(loadPlanner)

const addCategoryRow = (bankKey, section) => {
  if (bankKey === 'ing' && section === 'income') ingForm.value.incomeItems.push(createCategoryRow())
  if (bankKey === 'ing' && section === 'expense') ingForm.value.expenseItems.push(createCategoryRow())
  if (bankKey === 'bbva') bbvaForm.value.expenseItems.push(createCategoryRow())
}

const removeCategoryRow = (bankKey, section, rowId) => {
  if (bankKey === 'ing' && section === 'income') {
    ingForm.value.incomeItems = ingForm.value.incomeItems.filter((row) => row.id !== rowId)
  }
  if (bankKey === 'ing' && section === 'expense') {
    ingForm.value.expenseItems = ingForm.value.expenseItems.filter((row) => row.id !== rowId)
  }
  if (bankKey === 'bbva') {
    bbvaForm.value.expenseItems = bbvaForm.value.expenseItems.filter((row) => row.id !== rowId)
  }
}

const addTemporaryIncome = () => {
  ingForm.value.temporaryIncomes.push(createTemporaryIncomeRow())
}

const removeTemporaryIncome = (rowId) => {
  ingForm.value.temporaryIncomes = ingForm.value.temporaryIncomes.filter((row) => row.id !== rowId)
}

const syncTransferToSuggestion = () => {
  ingForm.value.transferAmount = suggestedTransferAmount.value
}

const collapseItems = (items) => {
  const merged = new Map()

  items.forEach((item) => {
    const currentAmount = Number(item.planned_amount || 0)
    const itemKey = item.category_id || item.category
    if (!merged.has(itemKey)) {
      merged.set(itemKey, {
        category_id: item.category_id || '',
        category: item.category || resolveCategoryName(item.category_id),
        planned_amount: currentAmount
      })
      return
    }

    merged.get(itemKey).planned_amount += currentAmount
  })

  return Array.from(merged.values()).map((item) => ({
    category_id: item.category_id || null,
    category: item.category,
    planned_amount: item.planned_amount,
    spent_amount: 0
  }))
}

const sanitizeCategoryRows = (rows, sectionLabel) => {
  return rows.reduce((result, row) => {
    const categoryId = String(row.category_id || '').trim()
    const plannedAmount = Number(row.planned_amount || 0)

    if (!categoryId && !plannedAmount) {
      return result
    }

    if (!categoryId || plannedAmount <= 0) {
      throw new Error(`Completa correctamente los valores de ${sectionLabel}.`)
    }

    result.push({ category_id: categoryId, category: resolveCategoryName(categoryId), planned_amount: plannedAmount, spent_amount: 0 })
    return result
  }, [])
}

const sanitizeTemporaryIncomes = (rows) => {
  return rows.reduce((result, row) => {
    const label = String(row.label || '').trim()
    const amount = Number(row.amount || 0)

    if (!label && !amount) {
      return result
    }

    if (!label || amount <= 0) {
      throw new Error('Completa correctamente los ingresos temporales.')
    }

    result.push({ label, amount })
    return result
  }, [])
}

const buildPayload = (bankKey) => {
  if (bankKey === 'ing') {
    const incomeItems = sanitizeCategoryRows(ingForm.value.incomeItems, 'los ingresos de ING')
    const expenseItems = sanitizeCategoryRows(ingForm.value.expenseItems, 'las salidas de ING')
    const temporaryIncomes = sanitizeTemporaryIncomes(ingForm.value.temporaryIncomes)
    const transferAmount = Number(ingForm.value.transferAmount || 0)
    const transferCategoryId = resolveCategoryId(TRANSFER_CATEGORY)
    const transferItems = transferAmount > 0
      ? [{ category_id: transferCategoryId, category: TRANSFER_CATEGORY, planned_amount: transferAmount, spent_amount: 0 }]
      : []

    return {
      name: ingForm.value.name.trim(),
      budget_month: budgetMonth.value,
      status: 'draft',
      budget_items: collapseItems([...incomeItems, ...expenseItems, ...transferItems]),
      planning_metadata: {
        planner_type: 'next-month',
        counterpart_bank: 'BBVA',
        temporary_incomes: temporaryIncomes
      }
    }
  }

  const expenseItems = sanitizeCategoryRows(bbvaForm.value.expenseItems, 'los gastos de BBVA')
  return {
    name: bbvaForm.value.name.trim(),
    budget_month: budgetMonth.value,
    status: 'draft',
    budget_items: collapseItems(expenseItems),
    planning_metadata: {
      planner_type: 'next-month',
      counterpart_bank: 'ING Direct',
      temporary_incomes: []
    }
  }
}

const savePlannerBudget = async (bankKey) => {
  const targetBudget = bankKey === 'ing' ? ingBudget.value : bbvaBudget.value
  if (!targetBudget) {
    return
  }

  const targetName = bankKey === 'ing' ? 'ING' : 'BBVA'

  try {
    savingKey.value = bankKey
    const payload = buildPayload(bankKey)

    if (!payload.name) {
      throw new Error(`El nombre del presupuesto ${targetName} es obligatorio.`)
    }

    await budgetStore.updateBudget(targetBudget._id, payload)
    await budgetStore.fetchBudgets({ status: 'draft', limit: 1000 })
    hydrateForms()

    toast.add({ severity: 'success', summary: `${targetName} guardado`, detail: 'El borrador se ha actualizado correctamente.', life: 3500 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'No se pudo guardar', detail: error.message || error.response?.data?.detail || 'Revisa los datos del presupuesto.', life: 5000 })
  } finally {
    savingKey.value = null
  }
}

const saveAllBudgets = async () => {
  savingKey.value = 'all'
  try {
    await savePlannerBudget('ing')
    await savePlannerBudget('bbva')
  } finally {
    savingKey.value = null
  }
}

const openRecurringDialog = (target) => {
  recurringDialogTarget.value = target
  selectedRecurringIds.value = []
  showRecurringDialog.value = true
}

const applyRecurringSelection = async () => {
  if (!recurringDialogTarget.value || selectedRecurringIds.value.length === 0) {
    toast.add({ severity: 'warn', summary: 'Selecciona recurrentes', detail: 'Debes marcar al menos un gasto recurrente.', life: 3500 })
    return
  }

  const budgetId = recurringDialogTarget.value === 'ing' ? ingBudget.value?._id : bbvaBudget.value?._id
  if (!budgetId) {
    return
  }

  try {
    const response = await recurringStore.applyToBudget(budgetId, selectedRecurringIds.value)
    await budgetStore.fetchBudgets({ status: 'draft', limit: 1000 })

    if (response?.bank === 'ING Direct') {
      ingForm.value = mapBudgetToForm(response)
    } else if (response?.bank === 'BBVA') {
      bbvaForm.value = mapBudgetToForm(response)
    } else {
      hydrateForms()
    }

    showRecurringDialog.value = false
    toast.add({ severity: 'success', summary: 'Recurrentes aplicados', detail: 'Las categorias recurrentes se han añadido al presupuesto.', life: 3500 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'No se pudieron aplicar', detail: error.response?.data?.detail || 'Intentalo de nuevo.', life: 5000 })
  }
}
</script>

<style scoped>
.next-month-planner-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.planner-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 1fr);
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 30px;
  background: linear-gradient(135deg, rgba(15, 139, 111, 0.12) 0%, rgba(10, 74, 191, 0.08) 52%, rgba(249, 115, 22, 0.12) 100%);
  border: 1px solid var(--surface-border);
}

.section-kicker,
.bank-kicker {
  display: inline-flex;
  width: fit-content;
  padding: 0.38rem 0.78rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--primary-color);
}

.section-kicker.subtle {
  background: color-mix(in srgb, var(--surface-ground) 78%, transparent);
}

.hero-copy h1 {
  margin: 0.65rem 0 0.4rem;
  font-size: clamp(2rem, 3vw, 3rem);
}

.hero-copy p,
.transfer-card p,
.bbva-insight-card p,
.recurring-dialog-copy,
.empty-inline-state {
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.hero-metric-tile,
.metric-chip,
.transfer-card,
.bbva-insight-card,
.line-item-row,
.recurring-picker-item {
  border-radius: 22px;
  border: 1px solid var(--surface-border);
  background: color-mix(in srgb, var(--surface-card) 86%, transparent);
}

.hero-metric-tile {
  padding: 1rem;
}

.hero-metric-tile span,
.metric-chip span {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--text-color-secondary);
  font-size: 0.78rem;
}

.hero-metric-tile strong,
.metric-chip strong {
  font-size: 1.15rem;
}

.planner-shell {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  align-items: start;
}

.planner-bank-card {
  border-radius: 28px;
}

.planner-bank-card-ing {
  box-shadow: inset 0 0 0 1px rgba(249, 115, 22, 0.1);
}

.planner-bank-card-bbva {
  box-shadow: inset 0 0 0 1px rgba(10, 74, 191, 0.1);
}

.bank-card-header,
.section-header,
.planner-footer-actions,
.bank-card-actions,
.transfer-controls,
.transfer-metrics,
.metric-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
}

.bank-card-header {
  align-items: flex-start;
  margin-bottom: 1rem;
}

.bank-name-input {
  display: block;
  margin: 0.65rem 0 0.35rem;
  font-size: 1.35rem;
  font-weight: 700;
  width: min(100%, 320px);
}

.bank-card-header small {
  color: var(--text-color-secondary);
}

.metric-strip,
.transfer-metrics {
  flex-wrap: wrap;
}

.metric-chip {
  padding: 0.9rem 1rem;
  min-width: 150px;
}

.metric-chip.success {
  background: rgba(16, 185, 129, 0.08);
}

.metric-chip.warning {
  background: rgba(245, 158, 11, 0.1);
}

.metric-chip.info {
  background: rgba(59, 130, 246, 0.08);
}

.metric-chip.danger {
  background: rgba(239, 68, 68, 0.08);
}

.planner-section {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin-top: 1.2rem;
}

.section-header {
  align-items: flex-start;
}

.section-header h3,
.transfer-card h3,
.bbva-insight-card h3 {
  margin: 0.55rem 0 0.3rem;
}

.line-items-list,
.recurring-picker-list {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.line-item-row,
.recurring-picker-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 0.8rem;
}

.flex-select {
  flex: 1;
}

.amount-input {
  width: 170px;
}

.transfer-card,
.bbva-insight-card {
  margin-top: 1.2rem;
  padding: 1rem;
}

.transfer-input {
  width: 190px;
}

.temporary-income-section {
  background: color-mix(in srgb, var(--surface-ground) 70%, transparent);
  padding: 1rem;
  border-radius: 24px;
}

.temp-row {
  background: rgba(255, 255, 255, 0.78);
}

.category-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.subcategory-indicator {
  color: var(--text-color-secondary);
  font-weight: 600;
}

.recurring-picker-item {
  align-items: flex-start;
}

.recurring-picker-copy {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.recurring-picker-copy small {
  color: var(--text-color-secondary);
}

.planner-footer-actions {
  justify-content: flex-end;
}

.planner-empty,
.loading-state {
  text-align: center;
  padding: 3rem 1rem;
}

.planner-empty i,
.loading-state i {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.text-green {
  color: var(--success-color);
}

.text-red {
  color: var(--danger-color);
}

@media (max-width: 1200px) {
  .planner-hero,
  .planner-shell {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-metrics {
    grid-template-columns: 1fr;
  }

  .bank-card-header,
  .section-header,
  .line-item-row,
  .planner-footer-actions,
  .transfer-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .amount-input,
  .transfer-input {
    width: 100%;
  }
}
</style>
