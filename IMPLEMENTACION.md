# Sistema de Finanzas del Hogar - Wicked App

## Estado de la Implementación

### ✅ Backend Completado (FastAPI + MongoDB)

El backend está completamente implementado con todas las funcionalidades requeridas:

#### Modelos de Datos
- ✅ **Category** - Categorías configurables (Agua, Luz, Netflix, etc.)
- ✅ **Budget** - Presupuestos mensuales con fechas flexibles
- ✅ **Transaction** - Transacciones de ingresos y egresos
- ✅ **BudgetTemplate** - Plantillas de presupuesto reutilizables
- ✅ **RecurringExpense** - Gastos recurrentes anuales

#### Endpoints API Implementados

**Categorías** (`/api/categories`)
- `GET /api/categories` - Listar todas las categorías
- `POST /api/categories` - Crear nueva categoría
- `GET /api/categories/{id}` - Obtener categoría específica
- `PUT /api/categories/{id}` - Actualizar categoría
- `DELETE /api/categories/{id}` - Eliminar categoría

**Presupuestos** (`/api/budgets`)
- `GET /api/budgets` - Listar presupuestos
- `GET /api/budgets/active` - Obtener presupuestos activos
- `GET /api/budgets/{id}` - Obtener presupuesto específico
- `GET /api/budgets/{id}/summary` - Resumen financiero del presupuesto
- `POST /api/budgets` - Crear nuevo presupuesto
- `PUT /api/budgets/{id}` - Actualizar presupuesto
- `DELETE /api/budgets/{id}` - Eliminar presupuesto

**Transacciones** (`/api/transactions`)
- `GET /api/transactions` - Listar transacciones (con filtros)
- `GET /api/transactions/budget/{id}` - Transacciones por presupuesto
- `GET /api/transactions/{id}` - Obtener transacción específica
- `POST /api/transactions` - Crear transacción
- `POST /api/transactions/bulk` - Crear múltiples transacciones
- `PUT /api/transactions/{id}` - Actualizar transacción
- `PATCH /api/transactions/{id}/charge` - Marcar como cobrado/pagado
- `DELETE /api/transactions/{id}` - Eliminar transacción

**Plantillas** (`/api/templates`)
- `GET /api/templates` - Listar plantillas
- `GET /api/templates/{id}` - Obtener plantilla específica
- `POST /api/templates` - Crear plantilla
- `PUT /api/templates/{id}` - Actualizar plantilla
- `DELETE /api/templates/{id}` - Eliminar plantilla

**Gastos Recurrentes** (`/api/recurring-expenses`)
- `GET /api/recurring-expenses` - Listar gastos recurrentes
- `GET /api/recurring-expenses/active` - Solo gastos activos
- `GET /api/recurring-expenses/{id}` - Obtener gasto específico
- `POST /api/recurring-expenses` - Crear gasto recurrente
- `PUT /api/recurring-expenses/{id}` - Actualizar gasto recurrente
- `DELETE /api/recurring-expenses/{id}` - Eliminar gasto recurrente
- `POST /api/recurring-expenses/apply-to-budget` - Aplicar a presupuesto

**Dashboard** (`/api/dashboard`)
- `GET /api/dashboard/daily-progress/{budget_id}` - Progreso día a día
- `GET /api/dashboard/category-summary/{budget_id}` - Resumen por categoría
- `GET /api/dashboard/payment-method-summary/{budget_id}` - Resumen por método de pago
- `GET /api/dashboard/upcoming-expenses` - Próximos gastos recurrentes
- `GET /api/dashboard/budget-comparison` - Comparar presupuestos

### ✅ Frontend Base Completado (Vue 3 + Pinia + PrimeVue)

#### Servicios API
- ✅ `categoryService.js` - Servicio para categorías
- ✅ `budgetService.js` - Servicio para presupuestos
- ✅ `transactionService.js` - Servicio para transacciones
- ✅ `templateService.js` - Servicio para plantillas
- ✅ `recurringService.js` - Servicio para gastos recurrentes
- ✅ `dashboardService.js` - Servicio para dashboard

#### Stores Pinia
- ✅ `categories.js` - Store de categorías
- ✅ `budgets.js` - Store de presupuestos
- ✅ `transactions.js` - Store de transacciones
- ✅ `templates.js` - Store de plantillas
- ✅ `recurring.js` - Store de gastos recurrentes
- ✅ `dashboard.js` - Store de dashboard

#### Composables
- ✅ `useFormatters.js` - Formateo de moneda, fechas y utilidades

### ✅ Base de Datos Inicializada
- ✅ Script de inicialización con 24 categorías predefinidas
- ✅ Índices optimizados para consultas

---

## Cómo Iniciar el Sistema

### 1. Iniciar con Docker Compose (Recomendado)

```bash
# Desde el directorio raíz del proyecto
docker-compose up -d --build

# Esto iniciará:
# - MongoDB en puerto 27017
# - Backend API en puerto 8000
# - Frontend en puerto 5173
```

### 2. Verificar que todo funciona

