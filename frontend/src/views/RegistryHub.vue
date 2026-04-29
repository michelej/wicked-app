<template>
  <div class="registry-hub">
    <section class="registry-hero">
      <div class="hero-copy">
        <span class="hero-kicker">Registro</span>
        <h1>{{ currentView.title }}</h1>
        <p>{{ currentView.description }}</p>

        <div class="hero-actions">
          <Button label="Nuevo registro" icon="pi pi-plus" severity="info" @click="openCreateDialog()" />
          <Button label="Timeline" icon="pi pi-calendar-clock" outlined @click="goToRoute('registry-timeline')" />
        </div>
      </div>

      <div class="hero-summary-card">
        <span class="summary-label">Panorama</span>
        <strong>{{ filteredItems.length }} items visibles · {{ registryStore.items.length }} totales</strong>
        <small>Un sistema de registro personal estructurado para fechas, viajes, compras, garantias, documentos y mas.</small>
      </div>
    </section>

    <section class="registry-nav-strip">
      <button
        v-for="item in navItems"
        :key="item.routeName"
        type="button"
        class="nav-pill"
        :class="{ active: route.name === item.routeName }"
        @click="goToRoute(item.routeName)"
      >
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </button>
    </section>

    <section class="registry-toolbar">
      <div class="toolbar-block toolbar-search">
        <span class="toolbar-label">Buscar</span>
        <input v-model.trim="filters.search" class="search-input" type="text" placeholder="Titulo, descripcion, ubicacion, tags..." />
      </div>

      <div class="toolbar-block toolbar-selects">
        <div class="field-shell">
          <span class="toolbar-label">Tipo</span>
          <Select v-model="filters.type" :options="typeFilterOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>
        <div class="field-shell">
          <span class="toolbar-label">Estado</span>
          <Select v-model="filters.status" :options="statusFilterOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>
        <div class="field-shell">
          <span class="toolbar-label">Tag</span>
          <Select v-model="filters.tag" :options="tagFilterOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>
      </div>

      <div class="toolbar-block toolbar-layouts">
        <span class="toolbar-label">Vista</span>
        <div class="layout-pill-row">
          <button
            v-for="option in layoutOptions"
            :key="option.value"
            type="button"
            class="layout-pill"
            :class="{ active: layoutMode === option.value }"
            @click="layoutMode = option.value"
          >
            <i :class="option.icon"></i>
            <span>{{ option.label }}</span>
          </button>
        </div>
      </div>
    </section>

    <div v-if="registryStore.loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando registros...</p>
    </div>

    <div v-else-if="registryStore.error" class="error-state">
      <i class="pi pi-exclamation-triangle"></i>
      <span>{{ registryStore.error }}</span>
    </div>

    <template v-else>
      <section class="registry-metrics-grid">
        <div class="metric-card">
          <span>Total</span>
          <strong>{{ registryStore.items.length }}</strong>
        </div>
        <div class="metric-card">
          <span>Activos</span>
          <strong>{{ activeCount }}</strong>
        </div>
        <div class="metric-card">
          <span>Archivados</span>
          <strong>{{ archivedCount }}</strong>
        </div>
        <div class="metric-card">
          <span>Importe visible</span>
          <strong>{{ formatCurrency(totalVisibleAmount) }}</strong>
        </div>
      </section>

      <section v-if="layoutMode === 'timeline'" class="timeline-shell">
        <div v-for="group in timelineGroups" :key="group.label" class="timeline-group">
          <div class="timeline-heading">
            <span class="timeline-month">{{ group.label }}</span>
            <small>{{ group.items.length }} registros</small>
          </div>

          <div class="timeline-items">
            <article v-for="item in group.items" :key="item._id" class="timeline-card">
              <div class="card-top-row">
                <span class="type-pill">{{ typeLabels[item.type] }}</span>
                <Tag :value="statusLabels[item.status]" :severity="statusSeverities[item.status]" />
              </div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.description || 'Sin descripcion adicional.' }}</p>
              <div class="info-row">
                <span><i class="pi pi-calendar"></i> {{ getPrimaryDateLabel(item) }}</span>
                <span v-if="item.location"><i class="pi pi-map-marker"></i> {{ item.location }}</span>
              </div>
              <div class="tag-row">
                <span v-for="tag in item.tags" :key="tag" class="tag-chip">{{ tag }}</span>
              </div>
              <div class="card-actions-row">
                <Button icon="pi pi-pencil" text rounded severity="secondary" @click="openEditDialog(item)" />
                <Button icon="pi pi-copy" text rounded severity="info" @click="duplicateItem(item)" />
                <Button v-if="item.status !== 'archived'" icon="pi pi-box" text rounded severity="warning" @click="archiveItem(item)" />
                <Button icon="pi pi-trash" text rounded severity="danger" @click="deleteItem(item)" />
              </div>
            </article>
          </div>
        </div>

        <div v-if="timelineGroups.length === 0" class="empty-state-card">No hay registros para mostrar en la timeline.</div>
      </section>

      <section v-else-if="layoutMode === 'cards'" class="cards-grid">
        <article v-for="item in filteredItems" :key="item._id" class="registry-card">
          <div class="card-top-row">
            <span class="type-pill">{{ typeLabels[item.type] }}</span>
            <Tag :value="statusLabels[item.status]" :severity="statusSeverities[item.status]" />
          </div>

          <strong>{{ item.title }}</strong>
          <p>{{ item.description || 'Sin descripcion adicional.' }}</p>

          <div class="info-row stacked-info-row">
            <span><i class="pi pi-calendar"></i> {{ getPrimaryDateLabel(item) }}</span>
            <span v-if="item.amount !== null && item.amount !== undefined"><i class="pi pi-wallet"></i> {{ formatCurrency(item.amount) }}</span>
            <span v-if="item.location"><i class="pi pi-map-marker"></i> {{ item.location }}</span>
          </div>

          <div class="tag-row">
            <span v-for="tag in item.tags" :key="tag" class="tag-chip">{{ tag }}</span>
          </div>

          <div class="custom-field-preview" v-if="item.customFields?.length">
            <div v-for="field in item.customFields.slice(0, 3)" :key="`${item._id}-${field.key}`" class="custom-field-chip">
              <span>{{ field.label }}</span>
              <strong>{{ formatFieldValue(field) }}</strong>
            </div>
          </div>

          <div class="card-actions-row">
            <Button label="Editar" icon="pi pi-pencil" text severity="secondary" @click="openEditDialog(item)" />
            <Button label="Duplicar" icon="pi pi-copy" text severity="info" @click="duplicateItem(item)" />
            <Button v-if="item.status !== 'archived'" label="Archivar" icon="pi pi-box" text severity="warning" @click="archiveItem(item)" />
            <Button label="Eliminar" icon="pi pi-trash" text severity="danger" @click="deleteItem(item)" />
          </div>
        </article>

        <div v-if="filteredItems.length === 0" class="empty-state-card">No hay registros que coincidan con los filtros actuales.</div>
      </section>

      <section v-else class="table-shell">
        <DataTable :value="filteredItems" class="registry-table" stripedRows showGridlines>
          <Column field="title" header="Titulo" sortable>
            <template #body="{ data }">
              <div class="table-title-cell">
                <strong>{{ data.title }}</strong>
                <small>{{ typeLabels[data.type] }}</small>
              </div>
            </template>
          </Column>
          <Column field="status" header="Estado" sortable>
            <template #body="{ data }">
              <Tag :value="statusLabels[data.status]" :severity="statusSeverities[data.status]" />
            </template>
          </Column>
          <Column header="Fecha" sortable>
            <template #body="{ data }">
              {{ getPrimaryDateLabel(data) }}
            </template>
          </Column>
          <Column header="Importe" sortable>
            <template #body="{ data }">
              {{ data.amount !== null && data.amount !== undefined ? formatCurrency(data.amount) : '-' }}
            </template>
          </Column>
          <Column header="Ubicacion">
            <template #body="{ data }">
              {{ data.location || '-' }}
            </template>
          </Column>
          <Column header="Acciones">
            <template #body="{ data }">
              <div class="table-actions-row">
                <Button icon="pi pi-pencil" text rounded severity="secondary" @click="openEditDialog(data)" />
                <Button icon="pi pi-copy" text rounded severity="info" @click="duplicateItem(data)" />
                <Button v-if="data.status !== 'archived'" icon="pi pi-box" text rounded severity="warning" @click="archiveItem(data)" />
                <Button icon="pi pi-trash" text rounded severity="danger" @click="deleteItem(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </section>
    </template>

    <Dialog v-model:visible="showEditor" modal :style="{ width: '980px' }" :header="editingItem ? 'Editar registro' : 'Nuevo registro'">
      <div class="editor-shell">
        <div class="editor-grid">
          <div class="form-field wide-field">
            <label>Titulo *</label>
            <InputText v-model="form.title" class="w-full" />
          </div>

          <div class="form-field">
            <label>Tipo *</label>
            <Select v-model="form.type" :options="typeOptions" optionLabel="label" optionValue="value" class="w-full" @change="applyTemplateDefaults(form.type)" />
          </div>

          <div class="form-field">
            <label>Estado</label>
            <Select v-model="form.status" :options="statusOptions" optionLabel="label" optionValue="value" class="w-full" />
          </div>

          <div class="form-field">
            <label>Fecha</label>
            <Calendar v-model="form.date" dateFormat="dd/mm/yy" class="w-full" />
          </div>

          <div class="form-field">
            <label>Inicio</label>
            <Calendar v-model="form.startDate" dateFormat="dd/mm/yy" class="w-full" />
          </div>

          <div class="form-field">
            <label>Fin</label>
            <Calendar v-model="form.endDate" dateFormat="dd/mm/yy" class="w-full" />
          </div>

          <div class="form-field">
            <label>Importe</label>
            <InputNumber v-model="form.amount" mode="currency" currency="EUR" locale="es-ES" class="w-full" />
          </div>

          <div class="form-field">
            <label>Moneda</label>
            <InputText v-model="form.currency" class="w-full" placeholder="EUR" />
          </div>

          <div class="form-field">
            <label>Ubicacion</label>
            <InputText v-model="form.location" class="w-full" />
          </div>

          <div class="form-field wide-field">
            <label>Descripcion</label>
            <Textarea v-model="form.description" rows="4" class="w-full" />
          </div>

          <div class="form-field wide-field">
            <label>Tags</label>
            <InputText v-model="tagsInput" class="w-full" placeholder="viaje, garantia, familia" />
          </div>
        </div>

        <div class="dynamic-sections">
          <div class="section-toggle-card">
            <button type="button" class="section-toggle" @click="showCustomFields = !showCustomFields">
              <span>Campos personalizados</span>
              <i :class="showCustomFields ? 'pi pi-angle-up' : 'pi pi-angle-down'"></i>
            </button>

            <div v-if="showCustomFields" class="dynamic-list">
              <div v-for="(field, index) in form.customFields" :key="`field-${index}`" class="dynamic-row">
                <InputText v-model="field.label" placeholder="Etiqueta" class="flex-1" />
                <InputText v-model="field.key" placeholder="key" class="narrow-input" />
                <Select v-model="field.type" :options="customFieldTypeOptions" optionLabel="label" optionValue="value" class="narrow-input" />
                <InputText v-model="field.value" placeholder="Valor" class="flex-1" />
                <Button icon="pi pi-trash" text severity="danger" @click="removeCustomField(index)" />
              </div>
              <Button label="Agregar campo" icon="pi pi-plus" text @click="addCustomField" />
            </div>
          </div>

          <div class="section-toggle-card">
            <button type="button" class="section-toggle" @click="showRelatedEntities = !showRelatedEntities">
              <span>Relaciones</span>
              <i :class="showRelatedEntities ? 'pi pi-angle-up' : 'pi pi-angle-down'"></i>
            </button>

            <div v-if="showRelatedEntities" class="dynamic-list">
              <div v-for="(relation, index) in form.relatedEntities" :key="`relation-${index}`" class="dynamic-row">
                <Select v-model="relation.entityType" :options="relatedEntityTypeOptions" optionLabel="label" optionValue="value" class="narrow-input" />
                <InputText v-model="relation.entityId" placeholder="ID entidad" class="flex-1" />
                <InputText v-model="relation.label" placeholder="Etiqueta" class="flex-1" />
                <Button icon="pi pi-trash" text severity="danger" @click="removeRelation(index)" />
              </div>
              <Button label="Agregar relacion" icon="pi pi-plus" text @click="addRelation" />
            </div>
          </div>

          <div class="section-toggle-card">
            <button type="button" class="section-toggle" @click="showAttachments = !showAttachments">
              <span>Adjuntos</span>
              <i :class="showAttachments ? 'pi pi-angle-up' : 'pi pi-angle-down'"></i>
            </button>

            <div v-if="showAttachments" class="dynamic-list">
              <div v-for="(attachment, index) in form.attachments" :key="`attachment-${index}`" class="dynamic-row">
                <InputText v-model="attachment.label" placeholder="Etiqueta" class="flex-1" />
                <InputText v-model="attachment.url" placeholder="URL" class="flex-1" />
                <InputText v-model="attachment.kind" placeholder="Tipo" class="narrow-input" />
                <Button icon="pi pi-trash" text severity="danger" @click="removeAttachment(index)" />
              </div>
              <Button label="Agregar adjunto" icon="pi pi-plus" text @click="addAttachment" />
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Cancelar" text @click="closeDialog" />
        <Button :label="editingItem ? 'Guardar cambios' : 'Crear registro'" icon="pi pi-check" severity="info" :loading="registryStore.saving" @click="saveItem" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useRegistryStore } from '@/stores/registry'
