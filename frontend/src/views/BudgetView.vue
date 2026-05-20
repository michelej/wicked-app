<template>
  <div class="budget-view">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando presupuesto...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-message">
      <i class="pi pi-exclamation-circle"></i>
      {{ error }}
    </div>

    <!-- Budget Details -->
    <div v-else-if="budget" class="budget-content">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <div class="header-left">
            <Button 
              icon="pi pi-arrow-left"
              text
              rounded
              @click="goBack"
              class="back-button"
            />
            <div class="header-text">
              <h1 class="page-title">{{ budget.name }}</h1>
              <div class="page-meta">
                <span class="budget-period">
                  <i class="pi pi-calendar"></i>
                  {{ formatDate(budget.start_date) }} - {{ formatDate(budget.end_date) }}
                </span>
                <span v-if="budget.bank" class="budget-bank-chip" :style="budgetBankStyle">
                  <span class="budget-bank-chip-mark">{{ budgetBankBrand.logoText }}</span>
                  {{ budget.bank }}
                </span>
                <Tag 
                  :value="formatBudgetStatus(budget.status).label" 
                  :severity="formatBudgetStatus(budget.status).severity"
                />
              </div>
            </div>
          </div>
          <div class="header-actions">
            <Button
              v-if="budget.status === 'active' || budget.status === 'closed'"
              :label="budget.status === 'active' ? 'Cerrar Presupuesto' : 'Abrir Presupuesto'"
              :icon="budget.status === 'active' ? 'pi pi-lock' : 'pi pi-lock-open'"
              :severity="budget.status === 'active' ? 'warning' : 'success'"
              outlined
              @click="toggleBudgetStatus"
            />
            <Button 
              label="Aplicar Gastos Recurrentes"
              icon="pi pi-replay"
              @click="showRecurringDialog = true"
              severity="secondary"
            />
            <Button 
              label="Nueva Transacción" 
              icon="pi pi-plus"
              @click="showTransactionDialog = true"
              severity="success"
            />
          </div>
        </div>
      </div>

      <!-- Summary Cards -->
      <div class="stats-grid">
        <div class="stat-card stat-card-balance">
          <div class="stat-icon">
            <i class="pi pi-wallet"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value" :class="{ 'negative': saldoReal < 0 }">
              {{ formatCurrency(saldoReal) }}
            </h3>
            <p class="stat-label">Saldo Actual</p>
            <small class="stat-detail">Dinero real disponible segun ingresos y gastos registrados</small>
          </div>
        </div>

        <div class="stat-card stat-card-income">
          <div class="stat-icon">
            <i class="pi pi-lock"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ formatCurrency(pendienteReservado) }}</h3>
            <p class="stat-label">Presupuesto Pendiente</p>
            <small class="stat-detail">Dinero que todavia deberia reservarse para terminar el periodo</small>
          </div>
        </div>

        <div class="stat-card stat-card-expense">
          <div class="stat-icon">
            <i class="pi pi-arrow-up"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ formatCurrency(excesoTotal) }}</h3>
            <p class="stat-label">Exceso Acumulado</p>
            <small class="stat-detail">Suma del sobre gasto de categorias excedidas</small>
          </div>
        </div>

        <div class="stat-card stat-card-pending">
          <div class="stat-icon">
            <i class="pi pi-chart-line"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value" :class="{ 'negative': dineroLibreReal < 0 }">{{ formatCurrency(dineroLibreReal) }}</h3>
            <p class="stat-label">Dinero Libre Real</p>
            <small class="stat-detail">Saldo actual menos dinero comprometido pendiente</small>
          </div>
        </div>

        <div class="stat-card stat-card-status" :class="`status-${financialStatusTone}`">
          <div class="stat-icon">
            <i :class="financialStatusMeta.icon"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ financialStatusMeta.label }}</h3>
            <p class="stat-label">Estado Financiero</p>
            <small class="stat-detail">{{ financialStatusMeta.description }}</small>
          </div>
        </div>
      </div>

      <!-- Budget Feasibility Summary -->
      <Card v-if="hasBudgetItems" class="budget-feasibility-card">
        <template #content>
          <div class="feasibility-summary">
            <div class="feasibility-copy">
              <span class="feasibility-kicker">Resumen del presupuesto</span>
              <h2>Estado financiero del periodo</h2>
              <p>
                {{ financialStatus === 'CRITICAL'
                  ? 'El saldo actual ya no alcanza para cubrir todo lo que queda pendiente del presupuesto.'
                  : financialStatus === 'WARNING'
                    ? 'El presupuesto sigue en pie, pero ya existen categorias excedidas o no queda margen real.'
                    : 'El saldo actual cubre lo pendiente y todavia mantiene dinero libre para el resto del periodo.' }}
              </p>
            </div>

            <div class="feasibility-metrics">
              <div class="feasibility-metric">
                <span class="metric-label">Saldo actual</span>
                <strong class="metric-value" :class="{ 'text-red': saldoReal < 0, 'text-green': saldoReal >= 0 }">{{ formatCurrency(saldoReal) }}</strong>
              </div>
              <div class="feasibility-metric" :class="pendienteReservado > 0 ? 'metric-alert' : 'metric-ok'">
                <span class="metric-label">Pendiente reservado</span>
                <strong class="metric-value">{{ formatCurrency(pendienteReservado) }}</strong>
              </div>
              <div class="feasibility-metric" :class="excesoTotal > 0 ? 'metric-alert' : 'metric-ok'">
                <span class="metric-label">Exceso acumulado</span>
                <strong class="metric-value">{{ formatCurrency(excesoTotal) }}</strong>
              </div>
              <div class="feasibility-metric" :class="dineroLibreReal >= 0 ? 'metric-ok' : 'metric-alert'">
                <span class="metric-label">Dinero libre real</span>
                <strong class="metric-value">{{ formatCurrency(dineroLibreReal) }}</strong>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Budget Items Progress -->
      <Card v-if="hasBudgetItems" class="budget-items-card">
        <template #header>
          <div class="card-header">
            <div class="header-title-section">
              <h2>Progreso por Categoría</h2>
              <div class="header-actions-section">
                <Button
                  v-if="!editingBudgetItems"
                  label="Editar Categorías"
                  icon="pi pi-pencil"
                  size="small"
                  text
                  @click="startEditingBudgetItems"
                />
                <template v-else>
                  <Button
                    label="Cancelar"
                    icon="pi pi-times"
                    size="small"
                    text
                    severity="secondary"
                    @click="cancelEditingBudgetItems"
                  />
                  <Button
                    label="Guardar"
                    icon="pi pi-check"
                    size="small"
                    severity="success"
                    @click="saveBudgetItems"
                    :loading="budgetStore.loading"
                  />
                </template>
              </div>
            </div>
            <div class="summary-stats">
              <span class="stat-item">
                <strong>Total Planificado:</strong> {{ formatCurrency(summary.total_planned) }}
              </span>
              <span class="stat-item">
                <strong>Total Gastado:</strong> {{ formatCurrency(summary.total_spent) }}
              </span>
              <span class="stat-item" :class="{ 'text-green': summary.total_remaining >= 0, 'text-red': summary.total_remaining < 0 }">
                <strong>Restante:</strong> {{ formatCurrency(summary.total_remaining) }}
              </span>
            </div>
          </div>
        </template>

        <template #content>
          <!-- Add Category Button (Edit Mode) -->
          <div v-if="editingBudgetItems" class="add-category-section">
            <div class="editing-toolbar">
              <Button
                label="Agregar Categoría"
                icon="pi pi-plus"
                size="small"
                @click="addNewBudgetItem"
              />

              <div v-if="balanceClipboard" class="balance-clipboard-pill">
                <span class="clipboard-label">Clipboard activo</span>
                <strong>{{ formatCurrency(balanceClipboard.amount) }}</strong>
                <small>Extraido de {{ balanceClipboard.sourceCategoryName }}</small>
              </div>

              <Button
                v-if="balanceClipboard"
                label="Reiniciar"
                icon="pi pi-replay"
                size="small"
                severity="secondary"
                outlined
                @click="resetBudgetBalanceClipboard"
              />
            </div>
          </div>

          <DataTable
            :value="editingBudgetItems ? tempBudgetItems : enrichedBudgetItems"
            class="budget-items-table"
            stripedRows
            showGridlines
            :rowClass="rowClass"
          >
            <Column field="category" header="Categoría" :sortable="true">
              <template #body="{ data, index }">
                <div v-if="!editingBudgetItems" class="category-cell">
                  <div class="category-copy">
                    <span>{{ data.category }}</span>
                    <small class="category-meta-inline">
                      {{ formatBudgetCategoryType(getBudgetCategoryType(data)) }} · {{ formatBudgetItemStatus(getBudgetCategoryStatus(data)) }}
                    </small>
                  </div>
                </div>
                <Select
                  v-else
                  v-model="data.category_id"
                  :options="categoryStore.sortedExpenseCategories"
                  optionLabel="name"
                  optionValue="_id"
                  placeholder="Seleccionar categoría"
                  filter
                  class="w-full"
                >
                  <template #option="{ option }">
                    <div class="category-option">
                      <span v-if="option.parent_id" class="subcategory-indicator">↳</span>
                      <i :class="normalizeIcon(option.icon)" :style="{ color: option.color }"></i>
                      <span>{{ option.name }}</span>
                    </div>
                  </template>
                </Select>
              </template>
            </Column>

            <Column field="planned_amount" header="Monto Planificado" :sortable="true">
              <template #body="{ data }">
                <InputNumber
                  v-if="editingBudgetItems"
                  v-model="data.planned_amount"
                  mode="currency"
                  currency="EUR"
                  locale="es-ES"
                  :minFractionDigits="2"
                  :maxFractionDigits="2"
                  class="w-full"
                />
                <span v-else class="amount-value">{{ formatCurrency(data.planned_amount) }}</span>
              </template>
            </Column>

            <Column field="spent_amount" header="Gastado" :sortable="true">
              <template #body="{ data }">
                <span class="amount-value spent">{{ formatCurrency(data.spent_amount) }}</span>
              </template>
            </Column>

            <Column field="remaining" header="Restante" :sortable="true">
              <template #body="{ data }">
                <span 
                  class="amount-value"
                  :class="{ 'text-red': getRemainingAmount(data) < 0, 'text-green': getRemainingAmount(data) >= 0 }"
                >
                  {{ formatCurrency(getRemainingAmount(data)) }}
                </span>
              </template>
            </Column>

            <Column field="percentage" header="% Restante" :sortable="true">
              <template #body="{ data }">
                <div class="percentage-cell">
                  <span 
                    class="percentage-value"
                    :class="getRemainingStateClass(data)"
                  >
                    {{ getRemainingPercentage(data).toFixed(1) }}%
                  </span>
                  <small class="percentage-caption" :class="getRemainingStateClass(data)">
                    {{ getRemainingStateLabel(data) }}
                  </small>
                  <div class="mini-progress-bar">
                    <div 
                      class="mini-progress-fill"
                      :class="getRemainingProgressClass(data)"
                      :style="{ width: getRemainingProgressWidth(data) + '%' }"
                    ></div>
                  </div>
                </div>
              </template>
            </Column>

           

            <Column v-if="editingBudgetItems" header="Acciones" :exportable="false" style="width: 14rem">
              <template #body="{ data, index }">
                <div class="budget-item-actions">
                  <Button
                    label="Extraer"
                    size="small"
                    text
                    severity="warning"
                    :disabled="!canExtractBudgetBalance(data)"
                    @click="extractBudgetBalance(data)"
                  />
                  <Button
                    label="Incluir"
                    size="small"
                    text
                    severity="success"
                    :disabled="!balanceClipboard"
                    @click="includeBudgetBalance(data)"
                  />
                  <Button
                    icon="pi pi-trash"
                    size="small"
                    text
                    severity="danger"
                    @click="removeBudgetItem(index)"
                  />
                </div>
              </template>
            </Column>
          </DataTable>

          <div
            v-if="progressItemsSource.length > 0"
            class="budget-items-totals"
            :class="{ 'with-actions': editingBudgetItems }"
          >
            <div class="totals-cell totals-label">Totales</div>
            <div class="totals-cell totals-value">{{ formatCurrency(progressTotals.planned) }}</div>
            <div class="totals-cell totals-value spent">{{ formatCurrency(progressTotals.spent) }}</div>
            <div class="totals-cell totals-value" :class="{ 'text-red': progressTotals.remaining < 0, 'text-green': progressTotals.remaining >= 0 }">
              {{ formatCurrency(progressTotals.remaining) }}
            </div>
            <div class="totals-cell totals-placeholder">-</div>
            <div v-if="editingBudgetItems" class="totals-cell totals-placeholder">-</div>
          </div>
        </template>
      </Card>

      <Card v-if="hasBudgetItems" class="budget-feasibility-card budget-availability-card">
        <template #content>
          <div class="feasibility-summary">
            <div class="feasibility-copy">
              <span class="feasibility-kicker">Reserva operativa</span>
              <h2>Proyeccion de cierre del mes</h2>
              <p>
                {{ dineroLibreReal < 0
                  ? 'El dinero libre real es negativo: hay riesgo claro de no terminar el mes con el saldo actual.'
                  : excesoTotal > 0
                    ? 'Aunque el saldo aguanta, ya existen categorias excedidas que conviene vigilar.'
                    : 'El dinero libre real sigue en positivo y la proyeccion del mes es estable.' }}
              </p>
            </div>

            <div class="feasibility-metrics">
              <div class="feasibility-metric">
                <span class="metric-label">Balance actual</span>
                <strong class="metric-value" :class="{ 'text-red': saldoReal < 0, 'text-green': saldoReal >= 0 }">
                  {{ formatCurrency(saldoReal) }}
                </strong>
              </div>
              <div class="feasibility-metric">
                <span class="metric-label">Categorias excedidas</span>
                <strong class="metric-value">{{ exceededCategoriesCount }}</strong>
              </div>
              <div class="feasibility-metric" :class="dineroLibreReal >= 0 ? 'metric-ok' : 'metric-alert'">
                <span class="metric-label">Dinero libre real</span>
                <strong class="metric-value">{{ formatCurrency(dineroLibreReal) }}</strong>
              </div>
              <div class="feasibility-metric" :class="projectedCoverageGap > 0 ? 'metric-alert' : 'metric-ok'">
                <span class="metric-label">Valor faltante</span>
                <strong class="metric-value">{{ formatCurrency(projectedCoverageGap) }}</strong>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Transactions Section -->
      <Card class="transactions-card">
        <template #header>
          <div class="card-header">
            <h2>Transacciones</h2>
            <div class="header-filters">
              <InputText 
                v-model="searchQuery"
                placeholder="Buscar..."
                class="search-input"
              >
                <template #prefix>
                  <i class="pi pi-search"></i>
                </template>
              </InputText>
              <Select 
                v-model="filterType"
                :options="typeOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Tipo"
              />
            </div>
          </div>
        </template>

        <template #content>
          <!-- Transaction Summary -->
          <div class="transaction-summary">
            <div class="summary-item">
              <div class="summary-icon income-icon">
                <i class="pi pi-arrow-down"></i>
              </div>
              <div class="summary-content">
                <h4 class="summary-value">{{ formatCurrency(transactionSummary.totalIncome) }}</h4>
                <p class="summary-label">Total Ingresos</p>
              </div>
            </div>
            <div class="summary-item">
              <div class="summary-icon expense-icon">
                <i class="pi pi-arrow-up"></i>
              </div>
              <div class="summary-content">
                <h4 class="summary-value">{{ formatCurrency(transactionSummary.totalExpense) }}</h4>
                <p class="summary-label">Total Gastos</p>
              </div>
            </div>
            <div class="summary-item">
              <div class="summary-icon balance-icon">
                <i class="pi pi-wallet"></i>
              </div>
              <div class="summary-content">
                <h4 class="summary-value" :class="{ 'negative': transactionSummary.balance < 0 }">
                  {{ formatCurrency(transactionSummary.balance) }}
                </h4>
                <p class="summary-label">Balance</p>
              </div>
            </div>
          </div>

          <DataTable 
            :value="transactionsWithBalance"
            :loading="transactionStore.loading"
            stripedRows
            paginator
            :rows="10"
            :rowsPerPageOptions="[10, 20, 50]"
            class="transactions-table"
            :rowClass="transactionRowClass"
            @row-click="toggleTransactionHighlight"
          >
            <template #empty>
              <div class="empty-state">
                <i class="pi pi-inbox"></i>
                <p>No hay transacciones</p>
                <Button 
                  label="Agregar Transacción"
                  icon="pi pi-plus"
                  @click="showTransactionDialog = true"
                  text
                />
              </div>
            </template>

            <Column field="timestamp" header="Fecha" sortable>
              <template #body="{ data }">
                <span class="date-text">{{ formatDateTime(data.timestamp) }}</span>
              </template>
            </Column>

            <Column field="category" header="Categoría" sortable>
              <template #body="{ data }">
                <Tag :value="data.category" severity="secondary" />
              </template>
            </Column>

            <Column field="type" header="Tipo" sortable>
              <template #body="{ data }">
                <Tag 
                  :value="formatTransactionType(data.type)"
                  :severity="data.type === 'income' ? 'success' : 'danger'"
                />
              </template>
            </Column>

            <Column field="amount" header="Monto" sortable>
              <template #body="{ data }">
                <span 
                  class="amount-text"
                  :class="{ 'text-green': data.type === 'income', 'text-red': data.type === 'expense' }"
                >
                  {{ data.type === 'income' ? '+' : '-' }}{{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>

            <Column field="runningBalance" header="Saldo" sortable>
              <template #body="{ data }">
                <span 
                  class="balance-text"
                  :class="{ 'text-green': data.runningBalance >= 0, 'text-red': data.runningBalance < 0 }"
                >
                  {{ formatCurrency(data.runningBalance) }}
                </span>
              </template>
            </Column>

            <Column field="payment_method" header="Método">
              <template #body="{ data }">
                {{ formatPaymentMethod(data.payment_method) }}
              </template>
            </Column>

            <Column field="bank" header="Banco" sortable />

            <Column field="is_charged" header="Estado">
              <template #body="{ data }">
                <Tag 
                  :value="data.is_charged ? 'Cobrado' : 'Pendiente'"
                  :severity="data.is_charged ? 'success' : 'warning'"
                />
              </template>
            </Column>

            <Column header="Comentario">
              <template #body="{ data }">
                <span
                  v-if="data.comment"
                  class="comment-hover"
                  v-tooltip.top="data.comment"
                >
                  <i class="pi pi-comment"></i>
                  <span>Ver</span>
                </span>
                <span v-else class="comment-empty">-</span>
              </template>
            </Column>

            <Column header="Acciones">
              <template #body="{ data }">
                <div class="action-buttons">
                  <Button 
                    v-if="!data.is_charged"
                    icon="pi pi-check"
                    text
                    rounded
                    severity="success"
                    v-tooltip.top="'Marcar como cobrado'"
                    @click.stop="markAsCharged(data)"
                  />
                  <Button 
                    icon="pi pi-pencil"
                    text
                    rounded
                    severity="secondary"
                    v-tooltip.top="'Editar'"
                    @click.stop="editTransaction(data)"
                  />
                  <Button 
                    icon="pi pi-trash"
                    text
                    rounded
                    severity="danger"
                    v-tooltip.top="'Eliminar'"
                    @click.stop="confirmDeleteTransaction(data)"
                  />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>

      <!-- Expenses by Category Summary -->
      <Card class="expenses-summary-card">
        <template #header>
          <div class="card-header">
            <h2>Gastos Reales por Categoría</h2>
            <div class="summary-stats">
              <span class="stat-item">
                <strong>Total Gastado:</strong> {{ formatCurrency(expensesByCategory.filter(item => !item.isIndented).reduce((sum, cat) => sum + cat.totalSpent, 0)) }}
              </span>
              <span class="stat-item">
                <strong>Categorías:</strong> {{ expensesByCategory.filter(item => !item.isIndented).length }}
              </span>
            </div>
          </div>
        </template>

        <template #content>
          <DataTable
            :value="expensesByCategory"
            class="expenses-summary-table"
            stripedRows
            showGridlines
          >
            <template #empty>
              <div class="empty-state">
                <i class="pi pi-chart-bar"></i>
                <p>No hay gastos registrados</p>
              </div>
            </template>

            <Column field="category" header="Categoría" sortable>
              <template #body="{ data }">
                <button
                  type="button"
                  class="category-link-button"
                  :class="{ 'parent-category': data.isParent, 'subcategory': data.isIndented }"
                  @click="goToTransactionsForCategory(data)"
                >
                  <div class="category-cell">
                    <span v-if="data.isParent" class="parent-indicator">📁</span>
                    <span v-if="data.isIndented" class="subcategory-indicator">↳</span>
                    <Tag 
                      :value="data.category" 
                      :severity="data.isParent ? 'primary' : 'secondary'"
                      :class="{ 'parent-tag': data.isParent }"
                    />
                    <span v-if="data.isParent" class="subcategory-count">
                      ({{ data.subcategories.length }} subcategorías)
                    </span>
                  </div>
                </button>
              </template>
            </Column>

            <Column field="totalSpent" header="Total Gastado" sortable>
              <template #body="{ data }">
                <span class="amount-text text-red">
                  {{ formatCurrency(data.totalSpent) }}
                </span>
              </template>
            </Column>

            <Column field="transactionCount" header="Transacciones" sortable>
              <template #body="{ data }">
                <span class="transaction-count">{{ data.transactionCount }}</span>
              </template>
            </Column>

            <Column field="banks" header="Bancos">
              <template #body="{ data }">
                <div class="banks-list">
                  <Tag 
                    v-for="bank in data.banks.slice(0, 2)" 
                    :key="bank"
                    :value="bank"
                    severity="info"
                    class="bank-tag"
                  />
                  <Tag 
                    v-if="data.banks.length > 2"
                    :value="`+${data.banks.length - 2} más`"
                    severity="secondary"
                    class="bank-tag"
                  />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <!-- Transaction Dialog -->
    <Dialog 
      v-model:visible="showTransactionDialog"
      modal
      :header="editingTransaction ? 'Editar Transacción' : 'Nueva Transacción'"
      :style="{ width: '600px' }"
      class="transaction-dialog"
    >
      <div class="dialog-content">
        <div class="form-field">
          <label>Tipo *</label>
          <div class="button-group">
            <Button 
              label="Ingreso"
              icon="pi pi-arrow-down"
              :severity="transactionForm.type === 'income' ? 'success' : 'secondary'"
              :outlined="transactionForm.type !== 'income'"
              @click="transactionForm.type = 'income'"
            />
            <Button 
              label="Gasto"
              icon="pi pi-arrow-up"
              :severity="transactionForm.type === 'expense' ? 'danger' : 'secondary'"
              :outlined="transactionForm.type !== 'expense'"
              @click="transactionForm.type = 'expense'"
            />
          </div>
        </div>

        <div class="form-field">
          <label for="amount">Monto *</label>
          <InputNumber 
            id="amount"
            v-model="transactionForm.amount"
            mode="currency"
            currency="EUR"
            locale="es-ES"
            :minFractionDigits="2"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="category">Categoría *</label>
          <Select 
            id="category"
            v-model="transactionForm.category_id"
            :options="availableCategories"
            optionLabel="displayName"
            optionValue="_id"
            placeholder="Selecciona categoría"
            filter
            class="w-full"
          >
            <template #option="{ option }">
              <div class="category-option">
                <span v-if="option.parent_id" class="subcategory-indicator">↳</span>
                <i :class="normalizeIcon(option.icon)" :style="{ color: option.color }"></i>
                <span>{{ option.name }}</span>
              </div>
            </template>
          </Select>
        </div>

        <div class="form-row">
          <div class="form-field">
            <label for="bank">Banco *</label>
            <div v-if="budget?.bank" class="locked-bank-field" :style="budgetBankStyle">
              <span class="locked-bank-logo">{{ budgetBankBrand.logoText }}</span>
              <div class="locked-bank-copy">
                <strong>{{ budget.bank }}</strong>
                <small>Este presupuesto opera solo con este banco.</small>
              </div>
            </div>
            <Select
              v-else
              id="bank"
              v-model="transactionForm.bank"
              :options="budgetBankOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecciona banco"
              class="w-full"
            />
          </div>
          <div class="form-field">
            <label for="paymentMethod">Método de Pago *</label>
            <Select 
              id="paymentMethod"
              v-model="transactionForm.payment_method"
              :options="paymentMethodOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecciona método"
              class="w-full"
            />
          </div>
        </div>

        <div class="form-field">
          <label for="timestamp">Fecha y Hora *</label>
          <Calendar 
            id="timestamp"
            v-model="transactionForm.timestamp"
            showTime
            hourFormat="24"
            dateFormat="dd/mm/yy"
            placeholder="Selecciona fecha y hora"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="comment">Comentario</label>
          <Textarea 
            id="comment"
            v-model="transactionForm.comment"
            rows="3"
            placeholder="Descripción opcional"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <div class="checkbox-field">
            <Checkbox 
              v-model="transactionForm.is_charged"
              :binary="true"
              inputId="isCharged"
            />
            <label for="isCharged">Marcar como cobrado</label>
          </div>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancelar"
          text
          @click="closeTransactionDialog"
        />
        <Button 
          :label="editingTransaction ? 'Actualizar' : 'Crear'"
          icon="pi pi-check"
          @click="saveTransaction"
          :loading="transactionStore.loading"
          severity="success"
        />
      </template>
    </Dialog>

    <!-- Recurring Expenses Dialog -->
    <Dialog 
      v-model:visible="showRecurringDialog"
      modal
      header="Aplicar Gastos Recurrentes"
      :style="{ width: '600px' }"
    >
      <div class="dialog-content">
        <p class="dialog-description">
          Selecciona los gastos recurrentes que deseas agregar al presupuesto como montos planificados. Los gastos se sumarán a las categorías correspondientes del presupuesto.
        </p>

        <div v-if="recurringStore.loading" class="loading-state">
          <ProgressSpinner style="width: 50px; height: 50px" />
        </div>

        <div v-else-if="recurringStore.activeExpenses.length === 0" class="empty-state">
          <p>No hay gastos recurrentes activos</p>
        </div>

        <div v-else class="recurring-list">
          <div 
            v-for="expense in recurringStore.activeExpenses"
            :key="expense._id"
            class="recurring-item"
          >
            <Checkbox 
              v-model="selectedRecurring"
              :value="expense._id"
              :inputId="expense._id"
            />
            <label :for="expense._id" class="recurring-label">
              <div class="recurring-info">
                <span class="recurring-name">{{ expense.name }}</span>
                <span class="recurring-detail">
                  {{ formatCurrency(expense.amount) }} - {{ expense.category }} - {{ formatFrequency(expense.frequency) }}
                </span>
              </div>
            </label>
          </div>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancelar"
          text
          @click="showRecurringDialog = false"
        />
        <Button 
          label="Aplicar"
          icon="pi pi-check"
          @click="applyRecurringExpenses"
          :loading="recurringStore.loading"
          :disabled="selectedRecurring.length === 0"
          severity="success"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation -->
    <Dialog 
      v-model:visible="showDeleteDialog"
      modal
      header="Confirmar Eliminación"
      :style="{ width: '450px' }"
    >
      <p>¿Estás seguro de que deseas eliminar esta transacción?</p>
      
      <template #footer>
        <Button 
          label="Cancelar"
          text
          @click="showDeleteDialog = false"
        />
        <Button 
          label="Eliminar"
          icon="pi pi-trash"
          @click="deleteTransaction"
          :loading="transactionStore.loading"
          severity="danger"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBudgetStore } from '@/stores/budgets'
import { useTransactionStore } from '@/stores/transactions'
import { useCategoryStore } from '@/stores/categories'
import { useRecurringStore } from '@/stores/recurring'
import { useFormatters } from '@/composables/useFormatters'
import { BUDGET_BANK_OPTIONS, getBankBrand } from '@/constants/banks'
import { useToast } from 'primevue/usetoast'
import ProgressSpinner from 'primevue/progressspinner'
import Calendar from 'primevue/calendar'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'

const route = useRoute()
const router = useRouter()
const budgetStore = useBudgetStore()
const transactionStore = useTransactionStore()
const categoryStore = useCategoryStore()
const recurringStore = useRecurringStore()
const toast = useToast()
const { 
  formatCurrency, 
  formatDate, 
  formatDateTime,
  formatBudgetStatus, 
  formatTransactionType,
  formatPaymentMethod,
  formatFrequency
} = useFormatters()

// State
const budgetId = ref(route.params.id)
const budget = ref(null)
const summary = ref({})
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const filterType = ref('all')
const showTransactionDialog = ref(false)
const showRecurringDialog = ref(false)
const showDeleteDialog = ref(false)
const editingTransaction = ref(null)
const transactionToDelete = ref(null)
const selectedRecurring = ref([])
const editingBudgetItems = ref(false)
const tempBudgetItems = ref([])
const balanceClipboard = ref(null)
const highlightedTransactionIds = ref([])

const budgetBankOptions = BUDGET_BANK_OPTIONS

const createDefaultTransactionForm = () => ({
  type: 'expense',
  amount: 0,
  category_id: '',
  bank: budget.value?.bank || '',
  payment_method: 'debit',
  timestamp: new Date(),
  comment: '',
  is_charged: false
})

const transactionForm = ref(createDefaultTransactionForm())

const typeOptions = [
  { label: 'Todos', value: 'all' },
  { label: 'Ingresos', value: 'income' },
  { label: 'Gastos', value: 'expense' }
]

const paymentMethodOptions = [
  { label: 'Efectivo', value: 'cash' },
  { label: 'Débito', value: 'debit' },
  { label: 'Crédito', value: 'credit' }
]

// Computed
const availableCategories = computed(() => {
  const categories = transactionForm.value.type === 'income'
    ? categoryStore.sortedIncomeCategories
    : transactionForm.value.type === 'expense'
      ? categoryStore.sortedExpenseCategories
      : categoryStore.sortedActiveCategories

  return categories.map((category) => ({
    ...category,
    displayName: category.parent_id ? `↳ ${category.name}` : category.name
  }))
})

const resolveCategoryId = (categoryValue) => {
  if (!categoryValue) {
    return ''
  }

  const exactIdMatch = categoryStore.categories.find((category) => category._id === categoryValue)
  if (exactIdMatch) {
    return exactIdMatch._id
  }

  return categoryStore.categories.find((category) => category.name === categoryValue)?._id || ''
}

const resolveCategoryName = (categoryId) => {
  if (!categoryId) {
    return ''
  }

  return categoryStore.categories.find((category) => category._id === categoryId)?.name || ''
}

const roundMoney = (value) => {
  return Math.round((Number(value || 0) + Number.EPSILON) * 100) / 100
}

const createTempBudgetItem = (item = {}) => ({
  temp_id: item.temp_id || `${Date.now()}-${Math.random().toString(16).slice(2)}`,
  category_id: item.category_id || '',
  category: item.category || '',
  planned_amount: Number(item.planned_amount || 0),
  spent_amount: Number(item.spent_amount || 0)
})

const getCategoryRecord = (item) => {
  if (item?.category_id) {
    const categoryById = categoryStore.categories.find((category) => category._id === item.category_id)
    if (categoryById) {
      return categoryById
    }
  }

  return categoryStore.categories.find((category) => category.name === item?.category) || null
}

const getBudgetCategoryType = (item) => {
  return item?.budget_category_type || getCategoryRecord(item)?.budget_category_type || 'variable'
}

const getBudgetCategoryStatus = (item) => {
  if (item?.budget_status) {
    return item.budget_status
  }

  const remainingAmount = getRemainingAmount(item)
  const budgetCategoryType = getBudgetCategoryType(item)

  if (remainingAmount < 0) return 'exceeded'
  if (budgetCategoryType === 'fixed') return remainingAmount === 0 ? 'paid' : 'pending'
  return remainingAmount === 0 ? 'no_margin' : 'available'
}

const formatBudgetCategoryType = (type) => {
  return budgetCategoryTypeLabels[type] || 'Variable'
}

const formatBudgetItemStatus = (status) => {
  return budgetStatusLabels[status] || status
}

const isReservableBudgetItem = (item) => {
  const categoryRecord = getCategoryRecord(item)
  const categoryName = item?.category || categoryRecord?.name

  if (categoryName === 'Transferido Cuentas') {
    return false
  }

  if (categoryRecord && categoryRecord.is_active === false) {
    return false
  }

  return !categoryRecord || categoryRecord.type === 'expense' || categoryRecord.type === 'both'
}

const hasBudgetItems = computed(() => {
  return Array.isArray(summary.value.budget_items) && summary.value.budget_items.length > 0
})

const budgetCategoryTypeLabels = {
  fixed: 'Fijo',
  variable: 'Variable'
}

const budgetStatusLabels = {
  pending: 'Pendiente',
  paid: 'Pagado',
  available: 'Disponible',
  no_margin: 'Sin margen',
  exceeded: 'Excedido'
}

const financialStatusMetaMap = {
  HEALTHY: {
    label: 'Saludable',
    icon: 'pi pi-check-circle',
    tone: 'healthy',
    description: 'El saldo actual alcanza para cubrir lo pendiente y aun deja margen real.'
  },
  WARNING: {
    label: 'Atención',
    icon: 'pi pi-exclamation-triangle',
    tone: 'warning',
    description: 'No sobra margen o ya existen categorias excedidas que requieren atencion.'
  },
  CRITICAL: {
    label: 'Crítico',
    icon: 'pi pi-times-circle',
    tone: 'critical',
    description: 'El saldo actual no alcanza para cubrir lo pendiente del periodo.'
  }
}

const budgetBankBrand = computed(() => getBankBrand(budget.value?.bank))

const budgetBankStyle = computed(() => ({
  '--budget-bank-accent': budgetBankBrand.value.accent,
  '--budget-bank-surface': budgetBankBrand.value.surface,
  '--budget-bank-pill-bg': budgetBankBrand.value.pillBackground,
  '--budget-bank-pill-color': budgetBankBrand.value.pillColor,
  '--budget-bank-shadow': budgetBankBrand.value.shadow
}))

const saldoReal = computed(() => Number(summary.value.saldo_real ?? summary.value.balance ?? 0))
const pendienteReservado = computed(() => Number(summary.value.pendiente_reservado ?? 0))
const excesoTotal = computed(() => Number(summary.value.exceso_total ?? 0))
const dineroLibreReal = computed(() => Number(summary.value.dinero_libre_real ?? (saldoReal.value - pendienteReservado.value)))
const financialStatus = computed(() => summary.value.financial_status || 'HEALTHY')
const financialStatusMeta = computed(() => financialStatusMetaMap[financialStatus.value] || financialStatusMetaMap.HEALTHY)
const financialStatusTone = computed(() => financialStatusMeta.value.tone)
const exceededCategoriesCount = computed(() => {
  return summary.value.budget_items?.filter((item) => getBudgetCategoryStatus(item) === 'exceeded').length || 0
})

const sortedBudgetItems = computed(() => {
  if (!summary.value.budget_items || summary.value.budget_items.length === 0) {
    return []
  }

  // Create a map of category names to their parent_id
  const categoryMap = {}
  categoryStore.categories.forEach(cat => {
    categoryMap[cat.name] = cat.parent_id
  })

  // Create hierarchical sorted list
  const result = []
  const items = [...summary.value.budget_items]

  // First, add items for parent categories
  const parentItems = items.filter(item => !categoryMap[item.category])
  result.push(...parentItems)

  // Then, add items for child categories after their parents
  const processedParents = new Set()
  parentItems.forEach(parentItem => {
    processedParents.add(parentItem.category)
    
    // Find the parent category ID
    const parentCategory = categoryStore.categories.find(c => c.name === parentItem.category)
    if (parentCategory) {
      // Add all child items of this parent
      const childItems = items.filter(item => {
        const itemCategory = categoryStore.categories.find(c => c.name === item.category)
        return itemCategory && itemCategory.parent_id === parentCategory._id
      })
      result.push(...childItems)
    }
  })

  // Add any remaining items that don't have a parent in the budget
  items.forEach(item => {
    if (!result.find(r => r.category === item.category)) {
      result.push(item)
    }
  })

  return result
})

const enrichedBudgetItems = computed(() => {
  // Add bank information to each budget item based on transactions
  return sortedBudgetItems.value.map(item => {
    // Find all transactions for this category in this budget
    const categoryTransactions = transactionStore.transactions.filter(t => 
      t.budget_id === budgetId.value && 
      t.category === item.category &&
      t.type === 'expense'
    )
    
    // Extract unique banks
    const banks = [...new Set(categoryTransactions.map(t => t.bank).filter(Boolean))]
    
    return {
      ...item,
      banks: banks
    }
  })
})

const budgetItemsForProjection = computed(() => {
  return editingBudgetItems.value ? tempBudgetItems.value : sortedBudgetItems.value
})

const totalRemainingProgress = computed(() => {
  return budgetItemsForProjection.value
    .filter((item) => isReservableBudgetItem(item))
    .reduce((sum, item) => sum + Math.max(getRemainingAmount(item), 0), 0)
})

const progressItemsSource = computed(() => {
  return editingBudgetItems.value ? tempBudgetItems.value : enrichedBudgetItems.value
})

const progressTotals = computed(() => {
  return progressItemsSource.value.reduce((totals, item) => {
    totals.planned += Number(item.planned_amount || 0)
    totals.spent += Number(item.spent_amount || 0)
    totals.remaining += getRemainingAmount(item)
    return totals
  }, {
    planned: 0,
    spent: 0,
    remaining: 0
  })
})

const projectedAvailableBalance = computed(() => {
  return dineroLibreReal.value
})

const projectedCoverageGap = computed(() => {
  return Math.max(0 - dineroLibreReal.value, 0)
})

const filteredTransactions = computed(() => {
  let transactions = transactionStore.transactions.filter(t => 
    t.budget_id === budgetId.value
  )

  if (filterType.value !== 'all') {
    transactions = transactions.filter(t => t.type === filterType.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    transactions = transactions.filter(t =>
      t.category.toLowerCase().includes(query) ||
      t.bank.toLowerCase().includes(query) ||
      t.comment?.toLowerCase().includes(query)
    )
  }

  return transactions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const transactionsWithBalance = computed(() => {
  // Get filtered transactions and sort by date ascending (oldest first)
  const sortedTransactions = [...filteredTransactions.value].sort((a, b) => 
    new Date(a.timestamp) - new Date(b.timestamp)
  )
  
  // Calculate running balance
  let runningBalance = 0
  const transactionsWithBalance = sortedTransactions.map(transaction => {
    const amount = transaction.type === 'income' ? transaction.amount : -transaction.amount
    runningBalance += amount
    
    return {
      ...transaction,
      runningBalance
    }
  })
  
  // Return sorted by date descending (newest first) for display
  return transactionsWithBalance.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

watch(
  () => transactionsWithBalance.value.map((transaction) => transaction._id),
  (visibleTransactionIds) => {
    highlightedTransactionIds.value = highlightedTransactionIds.value.filter((id) => visibleTransactionIds.includes(id))
  }
)

const transactionSummary = computed(() => {
  const transactions = filteredTransactions.value
  
  const totalIncome = transactions
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + t.amount, 0)
  
  const totalExpense = transactions
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0)
  
  const balance = totalIncome - totalExpense
  
  return {
    totalIncome,
    totalExpense,
    balance
  }
})

const expensesByCategory = computed(() => {
  const transactions = transactionStore.transactions.filter(t => 
    t.budget_id === budgetId.value && t.type === 'expense'
  )
  
  // Create a map of category names to their details
  const categoryMap = {}
  categoryStore.categories.forEach(cat => {
    categoryMap[cat.name] = {
      id: cat._id,
      name: cat.name,
      parent_id: cat.parent_id,
      icon: cat.icon,
      color: cat.color
    }
  })
  
  // Calculate totals per category
  const categoryTotals = {}
  
  transactions.forEach(transaction => {
    const category = transaction.category
    if (!categoryTotals[category]) {
      categoryTotals[category] = {
        category,
        totalSpent: 0,
        transactionCount: 0,
        banks: new Set(),
        categoryInfo: categoryMap[category] || null,
        isSubcategory: false,
        parentCategory: null
      }
    }
    
    categoryTotals[category].totalSpent += transaction.amount
    categoryTotals[category].transactionCount += 1
    if (transaction.bank) {
      categoryTotals[category].banks.add(transaction.bank)
    }
  })
  
  // Group subcategories under their parents
  const parentTotals = {}
  const standaloneCategories = []
  
  // First pass: identify subcategories and accumulate parent totals
  Object.values(categoryTotals).forEach(item => {
    const catInfo = item.categoryInfo
    if (catInfo && catInfo.parent_id) {
      // This is a subcategory
      item.isSubcategory = true
      
      // Find parent category
      const parentCat = categoryStore.categories.find(c => c._id === catInfo.parent_id)
      if (parentCat) {
        item.parentCategory = parentCat.name
        
        // Accumulate in parent total
        if (!parentTotals[parentCat.name]) {
          parentTotals[parentCat.name] = {
            category: parentCat.name,
            totalSpent: 0,
            transactionCount: 0,
            banks: new Set(),
            categoryInfo: {
              id: parentCat._id,
              name: parentCat.name,
              parent_id: null,
              icon: parentCat.icon,
              color: parentCat.color
            },
            isParent: true,
            subcategories: []
          }
        }
        
        parentTotals[parentCat.name].totalSpent += item.totalSpent
        parentTotals[parentCat.name].transactionCount += item.transactionCount
        item.banks.forEach(bank => parentTotals[parentCat.name].banks.add(bank))
        parentTotals[parentCat.name].subcategories.push(item)
      } else {
        // Parent not found, treat as regular category
        standaloneCategories.push({
          ...item,
          banks: Array.from(item.banks)
        })
      }
    } else {
      // This is a parent category or standalone category
      standaloneCategories.push({
        ...item,
        banks: Array.from(item.banks)
      })
    }
  })
  
  // Build final result maintaining hierarchy
  const finalResult = []
  
  // Sort parent categories by total spent descending
  const sortedParents = Object.values(parentTotals).sort((a, b) => b.totalSpent - a.totalSpent)
  
  // Add each parent with its sorted subcategories
  sortedParents.forEach(parent => {
    // Sort subcategories by amount descending
    parent.subcategories.sort((a, b) => b.totalSpent - a.totalSpent)
    parent.banks = Array.from(parent.banks)
    
    finalResult.push(parent)
    
    // Add subcategories indented
    parent.subcategories.forEach(sub => {
      finalResult.push({
        ...sub,
        banks: Array.from(sub.banks),
        isIndented: true
      })
    })
  })
  
  // Add remaining standalone categories (not parents and not subcategories)
  const remainingStandalone = standaloneCategories.filter(item => 
    !sortedParents.find(p => p.category === item.category)
  ).sort((a, b) => b.totalSpent - a.totalSpent)
  
  finalResult.push(...remainingStandalone)
  
  return finalResult
})

// Lifecycle
onMounted(async () => {
  try {
    loading.value = true
    
    // Load budget, summary, transactions, categories, and recurring expenses
    await Promise.all([
      loadBudget(),
      transactionStore.fetchTransactionsByBudget(budgetId.value),
      categoryStore.fetchCategories(),
      recurringStore.fetchRecurringExpenses()
    ])
  } catch (err) {
    error.value = 'Error al cargar los datos del presupuesto'
    console.error(err)
  } finally {
    loading.value = false
  }
})

// Methods
const loadBudget = async () => {
  budget.value = await budgetStore.getBudget(budgetId.value)
  summary.value = await budgetStore.getBudgetSummary(budgetId.value)

  if (!editingTransaction.value && budget.value?.bank) {
    transactionForm.value.bank = budget.value.bank
  }
}

const goBack = () => {
  router.push('/budgets')
}

const goToTransactionsForCategory = (categoryRow) => {
  const query = {
    budgetId: budgetId.value,
    type: 'expense'
  }

  if (categoryRow.isParent) {
    query.parentCategory = categoryRow.category
  } else {
    query.category = categoryRow.category
  }

  router.push({
    name: 'transactions',
    query
  })
}

const toggleBudgetStatus = async () => {
  const nextStatus = budget.value.status === 'closed' ? 'active' : 'closed'
  const actionLabel = nextStatus === 'closed' ? 'cerrado' : 'abierto'

  try {
    await budgetStore.updateBudget(budgetId.value, {
      status: nextStatus
    })

    toast.add({
      severity: 'success',
      summary: `Presupuesto ${actionLabel}`,
      detail: `"${budget.value.name}" ahora está ${actionLabel}.`,
      life: 3000
    })

    await loadBudget()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `No se pudo ${nextStatus === 'closed' ? 'cerrar' : 'abrir'} el presupuesto`,
      life: 3000
    })
  }
}

// Budget Items Progress Helpers
const getProgressPercentage = (item) => {
  if (!item.planned_amount || item.planned_amount === 0) return 0
  return Math.min((item.spent_amount / item.planned_amount) * 100, 100)
}

const getRemainingProgressWidth = (item) => {
  return Math.max(Math.min(getRemainingPercentage(item), 100), 0)
}

const getRemainingAmount = (item) => {
  return item.planned_amount - item.spent_amount
}

const getRemainingPercentage = (item) => {
  if (!item.planned_amount || item.planned_amount === 0) return 0
  return ((item.planned_amount - item.spent_amount) / item.planned_amount) * 100
}

const getRemainingStateClass = (item) => {
  const budgetStatus = getBudgetCategoryStatus(item)

  if (budgetStatus === 'exceeded') return 'remaining-negative'
  if (budgetStatus === 'paid') return 'remaining-complete'
  if (budgetStatus === 'no_margin') return 'remaining-no-margin'

  const remainingPercentage = getRemainingPercentage(item)
  if (remainingPercentage <= 20) return 'remaining-low'
  if (remainingPercentage <= 50) return 'remaining-medium'
  return 'remaining-healthy'
}

const getRemainingStateLabel = (item) => {
  return formatBudgetItemStatus(getBudgetCategoryStatus(item))
}

const getRemainingProgressClass = (item) => {
  const budgetStatus = getBudgetCategoryStatus(item)
  if (budgetStatus === 'exceeded') return 'progress-negative'
  if (budgetStatus === 'no_margin') return 'progress-no-margin'

  const remainingPercentage = getRemainingPercentage(item)
  if (remainingPercentage <= 20) return 'progress-low'
  if (remainingPercentage <= 50) return 'progress-medium'
  return 'progress-healthy'
}

const isSubcategory = (categoryName) => {
  const category = categoryStore.categories.find(c => c.name === categoryName)
  return category && category.parent_id
}

const normalizeIcon = (icon) => {
  if (!icon) return 'pi pi-tag'
  if (icon.startsWith('pi pi-')) return icon
  if (icon.startsWith('pi-')) return `pi ${icon}`
  return `pi pi-${icon}`
}

const rowClass = (data) => {
  if (editingBudgetItems.value) {
    return 'editing-row'
  }
  
  const remaining = getRemainingAmount(data)
  if (remaining < 0) {
    return 'over-budget-row'
  }
  return ''
}

const transactionRowClass = (data) => {
  return highlightedTransactionIds.value.includes(data._id) ? 'highlighted-transaction-row' : ''
}

const toggleTransactionHighlight = (event) => {
  const clickTarget = event.originalEvent?.target
  if (clickTarget?.closest('button, .p-button, a, input, textarea, select, [role="button"]')) {
    return
  }

  const transactionId = event.data?._id
  if (!transactionId) {
    return
  }

  if (highlightedTransactionIds.value.includes(transactionId)) {
    highlightedTransactionIds.value = highlightedTransactionIds.value.filter((id) => id !== transactionId)
    return
  }

  highlightedTransactionIds.value = [...highlightedTransactionIds.value, transactionId]
}

const clearBudgetBalanceClipboard = () => {
  balanceClipboard.value = null
}

const canExtractBudgetBalance = (item) => {
  return !balanceClipboard.value && getRemainingAmount(item) > 0
}

const extractBudgetBalance = (item) => {
  if (balanceClipboard.value) {
    toast.add({
      severity: 'warn',
      summary: 'Clipboard ocupado',
      detail: 'Primero incluye o reinicia el importe ya extraído.',
      life: 3000
    })
    return
  }

  const amountToExtract = roundMoney(getRemainingAmount(item))
  if (amountToExtract <= 0) {
    toast.add({
      severity: 'warn',
      summary: 'Sin importe disponible',
      detail: 'Solo puedes extraer categorias con restante positivo.',
      life: 3000
    })
    return
  }

  item.planned_amount = roundMoney(item.planned_amount - amountToExtract)
  balanceClipboard.value = {
    amount: amountToExtract,
    sourceTempId: item.temp_id,
    sourceCategoryId: item.category_id,
    sourceCategoryName: resolveCategoryName(item.category_id) || item.category || 'Categoría'
  }
}

const includeBudgetBalance = (item) => {
  if (!balanceClipboard.value) {
    return
  }

  item.planned_amount = roundMoney(item.planned_amount + balanceClipboard.value.amount)
  clearBudgetBalanceClipboard()
}

const resetBudgetBalanceClipboard = () => {
  if (!balanceClipboard.value) {
    return
  }

  const sourceItem = tempBudgetItems.value.find((item) => item.temp_id === balanceClipboard.value.sourceTempId)
  if (!sourceItem) {
    toast.add({
      severity: 'error',
      summary: 'No se pudo reiniciar',
      detail: 'La categoría origen ya no está disponible para devolver el importe.',
      life: 3500
    })
    clearBudgetBalanceClipboard()
    return
  }

  sourceItem.planned_amount = roundMoney(sourceItem.planned_amount + balanceClipboard.value.amount)
  clearBudgetBalanceClipboard()
}

const closeTransactionDialog = () => {
  showTransactionDialog.value = false
  editingTransaction.value = null
  transactionForm.value = createDefaultTransactionForm()
}

const saveTransaction = async () => {
  if (!transactionForm.value.amount || !transactionForm.value.category_id || !transactionForm.value.bank) {
    toast.add({
      severity: 'warn',
      summary: 'Campos requeridos',
      detail: 'Completa todos los campos obligatorios',
      life: 3000
    })
    return
  }

  try {
    const payload = {
      budget_id: budgetId.value,
      type: transactionForm.value.type,
      amount: transactionForm.value.amount,
      category_id: transactionForm.value.category_id,
      category: resolveCategoryName(transactionForm.value.category_id),
      bank: budget.value?.bank || transactionForm.value.bank,
      payment_method: transactionForm.value.payment_method,
      timestamp: transactionForm.value.timestamp.toISOString(),
      comment: transactionForm.value.comment,
      is_charged: transactionForm.value.is_charged
    }

    if (editingTransaction.value) {
      await transactionStore.updateTransaction(editingTransaction.value._id, payload)
      toast.add({
        severity: 'success',
        summary: 'Transacción actualizada',
        detail: 'La transacción se actualizó correctamente',
        life: 3000
      })
    } else {
      await transactionStore.createTransaction(payload)
      toast.add({
        severity: 'success',
        summary: 'Transacción creada',
        detail: 'La transacción se creó correctamente',
        life: 3000
      })
    }

    closeTransactionDialog()
    await loadBudget()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo guardar la transacción',
      life: 3000
    })
  }
}

