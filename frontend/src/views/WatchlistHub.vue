<template>
  <div class="watchlist-hub">
    <section class="watchlist-hero">
      <div class="hero-copy">
        <span class="hero-kicker">Series y Películas</span>
        <h1>{{ currentView.title }}</h1>
        <p>{{ currentView.description }}</p>

        <div class="hero-actions">
          <Button label="Añadir desde TMDb" icon="pi pi-search" severity="warning" @click="openSearchDialog" />
          <Button label="Ver pendientes" icon="pi pi-bookmark" outlined @click="goToRoute('watchlist-to-watch')" />
        </div>
      </div>

      <div class="hero-summary-card">
        <span class="summary-label">Estado actual</span>
        <strong>{{ watchlistStore.items.length }} titulos en seguimiento</strong>
        <small>Combina peliculas y series en una sola lista personal con estados simples: por ver, viendo y vistas.</small>
      </div>
    </section>

    <section class="watchlist-nav-strip">
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

    <section class="watchlist-toolbar">
      <div class="toolbar-field wide-field">
        <span class="toolbar-label">Buscar en tu lista</span>
        <input v-model.trim="filters.search" class="search-input" type="text" placeholder="Titulo, nota o tag" />
      </div>

      <div class="toolbar-field">
        <span class="toolbar-label">Formato</span>
        <Select v-model="filters.mediaType" :options="mediaTypeOptions" optionLabel="label" optionValue="value" class="w-full" />
      </div>
    </section>

    <div v-if="watchlistStore.loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando watchlist...</p>
    </div>

    <div v-else-if="watchlistStore.error && watchlistStore.items.length === 0" class="error-state">
      <i class="pi pi-exclamation-triangle"></i>
      <span>{{ watchlistStore.error }}</span>
    </div>

    <template v-else>
      <section class="metrics-grid">
        <div class="metric-card">
          <span>Por ver</span>
          <strong>{{ watchlistStore.toWatchItems.length }}</strong>
        </div>
        <div class="metric-card">
          <span>Viendo</span>
          <strong>{{ watchlistStore.watchingItems.length }}</strong>
        </div>
        <div class="metric-card">
          <span>Vistas</span>
          <strong>{{ watchlistStore.watchedItems.length }}</strong>
        </div>
        <div class="metric-card">
          <span>Series</span>
          <strong>{{ seriesCount }}</strong>
        </div>
      </section>

      <section class="watchlist-grid">
        <article v-for="item in filteredItems" :key="item._id" class="watch-card">
          <div class="poster-shell">
            <img v-if="item.poster_path" :src="item.poster_path" :alt="item.title" class="poster-image" />
            <div v-else class="poster-fallback">
              <i class="pi pi-video"></i>
            </div>

            <div class="poster-overlay">
              <div class="poster-overlay-top">
                <span class="type-pill media-pill">{{ item.media_type === 'movie' ? 'Película' : 'Serie' }}</span>
                <Tag :value="statusLabels[item.status]" :severity="statusSeverities[item.status]" />
              </div>

              <div class="poster-overlay-bottom">
                <div v-if="item.personal_rating !== null && item.personal_rating !== undefined" class="poster-rating-badge">
                  <i class="pi pi-star-fill"></i>
                  <span>{{ item.personal_rating }}</span>
                </div>

                <div class="poster-quick-actions">
                  <Button icon="pi pi-pencil" rounded severity="secondary" @click="openEditDialog(item)" />
                  <Button icon="pi pi-step-forward" rounded severity="warning" @click="advanceStatus(item)" />
                  <Button icon="pi pi-trash" rounded severity="danger" @click="deleteItem(item)" />
                </div>
              </div>
            </div>
          </div>

          <div class="watch-card-body">
            <strong class="watch-card-title">{{ item.title }}</strong>

            <div class="watch-card-meta">
              <small v-if="item.release_date">{{ item.release_date }}</small>
              <span v-if="item.personal_rating !== null && item.personal_rating !== undefined" class="rating-chip">
                <i class="pi pi-star-fill"></i>
                {{ item.personal_rating }}/10
              </span>
            </div>

            <p class="watch-card-overview">{{ item.overview || 'Sin sinopsis disponible.' }}</p>

            <div class="tag-row">
              <span v-for="genre in item.genres.slice(0, 3)" :key="`${item._id}-${genre}`" class="tag-chip">{{ genre }}</span>
              <span v-for="tag in item.tags.slice(0, 2)" :key="`${item._id}-${tag}`" class="tag-chip muted-chip">{{ tag }}</span>
            </div>

            <div class="meta-row compact-meta-row">
              <span v-if="item.notes"><i class="pi pi-comment"></i> {{ item.notes }}</span>
            </div>
          </div>
        </article>

        <div v-if="filteredItems.length === 0" class="empty-state-card">
          No hay títulos que coincidan con la vista o búsqueda actual.
        </div>
      </section>
    </template>

    <Dialog v-model:visible="showSearchDialog" modal header="Añadir serie o película" :style="{ width: '980px' }">
      <div class="dialog-shell">
        <div class="search-toolbar">
          <InputText v-model.trim="searchQuery" class="flex-1" placeholder="Buscar en TMDb" @keyup.enter="performCatalogSearch" />
          <Select v-model="searchMediaType" :options="searchMediaTypeOptions" optionLabel="label" optionValue="value" class="media-select" />
          <Button label="Buscar" icon="pi pi-search" severity="warning" :loading="watchlistStore.searching" @click="performCatalogSearch" />
        </div>

        <div v-if="watchlistStore.error && watchlistStore.searchResults.length === 0" class="inline-error">
          {{ watchlistStore.error }}
        </div>

        <div class="search-results-grid">
          <article v-for="result in watchlistStore.searchResults" :key="`${result.media_type}-${result.tmdb_id}`" class="search-result-card">
            <img v-if="result.poster_path" :src="result.poster_path" :alt="result.title" class="search-poster" />
            <div v-else class="poster-fallback search-poster-fallback">
              <i class="pi pi-video"></i>
            </div>

            <div class="search-copy">
              <div class="card-top-row">
                <span class="type-pill">{{ result.media_type === 'movie' ? 'Película' : 'Serie' }}</span>
                <small>{{ result.release_date || 'Sin fecha' }}</small>
              </div>
              <strong>{{ result.title }}</strong>
              <p>{{ result.overview || 'Sinopsis no disponible.' }}</p>
              <Button label="Añadir a Por ver" icon="pi pi-plus" severity="success" @click="addSearchResultToWatchlist(result)" :loading="watchlistStore.saving" />
            </div>
          </article>

          <div v-if="!watchlistStore.searching && watchlistStore.searchResults.length === 0" class="empty-state-card compact-empty">
            Busca un título para empezar a poblar tu lista.
          </div>
        </div>
      </div>
    </Dialog>

    <Dialog v-model:visible="showEditorDialog" modal :header="editingItem ? 'Editar seguimiento' : 'Editar'" :style="{ width: '720px' }">
      <div class="dialog-shell form-dialog-shell">
        <div class="editor-grid">
          <div class="form-field wide-field">
            <label>Título</label>
            <InputText v-model="form.title" class="w-full" disabled />
          </div>

          <div class="form-field">
            <label>Estado</label>
            <Select v-model="form.status" :options="statusOptions" optionLabel="label" optionValue="value" class="w-full" />
          </div>

          <div class="form-field">
            <label>Rating personal</label>
            <InputNumber v-model="form.personal_rating" :min="0" :max="10" :minFractionDigits="0" :maxFractionDigits="1" class="w-full" />
          </div>

          <div class="form-field wide-field">
            <label>Notas</label>
            <Textarea v-model="form.notes" rows="4" class="w-full" />
          </div>

          <div class="form-field wide-field">
            <label>Tags</label>
            <InputText v-model="tagsInput" class="w-full" placeholder="thriller, cine, rewatch" />
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Cancelar" text @click="closeEditDialog" />
        <Button label="Guardar" icon="pi pi-check" severity="warning" :loading="watchlistStore.saving" @click="saveEdit" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useWatchlistStore } from '@/stores/watchlist'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const watchlistStore = useWatchlistStore()