import { useFormatters } from '@/composables/useFormatters'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const registryStore = useRegistryStore()
const { formatCurrency, formatDate } = useFormatters()

const navItems = [
  { routeName: 'registry-all', label: 'Todo', icon: 'pi pi-table' },
  { routeName: 'registry-timeline', label: 'Timeline', icon: 'pi pi-calendar-clock' },
  { routeName: 'registry-dates', label: 'Fechas', icon: 'pi pi-calendar' },
  { routeName: 'registry-trips', label: 'Viajes', icon: 'pi pi-send' },
  { routeName: 'registry-purchases', label: 'Compras', icon: 'pi pi-shopping-bag' },
  { routeName: 'registry-documents', label: 'Documentos', icon: 'pi pi-folder' },
  { routeName: 'registry-subscriptions', label: 'Suscripciones', icon: 'pi pi-refresh' },
  { routeName: 'registry-notes', label: 'Notas', icon: 'pi pi-pencil' },
  { routeName: 'registry-archived', label: 'Archivados', icon: 'pi pi-box' }
]

const typeOptions = [
  { value: 'date', label: 'Fecha importante' },
  { value: 'trip', label: 'Viaje' },
  { value: 'purchase', label: 'Compra' },
  { value: 'warranty', label: 'Garantia' },
  { value: 'document', label: 'Documento' },
  { value: 'event', label: 'Evento' },
  { value: 'note', label: 'Nota' },
  { value: 'subscription', label: 'Suscripcion' },
  { value: 'task', label: 'Tarea' },
  { value: 'procedure', label: 'Tramite' },
  { value: 'other', label: 'Otro' }
]

