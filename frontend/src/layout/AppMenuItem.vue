<template>
  <li :class="containerClass">
    <div v-if="root && item.visible !== false" class="layout-menuitem-root-text">{{ item.label }}</div>
    <a
      v-if="!root && (!item.to || item.items) && item.visible !== false"
      :href="item.url"
      @click="itemClick($event, item)"
      :class="linkClass"
      :target="item.target"
      :aria-disabled="item.disabled ? 'true' : 'false'"
      tabindex="0"
    >
      <i v-if="item.icon" :class="item.icon" class="layout-menuitem-icon"></i>
      <span class="layout-menuitem-text">{{ item.label }}</span>
      <span v-if="item.featured" class="layout-menuitem-badge">Core</span>
      <i class="pi pi-fw pi-angle-down layout-submenu-toggler" v-if="item.items"></i>
    </a>
    <router-link
      v-if="item.to && !item.items && item.visible !== false"
      @click="itemClick($event, item)"
      :class="linkClass"
      :aria-disabled="item.disabled ? 'true' : 'false'"
      tabindex="0"
      :to="item.to"
    >
      <i :class="item.icon" class="layout-menuitem-icon"></i>
      <span class="layout-menuitem-text">{{ item.label }}</span>
      <span v-if="item.featured" class="layout-menuitem-badge">Core</span>
      <i class="pi pi-fw pi-angle-down layout-submenu-toggler" v-if="item.items"></i>
    </router-link>
    <Transition v-if="item.items && item.visible !== false" name="layout-submenu">
      <ul v-show="root ? true : isActiveMenu" class="layout-submenu">
        <app-menu-item v-for="(child, i) in item.items" :key="child" :index="i" :item="child" :parentItemKey="itemKey" :root="false"></app-menu-item>
      </ul>
    </Transition>
  </li>
</template>

