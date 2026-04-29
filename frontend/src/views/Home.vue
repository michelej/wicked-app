<template>
  <div class="hub-home">
    <section class="hub-hero">
      <div class="hero-copy">
        <span class="hero-kicker">Hub personal</span>
        <h1>Un espacio para tus herramientas personales, no solo para tus finanzas.</h1>
        <p>
          Convierte la aplicacion en un ecosistema modular: presupuestos, registros flexibles y micro apps de aprendizaje,
          todo accesible desde una entrada clara y preparada para crecer.
        </p>

        <div class="hero-actions">
          <Button
            label="Abrir Presupuestos"
            icon="pi pi-wallet"
            class="hero-primary-action"
            severity="success"
            @click="navigateToBudgets"
          />
          <Button
            label="Planificar mes siguiente"
            icon="pi pi-calendar"
            outlined
            class="hero-secondary-action"
            @click="navigateToPlanner"
          />
        </div>
      </div>

      <div class="hero-command-panel">
        <div class="command-bar-shell">
          <i class="pi pi-search"></i>
          <span>Buscar modulos, acciones o vistas...</span>
          <kbd>Ctrl K</kbd>
        </div>

        <div class="favorite-stack">
          <div class="favorite-card accent-finance">
            <span class="favorite-label">Favorito actual</span>
            <strong>Presupuestos</strong>
            <small>{{ budgetSnapshotLabel }}</small>
          </div>
          <div class="favorite-card accent-notes">
            <span class="favorite-label">Siguiente modulo</span>
            <strong>Registro</strong>
            <small>Fechas, viajes, compras, documentos y notas dentro de un mismo sistema.</small>
          </div>
        </div>
      </div>
    </section>

    <section class="quick-actions-panel">
      <div class="section-heading">
        <div>
          <span class="section-kicker">Accesos rapidos</span>
          <h2>Empieza por una accion, no por una categoria.</h2>
        </div>
      </div>

      <div class="quick-actions-grid">
        <button type="button" class="quick-action-card is-live" @click="navigateToBudgets">
          <span class="quick-action-icon"><i class="pi pi-plus-circle"></i></span>
          <strong>Nuevo presupuesto</strong>
          <p>Crea o ajusta el modulo financiero principal.</p>
        </button>

        <button type="button" class="quick-action-card is-live metadata-action" @click="navigateToRegistryRecords">
          <span class="quick-action-icon"><i class="pi pi-bookmark"></i></span>
          <strong>Nuevo registro</strong>
          <p>Prepara una entrada generica para viajes, compras o eventos.</p>
        </button>

        <button type="button" class="quick-action-card is-live japanese-action" @click="navigateToJapanesePractice">
          <span class="quick-action-icon"><i class="pi pi-language"></i></span>
          <strong>Practicar japones</strong>
          <p>Sesiones cortas de palabras y frases para repeticion diaria.</p>
        </button>
      </div>
    </section>

    <section class="apps-section">
      <div class="section-heading">
        <div>
          <span class="section-kicker">Aplicaciones</span>
          <h2>Modulos independientes con una misma experiencia base.</h2>
        </div>
      </div>

      <div class="apps-grid">
        <Card class="app-card app-card-finance">
          <template #content>
            <div class="app-card-head">
              <div>
                <span class="app-badge">Disponible</span>
                <h3>Presupuestos</h3>
                <p>El modulo operativo principal, reposicionado dentro del hub para mantenerlo visible pero no dominante.</p>
              </div>
              <div class="app-mark">01</div>
            </div>

            <div v-if="budgetStore.loading && activeBudgets.length === 0" class="module-loading-state">
              <ProgressSpinner style="width: 2rem; height: 2rem" strokeWidth="6" />
              <span>Sincronizando el modulo de presupuestos...</span>
            </div>

            <div v-else-if="budgetStore.error" class="module-inline-error">
              <i class="pi pi-exclamation-triangle"></i>
              <span>{{ budgetStore.error }}</span>
            </div>

            <template v-else>
              <div class="app-metrics-grid">
                <div class="app-metric-tile">
                  <span>Activos</span>
                  <strong>{{ activeBudgets.length }}</strong>
                </div>
                <div class="app-metric-tile">
                  <span>Balance</span>
                  <strong :class="{ negative: totalBalance < 0 }">{{ formatCurrency(totalBalance) }}</strong>
                </div>
                <div class="app-metric-tile">
                  <span>Vigilar</span>
                  <strong>{{ budgetsNeedingAttention }}</strong>
                </div>
                <div class="app-metric-tile">
                  <span>Pendiente</span>
                  <strong>{{ formatCurrency(totalPendingExpense) }}</strong>
                </div>
              </div>

              <div class="app-footer-strip">
                <span class="info-pill">
                  <i class="pi pi-chart-line"></i>
                  {{ budgetSnapshotLabel }}
                </span>
                <span class="info-pill muted-pill">
                  <i class="pi pi-arrow-right-arrow-left"></i>
                  Modulo ya operativo
                </span>
              </div>
            </template>

            <div class="app-card-actions">
              <Button label="Abrir" icon="pi pi-arrow-right" severity="success" @click="navigateToBudgets" />
              <Button label="Planificar" icon="pi pi-calendar-plus" text @click="navigateToPlanner" />
            </div>
          </template>
        </Card>

        <Card class="app-card app-card-metadata">
          <template #content>
            <div class="app-card-head">
              <div>
                <span class="app-badge app-badge-planned">Nuevo modulo</span>
                <h3>Registro</h3>
                <p>Un sistema centralizado para guardar informacion personal estructurada y escalable.</p>
              </div>
              <div class="app-mark">02</div>
            </div>

            <div class="preview-list">
              <div class="preview-item">
                <strong>Viajes</strong>
                <span>Fechas, lugares, recuerdos y coste contextual.</span>
              </div>
              <div class="preview-item">
                <strong>Compras</strong>
                <span>Registro de compra, fecha, motivo y trazabilidad.</span>
              </div>
              <div class="preview-item">
                <strong>Eventos</strong>
                <span>Fechas clave, hitos y notas asociadas.</span>
              </div>
            </div>

            <div class="app-footer-strip">
              <span class="info-pill muted-pill"><i class="pi pi-clone"></i> Base reutilizable</span>
              <span class="info-pill muted-pill"><i class="pi pi-sitemap"></i> Plantillas futuras</span>
            </div>

            <div class="app-card-actions">
              <Button label="Abrir" icon="pi pi-arrow-right" severity="info" @click="navigateToRegistry" />
              <Button label="Timeline" icon="pi pi-calendar-clock" text @click="navigateToRegistryTimeline" />
            </div>
          </template>
        </Card>

        <Card class="app-card app-card-language">
          <template #content>
            <div class="app-card-head">
              <div>
                <span class="app-badge app-badge-planned">Nuevo modulo</span>
                <h3>Aprendizaje de japones</h3>
                <p>Una mini app ligera para consumir vocabulario y frases con sesiones cortas, repetibles y directas.</p>
              </div>
              <div class="app-mark">03</div>
            </div>

            <div class="preview-list compact-preview-list">
              <div class="preview-item">
                <strong>Palabras</strong>
                <span>Listas cortas de lectura rapida.</span>
              </div>
              <div class="preview-item">
                <strong>Frases</strong>
                <span>Bloques utiles para repeticion diaria.</span>
              </div>
              <div class="preview-item">
                <strong>Practica</strong>
                <span>Consumo simple, enfocado y sin friccion.</span>
              </div>
            </div>

            <div class="app-footer-strip">
              <span class="info-pill muted-pill"><i class="pi pi-bolt"></i> Repeticion rapida</span>
              <span class="info-pill muted-pill"><i class="pi pi-refresh"></i> Micro sesiones</span>
            </div>

            <div class="app-card-actions">
              <Button label="Abrir" icon="pi pi-arrow-right" severity="warning" @click="navigateToJapanese" />
              <Button label="Practicar" icon="pi pi-bolt" text @click="navigateToJapanesePractice" />
            </div>
          </template>
        </Card>
      </div>
    </section>

    <section class="continue-section">
      <div class="section-heading">
        <div>
          <span class="section-kicker">Continuar</span>
          <h2>Retoma contexto reciente sin buscar entre menus.</h2>
        </div>
      </div>

      <div class="continue-grid">
        <button
          v-for="budget in recentBudgets"
          :key="budget._id"
          type="button"
          class="continue-card continue-card-live"
          @click="navigateToBudgetDetail(budget._id)"
        >
          <span class="continue-tag">Presupuesto</span>
          <strong>{{ budget.name }}</strong>
          <p>{{ formatDate(budget.start_date) }} - {{ formatDate(budget.end_date) }}</p>
          <small :class="{ negative: (budget.summary?.balance || 0) < 0 }">{{ formatCurrency(budget.summary?.balance || 0) }}</small>
        </button>

        <button type="button" class="continue-card continue-card-live metadata-continue" @click="navigateToRegistryRecords">
          <span class="continue-tag">Registro</span>
          <strong>Registro de viaje</strong>
          <p>Plantilla lista para viajes, eventos o compras con contexto.</p>
          <small>Abrir vista de registros</small>
        </button>

        <button type="button" class="continue-card continue-card-live japanese-continue" @click="navigateToJapaneseWords">
          <span class="continue-tag">Japonés</span>
          <strong>Lista de palabras N5</strong>
          <p>Entrada ligera para consumo rapido y repeticion diaria.</p>
          <small>Abrir lista de palabras</small>
        </button>
      </div>
    </section>

    <section class="future-section">
      <div class="future-copy">
        <span class="section-kicker">Escalabilidad</span>
        <h2>La home ya piensa en futuras herramientas personales.</h2>
        <p>
          El hub esta organizado como un launcher de modulos: cada feature puede crecer de forma independiente, compartir patrones de UI y entrar al ecosistema sin rehacer la entrada principal.
        </p>
      </div>

      <div class="future-grid">
        <div class="future-card">
          <strong>Grid de apps</strong>
          <p>Perfecto para agregar Salud, Notas, Inventario u Objetivos sin romper la navegacion.</p>
        </div>
        <div class="future-card">
          <strong>Favoritos</strong>
          <p>Permite fijar modulos o vistas frecuentes para usuarios con rutinas distintas.</p>
        </div>
        <div class="future-card">
          <strong>Continuidad</strong>
          <p>Las ultimas entidades abiertas pueden mostrarse siempre con el mismo componente reutilizable.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBudgetStore } from '@/stores/budgets'
