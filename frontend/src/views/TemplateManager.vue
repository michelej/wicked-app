<template>
  <div class="template-manager">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Plantillas de Presupuesto</h1>
          <p class="page-subtitle">Crea plantillas reutilizables para tus presupuestos con transacciones predefinidas</p>
        </div>
        <Button 
          label="Nueva Plantilla" 
          icon="pi pi-plus"
          @click="openCreateDialog"
          severity="success"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="templateStore.loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando plantillas...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="templateStore.error" class="error-message">
      <i class="pi pi-exclamation-circle"></i>
      {{ templateStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="templateStore.templates.length === 0" class="empty-state">
      <i class="pi pi-file"></i>
      <h2>No hay plantillas creadas</h2>
      <p>Crea tu primera plantilla para facilitar la creación de presupuestos recurrentes</p>
      <Button 
        label="Crear Plantilla" 
        icon="pi pi-plus"
        @click="openCreateDialog"
        severity="success"
      />
    </div>

    <!-- Templates List -->
    <div v-else class="templates-list">
      <Card 
        v-for="template in templateStore.templates" 
        :key="template.id"
        class="template-item"
      >
        <template #header>
          <div class="template-header">
            <div class="template-info">
              <h3>{{ template.name }}</h3>
              <p class="template-description" v-if="template.description">{{ template.description }}</p>
            </div>
          </div>
        </template>

        <template #content>
          <div class="template-details">
            <!-- Template Stats -->
            <div class="template-stats">
              <div class="stat-item">
                <span class="stat-label">Transacciones</span>
                <span class="stat-value">{{ template.template_items?.length || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Ingresos</span>
                <span class="stat-value income">{{ countByType(template, 'income') }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Gastos</span>
                <span class="stat-value expense">{{ countByType(template, 'expense') }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Total Estimado</span>
                <span class="stat-value amount-text">{{ formatCurrency(calculateTotal(template)) }}</span>
              </div>
            </div>

            <!-- Template Items Preview -->
            <div v-if="template.template_items?.length > 0" class="template-items-preview">
              <h4>Transacciones incluidas:</h4>
              <div class="items-list">
                <div 
                  v-for="(item, index) in template.template_items.slice(0, 3)" 
                  :key="index"
                  class="item-preview"
                >
                  <Tag 
                    :value="formatTransactionType(item.type)" 
                    :severity="item.type === 'income' ? 'success' : 'danger'"
                  />
                  <span class="item-category">{{ item.category }}</span>
                  <span class="item-amount">{{ formatCurrency(item.amount) }}</span>
                </div>
                <p v-if="template.template_items.length > 3" class="more-items">
                  +{{ template.template_items.length - 3 }} más
                </p>
              </div>
            </div>

            <!-- Dates -->
            <div class="template-meta">
              <span class="meta-item">
                <i class="pi pi-calendar"></i>
                Creada: {{ formatDate(template.created_at) }}
              </span>
              <span class="meta-item">
                <i class="pi pi-clock"></i>
                Actualizada: {{ formatDate(template.updated_at) }}
              </span>
            </div>
          </div>
        </template>

        <template #footer>
          <div class="template-actions">
            <Button 
              label="Aplicar a Presupuesto" 
              icon="pi pi-check"
              @click.stop="openApplyDialog(template)"
              severity="primary"
              outlined
            />
            <Button 
              label="Editar" 
              icon="pi pi-pencil"
              @click.stop="openEditDialog(template)"
              severity="secondary"
              outlined
            />
            <Button 
              icon="pi pi-trash" 
              @click.stop="confirmDelete(template)"
              severity="danger"
              outlined
            />
          </div>
        </template>
      </Card>
    </div>

    <!-- Create/Edit Template Dialog -->
    <Dialog 
      v-model:visible="showTemplateDialog" 
      :header="editingTemplate ? 'Editar Plantilla' : 'Nueva Plantilla'"
      :modal="true"
      :closable="true"
      :style="{ width: '800px' }"
      class="template-dialog"
    >
      <div class="dialog-content">
        <!-- Template Info -->
        <div class="form-section">
          <h3>Información de la Plantilla</h3>
          <div class="form-group">
            <label for="template-name">Nombre *</label>
            <InputText 
              id="template-name"
              v-model="templateForm.name" 
              placeholder="ej. Plantilla Gastos Mensuales"
              :class="{ 'p-invalid': submitted && !templateForm.name }"
            />
            <small v-if="submitted && !templateForm.name" class="p-error">El nombre es requerido</small>
          </div>

          <div class="form-group">
            <label for="template-description">Descripción</label>
            <Textarea 
              id="template-description"
              v-model="templateForm.description" 
              placeholder="Descripción opcional de la plantilla"
              rows="3"
            />
          </div>
        </div>

        <!-- Template Items -->
        <div class="form-section">
          <div class="section-header">
            <h3>Transacciones de la Plantilla</h3>
            <Button 
              label="Agregar Transacción" 
              icon="pi pi-plus"
              @click="addTemplateItem"
              size="small"
              severity="success"
            />
          </div>

          <div v-if="templateForm.template_items.length === 0" class="empty-items">
            <p>No hay transacciones en esta plantilla</p>
          </div>

          <div v-else class="template-items-list">
            <Card 
              v-for="(item, index) in templateForm.template_items" 
              :key="index"
              class="template-item-card"
            >
              <template #content>
                <div class="item-form">
                  <div class="form-row">
                    <div class="form-group">
                      <label>Tipo *</label>
                      <Select 
                        v-model="item.type" 
                        :options="transactionTypes"
                        optionLabel="label"
                        optionValue="value"
                        placeholder="Seleccionar"
                      />
                    </div>

                    <div class="form-group">
                      <label>Categoría *</label>
                      <Select 
                        v-model="item.category" 
                        :options="getFilteredCategories(item.type)"
                        optionLabel="name"
                        optionValue="name"
                        placeholder="Seleccionar categoría"
                        :filter="true"
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

                    <div class="form-group">
                      <label>Monto *</label>
                      <InputNumber 
                        v-model="item.amount" 
                        mode="currency"
                        currency="EUR"
                        locale="es-ES"
                        :minFractionDigits="2"
                        :maxFractionDigits="2"
                        placeholder="0,00 €"
                      />
                    </div>
                  </div>

                  <div class="form-row">
                    <div class="form-group">
                      <label>Banco</label>
                      <InputText 
                        v-model="item.bank" 
                        placeholder="ej. Banco Santander"
                      />
                    </div>

                    <div class="form-group">
                      <label>Método de Pago *</label>
                      <Select 
                        v-model="item.payment_method" 
                        :options="paymentMethods"
                        optionLabel="label"
                        optionValue="value"
                        placeholder="Seleccionar"
                      />
                    </div>

                    <div class="form-group checkbox-group">
                      <label>
                        <Checkbox v-model="item.is_recurring" :binary="true" />
                        Es recurrente
                      </label>
                    </div>
                  </div>

                  <div class="form-row">
                    <div class="form-group full-width">
                      <label>Comentario</label>
                      <InputText 
                        v-model="item.comment" 
                        placeholder="Comentario opcional"
                      />
                    </div>

                    <Button 
                      icon="pi pi-trash" 
                      @click="removeTemplateItem(index)"
                      severity="danger"
                      text
                      class="remove-btn"
                    />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancelar" 
          @click="showTemplateDialog = false"
          severity="secondary"
          text
        />
        <Button 
          :label="editingTemplate ? 'Actualizar' : 'Crear'" 
          @click="saveTemplate"
          severity="success"
          :loading="templateStore.loading"
        />
      </template>
    </Dialog>

    <!-- Apply Template Dialog -->
    <Dialog 
      v-model:visible="showApplyDialog" 
      header="Aplicar Plantilla a Presupuesto"
      :modal="true"
      :closable="true"
      :style="{ width: '600px' }"
    >
      <div class="dialog-content">
        <p class="dialog-description">
          Crea un nuevo presupuesto usando esta plantilla. Las transacciones de la plantilla 
          se aplicarán automáticamente al nuevo presupuesto.
        </p>

        <div class="form-group">
          <label for="budget-name">Nombre del Presupuesto *</label>
          <InputText 
            id="budget-name"
            v-model="applyForm.budgetName" 
            placeholder="ej. Presupuesto Marzo 2026"
            :class="{ 'p-invalid': applySubmitted && !applyForm.budgetName }"
          />
          <small v-if="applySubmitted && !applyForm.budgetName" class="p-error">El nombre es requerido</small>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="start-date">Fecha Inicio *</label>
            <Calendar 
              id="start-date"
              v-model="applyForm.startDate" 
              dateFormat="dd/mm/yy"
              placeholder="dd/mm/aaaa"
              :showIcon="true"
              :class="{ 'p-invalid': applySubmitted && !applyForm.startDate }"
            />
            <small v-if="applySubmitted && !applyForm.startDate" class="p-error">La fecha de inicio es requerida</small>
          </div>

          <div class="form-group">
            <label for="end-date">Fecha Fin *</label>
            <Calendar 
              id="end-date"
              v-model="applyForm.endDate" 
              dateFormat="dd/mm/yy"
              placeholder="dd/mm/aaaa"
              :showIcon="true"
              :minDate="applyForm.startDate"
              :class="{ 'p-invalid': applySubmitted && !applyForm.endDate }"
            />
            <small v-if="applySubmitted && !applyForm.endDate" class="p-error">La fecha de fin es requerida</small>
          </div>
        </div>

        <!-- Preview of transactions that will be created -->
        <div v-if="selectedTemplate" class="apply-preview">
          <h4>Se crearán {{ selectedTemplate.template_items?.length || 0 }} transacciones</h4>
          <div class="preview-stats">
            <div class="preview-stat">
              <span class="stat-label">Ingresos</span>
              <span class="stat-value income">{{ formatCurrency(calculateTypeTotal(selectedTemplate, 'income')) }}</span>
            </div>
            <div class="preview-stat">
              <span class="stat-label">Gastos</span>
              <span class="stat-value expense">{{ formatCurrency(calculateTypeTotal(selectedTemplate, 'expense')) }}</span>
            </div>
            <div class="preview-stat">
              <span class="stat-label">Balance</span>
              <span class="stat-value">{{ formatCurrency(calculateTotal(selectedTemplate)) }}</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancelar" 
          @click="showApplyDialog = false"
          severity="secondary"
          text
        />
        <Button 
          label="Crear Presupuesto" 
          @click="applyTemplate"
          severity="success"
          :loading="budgetStore.loading || transactionStore.loading"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="showDeleteDialog" 
      header="Confirmar Eliminación"
      :modal="true"
      :closable="true"
      :style="{ width: '450px' }"
    >
      <div class="dialog-content">
        <div class="confirmation-message">
          <i class="pi pi-exclamation-triangle"></i>
          <p>¿Estás seguro de que deseas eliminar la plantilla <strong>{{ templateToDelete?.name }}</strong>?</p>
          <p class="warning-text">Esta acción no se puede deshacer.</p>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancelar" 
          @click="showDeleteDialog = false"
          severity="secondary"
          text
        />
        <Button 
          label="Eliminar" 
          @click="deleteTemplate"
          severity="danger"
          :loading="templateStore.loading"
        />
      </template>
    </Dialog>

    <!-- Toast for notifications -->
    <Toast />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTemplateStore } from '@/stores/templates'
import { useCategoryStore } from '@/stores/categories'
import { useBudgetStore } from '@/stores/budgets'
import { useTransactionStore } from '@/stores/transactions'
import { useFormatters } from '@/composables/useFormatters'
import { useToast } from 'primevue/usetoast'

import Card from 'primevue/card'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import InputNumber from 'primevue/inputnumber'
import Calendar from 'primevue/calendar'
import Checkbox from 'primevue/checkbox'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'

const router = useRouter()
const templateStore = useTemplateStore()
const categoryStore = useCategoryStore()
const budgetStore = useBudgetStore()
const transactionStore = useTransactionStore()
const toast = useToast()

const { formatCurrency, formatDate, formatTransactionType, formatPaymentMethod } = useFormatters()

// Helper function for icon normalization
const normalizeIcon = (icon) => {
  if (!icon) return 'pi pi-tag'
  if (icon.startsWith('pi pi-')) return icon
  if (icon.startsWith('pi-')) return `pi ${icon}`
  return `pi pi-${icon}`
}

// Dialog states
const showTemplateDialog = ref(false)
const showApplyDialog = ref(false)
const showDeleteDialog = ref(false)
const submitted = ref(false)
const applySubmitted = ref(false)

// Form data
const editingTemplate = ref(null)
const templateToDelete = ref(null)
const selectedTemplate = ref(null)

const templateForm = ref({
  name: '',
  description: '',
  template_items: []
})

const applyForm = ref({
  budgetName: '',
  startDate: null,
  endDate: null
})

// Options
const transactionTypes = [
  { label: 'Ingreso', value: 'income' },
  { label: 'Gasto', value: 'expense' }
]

const paymentMethods = [
  { label: 'Efectivo', value: 'cash' },
  { label: 'Crédito', value: 'credit' },
  { label: 'Débito', value: 'debit' }
]

// Computed
const getFilteredCategories = (type) => {
  if (!type) return categoryStore.sortedActiveCategories
  
  if (type === 'income') {
    return categoryStore.sortedIncomeCategories
  } else if (type === 'expense') {
    return categoryStore.sortedExpenseCategories
  }
  
  return categoryStore.sortedActiveCategories.filter(cat => {
    if (cat.type === 'both') return true
    return cat.type === type
  })
}

// Helper functions
const countByType = (template, type) => {
  return template.template_items?.filter(item => item.type === type).length || 0
}

const calculateTotal = (template) => {
  if (!template.template_items) return 0
  
  return template.template_items.reduce((total, item) => {
    const amount = parseFloat(item.amount) || 0
    return item.type === 'income' ? total + amount : total - amount
  }, 0)
}

const calculateTypeTotal = (template, type) => {
  if (!template.template_items) return 0
  
  return template.template_items
    .filter(item => item.type === type)
    .reduce((total, item) => total + (parseFloat(item.amount) || 0), 0)
}

// Template CRUD operations
const openCreateDialog = () => {
  editingTemplate.value = null
  templateForm.value = {
    name: '',
    description: '',
    template_items: []
  }
  submitted.value = false
  showTemplateDialog.value = true
}

const openEditDialog = (template) => {
  editingTemplate.value = template
  templateForm.value = {
    name: template.name,
    description: template.description || '',
    template_items: JSON.parse(JSON.stringify(template.template_items || []))
  }
  submitted.value = false
  showTemplateDialog.value = true
}

const addTemplateItem = () => {
  templateForm.value.template_items.push({
    type: 'expense',
    amount: 0,
    category: '',
    bank: '',
    payment_method: 'cash',
    comment: '',
    is_recurring: false
  })
}

const removeTemplateItem = (index) => {
  templateForm.value.template_items.splice(index, 1)
}

const saveTemplate = async () => {
  submitted.value = true

  // Validate required fields
  if (!templateForm.value.name) {
    toast.add({
      severity: 'warn',
      summary: 'Validación',
      detail: 'El nombre de la plantilla es requerido',
      life: 3000
    })
    return
  }

  // Validate template items
  for (const item of templateForm.value.template_items) {
    if (!item.type || !item.category || !item.amount || item.amount <= 0 || !item.payment_method) {
      toast.add({
        severity: 'warn',
        summary: 'Validación',
        detail: 'Todas las transacciones deben tener tipo, categoría, monto válido y método de pago',
        life: 3000
      })
      return
    }
  }

  try {
    if (editingTemplate.value) {
      await templateStore.updateTemplate(editingTemplate.value.id, templateForm.value)
      toast.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Plantilla actualizada correctamente',
        life: 3000
      })
    } else {
      await templateStore.createTemplate(templateForm.value)
      toast.add({
        severity: 'success',
        summary: 'Éxito',
        detail: 'Plantilla creada correctamente',
        life: 3000
      })
    }
    showTemplateDialog.value = false
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'Error al guardar la plantilla',
      life: 5000
    })
  }
}

const confirmDelete = (template) => {
  templateToDelete.value = template
  showDeleteDialog.value = true
}

const deleteTemplate = async () => {
  try {
    await templateStore.deleteTemplate(templateToDelete.value.id)
    toast.add({
      severity: 'success',
      summary: 'Éxito',
      detail: 'Plantilla eliminada correctamente',
      life: 3000
    })
    showDeleteDialog.value = false
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'Error al eliminar la plantilla',
      life: 5000
    })
  }
}