const statusOptions = [
  { value: 'active', label: 'Activo' },
  { value: 'planned', label: 'Planificado' },
  { value: 'completed', label: 'Completado' },
  { value: 'cancelled', label: 'Cancelado' },
  { value: 'archived', label: 'Archivado' }
]

const customFieldTypeOptions = [
  { value: 'text', label: 'Texto' },
  { value: 'number', label: 'Numero' },
  { value: 'date', label: 'Fecha' },
  { value: 'boolean', label: 'Booleano' },
  { value: 'url', label: 'URL' },
  { value: 'select', label: 'Select' },
  { value: 'currency', label: 'Moneda' }
]

const relatedEntityTypeOptions = [
  { value: 'transaction', label: 'Transaccion' },
  { value: 'budget', label: 'Presupuesto' },
  { value: 'document', label: 'Documento' },
  { value: 'contact', label: 'Contacto' },
  { value: 'project', label: 'Proyecto' },
  { value: 'category', label: 'Categoria' }
]

const templates = {
  purchase: {
    status: 'completed',
    customFields: [
      { key: 'store', label: 'Tienda', type: 'text', value: '' },
      { key: 'warranty_until', label: 'Garantia hasta', type: 'date', value: '' }
    ]
  },
  trip: {
    status: 'planned',
    customFields: [
      { key: 'accommodation', label: 'Alojamiento', type: 'text', value: '' },
      { key: 'transport', label: 'Transporte', type: 'text', value: '' }
    ]
  },
  date: {
    status: 'planned',
    customFields: [
      { key: 'priority', label: 'Prioridad', type: 'select', value: 'media' }
    ]
  },
  document: {
    status: 'active',
    customFields: [
      { key: 'issuer', label: 'Emisor', type: 'text', value: '' },
      { key: 'expiry', label: 'Caducidad', type: 'date', value: '' }
    ]
  },
  subscription: {
    status: 'active',
    customFields: [
      { key: 'billing_cycle', label: 'Ciclo', type: 'select', value: 'monthly' },
      { key: 'renewal_date', label: 'Renovacion', type: 'date', value: '' }
    ]
  }
}

