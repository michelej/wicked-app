<template>
  <li :class="containerClass">
    <div v-if="root && item.visible !== false" class="layout-menuitem-root-text">{{ item.label }}</div>
    <a
      v-if="(!item.to || item.items) && item.visible !== false"
      :href="item.url"
      @click="itemClick($event, item)"
      :class="linkClass"
      :target="item.target"
      tabindex="0"
    >      
    </a>
    <router-link
      v-if="item.to && !item.items && item.visible !== false"
      @click="itemClick($event, item)"
      :class="linkClass"
      tabindex="0"
      :to="item.to"
    >
      <i :class="item.icon" class="layout-menuitem-icon"></i>
      <span class="layout-menuitem-text">{{ item.label }}</span>
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
})

watch(
  () => layoutState.activeMenuItem.value,
  (newVal) => {
    isActiveMenu.value = newVal === itemKey.value || newVal.startsWith(itemKey.value + '-')
  }
)

const itemClick = (event, item) => {
  if (item.disabled) {
    event.preventDefault()
    return
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
    'router-link-active': isActive.value,
    'router-link-exact-active': isExactActive.value
  }
])

const isActive = computed(() => {
  return route.path === props.item.to || route.path.startsWith(props.item.to + '/')
})

const isExactActive = computed(() => {
  return route.path === props.item.to
})
</script>

<style scoped>
.layout-menuitem-root-text {
  text-transform: uppercase;
  color: var(--text-color-secondary);
  font-weight: 600;
  margin: 0.75rem 0 0.5rem 0;
  font-size: 0.857rem;
}

.layout-menuitem-icon {
  margin-right: 0.5rem;
}

.layout-menuitem-text {
  vertical-align: middle;
}

.layout-submenu-toggler {
  margin-left: auto;
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
  padding: 0.75rem 1rem;
  border-radius: 12px;
  transition: background-color 0.2s, box-shadow 0.2s;
  text-decoration: none;
}

.layout-submenu a:hover {
  background-color: var(--surface-hover);
}

.layout-submenu a.router-link-active {
  font-weight: 700;
  color: var(--primary-color);
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
