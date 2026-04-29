import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layout/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/Home.vue')
        },
        {
          path: 'budgets',
          name: 'budgets',
          component: () => import('@/views/BudgetManager.vue')
        },
        {
          path: 'budgets/next-month-planner/setup',
          name: 'next-month-planner-setup',
          component: () => import('@/views/NextMonthPlannerSetup.vue')
        },
        {
          path: 'budgets/next-month-planner/:budgetMonth',
          name: 'next-month-planner',
          component: () => import('@/views/NextMonthPlanner.vue')
        },
        {
          path: 'budgets/monthly-summary',
          name: 'monthly-budget-summary',
          component: () => import('@/views/MonthlyBudgetSummary.vue')
        },
        {
          path: 'budgets/:id',
          name: 'budget-detail',
          component: () => import('@/views/BudgetView.vue')
        },
        {
          path: 'registry',
          name: 'registry-all',
          component: () => import('@/views/RegistryHub.vue')
        },
        {
          path: 'registry/timeline',
          name: 'registry-timeline',
          component: () => import('@/views/RegistryHub.vue')
        },
        {
          path: 'registry/dates',
          name: 'registry-dates',
          component: () => import('@/views/RegistryHub.vue')
        },
        {
          path: 'registry/trips',
          name: 'registry-trips',
          component: () => import('@/views/RegistryHub.vue')
        },
        {
          path: 'registry/purchases',
          name: 'registry-purchases',
          component: () => import('@/views/RegistryHub.vue')
        },
        {
          path: 'registry/documents',
          name: 'registry-documents',
          component: () => import('@/views/RegistryHub.vue')
        },
        {
          path: 'registry/subscriptions',
          name: 'registry-subscriptions',
          component: () => import('@/views/RegistryHub.vue')
        },
        {
          path: 'registry/notes',
          name: 'registry-notes',
          component: () => import('@/views/RegistryHub.vue')
        },
        {
          path: 'registry/archived',
          name: 'registry-archived',
          component: () => import('@/views/RegistryHub.vue')
        },
        {
          path: 'metadata',
          redirect: { name: 'registry-all' }
        },
        {
          path: 'metadata/records',
          redirect: { name: 'registry-all' }
        },
        {
          path: 'metadata/templates',
          redirect: { name: 'registry-all' }
        },
        {
          path: 'japanese',
          name: 'japanese-hub',
          component: () => import('@/views/JapaneseHub.vue')
        },
        {
          path: 'japanese/words',
          name: 'japanese-words',
          component: () => import('@/views/JapaneseHub.vue')
        },
        {
          path: 'japanese/phrases',
          name: 'japanese-phrases',
          component: () => import('@/views/JapaneseHub.vue')
        },
        {
          path: 'japanese/practice',
          name: 'japanese-practice',
          component: () => import('@/views/JapaneseHub.vue')
        },
        {
          path: 'transactions',
          name: 'transactions',
          component: () => import('@/views/TransactionManager.vue')
        },
        {
          path: 'credit-cards',
          name: 'credit-cards',
          component: () => import('@/views/CreditCardManager.vue')
        },
        {
          path: 'imports/upload',
          name: 'imports-upload',
          component: () => import('@/views/ImportedTransactionUpload.vue')
        },
        {
          path: 'imports/review',
          name: 'imports-review',
          component: () => import('@/views/ImportedTransactionReview.vue')
        },
        {
          path: 'recurring',
          name: 'recurring',
          component: () => import('@/views/RecurringManager.vue')
        },
        {
          path: 'categories',
          name: 'categories',
          component: () => import('@/views/CategoryManager.vue')
        }
      ]
    }
  ]
})

export default router