const routePresets = {
  'registry-all': { type: null, status: null, layout: 'cards' },
  'registry-timeline': { type: null, status: null, layout: 'timeline' },
  'registry-dates': { type: 'date', status: null, layout: 'timeline' },
  'registry-trips': { type: 'trip', status: null, layout: 'cards' },
  'registry-purchases': { type: 'purchase', status: null, layout: 'table' },
  'registry-documents': { type: 'document', status: null, layout: 'cards' },
  'registry-subscriptions': { type: 'subscription', status: null, layout: 'cards' },
  'registry-notes': { type: 'note', status: null, layout: 'cards' },
  'registry-archived': { type: null, status: 'archived', layout: 'table' }
}

const viewMap = {
  'registry-all': {
    title: 'Un sistema de registro personal inteligente para informacion estructurada.',
    description: 'Reemplaza por completo el modulo anterior y unifica fechas, viajes, compras, garantias, documentos, notas y mas dentro de un solo sistema flexible.'
  },
  'registry-timeline': {
    title: 'Una timeline global para leer el contexto personal como una secuencia viva.',
    description: 'Organiza los registros por tiempo para detectar hitos, periodos y relacion entre eventos.'
  },
  'registry-dates': {
    title: 'Fechas importantes con estructura, prioridad y seguimiento.',
    description: 'Pensado para renovaciones, vencimientos, recordatorios o hitos personales.'
  },
  'registry-trips': {
    title: 'Viajes con fechas, ubicacion, presupuesto y contexto asociado.',
    description: 'Guarda itinerarios, ideas, reservas y notas relacionadas con desplazamientos o vacaciones.'
  },
  'registry-purchases': {
    title: 'Compras relevantes trazables mas alla del simple gasto.',
    description: 'Ideal para garantias, tickets, contexto de compra y relacion con transacciones.'
  },
  'registry-documents': {
    title: 'Documentos y tramites en un solo sistema de consulta y seguimiento.',
    description: 'Agrupa identificaciones, archivos, fechas de caducidad y referencias cruzadas.'
  },
  'registry-subscriptions': {
    title: 'Suscripciones, renovaciones y ciclos recurrentes bajo control.',
    description: 'Centraliza servicios activos, importes, renovaciones y notas clave.'
  },
  'registry-notes': {
    title: 'Notas estructuradas para que el contexto no se pierda en texto suelto.',
    description: 'Mantiene ideas, observaciones y recordatorios dentro del mismo dominio de registro.'
  },
  'registry-archived': {
    title: 'Un archivo vivo para consultar historial sin mezclarlo con lo operativo.',
    description: 'Todo lo archivado sigue accesible para busqueda, consulta y relaciones futuras.'
  }
}