**Backend API:**
```bash
# Ver documentación interactiva
http://localhost:8000/docs

# Health check
curl http://localhost:8000/health

# Listar categorías (debería mostrar 24 categorías)
curl http://localhost:8000/api/categories
```

**Frontend:**
```bash
# Abrir en navegador
http://localhost:5173
```

### 3. Desarrollo Local (Sin Docker)

#### Backend
```bash
cd backend

# Instalar Poetry si no lo tienes
pip install poetry

# Instalar dependencias
poetry install

# Asegúrate de que MongoDB esté corriendo
# Ejecutar el servidor
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

---

## Próximos Pasos: Implementar Vistas del Frontend

Aunque el backend está completo, las vistas del frontend necesitan ser implementadas. Aquí te indico las vistas críticas que debes crear:

### Vistas Prioritarias

#### 1. **Dashboard Principal** (`/src/views/Dashboard.vue`)
- Mostrar presupuestos activos con resumen
- Tarjetas con balance, ingresos, egresos
- Lista de próximos gastos recurrentes
- Accesos rápidos a otras secciones

#### 2. **Gestión de Presupuestos** (`/src/views/BudgetManager.vue`)
- Lista de todos los presupuestos (activos, cerrados, borradores)
- Botón para crear nuevo presupuesto
- Card por cada presupuesto mostrando resumen
- Opción para editar/eliminar/ver detalles

#### 3. **Vista de Presupuesto Individual** (`/src/views/BudgetView.vue`)
- Detalles del presupuesto
- Lista de transacciones del presupuesto
- Formulario para agregar transacciones
- Gráfica de progreso día a día
- Resumen financiero (balance, ingresos, egresos)
- Filtros por categoría, tipo, método de pago

#### 4. **Crear/Editar Presupuesto** (`/src/views/BudgetForm.vue`)
- Formulario con nombre, fecha inicio, fecha fin
- Opción para crear desde plantilla
- **Selector de gastos recurrentes a incluir**
- Vista previa del presupuesto antes de crearlo

#### 5. **Gestión de Transacciones** (`/src/views/TransactionManager.vue`)
- DataTable con todas las transacciones
- Filtros avanzados (fecha, presupuesto, categoría, tipo)
- Marcar transacciones como cobradas/pagadas
- Editar/eliminar transacciones

#### 6. **Gestión de Gastos Recurrentes** (`/src/views/RecurringManager.vue`)
- Lista de gastos recurrentes
- Crear/editar/eliminar gastos
- Activar/desactivar gastos
- Indicador de próximos cobros

#### 7. **Gestión de Categorías** (`/src/views/CategoryManager.vue`)
- Lista de categorías
- Crear/editar/eliminar categorías
- Selector de icono y color
- Filtro por tipo (ingreso/egreso/ambos)

### Componentes Reutilizables a Crear

```
/src/components/
├── budgets/
│   ├── BudgetCard.vue           # Tarjeta de presupuesto
│   ├── BudgetForm.vue           # Formulario crear/editar
│   ├── BudgetSummary.vue        # Resumen financiero
│   └── RecurringSelector.vue     # Selector gastos recurrentes
├── transactions/
│   ├── TransactionForm.vue      # Formulario transacción
│   ├── TransactionTable.vue     # Tabla de transacciones
│   └── TransactionFilters.vue   # Filtros avanzados
├── dashboard/
│   ├── DailyProgressChart.vue   # Gráfica progreso día a día
│   ├── CategoryChart.vue        # Gráfica por categorías
│   └── BalanceCard.vue          # Tarjeta de balance
└── common/
    ├── DateRangePicker.vue      # Selector rango de fechas
    └── AmountInput.vue          # Input de monto con formato
