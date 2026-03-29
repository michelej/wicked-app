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
          path: 'transactions',
          name: 'transactions',
          component: () => import('@/views/TransactionManager.vue')
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