const typeLabels = Object.fromEntries(typeOptions.map((option) => [option.value, option.label]))
const statusLabels = Object.fromEntries(statusOptions.map((option) => [option.value, option.label]))
const statusSeverities = {
  active: 'success',
  planned: 'info',
  completed: 'secondary',
  cancelled: 'danger',
  archived: 'contrast'
}

const layoutOptions = [
  { value: 'cards', label: 'Cards', icon: 'pi pi-th-large' },
  { value: 'timeline', label: 'Timeline', icon: 'pi pi-calendar-clock' },
  { value: 'table', label: 'Tabla', icon: 'pi pi-table' }
]

const defaultForm = () => ({
  title: '',
  description: '',
  type: 'note',
  status: 'active',
  date: null,
  startDate: null,
  endDate: null,
  amount: null,
  currency: 'EUR',
  location: '',
  tags: [],
  relatedEntities: [],
  customFields: [],
  attachments: []
})

const filters = ref({ search: '', type: 'all', status: 'all', tag: 'all' })
const layoutMode = ref('cards')
const showEditor = ref(false)
const editingItem = ref(null)
const form = ref(defaultForm())
const tagsInput = ref('')
const showCustomFields = ref(true)
const showRelatedEntities = ref(false)
const showAttachments = ref(false)

const currentView = computed(() => viewMap[route.name] || viewMap['registry-all'])
const routePreset = computed(() => routePresets[route.name] || routePresets['registry-all'])
const allTags = computed(() => [...new Set(registryStore.items.flatMap((item) => item.tags || []))].sort())
const tagFilterOptions = computed(() => [{ label: 'Todos', value: 'all' }, ...allTags.value.map((tag) => ({ label: tag, value: tag }))])
const typeFilterOptions = computed(() => [{ label: 'Todos', value: 'all' }, ...typeOptions])
const statusFilterOptions = computed(() => [{ label: 'Todos', value: 'all' }, ...statusOptions])

const filteredItems = computed(() => {
  const query = filters.value.search.toLowerCase()

  return registryStore.items.filter((item) => {
    const effectiveType = routePreset.value.type || (filters.value.type !== 'all' ? filters.value.type : null)
    const effectiveStatus = routePreset.value.status || (filters.value.status !== 'all' ? filters.value.status : null)

    if (effectiveType && item.type !== effectiveType) {
      return false
    }

    if (effectiveStatus && item.status !== effectiveStatus) {
      return false
    }

    if (filters.value.tag !== 'all' && !item.tags?.includes(filters.value.tag)) {
      return false
    }

    if (!query) {
      return true
    }

    const customFieldText = (item.customFields || []).map((field) => `${field.label} ${field.value ?? ''}`).join(' ')
    const haystack = `${item.title} ${item.description || ''} ${item.location || ''} ${(item.tags || []).join(' ')} ${customFieldText}`.toLowerCase()
    return haystack.includes(query)
  }).sort((first, second) => {
    const firstDate = getSortDate(first)
    const secondDate = getSortDate(second)
    return secondDate - firstDate
  })
})

