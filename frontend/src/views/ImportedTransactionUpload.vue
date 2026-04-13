<template>
  <div class="import-upload-view">
    <section class="hero-panel">
      <div class="hero-copy">
        <span class="hero-kicker">Importacion bancaria</span>
        <h1 class="page-title">Sube extractos y prepara movimientos antes de incorporarlos.</h1>
        <p class="page-subtitle">
          Los ficheros se cargan a una bandeja separada para revisar presupuesto, categoria, comentario y metadatos antes de convertirlos en transacciones reales.
        </p>
      </div>

      <div class="hero-metrics-grid">
        <div class="hero-metric-tile">
          <span>Pendientes totales</span>
          <strong>{{ pendingCount }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>BBVA</span>
          <strong>{{ bbvaPendingCount }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>ING Direct</span>
          <strong>{{ ingPendingCount }}</strong>
        </div>
        <div class="hero-metric-tile">
          <span>Ultima carga</span>
          <strong>{{ importedTransactionStore.lastUploadResult?.imported_count || 0 }}</strong>
        </div>
      </div>
    </section>

    <div class="upload-grid">
      <Card class="upload-card">
        <template #content>
          <div class="upload-card-body">
            <div class="upload-card-header">
              <div>
                <span class="section-kicker">Banco</span>
                <h2>BBVA</h2>
              </div>
              <Tag value="Operativo" severity="success" />
            </div>

            <p class="upload-description">
              Usa el formato `.xlsx` del extracto de BBVA. Se importan fecha de valor, concepto, movimiento, importe, observaciones y sugerencias para comentario.
            </p>

            <div class="upload-features">
              <span><i class="pi pi-check-circle"></i> Convierte importes negativos a positivos</span>
              <span><i class="pi pi-check-circle"></i> Concatena `Concepto` + `Observaciones`</span>
              <span><i class="pi pi-check-circle"></i> Crea registros pendientes por validar</span>
            </div>

            <input
              ref="bbvaInput"
              type="file"
              accept=".xlsx"
              class="hidden-input"
              @change="onFileSelected('bbva', $event)"
            />

            <div class="upload-actions">
              <Button
                label="Subir fichero BBVA"
                icon="pi pi-upload"
                severity="success"
                @click="bbvaInput?.click()"
                :loading="isUploadingBank === 'bbva'"
              />
              <Button
                label="Revisar pendientes"
                icon="pi pi-arrow-right"
                text
                @click="router.push('/imports/review')"
              />
            </div>
          </div>
        </template>
      </Card>

      <Card class="upload-card is-secondary">
        <template #content>
          <div class="upload-card-body">
            <div class="upload-card-header">
              <div>
                <span class="section-kicker">Banco</span>
                <h2>ING Direct</h2>
              </div>
              <Tag value="Operativo" severity="success" />
            </div>

            <p class="upload-description">
              Importa extractos `.xls` o `.xlsx` de ING Direct. Se leen fecha valor, categoria, subcategoria, descripcion, comentario, importe y saldo para pasar a la bandeja de validacion.
            </p>

            <div class="upload-features">
              <span><i class="pi pi-check-circle"></i> Soporta formato exportado de ING Direct</span>
              <span><i class="pi pi-check-circle"></i> Usa categoria y subcategoria como pista</span>
              <span><i class="pi pi-check-circle"></i> Mismo flujo de validacion que BBVA</span>
            </div>

            <input
              ref="ingInput"
              type="file"
              accept=".xls,.xlsx"
              class="hidden-input"
              @change="onFileSelected('ing_direct', $event)"
            />

            <div class="upload-actions">
              <Button
                label="Subir fichero ING"
                icon="pi pi-upload"
                severity="success"                
                @click="ingInput?.click()"
                :loading="isUploadingBank === 'ing_direct'"
              />
              <Button
                label="Revisar pendientes"
                icon="pi pi-arrow-right"
                text
                @click="router.push('/imports/review')"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>

    <Card v-if="importedTransactionStore.lastUploadResult" class="result-card">
      <template #content>
        <div class="result-header">
          <div>
            <span class="section-kicker">Resultado</span>
            <h2>Ultima importacion</h2>
          </div>
          <Tag :value="bankLabel(importedTransactionStore.lastUploadResult.source_bank)" severity="info" />
        </div>

        <div class="result-grid">
          <div class="result-item">
            <span>Filas detectadas</span>
            <strong>{{ importedTransactionStore.lastUploadResult.total_rows }}</strong>
          </div>
          <div class="result-item">
            <span>Nuevas importadas</span>
            <strong>{{ importedTransactionStore.lastUploadResult.imported_count }}</strong>
          </div>
          <div class="result-item">
            <span>Duplicadas</span>
            <strong>{{ importedTransactionStore.lastUploadResult.duplicate_count }}</strong>
          </div>
          <div class="result-item">
            <span>Pendientes del banco</span>
            <strong>{{ importedTransactionStore.lastUploadResult.pending_count }}</strong>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useImportedTransactionStore } from '@/stores/importedTransactions'

const router = useRouter()
const toast = useToast()
const importedTransactionStore = useImportedTransactionStore()

const bbvaInput = ref(null)
const ingInput = ref(null)
const isUploadingBank = ref(null)

const pendingCount = computed(() => {
  return importedTransactionStore.pendingTransactions.length
})

const bbvaPendingCount = computed(() => {
  return importedTransactionStore.pendingTransactions.filter((item) => item.source_bank === 'bbva').length
})

const ingPendingCount = computed(() => {
  return importedTransactionStore.pendingTransactions.filter((item) => item.source_bank === 'ing_direct').length
})

onMounted(async () => {
  await importedTransactionStore.fetchImportedTransactions({ status: 'pending', limit: 1000 })
})

const onFileSelected = async (sourceBank, event) => {
  const file = event.target.files?.[0]
  if (!file) {
    return
  }

  isUploadingBank.value = sourceBank

  try {
    const result = await importedTransactionStore.uploadImportedTransactions(sourceBank, file)
    await importedTransactionStore.fetchImportedTransactions({ status: 'pending', limit: 1000 })

    toast.add({
      severity: 'success',
      summary: 'Importacion completada',
      detail: `${result.imported_count} movimientos cargados y ${result.duplicate_count} duplicados omitidos.`,
      life: 4000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error al importar',
      detail: error.response?.data?.detail || 'No se pudo procesar el fichero.',
      life: 5000
    })
  } finally {
    event.target.value = ''
    isUploadingBank.value = null
  }
}

const bankLabel = (sourceBank) => {
  return sourceBank === 'bbva' ? 'BBVA' : 'ING Direct'
}
</script>

<style scoped>
.import-upload-view {
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
  max-width: 12ch;
  font-size: clamp(2.2rem, 3.8vw, 3.4rem);
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--heading-color);
}