const editTransaction = (transaction) => {
  editingTransaction.value = transaction
  transactionForm.value = {
    type: transaction.type,
    amount: transaction.amount,
    category_id: resolveCategoryId(transaction.category_id || transaction.category),
    bank: budget.value?.bank || transaction.bank,
    payment_method: transaction.payment_method,
    timestamp: new Date(transaction.timestamp),
    comment: transaction.comment || '',
    is_charged: transaction.is_charged
  }
  showTransactionDialog.value = true
}

const markAsCharged = async (transaction) => {
  try {
    await transactionStore.markCharged(transaction._id)
    toast.add({
      severity: 'success',
      summary: 'Transacción actualizada',
      detail: 'La transacción se marcó como cobrada',
      life: 3000
    })
    await loadBudget()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo actualizar la transacción',
      life: 3000
    })
  }
}

const confirmDeleteTransaction = (transaction) => {
  transactionToDelete.value = transaction
  showDeleteDialog.value = true
}

const deleteTransaction = async () => {
  try {
    await transactionStore.deleteTransaction(transactionToDelete.value._id)
    toast.add({
      severity: 'success',
      summary: 'Transacción eliminada',
      detail: 'La transacción se eliminó correctamente',
      life: 3000
    })
    showDeleteDialog.value = false
    transactionToDelete.value = null
    await loadBudget()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo eliminar la transacción',
      life: 3000
    })
  }
}