import { useFormatters } from '@/composables/useFormatters'
import ProgressSpinner from 'primevue/progressspinner'

const router = useRouter()
const budgetStore = useBudgetStore()
const { formatCurrency, formatDate } = useFormatters()

onMounted(async () => {
  await budgetStore.fetchBudgets()
  await budgetStore.getBudgetSummaries(budgetStore.activeBudgets.map((budget) => budget._id))
})

const activeBudgets = computed(() => {
  return budgetStore.activeBudgets.map((budget) => ({
    ...budget,
    summary: budgetStore.budgetSummaries[budget._id]
  }))
})

const totalBalance = computed(() => {
  return activeBudgets.value.reduce((sum, budget) => sum + Number(budget.summary?.balance || 0), 0)
})

const totalPendingExpense = computed(() => {
  return activeBudgets.value.reduce((sum, budget) => sum + Number(budget.summary?.pending_expense || 0), 0)
})

const budgetsNeedingAttention = computed(() => {
  return activeBudgets.value.filter((budget) => {
    const balance = Number(budget.summary?.balance || 0)
    const pending = Number(budget.summary?.pending_expense || 0)
    return balance < 0 || pending > Math.max(balance, 0)
  }).length
})

const recentBudgets = computed(() => activeBudgets.value.slice(0, 3))

