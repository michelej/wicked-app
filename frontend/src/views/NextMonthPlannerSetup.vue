<template>
  <div class="planner-setup-view">
    <section class="setup-hero">
      <div class="setup-copy">
        <span class="section-kicker">Planeacion</span>
        <h1>Preparar presupuestos del mes siguiente</h1>
        <p>
          Crea el borrador de ING y BBVA para el siguiente mes, define el nombre de ambos presupuestos y el valor de
          <strong>Mes del presupuesto</strong> que agrupara la pareja.
        </p>
      </div>

      <div class="setup-summary-card">
        <span class="summary-kicker">Periodo sugerido</span>
        <strong>{{ periodLabel }}</strong>
        <small>{{ formatDateRange(form.start_date, form.end_date) }}</small>
      </div>
    </section>

    <div class="setup-grid">
      <Card class="setup-form-card">
        <template #content>
          <div class="card-header-block">
            <div>
              <span class="section-kicker">Configuracion inicial</span>
              <h2>Datos del par de presupuestos</h2>
            </div>
            <Tag :value="existingPair ? 'Borradores encontrados' : 'Nueva planificacion'" :severity="existingPair ? 'info' : 'success'" />
          </div>

          <div class="form-grid">
            <div class="form-field">
              <label for="budgetMonth">Mes del presupuesto</label>
              <InputText id="budgetMonth" v-model="form.budget_month" class="w-full" />
              <small>Formato esperado: `Mes-YYYY`.</small>
            </div>

            <div class="form-field">
              <label for="ingName">Nombre presupuesto ING</label>
              <InputText id="ingName" v-model="form.ing_name" class="w-full" />
            </div>

            <div class="form-field">
              <label for="bbvaName">Nombre presupuesto BBVA</label>
              <InputText id="bbvaName" v-model="form.bbva_name" class="w-full" />
            </div>

            <div class="form-field">
              <label for="startDate">Fecha de inicio</label>
              <Calendar id="startDate" v-model="form.start_date" dateFormat="dd/mm/yy" class="w-full" />
            </div>

            <div class="form-field">
              <label for="endDate">Fecha de fin</label>
              <Calendar id="endDate" v-model="form.end_date" dateFormat="dd/mm/yy" class="w-full" />
            </div>
          </div>

          <div class="period-preview">
            <div class="preview-metric">
              <span>Inicio</span>
              <strong>{{ formatDate(form.start_date) }}</strong>
            </div>
            <div class="preview-metric">
              <span>Fin</span>
              <strong>{{ formatDate(form.end_date) }}</strong>
            </div>
            <div class="preview-metric">
              <span>Estado</span>
              <strong>Borrador</strong>
            </div>
          </div>

          <div class="action-row">
            <Button label="Volver a presupuestos" text icon="pi pi-arrow-left" @click="router.push({ name: 'budgets' })" />
            <Button
              :label="existingPair ? 'Continuar planificacion' : 'Crear borradores y continuar'"
              icon="pi pi-arrow-right"
              severity="success"
              @click="createOrContinue"
              :loading="budgetStore.loading || creating"
            />
          </div>
        </template>
      </Card>

      <Card class="setup-guidance-card">
        <template #content>
          <div class="guidance-stack">
            <div class="guidance-item ing">
              <span class="guidance-bank">ING Direct</span>
              <h3>Presupuesto de ingresos</h3>
              <p>Usalo para nomina, ingresos temporales y para preparar la transferencia prevista hacia BBVA.</p>
            </div>

            <div class="guidance-item bbva">
              <span class="guidance-bank">BBVA</span>
              <h3>Presupuesto de gastos</h3>
              <p>Usalo como presupuesto operativo del mes para repartir categorias de gasto y aplicar recurrentes.</p>
            </div>

            <div class="guidance-item neutral">
              <span class="guidance-bank">Flujo</span>
              <h3>Pareja enlazada</h3>
              <p>Despues veras ambos borradores lado a lado para ajustar categorias, ingresos temporales y el importe a transferir.</p>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useBudgetStore } from '@/stores/budgets'