// Apply template to budget
const openApplyDialog = (template) => {
  selectedTemplate.value = template
  applyForm.value = {
    budgetName: '',
    startDate: new Date(),
    endDate: new Date(new Date().setMonth(new Date().getMonth() + 1))
  }
  applySubmitted.value = false
  showApplyDialog.value = true
}

const applyTemplate = async () => {
  applySubmitted.value = true

  // Validate
  if (!applyForm.value.budgetName || !applyForm.value.startDate || !applyForm.value.endDate) {
    toast.add({
      severity: 'warn',
      summary: 'Validación',
      detail: 'Todos los campos son requeridos',
      life: 3000
    })
    return
  }

  if (applyForm.value.startDate >= applyForm.value.endDate) {
    toast.add({
      severity: 'warn',
      summary: 'Validación',
      detail: 'La fecha de fin debe ser posterior a la fecha de inicio',
      life: 3000
    })
    return
  }

  try {
    // Create budget
    const budgetData = {
      name: applyForm.value.budgetName,
      start_date: applyForm.value.startDate.toISOString().split('T')[0],
      end_date: applyForm.value.endDate.toISOString().split('T')[0],
      status: 'active',
      created_from_template: selectedTemplate.value.id
    }

    const newBudget = await budgetStore.createBudget(budgetData)

    // Create transactions from template items
    if (selectedTemplate.value.template_items && selectedTemplate.value.template_items.length > 0) {
      const transactions = selectedTemplate.value.template_items.map(item => ({
        type: item.type,
        amount: item.amount,
        category: item.category,
        bank: item.bank || null,
        payment_method: item.payment_method,
        comment: item.comment || null,
        is_charged: false,
        budget_ids: [newBudget.id],
        timestamp: new Date().toISOString()
      }))

      await transactionStore.bulkCreateTransactions(transactions)
    }

    toast.add({
      severity: 'success',
      summary: 'Éxito',
      detail: `Presupuesto "${applyForm.value.budgetName}" creado con ${selectedTemplate.value.template_items?.length || 0} transacciones`,
      life: 3000
    })

    showApplyDialog.value = false

    // Navigate to the new budget
    router.push(`/budget/${newBudget.id}`)
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.detail || 'Error al aplicar la plantilla',
      life: 5000
    })
  }
}

