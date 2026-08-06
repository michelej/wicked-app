# GitHub Copilot Instructions

This file describes the Wicked App full-stack project and helps Copilot understand where to find functionality, how the frontend is organized, and how the backend is structured.

## Project architecture overview

- **Backend**: `backend/`
  - FastAPI application
  - `backend/main.py` launches the app and configures CORS
  - `backend/app/api/routes.py` bundles endpoint routers
  - `backend/app/services/` contains business logic services
  - `backend/app/models/` contains domain models and data mapping
  - `backend/app/core/` contains config and database connection helpers

- **Database**: `database/`
  - MongoDB initialization scripts and Docker database setup
  - `docker-compose.yml` and `docker-compose.prod.yml` orchestrate the full stack

- **Frontend**: `frontend/`
  - Vue 3 application using Vite
  - Pinia for state management
  - PrimeVue for UI components
  - `frontend/src/router/index.js` defines page routes and URL structure
  - `frontend/src/services/*.js` wraps backend API calls
  - `frontend/src/stores/*.js` stores page state and data models
  - `frontend/src/views/*.vue` contains page-level routes
  - `frontend/src/layout/*.vue` contains shell layout and navigation UI

- **Scripts / Dev**: project-level scripts in `scripts/` provide local start/stop helpers for development and Docker.

## Frontend component overview

The frontend is organized around route-based view pages and layout components. Use the following table to locate pages quickly.

| Component | Route | Purpose | Notes |
|---|---|---|---|
| `Home.vue` | `/` | Main dashboard landing page | Dashboard summary and quick access |
| `BudgetManager.vue` | `/budgets` | Budget list and management | Budget CRUD interaction |
| `BudgetView.vue` | `/budgets/:id` | Single budget detail page | Budget detail and item view |
| `MonthlyBudgetSummary.vue` | `/budgets/monthly-summary` | Monthly budget summary | Aggregated budget analytics |
| `RegistryHub.vue` | `/registry*` | Metadata and registry hub | Registry tabs share this view |
| `WatchlistHub.vue` | `/watchlist*` | Watchlist hub for tracked items | Watchlist tabs share this view |
| `TransactionManager.vue` | `/transactions` | Transaction listing and management | Includes transaction filters |
| `CreditCardManager.vue` | `/credit-cards` | Credit card transaction management | Card-specific transaction workflows |
| `ImportedTransactionUpload.vue` | `/imports/upload` | Upload imported transaction files | File upload UI |
| `ImportedTransactionReview.vue` | `/imports/review` | Review imported transactions | Review and import confirmation |
| `RecurringManager.vue` | `/recurring` | Recurring expense management | Recurring schedule and rules |
| `CategoryManager.vue` | `/categories` | Category management | Category CRUD operations |

## Layout and shared UI components

| Component | Purpose |
|---|---|
| `App.vue` | Root application wrapper |
| `AppLayout.vue` | Main shell layout around views |
| `AppSidebar.vue` | Primary navigation sidebar |
| `AppTopbar.vue` | Top header and controls |
| `AppFooter.vue` | App footer and status |
| `AppMenu.vue` | Sidebar menu container |
| `AppMenuItem.vue` | Individual nav menu entries |

## Frontend service/store organization

- `frontend/src/services/api.js`: base API wrapper and Axios configuration
- `frontend/src/services/*.js`: one service per domain (`budgetService.js`, `categoryService.js`, `transactionService.js`, etc.)
- `frontend/src/stores/*.js`: Pinia stores aligned with domains (`budgets.js`, `categories.js`, `transactions.js`, `dashboard.js`, etc.)
- `frontend/src/composables/`: reusable composables such as `useFormatters.js` and `useMobile.js`

## Backend service and routing organization

- `backend/main.py`: FastAPI app startup, MongoDB lifecycle, root health endpoints
- `backend/app/api/routes.py`: registers the router prefix `/api`
- `backend/app/api/endpoints/*.py`: endpoint modules for categories, budgets, credit cards, transactions, imported transactions, recurring expenses, dashboard, registry items, and watchlist
- `backend/app/services/*.py`: application logic separated from route handlers
- `backend/app/core/config.py`: environment-driven settings
- `backend/app/core/database.py`: MongoDB connection utilities

## How to use this file

- Use this guidance when answering questions about app structure, writing new features, or modifying existing functionality.
- Prefer route-based views and domain-aligned stores/services when changing the frontend.
- Prefer service-layer business logic and reusable model patterns in the backend.
- Keep changes consistent with Vue 3 + Pinia + PrimeVue styling and FastAPI idioms.

## Summary and navigation keywords

- FastAPI, MongoDB, Vue 3, Pinia, PrimeVue, Vite
- backend: `main.py`, `app/api/routes.py`, `app/services`, `app/models`, `app/core`
- frontend: `src/router/index.js`, `src/views`, `src/layout`, `src/services`, `src/stores`, `src/composables`
- app domains: budgets, transactions, registry, watchlist, imported transactions, recurring, categories, dashboard
- development: `docker-compose.yml`, `docker-compose.prod.yml`, `frontend/package.json`, `backend/pyproject.toml`

> Use these keywords to navigate quickly and keep the assistant aligned with the project’s architecture and conventions.