import { useFormatters } from '@/composables/useFormatters'

const router = useRouter()
const toast = useToast()
const budgetStore = useBudgetStore()
const { formatDate, formatDateRange } = useFormatters()

const SPANISH_MONTHS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

const getNextMonthDates = () => {
  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth() + 1, 1)
  const end = new Date(now.getFullYear(), now.getMonth() + 2, 0)
  return { start, end }
}

const getBudgetMonthLabel = (date) => `${SPANISH_MONTHS[date.getMonth()]}-${date.getFullYear()}`

const nextMonthDates = getNextMonthDates()
const defaultBudgetMonth = getBudgetMonthLabel(nextMonthDates.start)

const form = ref({
  budget_month: defaultBudgetMonth,
  ing_name: `ING ${defaultBudgetMonth}`,
  bbva_name: `BBVA ${defaultBudgetMonth}`,
  start_date: nextMonthDates.start,
  end_date: nextMonthDates.end
})

const creating = ref(false)

const periodLabel = computed(() => `${SPANISH_MONTHS[nextMonthDates.start.getMonth()]} ${nextMonthDates.start.getFullYear()}`)

const existingIngBudget = computed(() => budgetStore.draftBudgets.find((budget) => budget.budget_month === form.value.budget_month && budget.bank === 'ING Direct') || null)
const existingBbvaBudget = computed(() => budgetStore.draftBudgets.find((budget) => budget.budget_month === form.value.budget_month && budget.bank === 'BBVA') || null)

const existingPair = computed(() => {
  return Boolean(existingIngBudget.value && existingBbvaBudget.value)
})

const isValidBudgetMonth = computed(() => /^[A-Za-z]+-\d{4}$/.test(form.value.budget_month.trim()))

const syncFormWithExistingDrafts = () => {
  const ingDraft = existingIngBudget.value
  const bbvaDraft = existingBbvaBudget.value
  const referenceDraft = ingDraft || bbvaDraft

  if (!referenceDraft) {
    form.value = {
      ...form.value,
      ing_name: `ING ${form.value.budget_month.trim() || defaultBudgetMonth}`,
      bbva_name: `BBVA ${form.value.budget_month.trim() || defaultBudgetMonth}`
    }
    return
  }

  form.value = {
    ...form.value,
    ing_name: ingDraft?.name || form.value.ing_name,
    bbva_name: bbvaDraft?.name || form.value.bbva_name,
    start_date: referenceDraft?.start_date ? new Date(referenceDraft.start_date) : form.value.start_date,
    end_date: referenceDraft?.end_date ? new Date(referenceDraft.end_date) : form.value.end_date
  }
}

onMounted(async () => {
  await budgetStore.fetchBudgets({ status: 'draft', limit: 1000 })
  syncFormWithExistingDrafts()
})

watch(() => form.value.budget_month, () => {
  syncFormWithExistingDrafts()
})