// Initialize
onMounted(async () => {
  await Promise.all([
    templateStore.fetchTemplates(),
    categoryStore.fetchCategories()
  ])
})
</script>

<style scoped>
.template-manager {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  font-size: 1rem;
  color: var(--text-color-secondary);
  margin: 0;
}

/* States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-state i,
.empty-state i {
  font-size: 4rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.empty-state h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: var(--text-color-secondary);
  margin: 0 0 1.5rem 0;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background-color: var(--red-50);
  border: 1px solid var(--red-300);
  border-radius: 0.5rem;
  color: var(--red-700);
}

/* Templates List */
.templates-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.template-item {
  height: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.template-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.template-header {
  padding: 1rem;
  border-bottom: 1px solid var(--surface-border);
}

.template-info h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.template-description {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.template-details {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Template Stats */
.template-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
}

.stat-value.income {
  color: var(--green-600);
}

.stat-value.expense {
  color: var(--red-600);
}

.amount-text {
  color: var(--primary-color);
}

/* Template Items Preview */
.template-items-preview h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.75rem 0;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item-preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background-color: var(--surface-50);
  border-radius: 0.375rem;
}

.item-category {
  flex: 1;
  font-size: 0.9rem;
  color: var(--text-color);
}

.item-amount {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-color);
}