const navItems = [
  { routeName: 'watchlist-all', label: 'Todo', icon: 'pi pi-table' },
  { routeName: 'watchlist-to-watch', label: 'Por ver', icon: 'pi pi-bookmark' },
  { routeName: 'watchlist-watching', label: 'Viendo', icon: 'pi pi-play-circle' },
  { routeName: 'watchlist-watched', label: 'Vistas', icon: 'pi pi-check-circle' }
]

const viewMap = {
  'watchlist-all': {
    title: 'Una watchlist personal para no perder de vista lo que quieres ver.',
    description: 'Guarda películas y series, busca en TMDb y mueve cada título entre por ver, viendo y vistas.'
  },
  'watchlist-to-watch': {
    title: 'Todo lo pendiente de ver en un solo lugar claro y visual.',
    description: 'Ideal para capturar recomendaciones rápidas y decidir qué ver después.'
  },
  'watchlist-watching': {
    title: 'Un espacio para lo que ya tienes en marcha.',
    description: 'Sigue series activas o películas pausadas sin perder el hilo.'
  },
  'watchlist-watched': {
    title: 'Historial visto con notas y rating personal.',
    description: 'Conserva un archivo ligero de lo que ya terminaste y cómo te dejó.'
  }
}

const statusOptions = [
  { value: 'to_watch', label: 'Por ver' },
  { value: 'watching', label: 'Viendo' },
  { value: 'watched', label: 'Vista' }
]