const timelineGroups = computed(() => {
  const groups = new Map()
  filteredItems.value.forEach((item) => {
    const date = new Date(getSortDate(item))
    const label = new Intl.DateTimeFormat('es-ES', { month: 'long', year: 'numeric' }).format(date)
    if (!groups.has(label)) {
      groups.set(label, [])
    }
    groups.get(label).push(item)
  })

  return Array.from(groups.entries()).map(([label, items]) => ({ label, items }))
})

const activeCount = computed(() => registryStore.items.filter((item) => item.status !== 'archived').length)
const archivedCount = computed(() => registryStore.items.filter((item) => item.status === 'archived').length)
const totalVisibleAmount = computed(() => filteredItems.value.reduce((sum, item) => sum + Number(item.amount || 0), 0))

watch(
  () => route.name,
  () => {
    layoutMode.value = routePreset.value.layout
    filters.value.type = 'all'
    filters.value.status = 'all'
  },
  { immediate: true }
)

onMounted(async () => {
  await registryStore.fetchItems({ limit: 500 })
})

const goToRoute = (routeName) => {
  router.push({ name: routeName })
}

const getSortDate = (item) => {
  return new Date(item.date || item.startDate || item.endDate || item.createdAt || Date.now()).getTime()
}

const getPrimaryDateLabel = (item) => {
  if (item.date) {
    return formatDate(item.date)
  }

  if (item.startDate && item.endDate) {
    return `${formatDate(item.startDate)} - ${formatDate(item.endDate)}`
  }

  if (item.startDate) {
    return formatDate(item.startDate)
  }

  if (item.endDate) {
    return formatDate(item.endDate)
  }

  return formatDate(item.createdAt)
}

const formatFieldValue = (field) => {
  if (field.type === 'date' && field.value) {
    return formatDate(field.value)
  }

  if (field.type === 'currency' && field.value !== null && field.value !== undefined && field.value !== '') {
    return formatCurrency(Number(field.value))
  }

  if (field.type === 'boolean') {
    return field.value ? 'Si' : 'No'
  }

  return field.value || '-'
}

const applyTemplateDefaults = (type) => {
  const template = templates[type]
  if (!template) {
    return
  }

  form.value.status = template.status
  if (form.value.customFields.length === 0) {
    form.value.customFields = template.customFields.map((field) => ({ ...field }))
  }
}

const normalizeTags = () => {
  form.value.tags = tagsInput.value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

const normalizePayload = () => {
  normalizeTags()
  return {
    ...form.value,
    amount: form.value.amount === null || form.value.amount === '' ? null : Number(form.value.amount),
    currency: form.value.currency || null,
    location: form.value.location || null,
    description: form.value.description || null,
    date: form.value.date ? new Date(form.value.date).toISOString() : null,
    startDate: form.value.startDate ? new Date(form.value.startDate).toISOString() : null,
    endDate: form.value.endDate ? new Date(form.value.endDate).toISOString() : null,
    relatedEntities: form.value.relatedEntities.filter((item) => item.entityType && item.entityId),
    customFields: form.value.customFields.filter((field) => field.key && field.label),
    attachments: form.value.attachments.filter((attachment) => attachment.label && attachment.url)
  }
}

const openCreateDialog = () => {
  editingItem.value = null
  form.value = defaultForm()
  tagsInput.value = ''
  showEditor.value = true
  showCustomFields.value = true
  showRelatedEntities.value = false
  showAttachments.value = false
}

const openEditDialog = (item) => {
  editingItem.value = item
  form.value = {
    title: item.title,
    description: item.description || '',
    type: item.type,
    status: item.status,
    date: item.date ? new Date(item.date) : null,
    startDate: item.startDate ? new Date(item.startDate) : null,
    endDate: item.endDate ? new Date(item.endDate) : null,
    amount: item.amount ?? null,
    currency: item.currency || 'EUR',
    location: item.location || '',
    tags: [...(item.tags || [])],
    relatedEntities: (item.relatedEntities || []).map((relation) => ({ ...relation })),
    customFields: (item.customFields || []).map((field) => ({ ...field })),
    attachments: (item.attachments || []).map((attachment) => ({ ...attachment }))
  }
  tagsInput.value = form.value.tags.join(', ')
  showEditor.value = true
  showCustomFields.value = true
  showRelatedEntities.value = (item.relatedEntities || []).length > 0
  showAttachments.value = (item.attachments || []).length > 0
}

const closeDialog = () => {
  showEditor.value = false
}

const addCustomField = () => {
  form.value.customFields.push({ key: '', label: '', type: 'text', value: '' })
}

const removeCustomField = (index) => {
  form.value.customFields.splice(index, 1)
}

const addRelation = () => {
  form.value.relatedEntities.push({ entityType: 'transaction', entityId: '', label: '' })
}

const removeRelation = (index) => {
  form.value.relatedEntities.splice(index, 1)
}

const addAttachment = () => {
  form.value.attachments.push({ label: '', url: '', kind: '' })
}

const removeAttachment = (index) => {
  form.value.attachments.splice(index, 1)
}

const saveItem = async () => {
  if (!form.value.title.trim()) {
    toast.add({ severity: 'warn', summary: 'Titulo requerido', detail: 'Debes indicar un titulo para el registro.', life: 3500 })
    return
  }

  const payload = normalizePayload()

  try {
    if (editingItem.value) {
      await registryStore.updateItem(editingItem.value._id, payload)
      toast.add({ severity: 'success', summary: 'Registro actualizado', detail: 'Se han guardado los cambios.', life: 3000 })
    } else {
      await registryStore.createItem(payload)
      toast.add({ severity: 'success', summary: 'Registro creado', detail: 'El nuevo item ya forma parte del registro.', life: 3000 })
    }

    closeDialog()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: registryStore.error || 'No se pudo guardar el registro.', life: 4000 })
  }
}