const applyRecurringExpenses = async () => {
  try {
    await recurringStore.applyToBudget(budgetId.value, selectedRecurring.value)
    toast.add({
      severity: 'success',
      summary: 'Gastos agregados',
      detail: `Se agregaron ${selectedRecurring.value.length} gastos recurrentes al presupuesto como montos planificados`,
      life: 3000
    })
    showRecurringDialog.value = false
    selectedRecurring.value = []
    await loadBudget()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron aplicar los gastos recurrentes',
      life: 3000
    })
  }
}

// Budget Items Editing Functions
const startEditingBudgetItems = () => {
  editingBudgetItems.value = true
  tempBudgetItems.value = JSON.parse(JSON.stringify(budget.value.budget_items || [])).map((item) => createTempBudgetItem({
    ...item,
    category_id: resolveCategoryId(item.category_id || item.category)
  }))
  clearBudgetBalanceClipboard()
}

const cancelEditingBudgetItems = () => {
  editingBudgetItems.value = false
  tempBudgetItems.value = []
  clearBudgetBalanceClipboard()
}

const addNewBudgetItem = () => {
  tempBudgetItems.value.push(createTempBudgetItem())
}

const removeBudgetItem = (index) => {
  const targetItem = tempBudgetItems.value[index]
  if (balanceClipboard.value?.sourceTempId === targetItem?.temp_id) {
    toast.add({
      severity: 'warn',
      summary: 'Reinicio pendiente',
      detail: 'No puedes eliminar la categoría origen mientras el clipboard siga activo.',
      life: 3000
    })
    return
  }

  tempBudgetItems.value.splice(index, 1)
}