.more-items {
  font-size: 0.85rem;
  color: var(--text-color-secondary);
  font-style: italic;
  margin: 0.25rem 0 0 0;
}

/* Template Meta */
.template-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--surface-border);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-color-secondary);
}

.meta-item i {
  font-size: 0.85rem;
}

/* Template Actions */
.template-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Dialogs */
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dialog-description {
  color: var(--text-color-secondary);
  margin: 0;
  line-height: 1.6;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.form-group.full-width {
  flex: 1;
}

.form-group.checkbox-group {
  justify-content: flex-end;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-color);
}

.form-row {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

/* Template Items */
.empty-items {
  padding: 2rem;
  text-align: center;
  background-color: var(--surface-50);
  border-radius: 0.5rem;
  color: var(--text-color-secondary);
}

.template-items-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.template-item-card {
  background-color: var(--surface-50);
}

.item-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.remove-btn {
  align-self: flex-end;
}

/* Apply Preview */
.apply-preview {
  padding: 1rem;
  background-color: var(--surface-50);
  border-radius: 0.5rem;
}

.apply-preview h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.preview-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.preview-stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

/* Confirmation Dialog */
.confirmation-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}

.confirmation-message i {
  font-size: 3rem;
  color: var(--orange-500);
}

.confirmation-message p {
  margin: 0;
  color: var(--text-color);
}

.warning-text {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

/* Category Options Styling */
.category-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
}

.category-option i {
  font-size: 1rem;
}

.subcategory-indicator {
  color: var(--text-color-secondary);
  margin-right: 0.25rem;
  font-weight: 600;
}

/* Responsive */
@media (max-width: 768px) {
  .template-manager {
    padding: 1rem;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .templates-list {
    grid-template-columns: 1fr;
  }

  .template-stats {
    grid-template-columns: 1fr;
  }

  .form-row {
    flex-direction: column;
  }

  .preview-stats {
    grid-template-columns: 1fr;
  }
}
</style>