const budgetSnapshotLabel = computed(() => {
  if (budgetStore.loading && activeBudgets.value.length === 0) {
    return 'Sincronizando estado financiero'
  }

  if (activeBudgets.value.length === 0) {
    return 'Sin presupuestos activos por ahora'
  }

  if (budgetsNeedingAttention.value === 0) {
    return `${activeBudgets.value.length} modulos financieros en buen estado`
  }

  return `${budgetsNeedingAttention.value} presupuestos requieren atencion` 
})

const navigateToBudgets = () => {
  router.push('/budgets')
}

const navigateToPlanner = () => {
  router.push({ name: 'next-month-planner-setup' })
}

const navigateToRegistry = () => {
  router.push({ name: 'registry-all' })
}

const navigateToRegistryRecords = () => {
  router.push({ name: 'registry-all' })
}

const navigateToRegistryTimeline = () => {
  router.push({ name: 'registry-timeline' })
}

const navigateToJapanese = () => {
  router.push({ name: 'japanese-hub' })
}

const navigateToJapaneseWords = () => {
  router.push({ name: 'japanese-words' })
}

const navigateToJapanesePractice = () => {
  router.push({ name: 'japanese-practice' })
}

const navigateToBudgetDetail = (budgetId) => {
  router.push(`/budgets/${budgetId}`)
}
</script>

