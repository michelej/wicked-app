<template>
  <div class="sidebar-menu-shell">
    <div class="menu-intro">
      <span class="menu-kicker">Hub personal</span>
      <h2>Un launcher para modulos que crecen contigo.</h2>
      <p>Selecciona una feature y despliega solo sus herramientas. El sidebar cambia de contexto sin perder consistencia.</p>
    </div>

    <ul class="layout-menu">
      <template v-for="(item, i) in model" :key="item.label">
        <app-menu-item v-if="!item.separator" :item="item" :index="i" :root="true"></app-menu-item>
        <li v-if="item.separator" class="menu-separator"></li>
      </template>
    </ul>

    <div class="menu-support-card">
      <span class="support-label">Ecosistema</span>
      <strong>Presupuestos, registro y japones ya funcionan como modulos independientes dentro del mismo hub.</strong>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppMenuItem from './AppMenuItem.vue'

const router = useRouter()

const model = ref([
  {
    label: 'Hub',
    items: [
      {
        label: 'Inicio',
        icon: 'pi pi-fw pi-home',
        to: '/',
        activeRouteNames: ['dashboard']
      }
    ]
  },
  {
    label: 'Features',
    items: [
      {
        label: 'Presupuestos',
        icon: 'pi pi-fw pi-wallet',
        to: '/budgets',
        activeRouteNames: ['budgets', 'budget-detail', 'next-month-planner-setup', 'next-month-planner', 'monthly-budget-summary', 'transactions', 'credit-cards', 'imports-upload', 'imports-review', 'recurring', 'categories'],
        command: () => router.push('/budgets'),
        items: [
          {
            label: 'Panel de presupuestos',
            icon: 'pi pi-fw pi-briefcase',
            to: '/budgets',
            activeRouteNames: ['budgets']
          },
          {
            label: 'Planificador mensual',
            icon: 'pi pi-fw pi-calendar-plus',
            to: '/budgets/next-month-planner/setup',
            activeRouteNames: ['next-month-planner-setup', 'next-month-planner']
          },
          {
            label: 'Resumen mensual',
            icon: 'pi pi-fw pi-calendar',
            to: '/budgets/monthly-summary',
            activeRouteNames: ['monthly-budget-summary']
          },
          {
            label: 'Transacciones',
            icon: 'pi pi-fw pi-list',
            to: '/transactions',
            activeRouteNames: ['transactions']
          },
          {
            label: 'Tarjeta de credito',
            icon: 'pi pi-fw pi-credit-card',
            to: '/credit-cards',
            activeRouteNames: ['credit-cards']
          },
          {
            label: 'Importar extractos',
            icon: 'pi pi-fw pi-upload',
            to: '/imports/upload',
            activeRouteNames: ['imports-upload']
          },
          {
            label: 'Por validar',
            icon: 'pi pi-fw pi-inbox',
            to: '/imports/review',
            activeRouteNames: ['imports-review']
          },
          {
            label: 'Gastos recurrentes',
            icon: 'pi pi-fw pi-replay',
            to: '/recurring',
            activeRouteNames: ['recurring']
          },
          {
            label: 'Categorias',
            icon: 'pi pi-fw pi-tags',
            to: '/categories',
            activeRouteNames: ['categories']
          }
        ]
      },
      {
        label: 'Registro',
        icon: 'pi pi-fw pi-bookmark',
        to: { name: 'registry-all' },
        activeRouteNames: ['registry-all', 'registry-timeline', 'registry-dates', 'registry-trips', 'registry-purchases', 'registry-documents', 'registry-subscriptions', 'registry-notes', 'registry-archived'],
        command: () => router.push({ name: 'registry-all' }),
        items: [
          {
            label: 'Todo',
            icon: 'pi pi-fw pi-table',
            to: { name: 'registry-all' },
            activeRouteNames: ['registry-all']
          },
          {
            label: 'Timeline',
            icon: 'pi pi-fw pi-calendar-clock',
            to: { name: 'registry-timeline' },
            activeRouteNames: ['registry-timeline']
          },
          {
            label: 'Fechas',
            icon: 'pi pi-fw pi-calendar',
            to: { name: 'registry-dates' },
            activeRouteNames: ['registry-dates']
          },
          {
            label: 'Viajes',
            icon: 'pi pi-fw pi-send',
            to: { name: 'registry-trips' },
            activeRouteNames: ['registry-trips']
          },
          {
            label: 'Compras',
            icon: 'pi pi-fw pi-shopping-bag',
            to: { name: 'registry-purchases' },
            activeRouteNames: ['registry-purchases']
          },
          {
            label: 'Documentos',
            icon: 'pi pi-fw pi-folder',
            to: { name: 'registry-documents' },
            activeRouteNames: ['registry-documents']
          },
          {
            label: 'Suscripciones',
            icon: 'pi pi-fw pi-refresh',
            to: { name: 'registry-subscriptions' },
            activeRouteNames: ['registry-subscriptions']
          },
          {
            label: 'Notas',
            icon: 'pi pi-fw pi-pencil',
            to: { name: 'registry-notes' },
            activeRouteNames: ['registry-notes']
          },
          {
            label: 'Archivados',
            icon: 'pi pi-fw pi-box',
            to: { name: 'registry-archived' },
            activeRouteNames: ['registry-archived']
          }
        ]
      },
      {
        label: 'Japones',
        icon: 'pi pi-fw pi-language',
        to: { name: 'japanese-hub' },
        activeRouteNames: ['japanese-hub', 'japanese-words', 'japanese-phrases', 'japanese-practice'],
        command: () => router.push({ name: 'japanese-hub' }),
        items: [
          {
            label: 'Vista general',
            icon: 'pi pi-fw pi-sparkles',
            to: { name: 'japanese-hub' },
            activeRouteNames: ['japanese-hub']
          },
          {
            label: 'Palabras',
            icon: 'pi pi-fw pi-list-check',
            to: { name: 'japanese-words' },
            activeRouteNames: ['japanese-words']
          },
          {
            label: 'Frases',
            icon: 'pi pi-fw pi-comment',
            to: { name: 'japanese-phrases' },
            activeRouteNames: ['japanese-phrases']
          },
          {
            label: 'Practicar',
            icon: 'pi pi-fw pi-bolt',
            to: { name: 'japanese-practice' },
            activeRouteNames: ['japanese-practice']
          }
        ]
      }
    ]
  }
])
</script>