const saveBudgetItems = async () => {
  try {
    if (balanceClipboard.value) {
      toast.add({
        severity: 'warn',
        summary: 'Clipboard activo',
        detail: 'Incluye o reinicia el importe extraído antes de guardar.',
        life: 3500
      })
      return
    }

    // Validate that all items have a category and amount
    const invalidItems = tempBudgetItems.value.filter(item => !item.category_id || !item.planned_amount)
    if (invalidItems.length > 0) {
      toast.add({
        severity: 'warn',
        summary: 'Validación',
        detail: 'Todas las categorías deben tener un nombre y monto planificado',
        life: 3000
      })
      return
    }

    await budgetStore.updateBudget(budgetId.value, {
      budget_items: tempBudgetItems.value.map((item) => ({
        category_id: item.category_id,
        planned_amount: item.planned_amount,
        spent_amount: item.spent_amount,
        category: resolveCategoryName(item.category_id)
      }))
    })

    toast.add({
      severity: 'success',
      summary: 'Categorías actualizadas',
      detail: 'Los items del presupuesto se actualizaron correctamente',
      life: 3000
    })

    editingBudgetItems.value = false
    tempBudgetItems.value = []
    clearBudgetBalanceClipboard()
    await loadBudget()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron actualizar los items del presupuesto',
      life: 3000
    })
  }
}
</script>