const archiveItem = async (item) => {
  try {
    await registryStore.archiveItem(item._id)
    toast.add({ severity: 'success', summary: 'Registro archivado', detail: `"${item.title}" ahora esta archivado.`, life: 3000 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: registryStore.error || 'No se pudo archivar el registro.', life: 4000 })
  }
}

const duplicateItem = async (item) => {
  try {
    await registryStore.duplicateItem(item._id)
    toast.add({ severity: 'success', summary: 'Registro duplicado', detail: `Se creo una copia de "${item.title}".`, life: 3000 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: registryStore.error || 'No se pudo duplicar el registro.', life: 4000 })
  }
}

const deleteItem = async (item) => {
  try {
    await registryStore.deleteItem(item._id)
    toast.add({ severity: 'success', summary: 'Registro eliminado', detail: `"${item.title}" se elimino correctamente.`, life: 3000 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: registryStore.error || 'No se pudo eliminar el registro.', life: 4000 })
  }
}
</script>

<style scoped>
.registry-hub {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.registry-hero,
.registry-nav-strip,
.registry-toolbar,
.registry-metrics-grid,
.timeline-shell,
.table-shell,
.cards-grid,
.loading-state,
.error-state {
  width: 100%;
}

.registry-hero,
.registry-nav-strip,
.registry-toolbar,
.metric-card,
.timeline-card,
.registry-card,
.timeline-heading,
.empty-state-card,
.loading-state,
.error-state,
.section-toggle-card,
.table-shell :deep(.p-datatable),
.editor-shell {
  border: 1px solid var(--surface-border);
  border-radius: 28px;
  background: color-mix(in srgb, var(--surface-card) 88%, transparent);
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.08);
}

.registry-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.85fr);
  gap: 1rem;
  padding: 1.4rem;
  background:
    radial-gradient(circle at top right, rgba(37, 99, 235, 0.14), transparent 28%),
    linear-gradient(145deg, rgba(248, 250, 255, 0.96) 0%, rgba(250, 250, 247, 0.96) 100%);
}

.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.hero-kicker,
.summary-label,
.toolbar-label,
.type-pill,
.tag-chip,
.nav-pill,
.layout-pill,
.filter-pill,
.practice-counter,
.custom-field-chip {
  display: inline-flex;
  width: fit-content;
  border-radius: 999px;
}

.hero-kicker,
.summary-label,
.toolbar-label,
.type-pill {
  padding: 0.42rem 0.8rem;
  background: rgba(255, 255, 255, 0.74);
  color: #2563eb;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 700;
}

.hero-copy h1 {
  max-width: 12ch;
  font-size: clamp(2.2rem, 4vw, 3.5rem);
  line-height: 0.96;
  letter-spacing: -0.05em;
  color: var(--heading-color);
}