const createOrContinue = async () => {
  if (!form.value.ing_name.trim() || !form.value.bbva_name.trim() || !form.value.budget_month.trim()) {
    toast.add({ severity: 'warn', summary: 'Completa los datos', detail: 'Debes indicar mes del presupuesto y los dos nombres.', life: 4000 })
    return
  }

  if (!isValidBudgetMonth.value) {
    toast.add({ severity: 'warn', summary: 'Mes invalido', detail: 'Usa el formato Mes-YYYY, por ejemplo Mayo-2026.', life: 4000 })
    return
  }

  if (!form.value.start_date || !form.value.end_date) {
    toast.add({ severity: 'warn', summary: 'Fechas requeridas', detail: 'Selecciona la fecha de inicio y la fecha de fin.', life: 4000 })
    return
  }

  if (new Date(form.value.start_date) >= new Date(form.value.end_date)) {
    toast.add({ severity: 'warn', summary: 'Rango invalido', detail: 'La fecha de inicio debe ser anterior a la fecha de fin.', life: 4000 })
    return
  }

  creating.value = true

  try {
    const commonPayload = {
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      budget_month: form.value.budget_month.trim(),
      status: 'draft',
      budget_items: [],
      planning_metadata: {
        planner_type: 'next-month',
        temporary_incomes: []
      }
    }

    const ingPayload = {
      ...commonPayload,
      name: form.value.ing_name.trim(),
      bank: 'ING Direct',
      planning_metadata: {
        ...commonPayload.planning_metadata,
        counterpart_bank: 'BBVA'
      }
    }

    const bbvaPayload = {
      ...commonPayload,
      name: form.value.bbva_name.trim(),
      bank: 'BBVA',
      planning_metadata: {
        ...commonPayload.planning_metadata,
        counterpart_bank: 'ING Direct'
      }
    }

    if (existingIngBudget.value) {
      await budgetStore.updateBudget(existingIngBudget.value._id, ingPayload)
    } else {
      await budgetStore.createBudget(ingPayload)
    }

    if (existingBbvaBudget.value) {
      await budgetStore.updateBudget(existingBbvaBudget.value._id, bbvaPayload)
    } else {
      await budgetStore.createBudget(bbvaPayload)
    }

    toast.add({ severity: 'success', summary: existingPair.value ? 'Borradores actualizados' : 'Borradores creados', detail: 'Ya puedes planificar ING y BBVA lado a lado.', life: 4000 })
    router.push({ name: 'next-month-planner', params: { budgetMonth: form.value.budget_month.trim() } })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'No se pudo crear la planificacion', detail: error.response?.data?.detail || 'Intentalo de nuevo.', life: 5000 })
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.planner-setup-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.setup-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(300px, 0.8fr);
  gap: 1rem;
  padding: 1.6rem;
  border-radius: 30px;
  background: linear-gradient(135deg, rgba(15, 139, 111, 0.12) 0%, rgba(249, 115, 22, 0.12) 100%);
  border: 1px solid var(--surface-border);
}

.section-kicker,
.summary-kicker,
.guidance-bank {
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

.setup-copy h1,
.card-header-block h2 {
  margin: 0.6rem 0 0.45rem;
  font-size: 2rem;
}

.setup-copy p,
.guidance-item p {
  color: var(--text-color-secondary);
  line-height: 1.65;
}

.setup-summary-card,
.setup-form-card,
.setup-guidance-card {
  border-radius: 28px;
}

.setup-summary-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.4rem;
  padding: 1.35rem;
  border: 1px solid var(--surface-border);
  background: color-mix(in srgb, var(--surface-card) 82%, transparent);
}

.setup-summary-card strong {
  font-size: 1.8rem;
  color: var(--heading-color);
}

.setup-summary-card small,
.form-field small {
  color: var(--text-color-secondary);
}

.setup-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.95fr);
  gap: 1rem;
}

.card-header-block,
.action-row,
.period-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.card-header-block {
  align-items: flex-start;
  margin-bottom: 1rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.form-field:first-child {
  grid-column: 1 / -1;
}

.form-field label {
  font-weight: 600;
}

.period-preview {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 20px;
  border: 1px solid var(--surface-border);
  background: var(--surface-ground);
}

.preview-metric {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.preview-metric span {
  font-size: 0.78rem;
  color: var(--text-color-secondary);
}

.preview-metric strong {
  font-size: 1rem;
}

.action-row {
  margin-top: 1.25rem;
}

.guidance-stack {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.guidance-item {
  padding: 1rem;
  border-radius: 22px;
  border: 1px solid var(--surface-border);
  background: color-mix(in srgb, var(--surface-card) 86%, transparent);
}

.guidance-item h3 {
  margin: 0.7rem 0 0.35rem;
}

.guidance-item.ing {
  box-shadow: inset 0 0 0 1px rgba(249, 115, 22, 0.12);
}

.guidance-item.bbva {
  box-shadow: inset 0 0 0 1px rgba(10, 74, 191, 0.12);
}

.w-full {
  width: 100%;
}

@media (max-width: 1024px) {
  .setup-hero,
  .setup-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .period-preview,
  .action-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