const statusLabels = {
  to_watch: 'Por ver',
  watching: 'Viendo',
  watched: 'Vista'
}

const statusSeverities = {
  to_watch: 'secondary',
  watching: 'warning',
  watched: 'success'
}

const mediaTypeOptions = [
  { value: 'all', label: 'Todo' },
  { value: 'movie', label: 'Películas' },
  { value: 'tv', label: 'Series' }
]

const searchMediaTypeOptions = [
  { value: 'multi', label: 'Todo' },
  { value: 'movie', label: 'Películas' },
  { value: 'tv', label: 'Series' }
]

const routeStatusMap = {
  'watchlist-all': null,
  'watchlist-to-watch': 'to_watch',
  'watchlist-watching': 'watching',
  'watchlist-watched': 'watched'
}

const filters = ref({
  search: '',
  mediaType: 'all'
})

const showSearchDialog = ref(false)
const searchQuery = ref('')
const searchMediaType = ref('multi')
const showEditorDialog = ref(false)
const editingItem = ref(null)
const form = ref({
  title: '',
  status: 'to_watch',
  personal_rating: null,
  notes: '',
  tags: []
})
const tagsInput = ref('')

const currentView = computed(() => viewMap[route.name] || viewMap['watchlist-all'])
const activeStatusFilter = computed(() => routeStatusMap[route.name] ?? null)
const filteredItems = computed(() => {
  const query = filters.value.search.toLowerCase()

  return watchlistStore.items.filter((item) => {
    if (activeStatusFilter.value && item.status !== activeStatusFilter.value) {
      return false
    }

    if (filters.value.mediaType !== 'all' && item.media_type !== filters.value.mediaType) {
      return false
    }

    if (!query) {
      return true
    }

    const haystack = `${item.title} ${item.original_title || ''} ${item.notes || ''} ${(item.tags || []).join(' ')}`.toLowerCase()
    return haystack.includes(query)
  })
})

const seriesCount = computed(() => watchlistStore.items.filter((item) => item.media_type === 'tv').length)

watch(
  () => route.name,
  () => {
    filters.value.search = ''
  }
)

onMounted(async () => {
  await watchlistStore.fetchItems()
})

const goToRoute = (routeName) => {
  router.push({ name: routeName })
}

const openSearchDialog = () => {
  showSearchDialog.value = true
}

const performCatalogSearch = async () => {
  if (!searchQuery.value.trim()) {
    toast.add({ severity: 'warn', summary: 'Busca un título', detail: 'Introduce al menos 2 caracteres para consultar TMDb.', life: 3000 })
    return
  }

  try {
    await watchlistStore.searchCatalog({ q: searchQuery.value.trim(), mediaType: searchMediaType.value })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Búsqueda no disponible', detail: watchlistStore.error || 'No se pudo consultar TMDb.', life: 4000 })
  }
}

const addSearchResultToWatchlist = async (result) => {
  try {
    await watchlistStore.createItem({
      tmdb_id: result.tmdb_id,
      media_type: result.media_type,
      title: result.title,
      original_title: result.original_title,
      overview: result.overview,
      poster_path: result.poster_path,
      backdrop_path: result.backdrop_path,
      release_date: result.release_date,
      genres: result.genres || [],
      status: 'to_watch',
      notes: '',
      tags: []
    })
    toast.add({ severity: 'success', summary: 'Añadido', detail: `"${result.title}" ya está en tu lista.`, life: 3000 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'No se pudo añadir', detail: watchlistStore.error || 'Revisa la configuración de TMDb o si el título ya existe.', life: 4000 })
  }
}