<style scoped>
.budget-view {
  width: 100%;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Loading and Error States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  gap: 1rem;
  color: var(--text-color-secondary);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 12px;
  color: #dc2626;
}

/* Header */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  flex: 1;
}

.back-button {
  margin-top: 0.5rem;
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}

.page-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.budget-period {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  color: var(--text-color-secondary);
}

.budget-bank-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  background: var(--budget-bank-pill-bg);
  color: var(--budget-bank-pill-color);
  font-size: 0.85rem;
  font-weight: 700;
}

.budget-bank-chip-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.8rem;
  padding: 0.2rem 0.45rem;
  border-radius: 999px;
  color: white;
  background: var(--budget-bank-surface);
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  box-shadow: 0 12px 20px var(--budget-bank-shadow);
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--surface-card);
  border-radius: 16px;
  padding: 1.75rem;
  border: 1px solid var(--surface-border);
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
  color: white;
}

.stat-card-balance .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card-income .stat-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-card-expense .stat-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-card-pending .stat-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-card-status .stat-icon {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.stat-card-status.status-warning .stat-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-card-status.status-critical .stat-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.25rem;
  line-height: 1;
}

.stat-value.negative {
  color: #ef4444;
}

.stat-card-status.status-healthy .stat-value {
  color: #0f8b6f;
}

