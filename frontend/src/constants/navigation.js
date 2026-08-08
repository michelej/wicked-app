export const dashboardRoute = { name: 'dashboard' }

export const primaryNavigationItems = [
  {
    key: 'budgets',
    label: 'Presupuestos',
    icon: 'pi pi-fw pi-wallet',
    description: 'Accede al panel principal y a tus vistas financieras.',
    featuredTone: 'finance',
    to: { name: 'budgets' },
    activeRouteNames: ['budgets', 'budget-detail', 'monthly-budget-summary', 'transactions', 'credit-cards', 'imports-upload', 'imports-review', 'recurring', 'categories'],
    items: [
      {
        label: 'Panel de presupuestos',
        icon: 'pi pi-fw pi-briefcase',
        to: { name: 'budgets' },
        activeRouteNames: ['budgets']
      },
      {
        label: 'Resumen mensual',
        icon: 'pi pi-fw pi-calendar',
        to: { name: 'monthly-budget-summary' },
        activeRouteNames: ['monthly-budget-summary']
      },
      {
        label: 'Transacciones',
        icon: 'pi pi-fw pi-list',
        to: { name: 'transactions' },
        activeRouteNames: ['transactions']
      },
      {
        label: 'Tarjeta de credito',
        icon: 'pi pi-fw pi-credit-card',
        to: { name: 'credit-cards' },
        activeRouteNames: ['credit-cards']
      },
      {
        label: 'Importar extractos',
        icon: 'pi pi-fw pi-upload',
        to: { name: 'imports-upload' },
        activeRouteNames: ['imports-upload']
      },
      {
        label: 'Por validar',
        icon: 'pi pi-fw pi-inbox',
        to: { name: 'imports-review' },
        activeRouteNames: ['imports-review']
      },
      {
        label: 'Gastos recurrentes',
        icon: 'pi pi-fw pi-replay',
        to: { name: 'recurring' },
        activeRouteNames: ['recurring']
      },
      {
        label: 'Categorias',
        icon: 'pi pi-fw pi-tags',
        to: { name: 'categories' },
        activeRouteNames: ['categories']
      }
    ]
  },
  {
    key: 'registry',
    label: 'Registro',
    icon: 'pi pi-fw pi-bookmark',
    description: 'Entra directamente en la vista Todo del registro.',
    featuredTone: 'registry',
    to: { name: 'registry-all' },
    activeRouteNames: ['registry-all', 'registry-timeline', 'registry-dates', 'registry-trips', 'registry-purchases', 'registry-documents', 'registry-subscriptions', 'registry-notes', 'registry-archived'],
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
    key: 'watchlist',
    label: 'Series y Películas',
    icon: 'pi pi-fw pi-video',
    description: 'Abre la lista completa y navega desde ahi.',
    featuredTone: 'media',
    to: { name: 'watchlist-all' },
    activeRouteNames: ['watchlist-all', 'watchlist-to-watch', 'watchlist-watching', 'watchlist-watched'],
    items: [
      {
        label: 'Todo',
        icon: 'pi pi-fw pi-table',
        to: { name: 'watchlist-all' },
        activeRouteNames: ['watchlist-all']
      },
      {
        label: 'Por ver',
        icon: 'pi pi-fw pi-bookmark',
        to: { name: 'watchlist-to-watch' },
        activeRouteNames: ['watchlist-to-watch']
      },
      {
        label: 'Viendo',
        icon: 'pi pi-fw pi-play-circle',
        to: { name: 'watchlist-watching' },
        activeRouteNames: ['watchlist-watching']
      },
      {
        label: 'Vistas',
        icon: 'pi pi-fw pi-check-circle',
        to: { name: 'watchlist-watched' },
        activeRouteNames: ['watchlist-watched']
      }
    ]
  }
]

const primaryNavigationMap = Object.fromEntries(primaryNavigationItems.map((item) => [item.key, item]))

const createMobileNavigationEntry = (item) => ({
  key: item.key,
  label: item.label,
  icon: item.icon,
  description: item.description,
  tone: item.featuredTone,
  to: item.to,
  activeRouteNames: item.activeRouteNames
})

export const mobileHomeItems = primaryNavigationItems.map((item) => createMobileNavigationEntry(item))

export const mobileBottomNavigationItems = [
  {
    key: 'dashboard',
    label: 'Inicio',
    icon: 'pi pi-fw pi-home',
    to: dashboardRoute,
    activeRouteNames: ['dashboard']
  },
  createMobileNavigationEntry(primaryNavigationMap.budgets),
  createMobileNavigationEntry(primaryNavigationMap.registry)
]

export const mobileMoreNavigationItems = [
  createMobileNavigationEntry(primaryNavigationMap.watchlist)
]

export function createSidebarNavigationModel(router) {
  return [
    {
      label: 'Hub',
      items: [
        {
          label: 'Inicio',
          icon: 'pi pi-fw pi-home',
          to: dashboardRoute,
          activeRouteNames: ['dashboard']
        }
      ]
    },
    {
      label: 'Features',
      items: primaryNavigationItems.map((item) => ({
        label: item.label,
        icon: item.icon,
        featured: true,
        featuredTone: item.featuredTone,
        to: item.to,
        activeRouteNames: item.activeRouteNames,
        command: () => router.push(item.to),
        items: item.items
      }))
    }
  ]
}