```

### Actualizar Router

```javascript
// /src/router/index.js
const routes = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', name: 'dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'budgets', name: 'budgets', component: () => import('@/views/BudgetManager.vue') },
      { path: 'budgets/new', name: 'budget-new', component: () => import('@/views/BudgetForm.vue') },
      { path: 'budgets/:id', name: 'budget-view', component: () => import('@/views/BudgetView.vue') },
      { path: 'budgets/:id/edit', name: 'budget-edit', component: () => import('@/views/BudgetForm.vue') },
      { path: 'transactions', name: 'transactions', component: () => import('@/views/TransactionManager.vue') },
      { path: 'recurring', name: 'recurring', component: () => import('@/views/RecurringManager.vue') },
      { path: 'categories', name: 'categories', component: () => import('@/views/CategoryManager.vue') },
      { path: 'templates', name: 'templates', component: () => import('@/views/TemplateManager.vue') }
    ]
  }
]
```

### Actualizar Menú de Navegación

```javascript
// /src/layout/AppMenu.vue
const menuItems = [
  { label: 'Dashboard', icon: 'pi-home', to: '/' },
  { label: 'Presupuestos', icon: 'pi-wallet', to: '/budgets' },
  { label: 'Transacciones', icon: 'pi-money-bill', to: '/transactions' },
  { label: 'Gastos Recurrentes', icon: 'pi-sync', to: '/recurring' },
  { label: 'Plantillas', icon: 'pi-clone', to: '/templates' },
  { label: 'Categorías', icon: 'pi-tags', to: '/categories' }
]
```

---

## Estructura de Datos - Referencia Rápida

### Transaction
```javascript
{
  budget_ids: ["budget_id"],  // Puede pertenecer a múltiples presupuestos
  type: "income" | "expense",
  amount: 12.99,
  category: "Netflix",
  bank: "Banco Santander",
  payment_method: "cash" | "credit" | "debit",
  comment: "Comentario opcional",
  timestamp: "2026-03-01T10:00:00",
  is_charged: true
}
```

### Budget
```javascript
{
  name: "Marzo 2026",
  start_date: "2026-03-01T00:00:00",
  end_date: "2026-03-31T23:59:59",
  status: "active" | "closed" | "draft",
  created_from_template: "template_id" // opcional
}
```

### RecurringExpense
```javascript
{
  name: "Netflix Premium",
  category: "Netflix",
  amount: 12.99,
  bank: "Banco Santander",
  payment_method: "credit",
  frequency: "monthly" | "annual" | "quarterly",
  day_of_month: 5,  // Día 1-31
  comment: "Opcional",
  is_active: true
}
```

---

## Flujo de Usuario Principal: Crear Presupuesto

1. Usuario va a `/budgets/new`
2. Completa el formulario:
   - Nombre (ej: "Marzo 2026")
   - Fecha inicio y fin
   - Opcionalmente seleccionar plantilla
3. Sistema muestra **selector de gastos recurrentes**
4. Usuario marca los gastos que quiere incluir
5. Usuario confirma creación
6. Backend:
   - Crea el presupuesto
   - Genera transacciones desde gastos recurrentes seleccionados
   - Usa `calculate_charge_date()` para calcular fecha de cobro
7. Usuario es redirigido a vista del presupuesto con transacciones creadas

---

## Tecnologías y Dependencias

### Backend
- FastAPI
- Motor (async MongoDB driver)
- Pydantic (validación de datos)
- Python 3.11+

### Frontend
- Vue 3 (Composition API)
- Pinia (state management)
- PrimeVue (componentes UI)
- Axios (HTTP client)
- Chart.js (gráficas)
- Vue Router

### Base de Datos
- MongoDB 7.0

---

## Comandos Útiles

### Docker
```bash
# Ver logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb

# Reiniciar servicios
docker-compose restart

# Parar todo
docker-compose down

# Limpiar volúmenes (¡cuidado! borra la base de datos)
docker-compose down -v
```

### MongoDB
```bash
# Conectar a MongoDB
docker exec -it wicked-mongodb mongosh

# Ver bases de datos
show dbs

# Usar base de datos
use wicked_db

# Ver colecciones
show collections

# Ver categorías
db.categories.find().pretty()

# Contar presupuestos
db.budgets.countDocuments()
```

---

## Testing de la API

### Crear Categoría
```bash
curl -X POST http://localhost:8000/api/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Amazon Prime",
    "type": "expense",
    "icon": "pi-amazon",
    "color": "#FF9900",
    "is_active": true
  }'
```

### Crear Presupuesto
```bash
curl -X POST http://localhost:8000/api/budgets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marzo 2026",
    "start_date": "2026-03-01T00:00:00",
    "end_date": "2026-03-31T23:59:59",
    "status": "active"
  }'
```

### Crear Transacción
```bash
curl -X POST http://localhost:8000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "budget_ids": ["<BUDGET_ID_AQUI>"],
    "type": "expense",
    "amount": 12.99,
    "category": "Netflix",
    "bank": "Banco Santander",
    "payment_method": "credit",
    "comment": "Subscripción mensual",
    "timestamp": "2026-03-05T10:00:00",
    "is_charged": true
  }'
```

### Obtener Resumen de Presupuesto
```bash
curl http://localhost:8000/api/budgets/<BUDGET_ID>/summary
```

---

## Próximos Pasos Recomendados

1. ✅ **Backend completado** - Probar todos los endpoints
2. ⏳ **Implementar vistas del frontend** - Comenzar con Dashboard y Gestión de Presupuestos
3. ⏳ **Implementar componentes reutilizables**
4. ⏳ **Agregar navegación en el menú lateral**
5. ⏳ **Testing manual completo** del flujo de usuario
6. ⏳ **Ajustes de UX/UI** según necesidades

---

## Soporte y Contacto

Si tienes preguntas sobre la implementación o necesitas ayuda:
- Revisa la documentación de FastAPI: https://fastapi.tiangolo.com/
- Revisa la documentación de PrimeVue: https://primevue.org/
- Revisa la documentación de Pinia: https://pinia.vuejs.org/

---

**¡El sistema está listo para ser usado!** El backend funciona completamente y puedes empezar a crear presupuestos mediante la API. Las vistas del frontend facilit arán la interacción, pero no son necesarias para la funcionalidad básica.