.stat-card-status.status-warning .stat-value {
  color: #d97706;
}

.stat-card-status.status-critical .stat-value {
  color: #ef4444;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  font-weight: 500;
  margin: 0 0 0.25rem 0;
}

.stat-detail {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

/* Transactions Card */
.transactions-card {
  border: 1px solid var(--surface-border);
  border-radius: 16px;
}

.transactions-card :deep(.p-card-body) {
  padding: 0;
}

.transactions-card :deep(.p-card-content) {
  padding: 0.75rem 0.85rem 0.9rem;
}

.transactions-card .card-header {
  padding: 0.95rem 1rem;
  gap: 0.75rem;
}

.transactions-card .card-header h2 {
  font-size: 1.1rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.card-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.header-filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.transactions-card .header-filters {
  gap: 0.55rem;
}

.transactions-card .header-filters :deep(.p-inputtext),
.transactions-card .header-filters :deep(.p-select-label) {
  padding: 0.42rem 0.65rem;
  font-size: 0.84rem;
}

.transactions-card .header-filters :deep(.p-select-dropdown) {
  width: 2.2rem;
}

.search-input {
  width: 250px;
}

/* Transaction Summary */
.transaction-summary {
  display: flex;
  gap: 0.9rem;
  margin-bottom: 0.75rem;
  padding: 0.75rem 0.85rem;
  background: var(--surface-ground);
  border-radius: 12px;
  border: 1px solid var(--surface-border);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex: 1;
  min-width: 0;
}

.summary-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  color: white;
  flex-shrink: 0;
}

.income-icon {
  background: #10b981;
}

.expense-icon {
  background: #ef4444;
}

.balance-icon {
  background: #3b82f6;
}

.summary-content {
  flex: 1;
}

.summary-value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.15rem 0;
  line-height: 1.1;
}