<script setup>
import { ref, computed, watch, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'
import { useLayout } from '@/layout/composables/layout.js'

const route = useRoute()

const { layoutState, setActiveMenuItem } = useLayout()

const props = defineProps({
  item: {
    type: Object,
    default: () => ({})
  },
  index: {
    type: Number,
    default: 0
  },
  root: {
    type: Boolean,
    default: true
  },
  parentItemKey: {
    type: String,
    default: null
  }
})

const isActiveMenu = ref(false)
const itemKey = ref(null)

onBeforeMount(() => {
  itemKey.value = props.parentItemKey ? props.parentItemKey + '-' + props.index : String(props.index)

  const activeItem = layoutState.activeMenuItem.value

  isActiveMenu.value = activeItem === itemKey.value || activeItem ? activeItem.startsWith(itemKey.value + '-') : false

  if (props.item.items && hasRouteMatch(props.item)) {
    isActiveMenu.value = true
  }
})

watch(
  () => layoutState.activeMenuItem.value,
  (newVal) => {
    isActiveMenu.value = newVal === itemKey.value || newVal.startsWith(itemKey.value + '-')
  }
)

watch(
  () => route.fullPath,
  () => {
    if (props.item.items && hasRouteMatch(props.item)) {
      isActiveMenu.value = true
    }
  }
)

const hasRouteMatch = (item) => {
  if (!item) {
    return false
  }

  if (Array.isArray(item.activeRouteNames) && item.activeRouteNames.includes(route.name)) {
    return true
  }

  if (item.to && (route.path === item.to || route.path.startsWith(item.to + '/'))) {
    return true
  }

  if (Array.isArray(item.items)) {
    return item.items.some((child) => hasRouteMatch(child))
  }

  return false
}

const itemClick = (event, item) => {
  if (item.disabled) {
    event.preventDefault()
    return
  }

  if (item.command || item.items) {
    event.preventDefault()
  }

  if ((item.to || item.url) && (layoutState.staticMenuMobileActive.value)) {
    layoutState.staticMenuMobileActive.value = false
  }

  if (item.command) {
    item.command({ originalEvent: event, item: item })
  }

  const foundItemKey = item.items ? (isActiveMenu.value ? props.parentItemKey : itemKey.value) : itemKey.value

  setActiveMenuItem(foundItemKey)
}

const containerClass = computed(() => [
  {
    'layout-root-menuitem': props.root,
    'active-menuitem': isActiveMenu.value
  }
])

const linkClass = computed(() => [
  'p-ripple',
  {
    'is-featured': props.item.featured,
    'is-disabled': props.item.disabled,
    'router-link-active': isActive.value,
    'router-link-exact-active': isExactActive.value
  }
])

const isActive = computed(() => {
  if (Array.isArray(props.item.activeRouteNames) && props.item.activeRouteNames.length > 0) {
    return props.item.activeRouteNames.includes(route.name)
  }

  return route.path === props.item.to || route.path.startsWith(props.item.to + '/')
})

const isExactActive = computed(() => {
  if (Array.isArray(props.item.activeRouteNames) && props.item.activeRouteNames.length > 0) {
    return props.item.activeRouteNames.includes(route.name)
  }

  return route.path === props.item.to
})
</script>

<style scoped>
.layout-menuitem-root-text {
  text-transform: uppercase;
  color: var(--text-color-secondary);
  font-weight: 700;
  margin: 0 0 0.35rem;
  font-size: 0.72rem;
  letter-spacing: 0.16em;
}

.layout-menuitem-icon {
  margin-right: 0.75rem;
  width: 1.1rem;
  text-align: center;
}

.layout-menuitem-text {
  vertical-align: middle;
}

.layout-menuitem-badge {
  margin-left: auto;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: rgba(15, 139, 111, 0.1);
  color: #0f8b6f;
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.layout-submenu-toggler {
  margin-left: 0.35rem;
  transition: transform 0.2s;
}

.active-menuitem > .layout-submenu-toggler {
  transform: rotate(-180deg);
}

.layout-submenu {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.layout-submenu a {
  display: flex;
  align-items: center;
  position: relative;
  outline: 0 none;
  color: var(--text-color);
  cursor: pointer;
  padding: 0.9rem 1rem;
  border-radius: 16px;
  transition: background-color 0.2s, box-shadow 0.2s, transform 0.2s, border-color 0.2s;
  text-decoration: none;
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.3);
}

.layout-submenu a:hover {
  background-color: color-mix(in srgb, var(--surface-hover) 74%, transparent);
  border-color: var(--surface-border);
  transform: translateX(2px);
}

.layout-submenu a.router-link-active {
  font-weight: 700;
  color: var(--primary-color);
  background: linear-gradient(135deg, rgba(15, 139, 111, 0.12) 0%, rgba(217, 119, 6, 0.08) 100%);
  border-color: rgba(15, 139, 111, 0.18);
  box-shadow: 0 14px 24px rgba(15, 139, 111, 0.1);
}

.layout-submenu a.is-featured {
  background: linear-gradient(135deg, rgba(15, 139, 111, 0.12) 0%, rgba(37, 99, 235, 0.08) 100%);
  border-color: rgba(15, 139, 111, 0.14);
  box-shadow: 0 12px 22px rgba(15, 23, 42, 0.06);
}

.layout-submenu a.is-featured:hover {
  border-color: rgba(15, 139, 111, 0.2);
}

.layout-submenu a.is-featured .layout-menuitem-icon {
  color: #0f8b6f;
}

.layout-submenu a.router-link-active::before {
  content: '';
  position: absolute;
  left: 0.45rem;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: calc(100% - 1rem);
  border-radius: 999px;
  background: linear-gradient(180deg, #0f8b6f 0%, #d97706 100%);
}

.layout-submenu a.is-disabled {
  opacity: 0.56;
  cursor: not-allowed;
  background: rgba(248, 250, 252, 0.52);
}

.layout-submenu a.is-disabled:hover {
  transform: none;
  border-color: transparent;
  background: rgba(248, 250, 252, 0.52);
}

.layout-submenu-enter-from,
.layout-submenu-leave-to {
  max-height: 0;
}

.layout-submenu-enter-to,
.layout-submenu-leave-from {
  max-height: 1000px;
}

.layout-submenu-enter-active {
  overflow: hidden;
  transition: max-height 1s ease-in-out;
}

.layout-submenu-leave-active {
  overflow: hidden;
  transition: max-height 0.45s cubic-bezier(0, 1, 0, 1);
}
</style>