<style scoped>
.hub-home {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
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

.hub-hero,
.quick-actions-panel,
.apps-section,
.continue-section,
.future-section {
  border: 1px solid var(--surface-border);
  border-radius: 30px;
  background: color-mix(in srgb, var(--surface-card) 84%, transparent);
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.08);
}

.hub-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.95fr);
  gap: 1rem;
  padding: 1.5rem;
  background:
    radial-gradient(circle at top right, rgba(214, 145, 65, 0.16), transparent 28%),
    radial-gradient(circle at left bottom, rgba(15, 139, 111, 0.14), transparent 26%),
    linear-gradient(145deg, rgba(255, 251, 244, 0.96) 0%, rgba(241, 247, 245, 0.96) 100%);
}

.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-content: space-between;
}

.hero-kicker,
.section-kicker,
.app-badge,
.continue-tag,
.favorite-label {
  display: inline-flex;
  width: fit-content;
  padding: 0.4rem 0.78rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 700;
}

.hero-kicker,
.section-kicker,
.favorite-label {
  background: rgba(255, 255, 255, 0.72);
  color: #0f8b6f;
}

.hero-copy h1 {
  max-width: 12ch;
  font-size: clamp(2.3rem, 4vw, 3.8rem);
  line-height: 0.96;
  letter-spacing: -0.05em;
  color: var(--heading-color);
}

.hero-copy p,
.future-copy p,
.app-card-head p,
.quick-action-card p,
.continue-card p,
.future-card p,
.preview-item span,
.module-inline-error span,
.module-loading-state span {
  color: var(--text-color-secondary);
  line-height: 1.65;
}

.hero-actions,
.app-card-actions,
.app-footer-strip,
.continue-grid,
.future-grid,
.quick-actions-grid,
.apps-grid,
.favorite-stack,
.app-metrics-grid {
  display: grid;
  gap: 0.9rem;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.hero-primary-action {
  box-shadow: 0 16px 28px rgba(15, 139, 111, 0.2);
}

.hero-command-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.command-bar-shell,
.favorite-card,
.quick-action-card,
.app-card,
.continue-card,
.future-card,
.app-metric-tile,
.preview-item,
.info-pill,
.module-inline-error,
.module-loading-state {
  border: 1px solid rgba(124, 97, 61, 0.12);
  background: rgba(255, 255, 255, 0.72);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
}

.command-bar-shell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.95rem 1rem;
  border-radius: 20px;
  color: var(--text-color-secondary);
}

.command-bar-shell kbd {
  margin-left: auto;
  padding: 0.2rem 0.45rem;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.06);
  font-size: 0.75rem;
}

.favorite-stack {
  grid-template-columns: 1fr;
}

.favorite-card {
  padding: 1rem;
  border-radius: 22px;
}

.favorite-card strong,
.app-card-head h3,
.continue-card strong,
.future-card strong,
.section-heading h2 {
  display: block;
  color: var(--heading-color);
}

.favorite-card strong {
  margin: 0.55rem 0 0.35rem;
  font-size: 1.1rem;
}

.accent-finance {
  background: linear-gradient(145deg, rgba(236, 250, 244, 0.92) 0%, rgba(255, 255, 255, 0.72) 100%);
}

.accent-notes {
  background: linear-gradient(145deg, rgba(241, 244, 255, 0.88) 0%, rgba(255, 255, 255, 0.72) 100%);
}

.quick-actions-panel,
.apps-section,
.continue-section,
.future-section {
  padding: 1.4rem;
}

.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-heading h2 {
  margin: 0.55rem 0 0;
  font-size: 1.45rem;
  line-height: 1.15;
}

.quick-actions-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.quick-action-card {
  text-align: left;
  padding: 1.15rem;
  border-radius: 24px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.quick-action-card.is-live:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 24px rgba(15, 23, 42, 0.1);
}