.summary-value.negative {
  color: #ef4444;
}

.summary-label {
  font-size: 0.78rem;
  color: var(--text-color-secondary);
  font-weight: 500;
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-color-secondary);
}

.empty-state i {
  font-size: 3rem;
  opacity: 0.5;
  margin-bottom: 1rem;
}

.date-text {
  color: var(--text-color-secondary);
  font-size: 0.8rem;
}

.amount-text {
  font-weight: 600;
  font-size: 0.84rem;
}

.balance-text {
  font-weight: 700;
  font-size: 0.84rem;
}

.text-green {
  color: #10b981 !important;
}

.text-red {
  color: #ef4444 !important;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.action-buttons :deep(.p-button) {
  width: 1.9rem;
  height: 1.9rem;
}

.comment-hover {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.22rem 0.45rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--surface-ground) 72%, transparent);
  color: var(--text-color-secondary);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: help;
}

.comment-empty {
  color: var(--text-color-secondary);
}

/* Dialog */
.dialog-content {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dialog-description {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-field label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9375rem;
}

.button-group {
  display: flex;
  gap: 0.5rem;
}

.button-group :deep(.p-button) {
  flex: 1;
}

.checkbox-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-field label {
  font-weight: 500;
  margin: 0;
  cursor: pointer;
}

.w-full {
  width: 100%;
}

.locked-bank-field {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem 1rem;
  border-radius: 14px;
  border: 1px solid color-mix(in srgb, var(--budget-bank-accent) 18%, transparent);
  background: var(--budget-bank-pill-bg);
}

.locked-bank-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 3.2rem;
  padding: 0.4rem 0.55rem;
  border-radius: 999px;
  color: white;
  background: var(--budget-bank-surface);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  box-shadow: 0 12px 20px var(--budget-bank-shadow);
}

.locked-bank-copy {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.locked-bank-copy strong {
  color: var(--text-color);
}

.locked-bank-copy small {
  color: var(--text-color-secondary);
}

/* Recurring List */
.recurring-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.recurring-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  transition: all 0.2s;
}

.recurring-item:hover {
  background: var(--surface-hover);
}

.recurring-label {
  flex: 1;
  cursor: pointer;
}

.recurring-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.recurring-name {
  font-weight: 600;
  color: var(--text-color);
}

.recurring-detail {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

/* Budget Items Card */
.budget-feasibility-card {
  margin-bottom: 1.5rem;
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  overflow: hidden;
}

.budget-availability-card .feasibility-summary {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(59, 130, 246, 0.08) 100%);
}

.feasibility-summary {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%);
}

.feasibility-copy {
  flex: 1;
}

.feasibility-kicker {
  display: inline-block;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-color);
}

.feasibility-copy h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
}

.feasibility-copy p {
  margin: 0;
  color: var(--text-color-secondary);
  line-height: 1.5;
}

.feasibility-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(170px, 1fr));
  gap: 1rem;
  flex: 1.2;
}

.feasibility-metric {
  padding: 1rem;
  border-radius: 14px;
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.metric-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-color-secondary);
}

.metric-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1.1;
}

.metric-alert {
  border-color: rgba(239, 68, 68, 0.25);
  background: rgba(239, 68, 68, 0.06);
}

.metric-alert .metric-value {
  color: #ef4444;
}

.metric-ok {
  border-color: rgba(16, 185, 129, 0.25);
  background: rgba(16, 185, 129, 0.08);
}

.metric-ok .metric-value {
  color: #10b981;
}

.budget-items-card {
  margin-bottom: 2rem;
}

.budget-items-card :deep(.p-card-body),
.budget-items-card :deep(.p-card-body) {
  padding: 0;
}

.budget-items-card :deep(.p-card-content) {
  padding: 0.55rem 0.7rem 0.75rem;
}

.budget-items-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.7rem;
  padding: 0.8rem 1rem;
  border-bottom: 1px solid var(--surface-border);
}

.budget-items-card .card-header h2 {
  font-size: 1.05rem;
}

.header-title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.7rem;
  flex: 1;
}

.header-actions-section {
  display: flex;
  gap: 0.45rem;
  align-items: center;
}

.budget-items-card .header-actions-section :deep(.p-button) {
  padding: 0.4rem 0.65rem;
  font-size: 0.76rem;
}

.budget-items-card .summary-stats {
  display: flex;
  gap: 0.8rem;
  font-size: 0.78rem;
  line-height: 1.1;
}

.budget-items-card .stat-item {
  color: var(--text-color-secondary);
}

.add-category-section {
  padding: 0.45rem 0.6rem 0.5rem;
  margin-bottom: 0.45rem;
  border-bottom: 1px solid var(--surface-border);
  background: var(--surface-50);
  border-radius: 10px;
}

