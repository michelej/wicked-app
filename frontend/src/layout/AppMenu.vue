<template>
  <ul class="layout-menu">
    <template v-for="(item, i) in model" :key="item">
      <app-menu-item v-if="!item.separator" :item="item" :index="i" :root="true"></app-menu-item>
      <li v-if="item.separator" class="menu-separator"></li>
    </template>
  </ul>
</template>

<script setup>
import { ref } from 'vue'
import AppMenuItem from './AppMenuItem.vue'

const model = ref([
  {
    label: 'Principal',
    items: [
      {
        label: 'Dashboard',
        icon: 'pi pi-fw pi-home',
        to: '/'
      }
    ]
  },
  {
    label: 'Finanzas',
    items: [
      {
        label: 'Presupuestos',
        icon: 'pi pi-fw pi-wallet',
        to: '/budgets'
      },
      {
        label: 'Transacciones',
        icon: 'pi pi-fw pi-list',
        to: '/transactions'
      },
      {
        label: 'Gastos Recurrentes',
        icon: 'pi pi-fw pi-replay',
        to: '/recurring'
      },
      {
        label: 'Categorías',
        icon: 'pi pi-fw pi-tags',
        to: '/categories'
      },
      {
        label: 'Plantillas',
        icon: 'pi pi-fw pi-copy',
        to: '/templates'
      }
    ]
  }
])
</script>

<style scoped>
.layout-menu {
  margin: 0;
  padding: 0;
  list-style-type: none;
}

.menu-separator {
  border-top: 1px solid var(--surface-border);
  margin: 0.75rem 0;
}
</style>
