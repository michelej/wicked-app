<template>
  <nav class="mobile-bottom-navigation" aria-label="Navegacion principal movil">
      <button
        v-for="item in items"
        :key="item.key"
        type="button"
        class="mobile-nav-item"
        :class="{ 'is-active': isItemActive(item) }"
        @click="navigateTo(item)"
      >
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </button>

      <button
        type="button"
        class="mobile-nav-item"
        :class="{ 'is-active': isMoreActive }"
        :aria-expanded="showMoreSheet ? 'true' : 'false'"
        aria-controls="mobile-more-sheet"
        @click="toggleMoreSheet"
      >
        <i class="pi pi-fw pi-ellipsis-h"></i>
        <span>Más</span>
      </button>
  </nav>

  <Transition name="mobile-sheet-fade">
    <div v-if="showMoreSheet" class="mobile-sheet-backdrop" @click.self="closeMoreSheet">
      <div id="mobile-more-sheet" class="mobile-sheet" role="dialog" aria-modal="true" aria-label="Mas secciones">
          <div class="sheet-handle" aria-hidden="true"></div>

          <div class="sheet-header">
            <div>
              <span class="sheet-kicker">Más</span>
              <h2>Otras secciones</h2>
            </div>

            <button type="button" class="sheet-close-button" aria-label="Cerrar mas opciones" @click="closeMoreSheet">
              <i class="pi pi-times"></i>
            </button>
          </div>

          <div class="sheet-actions">
            <button
              v-for="item in moreItems"
              :key="item.key"
              type="button"
              class="sheet-action"
              :class="{ 'is-active': isItemActive(item) }"
              @click="navigateTo(item)"
            >
              <span class="sheet-action-icon" :class="`is-${item.tone}`">
                <i :class="item.icon"></i>
              </span>

              <span class="sheet-action-copy">
                <strong>{{ item.label }}</strong>
                <small>{{ item.description }}</small>
              </span>

              <i class="pi pi-angle-right sheet-action-chevron"></i>
            </button>
          </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  moreItems: {
    type: Array,
    default: () => []
  }
})

const route = useRoute()
const router = useRouter()
const showMoreSheet = ref(false)

const isItemActive = (item) => {
  if (!item) {
    return false
  }

  return Array.isArray(item.activeRouteNames) && item.activeRouteNames.includes(route.name)
}

const isMoreActive = computed(() => props.moreItems.some((item) => isItemActive(item)))

const closeMoreSheet = () => {
  showMoreSheet.value = false
}

const toggleMoreSheet = () => {
  showMoreSheet.value = !showMoreSheet.value
}

const navigateTo = (item) => {
  closeMoreSheet()
  router.push(item.to)
}

watch(
  () => route.fullPath,
  () => {
    closeMoreSheet()
  }
)
</script>

<style scoped>
.mobile-bottom-navigation {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1002;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.35rem;
  padding: 0.65rem 0.75rem calc(0.65rem + env(safe-area-inset-bottom));
  background: color-mix(in srgb, var(--surface-card) 94%, transparent);
  border-top: 1px solid var(--surface-border);
  backdrop-filter: blur(22px);
  box-shadow: 0 -12px 32px rgba(15, 23, 42, 0.12);
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.28rem;
  min-height: 3.25rem;
  padding: 0.45rem 0.35rem;
  border: 0;
  border-radius: 18px;
  background: transparent;
  color: var(--text-color-secondary);
  font: inherit;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.mobile-nav-item i {
  font-size: 1.1rem;
}

.mobile-nav-item span {
  font-size: 0.72rem;
  font-weight: 700;
  line-height: 1.1;
}

.mobile-nav-item.is-active {
  color: var(--primary-color);
  background: linear-gradient(180deg, rgba(15, 139, 111, 0.14) 0%, rgba(217, 119, 6, 0.06) 100%);
}

.mobile-nav-item:active {
  transform: scale(0.98);
}

.mobile-sheet-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1001;
  display: flex;
  align-items: flex-end;
  padding: 1rem 0.85rem calc(5.75rem + env(safe-area-inset-bottom));
  background: rgba(15, 23, 42, 0.24);
  backdrop-filter: blur(3px);
}

.mobile-sheet {
  width: 100%;
  border: 1px solid var(--surface-border);
  border-radius: 28px;
  background:
    radial-gradient(circle at top right, rgba(214, 145, 65, 0.12), transparent 28%),
    linear-gradient(160deg, color-mix(in srgb, var(--surface-card) 98%, transparent) 0%, color-mix(in srgb, var(--surface-card) 94%, transparent) 100%);
  box-shadow: 0 22px 48px rgba(15, 23, 42, 0.18);
  overflow: hidden;
}

.sheet-handle {
  width: 3rem;
  height: 0.3rem;
  margin: 0.75rem auto 0;
  border-radius: 999px;
  background: rgba(100, 116, 139, 0.28);
}

.sheet-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1rem 0.8rem;
}

.sheet-kicker {
  display: inline-flex;
  margin-bottom: 0.45rem;
  padding: 0.35rem 0.72rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--primary-color);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.sheet-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--heading-color);
}

.sheet-close-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid var(--surface-border);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  color: var(--text-color-secondary);
}

.sheet-actions {
  display: grid;
  gap: 0.75rem;
  padding: 0 1rem 1rem;
}

.sheet-action {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.85rem;
  width: 100%;
  min-height: 4.5rem;
  padding: 0.9rem 0.95rem;
  border: 1px solid rgba(124, 97, 61, 0.12);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.68);
  text-align: left;
  color: inherit;
}

.sheet-action.is-active {
  border-color: rgba(15, 139, 111, 0.2);
  box-shadow: 0 14px 24px rgba(15, 139, 111, 0.1);
}

.sheet-action-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: 18px;
  color: white;
  background: linear-gradient(145deg, #0f8b6f 0%, #d97706 100%);
  box-shadow: 0 10px 18px rgba(15, 139, 111, 0.18);
}

.sheet-action-icon.is-registry {
  background: linear-gradient(145deg, #2563eb 0%, #0ea5e9 100%);
}

.sheet-action-icon.is-media {
  background: linear-gradient(145deg, #db2777 0%, #7c3aed 100%);
}

.sheet-action-copy {
  display: flex;
  flex-direction: column;
  gap: 0.18rem;
  min-width: 0;
}

.sheet-action-copy strong {
  font-size: 1rem;
  color: var(--heading-color);
}

.sheet-action-copy small,
.sheet-action-chevron {
  color: var(--text-color-secondary);
}

.mobile-sheet-fade-enter-active,
.mobile-sheet-fade-leave-active {
  transition: opacity 0.2s ease;
}

.mobile-sheet-fade-enter-from,
.mobile-sheet-fade-leave-to {
  opacity: 0;
}
</style>