<style scoped>
.sidebar-menu-shell {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.menu-intro {
  padding: 1.25rem;
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(214, 145, 65, 0.16), transparent 34%),
    linear-gradient(145deg, rgba(255, 251, 244, 0.96) 0%, rgba(239, 247, 241, 0.92) 100%);
  border: 1px solid rgba(124, 97, 61, 0.12);
  box-shadow: 0 18px 34px rgba(30, 41, 59, 0.08);
}

.menu-kicker {
  display: inline-flex;
  margin-bottom: 0.6rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--primary-color);
}

.menu-intro h2 {
  font-size: 1.15rem;
  line-height: 1.2;
  margin-bottom: 0.5rem;
}

.menu-intro p {
  font-size: 0.92rem;
  color: var(--text-color-secondary);
}

.layout-menu {
  margin: 0;
  padding: 0;
  list-style-type: none;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.menu-separator {
  border-top: 1px solid var(--surface-border);
  margin: 0.75rem 0;
}

.menu-support-card {
  padding: 1rem 1.1rem;
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(248, 250, 252, 0.9) 0%, rgba(255, 255, 255, 0.74) 100%);
  border: 1px solid var(--surface-border);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.support-label {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-color-secondary);
}

.menu-support-card strong {
  font-size: 0.93rem;
  line-height: 1.45;
  color: var(--text-color);
}
</style>