.editing-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.balance-clipboard-pill {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  background: rgba(251, 191, 36, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.clipboard-label {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #b45309;
}

.balance-clipboard-pill strong {
  font-family: 'Courier New', monospace;
  color: var(--heading-color);
}

.balance-clipboard-pill small {
  color: var(--text-color-secondary);
}

.add-category-section :deep(.p-button) {
  padding: 0.38rem 0.65rem;
  font-size: 0.75rem;
}

/* Excel-like Table Styles */
.budget-items-table {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.budget-items-table :deep(.p-datatable-thead > tr > th) {
  background: var(--primary-color);
  color: white;
  font-weight: 600;
  padding: 0.24rem 0.45rem;
  border: 1px solid var(--surface-border);
  text-align: left;
  font-size: 0.74rem;
  line-height: 1.05;
}

.budget-items-table :deep(.p-datatable-tbody > tr > td) {
  padding: 0.18rem 0.45rem;
  border: 1px solid var(--surface-border);
  vertical-align: middle;
  font-size: 0.75rem;
  line-height: 1.05;
}

.budget-items-table :deep(.p-column-title) {
  line-height: 1.05;
}

.budget-items-table :deep(.p-inputtext),
.budget-items-table :deep(.p-inputnumber-input),
.budget-items-table :deep(.p-select-label) {
  padding: 0.26rem 0.4rem;
  min-height: 2rem;
  font-size: 0.75rem;
}

.budget-items-table :deep(.p-select-dropdown) {
  width: 2rem;
}

.budget-items-totals {
  display: grid;
  grid-template-columns: minmax(280px, 2.2fr) minmax(120px, 1fr) minmax(120px, 1fr) minmax(120px, 1fr) minmax(120px, 1fr);
  margin-top: 0.45rem;
  border: 1px solid var(--surface-border);
  border-radius: 12px;
  overflow: hidden;
  background: color-mix(in srgb, var(--surface-card) 92%, transparent);
}

.budget-items-totals.with-actions {
  grid-template-columns: minmax(280px, 2.2fr) minmax(120px, 1fr) minmax(120px, 1fr) minmax(120px, 1fr) minmax(120px, 1fr) 5rem;
}

.totals-cell {
  min-height: 2rem;
  padding: 0.32rem 0.45rem;
  border-right: 1px solid var(--surface-border);
  background: rgba(248, 250, 252, 0.92);
  display: flex;
  align-items: center;
  font-size: 0.76rem;
  line-height: 1.05;
}

.totals-cell:last-child {
  border-right: 0;
}

.totals-label {
  font-weight: 700;
  color: var(--heading-color);
}

.totals-value {
  justify-content: flex-end;
  font-family: 'Courier New', monospace;
  font-weight: 700;
  color: var(--heading-color);
}

.totals-placeholder {
  justify-content: center;
  color: var(--text-color-secondary);
}

.budget-item-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.15rem;
  flex-wrap: wrap;
}

.transactions-table :deep(.p-datatable-thead > tr > th) {
  padding: 0.28rem 0.45rem;
  font-size: 0.78rem;
  line-height: 1.15;
}

.transactions-table :deep(.p-datatable-tbody > tr > td) {
  padding: 0.26rem 0.45rem;
  vertical-align: middle;
  font-size: 0.78rem;
  line-height: 1.15;
}

.transactions-table :deep(.p-datatable-tbody > tr) {
  cursor: pointer;
}

.transactions-table :deep(.p-datatable-tbody > tr.highlighted-transaction-row > td) {
  background: rgba(250, 204, 21, 0.24) !important;
}

.transactions-table :deep(.p-datatable-tbody > tr.highlighted-transaction-row:hover > td) {
  background: rgba(250, 204, 21, 0.32) !important;
}

.transactions-table :deep(.p-tag) {
  font-size: 0.72rem;
  padding: 0.2rem 0.42rem;
}

.transactions-table :deep(.p-paginator) {
  padding: 0.4rem 0.55rem;
}

.transactions-table :deep(.p-paginator .p-paginator-page),
.transactions-table :deep(.p-paginator .p-paginator-prev),
.transactions-table :deep(.p-paginator .p-paginator-next),
.transactions-table :deep(.p-paginator .p-paginator-first),
.transactions-table :deep(.p-paginator .p-paginator-last) {
  min-width: 1.9rem;
  height: 1.9rem;
}

.transactions-table :deep(.p-paginator .p-dropdown-label) {
  font-size: 0.78rem;
}

/* Expenses Summary Card */
.expenses-summary-card {
  margin-top: 2rem;
  border: 1px solid var(--surface-border);
  border-radius: 16px;
}

.expenses-summary-card :deep(.p-card-body) {
  padding: 0;
}

.expenses-summary-card :deep(.p-card-content) {
  padding: 0.65rem 0.85rem 0.9rem;
}

.expenses-summary-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.95rem 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.expenses-summary-card .card-header h2 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.expenses-summary-card .summary-stats {
  display: flex;
  gap: 0.85rem;
  font-size: 0.8rem;
  line-height: 1.15;
}

.expenses-summary-card .stat-item {
  color: var(--text-color-secondary);
}

.expenses-summary-table :deep(.p-datatable-thead > tr > th) {
  background: var(--primary-color);
  color: white;
  font-weight: 600;
  padding: 0.28rem 0.45rem;
  border: 1px solid var(--surface-border);
  text-align: left;
  font-size: 0.78rem;
  line-height: 1.15;
}

.expenses-summary-table :deep(.p-datatable-tbody > tr > td) {
  padding: 0.26rem 0.45rem;
  border: 1px solid var(--surface-border);
  vertical-align: middle;
  font-size: 0.78rem;
  line-height: 1.15;
}

.expenses-summary-table :deep(.p-tag) {
  font-size: 0.72rem;
  padding: 0.2rem 0.42rem;
}

.expenses-summary-table :deep(.p-paginator) {
  padding: 0.4rem 0.55rem;
}

.expenses-summary-table :deep(.p-paginator .p-paginator-page),
.expenses-summary-table :deep(.p-paginator .p-paginator-prev),
.expenses-summary-table :deep(.p-paginator .p-paginator-next),
.expenses-summary-table :deep(.p-paginator .p-paginator-first),
.expenses-summary-table :deep(.p-paginator .p-paginator-last) {
  min-width: 1.9rem;
  height: 1.9rem;
}

.expenses-summary-table :deep(.p-paginator .p-dropdown-label) {
  font-size: 0.78rem;
}

.transaction-count {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.78rem;
}

.banks-list {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.bank-tag {
  font-size: 0.72rem;
  padding: 0.18rem 0.42rem;
}

.budget-items-table :deep(.p-datatable-tbody > tr:hover) {
  background: var(--highlight-bg) !important;
}

.budget-items-table :deep(.p-datatable-tbody > tr.over-budget-row) {
  background: rgba(239, 68, 68, 0.05);
}

.budget-items-table :deep(.p-datatable-tbody > tr.editing-row) {
  background: var(--surface-100);
}

.category-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-link-button {
  width: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
  border-radius: 10px;
}

.category-link-button:focus-visible {
  outline: 2px solid color-mix(in srgb, var(--primary-color) 75%, white);
  outline-offset: 2px;
}

.category-link-button:hover .category-cell,
.category-link-button:focus-visible .category-cell {
  transform: translateX(1px);
}

.category-link-button .category-cell {
  transition: transform 0.18s ease;
}

.parent-category {
  font-weight: 600;
  background: rgba(59, 130, 246, 0.05);
  padding: 0.5rem;
  border-radius: 8px;
  margin: 0.25rem 0;
}

.subcategory {
  margin-left: 2rem;
  opacity: 0.9;
}

.parent-indicator {
  font-size: 1.1rem;
}

.subcategory-indicator {
  color: var(--primary-color);
  font-size: 1rem;
  font-weight: bold;
}

.parent-tag {
  font-weight: 600;
  font-size: 0.9rem;
}

.subcategory-count {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.category-cell {
  display: flex;
  align-items: center;
  gap: 0.22rem;
  font-weight: 500;
}

.category-copy {
  display: flex;
  flex-direction: column;
  gap: 0.08rem;
}

.category-meta-inline {
  color: var(--text-color-secondary);
  font-size: 0.65rem;
  line-height: 1.1;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.subcategory-indicator {
  color: var(--text-color-secondary);
  font-weight: 600;
  margin-right: 0.2rem;
}

.amount-value {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  font-size: 0.8rem;
}

.amount-value.spent {
  color: var(--primary-color);
}

.percentage-cell {
  display: flex;
  flex-direction: column;
  gap: 0.18rem;
}

.percentage-value {
  font-weight: 600;
  font-size: 0.78rem;
}

.percentage-caption {
  font-size: 0.68rem;
  line-height: 1;
  color: var(--text-color-secondary);
}

.percentage-value.remaining-healthy,
.percentage-caption.remaining-healthy {
  color: #0f8b6f;
}

.percentage-value.remaining-medium,
.percentage-caption.remaining-medium {
  color: #d97706;
}

.percentage-value.remaining-low,
.percentage-caption.remaining-low {
  color: #ef4444;
}

.percentage-value.remaining-complete,
.percentage-caption.remaining-complete {
  color: #0f8b6f;
}

.percentage-value.remaining-no-margin,
.percentage-caption.remaining-no-margin {
  color: #d97706;
}

.percentage-value.remaining-negative,
.percentage-caption.remaining-negative {
  color: #ef4444;
}

.mini-progress-bar {
  width: 100%;
  height: 4px;
  background: var(--surface-200);
  border-radius: 999px;
  overflow: hidden;
}

.mini-progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.mini-progress-fill.progress-healthy {
  background: #10b981;
}

.mini-progress-fill.progress-medium {
  background: #f59e0b;
}

.mini-progress-fill.progress-low {
  background: #ef4444;
}

.mini-progress-fill.progress-complete {
  background: #10b981;
}

.mini-progress-fill.progress-no-margin {
  background: #f59e0b;
}

.mini-progress-fill.progress-negative {
  background: #ef4444;
}

.banks-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.bank-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.no-banks {
  color: var(--text-color-secondary);
  font-style: italic;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
}

.category-option i {
  font-size: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.75rem;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .header-left {
    flex-direction: column;
  }

  .header-actions {
    flex-direction: column;
  }

  .header-actions :deep(.p-button) {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .feasibility-summary {
    flex-direction: column;
  }

  .feasibility-metrics {
    grid-template-columns: 1fr;
    width: 100%;
  }

  .budget-items-totals,
  .budget-items-totals.with-actions {
    grid-template-columns: 1fr;
  }

  .totals-cell {
    justify-content: space-between;
    border-right: 0;
    border-bottom: 1px solid var(--surface-border);
  }

  .totals-cell:last-child {
    border-bottom: 0;
  }

  .header-filters {
    flex-direction: column;
    width: 100%;
  }

  .search-input {
    width: 100%;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