const openEditDialog = (item) => {
  editingItem.value = item
  form.value = {
    title: item.title,
    status: item.status,
    personal_rating: item.personal_rating ?? null,
    notes: item.notes || '',
    tags: [...(item.tags || [])]
  }
  tagsInput.value = form.value.tags.join(', ')
  showEditorDialog.value = true
}

const closeEditDialog = () => {
  showEditorDialog.value = false
  editingItem.value = null
}

const saveEdit = async () => {
  if (!editingItem.value) {
    return
  }

  const tags = tagsInput.value.split(',').map((tag) => tag.trim()).filter(Boolean)
  try {
    await watchlistStore.updateItem(editingItem.value._id, {
      status: form.value.status,
      personal_rating: form.value.personal_rating,
      notes: form.value.notes,
      tags,
      watched_at: form.value.status === 'watched' ? new Date().toISOString() : null,
      started_at: form.value.status === 'watching' ? (editingItem.value.started_at || new Date().toISOString()) : null
    })
    toast.add({ severity: 'success', summary: 'Actualizado', detail: 'El seguimiento se guardó correctamente.', life: 3000 })
    closeEditDialog()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: watchlistStore.error || 'No se pudo guardar.', life: 4000 })
  }
}

const advanceStatus = async (item) => {
  const nextStatus = item.status === 'to_watch' ? 'watching' : item.status === 'watching' ? 'watched' : 'to_watch'

  try {
    await watchlistStore.updateItem(item._id, {
      status: nextStatus,
      started_at: nextStatus === 'watching' ? (item.started_at || new Date().toISOString()) : item.started_at,
      watched_at: nextStatus === 'watched' ? new Date().toISOString() : null
    })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: watchlistStore.error || 'No se pudo cambiar el estado.', life: 4000 })
  }
}

const deleteItem = async (item) => {
  try {
    await watchlistStore.deleteItem(item._id)
    toast.add({ severity: 'success', summary: 'Eliminado', detail: `"${item.title}" salió de tu lista.`, life: 3000 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: watchlistStore.error || 'No se pudo eliminar.', life: 4000 })
  }
}
</script>

<style scoped>
.watchlist-hub {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.watchlist-hero,
.watchlist-nav-strip,
.watchlist-toolbar,
.metric-card,
.watch-card,
.loading-state,
.error-state,
.dialog-shell,
.empty-state-card,
.search-result-card {
  border: 1px solid var(--surface-border);
  border-radius: 26px;
  background: color-mix(in srgb, var(--surface-card) 88%, transparent);
  box-shadow: 0 16px 30px rgba(15, 23, 42, 0.08);
}

.watchlist-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.8fr);
  gap: 1rem;
  padding: 1.4rem;
  background:
    radial-gradient(circle at top right, rgba(244, 114, 182, 0.16), transparent 26%),
    linear-gradient(145deg, rgba(255, 248, 244, 0.96) 0%, rgba(250, 247, 255, 0.96) 100%);
}

.hero-kicker,
.summary-label,
.toolbar-label,
.type-pill,
.tag-chip,
.nav-pill,
.layout-pill,
.filter-pill {
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
  color: #db2777;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 700;
}