.metadata-action .quick-action-icon,
.metadata-continue .continue-tag {
  background: linear-gradient(145deg, #2563eb 0%, #60a5fa 100%);
  color: white;
}

.japanese-action .quick-action-icon,
.japanese-continue .continue-tag {
  background: linear-gradient(145deg, #d97706 0%, #f59e0b 100%);
  color: white;
}

.quick-action-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.9rem;
  height: 2.9rem;
  margin-bottom: 0.9rem;
  border-radius: 16px;
  background: linear-gradient(145deg, #0f8b6f 0%, #d97706 100%);
  color: white;
  font-size: 1.1rem;
}

.quick-action-card strong {
  display: block;
  font-size: 1.05rem;
  margin-bottom: 0.35rem;
  color: var(--heading-color);
}

.apps-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.app-card {
  border-radius: 28px;
  overflow: hidden;
}

.app-card :deep(.p-card-body),
.app-card :deep(.p-card-content) {
  padding: 0;
}

.app-card :deep(.p-card-content) {
  padding: 1.25rem;
}

.app-card-head {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.app-badge {
  background: rgba(15, 139, 111, 0.1);
  color: #0f8b6f;
}

.app-badge-planned {
  background: rgba(100, 116, 139, 0.12);
  color: #475569;
}

.app-card-head h3 {
  margin: 0.65rem 0 0.35rem;
  font-size: 1.32rem;
}

.app-mark {
  font-size: 2.2rem;
  line-height: 1;
  font-weight: 800;
  letter-spacing: -0.08em;
  color: rgba(15, 23, 42, 0.14);
}

.module-loading-state,
.module-inline-error {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.9rem 1rem;
  border-radius: 18px;
  margin-bottom: 0.95rem;
}

.module-inline-error {
  color: var(--danger-color);
}

.app-metrics-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.app-metric-tile {
  padding: 0.9rem 1rem;
  border-radius: 18px;
}

.app-metric-tile span,
.preview-item strong,
.continue-card small,
.future-card p,
.info-pill {
  color: var(--text-color-secondary);
}

.app-metric-tile span {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.8rem;
}

.app-metric-tile strong {
  font-size: 1.1rem;
  color: var(--heading-color);
}

.app-metric-tile strong.negative,
.continue-card small.negative {
  color: var(--danger-color);
}

.app-footer-strip {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 0.95rem;
}

.info-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 0.85rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
}

.muted-pill {
  background: rgba(248, 250, 252, 0.78);
}

.preview-list {
  display: grid;
  gap: 0.75rem;
}

.preview-item {
  padding: 0.9rem 1rem;
  border-radius: 18px;
}

.preview-item strong {
  display: block;
  margin-bottom: 0.2rem;
  color: var(--heading-color);
}

.app-card-actions {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 1rem;
}

.continue-grid,
.future-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.continue-card,
.future-card {
  padding: 1rem;
  border-radius: 22px;
}

.continue-card-live {
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.continue-card-live:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 24px rgba(15, 23, 42, 0.1);
}

.continue-tag {
  background: rgba(15, 139, 111, 0.08);
  color: #0f8b6f;
}

.continue-card strong {
  margin: 0.7rem 0 0.35rem;
  font-size: 1.06rem;
}

.continue-card small {
  display: block;
  margin-top: 0.7rem;
  font-weight: 700;
}

.future-section {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1.2fr);
  gap: 1rem;
  background: linear-gradient(145deg, rgba(252, 252, 249, 0.96) 0%, rgba(245, 248, 252, 0.96) 100%);
}

.future-copy h2 {
  margin: 0.65rem 0 0.55rem;
  font-size: 1.5rem;
  color: var(--heading-color);
}

@media (max-width: 1200px) {
  .hub-hero,
  .future-section,
  .apps-grid,
  .continue-grid,
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hub-home {
    gap: 1rem;
  }

  .hub-hero,
  .quick-actions-panel,
  .apps-section,
  .continue-section,
  .future-section {
    padding: 1rem;
    border-radius: 24px;
  }

  .hero-copy h1 {
    font-size: 2.2rem;
    max-width: 100%;
  }

  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .app-card-actions,
  .app-footer-strip,
  .app-metrics-grid,
  .future-grid,
  .continue-grid {
    grid-template-columns: 1fr;
  }

  .hero-primary-action,
  .hero-secondary-action {
    width: 100%;
  }
}
</style>