.hero-copy p,
.hero-summary-card small,
.timeline-card p,
.registry-card p,
.empty-state-card,
.loading-state p,
.error-state span,
.table-title-cell small,
.custom-field-chip span,
.section-toggle,
.dynamic-row :deep(input),
.dynamic-row :deep(.p-select-label) {
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.hero-actions,
.card-actions-row,
.info-row,
.tag-row,
.hero-summary-card,
.toolbar-block,
.layout-pill-row,
.timeline-items,
.cards-grid,
.registry-metrics-grid,
.dynamic-sections,
.dynamic-list,
.editor-grid,
.practice-actions,
.table-actions-row {
  display: flex;
  gap: 0.75rem;
}

.hero-actions,
.layout-pill-row,
.tag-row,
.card-actions-row,
.table-actions-row {
  flex-wrap: wrap;
}

.hero-summary-card {
  flex-direction: column;
  justify-content: center;
  padding: 1.15rem;
}

.hero-summary-card strong {
  display: block;
  margin: 0.55rem 0 0.35rem;
  color: var(--heading-color);
  font-size: 1.2rem;
}

.registry-nav-strip,
.registry-toolbar,
.timeline-shell,
.table-shell,
.loading-state,
.error-state,
.editor-shell {
  padding: 1rem;
}

.nav-pill,
.layout-pill,
.filter-pill {
  align-items: center;
  gap: 0.45rem;
  padding: 0.58rem 0.85rem;
  border: 1px solid rgba(124, 97, 61, 0.12);
  background: rgba(255, 255, 255, 0.76);
  color: var(--text-color-secondary);
  cursor: pointer;
}

.nav-pill.active,
.layout-pill.active,
.filter-pill.active {
  background: rgba(219, 234, 254, 0.68);
  border-color: rgba(37, 99, 235, 0.24);
  color: #1d4ed8;
}

.registry-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) auto;
  gap: 1rem;
}

.toolbar-block {
  flex-direction: column;
}

.toolbar-selects {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.field-shell {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.search-input {
  border: 1px solid var(--surface-border);
  border-radius: 14px;
  padding: 0.78rem 0.92rem;
  background: rgba(255, 255, 255, 0.84);
}

.registry-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.8rem;
}

.metric-card,
.timeline-heading,
.empty-state-card {
  padding: 0.95rem 1rem;
}

.metric-card span,
.timeline-heading small {
  color: var(--text-color-secondary);
  display: block;
  margin-bottom: 0.25rem;
}

.metric-card strong,
.timeline-month,
.timeline-card strong,
.registry-card strong,
.table-title-cell strong,
.custom-field-chip strong,
.section-toggle span {
  color: var(--heading-color);
}

.timeline-shell {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.timeline-items,
.cards-grid {
  flex-wrap: wrap;
}

.timeline-card,
.registry-card {
  flex: 1 1 320px;
  padding: 1rem;
}

.info-row {
  align-items: center;
  color: var(--text-color-secondary);
  margin-top: 0.6rem;
}

.stacked-info-row {
  flex-direction: column;
  align-items: flex-start;
}

.tag-chip {
  padding: 0.28rem 0.62rem;
  background: rgba(219, 234, 254, 0.68);
  color: #1d4ed8;
  font-size: 0.76rem;
  font-weight: 600;
}

.custom-field-preview {
  display: grid;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.custom-field-chip {
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0.75rem;
  background: rgba(248, 250, 252, 0.8);
}

.table-shell :deep(.p-datatable-header) {
  display: none;
}

.table-title-cell {
  display: flex;
  flex-direction: column;
}

.editor-shell {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.editor-grid {
  flex-wrap: wrap;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1 1 220px;
}

.wide-field {
  flex-basis: 100%;
}

.dynamic-sections {
  flex-direction: column;
}

.section-toggle-card {
  display: flex;
  flex-direction: column;
  padding: 0.8rem 1rem;
}

.section-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background: transparent;
  border: 0;
  padding: 0;
  cursor: pointer;
}

.dynamic-list {
  flex-direction: column;
  margin-top: 0.75rem;
}

.dynamic-row {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  flex-wrap: wrap;
}

.flex-1 {
  flex: 1 1 180px;
}

.narrow-input {
  width: 160px;
}

.w-full {
  width: 100%;
}

@media (max-width: 1100px) {
  .registry-hero,
  .registry-toolbar,
  .registry-metrics-grid {
    grid-template-columns: 1fr;
  }

  .toolbar-selects {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-copy h1 {
    max-width: 100%;
    font-size: 2.2rem;
  }

  .timeline-card,
  .registry-card {
    flex-basis: 100%;
  }

  .dynamic-row {
    flex-direction: column;
    align-items: stretch;
  }

  .narrow-input {
    width: 100%;
  }
}
</style>