.page-subtitle {
  max-width: 62ch;
  color: var(--text-color-secondary);
  line-height: 1.7;
}

.hero-metrics-grid,
.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.hero-metric-tile,
.result-item {
  padding: 1rem;
  border-radius: 20px;
  border: 1px solid rgba(124, 97, 61, 0.12);
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(12px);
}

.hero-metric-tile span,
.result-item span {
  display: block;
  margin-bottom: 0.3rem;
  color: var(--text-color-secondary);
  font-size: 0.82rem;
}

.hero-metric-tile strong,
.result-item strong {
  color: var(--heading-color);
  font-size: 1.2rem;
}

.upload-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;
}

.upload-card,
.result-card {
  border-radius: 28px;
  border: 1px solid var(--surface-border);
  box-shadow: var(--shadow-sm);
}

.upload-card.is-secondary {
  background: color-mix(in srgb, var(--surface-card) 78%, transparent);
}

.upload-card-body {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.upload-card-header,
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.upload-card-header h2,
.result-header h2 {
  margin-top: 0.6rem;
  font-size: 1.3rem;
}

.upload-description {
  color: var(--text-color-secondary);
  line-height: 1.7;
}

.upload-features {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.upload-features span {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-color);
}

.upload-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.hidden-input {
  display: none;
}

@media (max-width: 1100px) {
  .hero-panel,
  .upload-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-panel {
    padding: 1.1rem;
    border-radius: 24px;
  }

  .hero-metrics-grid,
  .result-grid {
    grid-template-columns: 1fr;
  }

  .upload-actions {
    flex-direction: column;
  }

  .upload-actions :deep(.p-button) {
    width: 100%;
  }
}
</style>