.hero-copy,
.hero-summary-card,
.watch-card-body,
.search-copy,
.toolbar-field,
.dialog-shell {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.hero-copy h1 {
  max-width: 13ch;
  font-size: clamp(2.2rem, 4vw, 3.4rem);
  line-height: 0.96;
  letter-spacing: -0.05em;
  color: var(--heading-color);
}

.hero-copy p,
.hero-summary-card small,
.watch-card p,
.search-copy p,
.empty-state-card,
.loading-state p,
.error-state span,
.meta-row {
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.hero-actions,
.card-actions-row,
.tag-row,
.meta-row,
.search-toolbar {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.hero-summary-card,
.watchlist-nav-strip,
.watchlist-toolbar,
.loading-state,
.error-state,
.dialog-shell {
  padding: 1rem;
}

.hero-summary-card strong,
.metric-card strong,
.watch-card strong,
.search-copy strong {
  color: var(--heading-color);
}

.watchlist-nav-strip {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.nav-pill {
  align-items: center;
  gap: 0.45rem;
  padding: 0.58rem 0.85rem;
  border: 1px solid rgba(124, 97, 61, 0.12);
  background: rgba(255, 255, 255, 0.76);
  color: var(--text-color-secondary);
  cursor: pointer;
}

.nav-pill.active {
  background: rgba(251, 207, 232, 0.55);
  border-color: rgba(219, 39, 119, 0.2);
  color: #be185d;
}

.watchlist-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) 220px;
  gap: 1rem;
}

.toolbar-field {
  gap: 0.35rem;
}

.wide-field {
  width: 100%;
}

.search-input {
  border: 1px solid var(--surface-border);
  border-radius: 14px;
  padding: 0.78rem 0.92rem;
  background: rgba(255, 255, 255, 0.84);
}

.metrics-grid,
.watchlist-grid,
.search-results-grid,
.editor-grid {
  display: grid;
  gap: 0.85rem;
}

.metrics-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.metric-card {
  padding: 0.9rem 1rem;
}

.metric-card span {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--text-color-secondary);
}

.watchlist-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.watch-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.watch-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 38px rgba(15, 23, 42, 0.14);
}

.poster-shell {
  position: relative;
  aspect-ratio: 2 / 3;
  width: 100%;
  background: #111827;
  overflow: hidden;
}

.poster-image,
.search-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.poster-fallback {
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, rgba(244, 114, 182, 0.14), rgba(99, 102, 241, 0.08));
  color: #7c3aed;
  font-size: 2rem;
}

.poster-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.8rem;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.2) 0%, rgba(15, 23, 42, 0.02) 35%, rgba(15, 23, 42, 0.7) 100%);
  pointer-events: none;
}

.poster-overlay-top,
.poster-overlay-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
}

.media-pill {
  background: rgba(255, 255, 255, 0.88);
  color: #111827;
}

.poster-rating-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.45rem 0.65rem;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.78);
  color: #fbbf24;
  font-size: 0.82rem;
  font-weight: 800;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.18);
}

.poster-quick-actions {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin-left: auto;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.2s ease, transform 0.2s ease;
  pointer-events: auto;
}

.watch-card:hover .poster-quick-actions {
  opacity: 1;
  transform: translateY(0);
}

.poster-quick-actions :deep(.p-button) {
  width: 2.2rem;
  height: 2.2rem;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.18);
}

.watch-card-body {
  padding: 0.95rem 1rem 1rem;
}

.watch-card-title {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.7rem;
  margin-top: 0.15rem;
}

.watch-card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.rating-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.32rem;
  color: #b45309;
  font-size: 0.82rem;
  font-weight: 700;
}

.watch-card-overview {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 4.8rem;
}

.card-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.tag-row {
  align-items: center;
}

.tag-chip {
  padding: 0.28rem 0.62rem;
  background: rgba(251, 207, 232, 0.54);
  color: #be185d;
  font-size: 0.76rem;
  font-weight: 600;
}

.muted-chip {
  background: rgba(226, 232, 240, 0.72);
  color: #475569;
}

.meta-row {
  gap: 1rem;
}

.compact-meta-row {
  min-height: 1.5rem;
  font-size: 0.8rem;
}

.dialog-shell {
  gap: 1rem;
}

.search-toolbar {
  align-items: center;
}

.flex-1 {
  flex: 1 1 240px;
}

.media-select {
  width: 180px;
}

.search-results-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.search-result-card {
  overflow: hidden;
}

.search-poster {
  height: 220px;
}

.search-poster-fallback {
  min-height: 220px;
}

.search-copy {
  padding: 1rem;
}

.inline-error {
  padding: 0.9rem 1rem;
  border-radius: 18px;
  background: rgba(254, 242, 242, 0.8);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.18);
}

.editor-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.w-full {
  width: 100%;
}

.empty-state-card.compact-empty {
  padding: 1rem;
}

@media (max-width: 1100px) {
  .watchlist-hero,
  .watchlist-toolbar,
  .metrics-grid,
  .editor-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .poster-quick-actions {
    opacity: 1;
    transform: translateY(0);
  }

  .media-select {
    width: 100%;
  }
}
</style>
