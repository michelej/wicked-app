<template>
  <div class="category-manager">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Gestión de Categorías</h1>
          <p class="page-subtitle">Administra las categorías de ingresos y gastos</p>
        </div>
        <Button 
          label="Nueva Categoría" 
          icon="pi pi-plus"
          @click="showCreateDialog = true"
          severity="success"
        />
      </div>
    </div>

    <!-- Type Tabs -->
    <div class="type-tabs">
      <Button 
        :label="`Todas (${categoryStore.activeCategories.length})`"
        :severity="currentType === 'all' ? 'primary' : 'secondary'"
        :text="currentType !== 'all'"
        @click="currentType = 'all'"
      />
      <Button 
        :label="`Gastos (${categoryStore.expenseCategories.length})`"
        :severity="currentType === 'expense' ? 'primary' : 'secondary'"
        :text="currentType !== 'expense'"
        @click="currentType = 'expense'"
      />
      <Button 
        :label="`Ingresos (${categoryStore.incomeCategories.length})`"
        :severity="currentType === 'income' ? 'primary' : 'secondary'"
        :text="currentType !== 'income'"
        @click="currentType = 'income'"
      />
      <Button 
        :label="`Mixtas (${mixedCategories.length})`"
        :severity="currentType === 'both' ? 'primary' : 'secondary'"
        :text="currentType !== 'both'"
        @click="currentType = 'both'"
      />
    </div>

    <!-- Loading State -->
    <div v-if="categoryStore.loading" class="loading-state">
      <ProgressSpinner />
      <p>Cargando categorías...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="categoryStore.error" class="error-message">
      <i class="pi pi-exclamation-circle"></i>
      {{ categoryStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="displayedCategories.length === 0" class="empty-state">
      <i class="pi pi-tags"></i>
      <h2>No hay categorías</h2>
      <p>Crea tu primera categoría para empezar a organizar tus transacciones</p>
      <Button 
        label="Crear Categoría" 
        icon="pi pi-plus"
        @click="showCreateDialog = true"
        severity="success"
      />
    </div>

    <!-- Categories Grid -->
    <div v-else class="categories-grid">
      <Card 
        v-for="category in displayedCategories" 
        :key="category._id"
        class="category-card"
        :class="{ 'subcategory-card': category.parent_id }"
      >
        <template #content>
          <div class="category-content">
            <div 
              class="category-icon"
              :style="{ backgroundColor: category.color }"
            >
              <i :class="normalizeIcon(category.icon)"></i>
            </div>
            <div class="category-info">
              <div class="category-name-row">
                <span v-if="category.parent_id" class="subcategory-indicator">↳</span>
                <h3>{{ category.name }}</h3>
              </div>
              <div class="category-meta">
                <Tag 
                  :value="formatCategoryType(category.type)"
                  :severity="getCategoryTypeSeverity(category.type)"
                />
                <Tag 
                  :value="category.is_active ? 'Activa' : 'Inactiva'"
                  :severity="category.is_active ? 'success' : 'danger'"
                />
              </div>
            </div>
          </div>
        </template>

        <template #footer>
          <div class="category-actions">
            <Button 
              icon="pi pi-pencil"
              text
              rounded
              severity="secondary"
              v-tooltip.top="'Editar'"
              @click.stop="editCategory(category)"
            />
            <Button 
              :icon="category.is_active ? 'pi pi-times' : 'pi pi-check'"
              text
              rounded
              :severity="category.is_active ? 'warning' : 'success'"
              v-tooltip.top="category.is_active ? 'Desactivar' : 'Activar'"
              @click.stop="toggleActive(category)"
            />
            <Button 
              icon="pi pi-trash"
              text
              rounded
              severity="danger"
              v-tooltip.top="'Eliminar'"
              @click.stop="confirmDelete(category)"
            />
          </div>
        </template>
      </Card>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog 
      v-model:visible="showCreateDialog"
      modal
      :header="editingCategory ? 'Editar Categoría' : 'Nueva Categoría'"
      :style="{ width: '550px' }"
      class="category-dialog"
    >
      <div class="dialog-content">
        <div class="form-field">
          <label for="name">Nombre *</label>
          <InputText 
            id="name"
            v-model="categoryForm.name"
            placeholder="ej. Supermercado"
            class="w-full"
          />
        </div>      

        <div class="form-field">
          <label for="type">Tipo *</label>
          <Select 
            id="type"
            v-model="categoryForm.type"
            :options="typeOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Selecciona tipo"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="parent">Categoría Padre (opcional)</label>
          <Select 
            id="parent"
            v-model="categoryForm.parent_id"
            :options="parentCategoryOptions"
            optionLabel="name"
            optionValue="_id"
            placeholder="Sin categoría padre"
            showClear
            class="w-full"
          >
            <template #option="{ option }">
              <div class="category-option">
                <i :class="normalizeIcon(option.icon)"></i>
                <span>{{ option.name }}</span>
              </div>
            </template>
          </Select>
          <small class="form-help">Deja vacío para crear una categoría principal</small>
        </div>

        <div class="form-field">
          <label for="icon">Icono *</label>
          <Select 
            id="icon"
            v-model="categoryForm.icon"
            :options="iconOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Selecciona icono"
            filter
            class="w-full"
          >
            <template #option="{ option }">
              <div class="icon-option">
                <i :class="option.value"></i>
                <span>{{ option.label }}</span>
              </div>
            </template>
            <template #value="{ value }">
              <div v-if="value" class="icon-value">
                <i :class="value"></i>
                <span>{{ iconOptions.find(o => o.value === value)?.label }}</span>
              </div>
            </template>
          </Select>
        </div>

        <div class="form-field">
          <label for="color">Color *</label>
          <div class="color-picker">
            <div 
              v-for="color in colorOptions"
              :key="color"
              class="color-option"
              :class="{ 'selected': categoryForm.color === color }"
              :style="{ backgroundColor: color }"
              @click="categoryForm.color = color"
            >
              <i v-if="categoryForm.color === color" class="pi pi-check"></i>
            </div>
          </div>
        </div>

        <div class="form-field">
          <div class="checkbox-field">
            <Checkbox 
              v-model="categoryForm.is_active"
              :binary="true"
              inputId="isActive"
            />
            <label for="isActive">Activa</label>
          </div>
        </div>

        <!-- Preview -->
        <div class="category-preview">
          <h4>Vista Previa</h4>
          <div class="preview-card">
            <div 
              class="preview-icon"
              :style="{ backgroundColor: categoryForm.color || '#64748B' }"
            >
              <i :class="normalizeIcon(categoryForm.icon) || 'pi pi-tag'"></i>
            </div>
            <div class="preview-info">
              <span class="preview-name">{{ categoryForm.name || 'Nombre de Categoría' }}</span>
              <Tag 
                :value="formatCategoryType(categoryForm.type)"
                :severity="getCategoryTypeSeverity(categoryForm.type)"
              />
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancelar"
          text
          @click="closeDialog"
        />
        <Button 
          :label="editingCategory ? 'Actualizar' : 'Crear'"
          icon="pi pi-check"
          @click="saveCategory"
          :loading="categoryStore.loading"
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
      <p>¿Estás seguro de que deseas eliminar la categoría "{{ categoryToDelete?.name }}"?</p>
      <p class="warning-text">
        <i class="pi pi-exclamation-triangle"></i>
        Si hay transacciones usando esta categoría, no se podrá eliminar.
      </p>
      
      <template #footer>
        <Button 
          label="Cancelar"
          text
          @click="showDeleteDialog = false"
        />
        <Button 
          label="Eliminar"
          icon="pi pi-trash"
          @click="deleteCategory"
          :loading="categoryStore.loading"
          severity="danger"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCategoryStore } from '@/stores/categories'
import { useToast } from 'primevue/usetoast'
import ProgressSpinner from 'primevue/progressspinner'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Checkbox from 'primevue/checkbox'

const categoryStore = useCategoryStore()
const toast = useToast()

// State
const currentType = ref('all')
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const editingCategory = ref(null)
const categoryToDelete = ref(null)

const categoryForm = ref({
  name: '',
  type: 'expense',
  icon: 'pi pi-tag',
  color: '#64748B',
  parent_id: null,
  is_active: true
})

const typeOptions = [
  { label: 'Gasto', value: 'expense' },
  { label: 'Ingreso', value: 'income' },
  { label: 'Ambos', value: 'both' }
]

const iconOptions = [
  // General
  { label: 'Etiqueta', value: 'pi pi-tag' },
  { label: 'Estrella', value: 'pi pi-star' },
  { label: 'Corazón', value: 'pi pi-heart' },
  { label: 'Bandera', value: 'pi pi-flag' },
  { label: 'Marcador', value: 'pi pi-bookmark' },
  { label: 'Escudo', value: 'pi pi-shield' },
  
  // Hogar y Servicios
  { label: 'Casa', value: 'pi pi-home' },
  { label: 'Edificio', value: 'pi pi-building' },
  { label: 'Agua', value: 'pi pi-tint' },
  { label: 'Electricidad', value: 'pi pi-bolt' },
  { label: 'Fuego', value: 'pi pi-fire' },
  { label: 'WiFi', value: 'pi pi-wifi' },
  { label: 'Llave', value: 'pi pi-key' },
  
  // Compras y Comercio
  { label: 'Carrito', value: 'pi pi-shopping-cart' },
  { label: 'Bolsa', value: 'pi pi-shopping-bag' },
  { label: 'Caja', value: 'pi pi-box' },
  { label: 'Tienda', value: 'pi pi-building' },
  { label: 'Ticket', value: 'pi pi-ticket' },
  { label: 'Etiqueta precio', value: 'pi pi-tag' },
  
  // Comida y Bebida
  { label: 'Comida', value: 'pi pi-apple' },
  { label: 'Café', value: 'pi pi-coffee' },
  { label: 'Cubiertos', value: 'pi pi-star' },
  
  // Transporte
  { label: 'Auto', value: 'pi pi-car' },
  { label: 'Direcciones', value: 'pi pi-directions' },
  { label: 'Mapa', value: 'pi pi-map-marker' },
  { label: 'Maleta', value: 'pi pi-briefcase' },
  { label: 'Avión', value: 'pi pi-directions' },
  
  // Finanzas
  { label: 'Dinero', value: 'pi pi-money-bill' },
  { label: 'Dólar', value: 'pi pi-dollar' },
  { label: 'Cartera', value: 'pi pi-wallet' },
  { label: 'Banco', value: 'pi pi-building' },
  { label: 'Gráfico', value: 'pi pi-chart-line' },
  { label: 'Porcentaje', value: 'pi pi-percentage' },
  
  // Trabajo y Negocio
  { label: 'Maletín', value: 'pi pi-briefcase' },
  { label: 'Usuarios', value: 'pi pi-users' },
  { label: 'Usuario', value: 'pi pi-user' },
  { label: 'ID', value: 'pi pi-id-card' },
  { label: 'Calendario', value: 'pi pi-calendar' },
  
  // Tecnología
  { label: 'Teléfono', value: 'pi pi-phone' },
  { label: 'Móvil', value: 'pi pi-mobile' },
  { label: 'Tablet', value: 'pi pi-tablet' },
  { label: 'Desktop', value: 'pi pi-desktop' },
  { label: 'Impresora', value: 'pi pi-print' },
  { label: 'Cámara', value: 'pi pi-camera' },
  { label: 'Video', value: 'pi pi-video' },
  { label: 'Imagen', value: 'pi pi-image' },
  
  // Salud y Belleza
  { label: 'Salud', value: 'pi pi-heart' },
  { label: 'Hospital', value: 'pi pi-plus' },
  { label: 'Botiquín', value: 'pi pi-plus-circle' },
  
  // Educación y Cultura
  { label: 'Libro', value: 'pi pi-book' },
  { label: 'Graduación', value: 'pi pi-bookmark' },
  { label: 'Lápiz', value: 'pi pi-pencil' },
  
  // Entretenimiento
  { label: 'TV', value: 'pi pi-desktop' },
  { label: 'Juego', value: 'pi pi-star' },
  { label: 'Regalo', value: 'pi pi-gift' },
  { label: 'Globo', value: 'pi pi-globe' },
  
  // Utilidades
  { label: 'Herramienta', value: 'pi pi-wrench' },
  { label: 'Configuración', value: 'pi pi-cog' },
  { label: 'Nube', value: 'pi pi-cloud' },
  { label: 'Descarga', value: 'pi pi-download' },
  { label: 'Subir', value: 'pi pi-upload' },
  { label: 'Papelera', value: 'pi pi-trash' },
  
  // Misceláneos
  { label: 'Varios', value: 'pi pi-ellipsis-h' },
  { label: 'Info', value: 'pi pi-info-circle' },
  { label: 'Check', value: 'pi pi-check-circle' },
  { label: 'Alerta', value: 'pi pi-exclamation-triangle' },
  { label: 'Reloj', value: 'pi pi-clock' },
  { label: 'Candado', value: 'pi pi-lock' },
  { label: 'Candado abierto', value: 'pi pi-lock-open' }
]

const colorOptions = [
  // Rojos
  '#EF4444', '#DC2626', '#F87171', '#FCA5A5', '#B91C1C',
  // Naranjas
  '#F59E0B', '#F97316', '#FDBA74', '#FB923C', '#EA580C',
  // Amarillos
  '#FBBF24', '#FDE047', '#FEF08A', '#EAB308', '#CA8A04',
  // Verdes
  '#10B981', '#059669', '#34D399', '#84CC16', '#65A30D',
  '#14B8A6', '#0D9488', '#2DD4BF',
  // Azules
  '#3B82F6', '#2563EB', '#60A5FA', '#06B6D4', '#0891B2',
  '#0EA5E9', '#38BDF8', '#0284C7',
  // Púrpuras y Rosas
  '#8B5CF6', '#7C3AED', '#A78BFA', '#6366F1', '#4F46E5',
  '#EC4899', '#DB2777', '#F472B6', '#A855F7', '#9333EA',
  // Grises y Neutros
  '#64748B', '#475569', '#94A3B8', '#1E293B', '#334155',
  '#78716C', '#57534E', '#A8A29E'
]

// Computed
const parentCategoryOptions = computed(() => {
  // Solo mostrar categorías padre (sin parent_id) del mismo tipo o 'both'
  const formType = categoryForm.value.type
  return categoryStore.categories.filter(c => {
    // Excluir la categoría que se está editando
    if (editingCategory.value && c._id === editingCategory.value._id) {
      return false
    }
    // Solo categorías principales (sin parent_id)
    if (c.parent_id) {
      return false
    }
    // Filtrar por tipo
    return c.type === formType || c.type === 'both' || formType === 'both'
  })
})

const mixedCategories = computed(() => 
  categoryStore.activeCategories.filter(c => c.type === 'both' && !c.parent_id)
)

const displayedCategories = computed(() => {
  let filtered = []
  
  if (currentType.value === 'all') {
    filtered = categoryStore.activeCategories
  } else if (currentType.value === 'expense') {
    filtered = categoryStore.categories.filter(c => 
      (c.type === 'expense' || c.type === 'both') && c.is_active
    )
  } else if (currentType.value === 'income') {
    filtered = categoryStore.categories.filter(c => 
      (c.type === 'income' || c.type === 'both') && c.is_active
    )
  } else if (currentType.value === 'both') {
    filtered = mixedCategories.value
  }
  
  // Ordenar: primero categorías padre, luego subcategorías agrupadas
  const parents = filtered.filter(c => !c.parent_id).sort((a, b) => a.name.localeCompare(b.name))
  const result = []
  
  parents.forEach(parent => {
    result.push(parent)
    const children = filtered.filter(c => c.parent_id === parent._id).sort((a, b) => a.name.localeCompare(b.name))
    result.push(...children)
  })
  
  return result
})

// Lifecycle
onMounted(async () => {
  await categoryStore.fetchCategories()
})

// Methods
const formatCategoryType = (type) => {
  switch (type) {
    case 'expense': return 'Gasto'
    case 'income': return 'Ingreso'
    case 'both': return 'Ambos'
    default: return type
  }
}

const normalizeIcon = (icon) => {
  if (!icon) return 'pi pi-tag'
  // Si el icono ya tiene el prefijo 'pi pi-', retornarlo tal cual
  if (icon.startsWith('pi pi-')) return icon
  // Si solo tiene 'pi-', agregar el prefijo 'pi '
  if (icon.startsWith('pi-')) return `pi ${icon}`
  // Si no tiene prefijo, asumir que es un nombre de clase completo
  return icon
}

const getCategoryTypeSeverity = (type) => {
  switch (type) {
    case 'expense': return 'danger'
    case 'income': return 'success'
    case 'both': return 'info'
    default: return 'secondary'
  }
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingCategory.value = null
  categoryForm.value = {
    name: '',
    type: 'expense',
    icon: 'pi pi-tag',
    color: '#64748B',
    parent_id: null,
    is_active: true
  }
}

const saveCategory = async () => {
  if (!categoryForm.value.name) {
    toast.add({
      severity: 'warn',
      summary: 'Campo requerido',
      detail: 'El nombre es obligatorio',
      life: 3000
    })
    return
  }

  try {
    if (editingCategory.value) {
      await categoryStore.updateCategory(editingCategory.value._id, categoryForm.value)
      toast.add({
        severity: 'success',
        summary: 'Categoría actualizada',
        detail: 'La categoría se actualizó correctamente',
        life: 3000
      })
    } else {
      await categoryStore.createCategory(categoryForm.value)
      toast.add({
        severity: 'success',
        summary: 'Categoría creada',
        detail: 'La categoría se creó correctamente',
        life: 3000
      })
    }
    closeDialog()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: err.response?.data?.detail || 'No se pudo guardar la categoría',
      life: 3000
    })
  }
}

const editCategory = (category) => {
  editingCategory.value = category
  categoryForm.value = {
    name: category.name,
    type: category.type,
    icon: category.icon,
    color: category.color,
    parent_id: category.parent_id || null,
    is_active: category.is_active
  }
  showCreateDialog.value = true
}

const toggleActive = async (category) => {
  try {
    await categoryStore.updateCategory(category._id, {
      ...category,
      is_active: !category.is_active
    })
    toast.add({
      severity: 'success',
      summary: category.is_active ? 'Categoría desactivada' : 'Categoría activada',
      detail: `La categoría se ${category.is_active ? 'desactivó' : 'activó'} correctamente`,
      life: 3000
    })
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo actualizar la categoría',
      life: 3000
    })
  }
}

const confirmDelete = (category) => {
  categoryToDelete.value = category
  showDeleteDialog.value = true
}

const deleteCategory = async () => {
  try {
    await categoryStore.deleteCategory(categoryToDelete.value._id)
    toast.add({
      severity: 'success',
      summary: 'Categoría eliminada',
      detail: 'La categoría se eliminó correctamente',
      life: 3000
    })
    showDeleteDialog.value = false
    categoryToDelete.value = null
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: err.response?.data?.detail || 'No se pudo eliminar la categoría',
      life: 3000
    })
  }
}
</script>

<style scoped>
.category-manager {
  width: 100%;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
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

.header-text {
  flex: 1;
}

.page-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 1rem;
  color: var(--text-color-secondary);
  font-weight: 400;
}

/* Type Tabs */
.type-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

/* States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  gap: 1rem;
  color: var(--text-color-secondary);
}

.empty-state {
  text-align: center;
  padding: 4rem 1rem;
  color: var(--text-color-secondary);
}

.empty-state i {
  font-size: 4rem;
  opacity: 0.5;
  margin-bottom: 1.5rem;
}

.empty-state h2 {
  font-size: 1.5rem;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.empty-state p {
  font-size: 1rem;
  margin-bottom: 2rem;
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

/* Categories Grid */
.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.category-card {
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.subcategory-card {
  margin-left: 2rem;
  border-left: 3px solid var(--primary-color);
  background: var(--surface-ground);
}

.subcategory-card:hover {
  border-left-color: var(--primary-color);
}

.category-content {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 0.5rem 0;
}

.category-name-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.subcategory-indicator {
  color: var(--primary-color);
  font-size: 1.25rem;
  font-weight: bold;
  margin-right: 0.25rem;
}

.category-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  color: white;
  flex-shrink: 0;
}

.category-info {
  flex: 1;
  min-width: 0;
}

.category-info h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.category-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  padding-bottom: 1rem;
}

/* Dialog */
.dialog-content {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9375rem;
}

.form-help {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  margin-top: -0.25rem;
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

.icon-option, .icon-value {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.icon-option i, .icon-value i {
  font-size: 1.25rem;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.category-option i {
  font-size: 1.25rem;
  color: var(--text-color-secondary);
}

.color-picker {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
  gap: 0.75rem;
}

.color-option {
  aspect-ratio: 1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
}

.color-option:hover {
  transform: scale(1.1);
}

.color-option.selected {
  border-color: var(--text-color);
  box-shadow: 0 0 0 2px var(--surface-card), 0 0 0 4px var(--text-color);
}

.category-preview {
  padding: 1rem;
  background: var(--surface-hover);
  border-radius: 8px;
}

.category-preview h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1rem;
}

.preview-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--surface-card);
  border-radius: 8px;
}

.preview-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  flex-shrink: 0;
}

.preview-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-name {
  font-weight: 600;
  color: var(--text-color);
}

.warning-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(251, 146, 60, 0.1);
  border-radius: 8px;
  color: #f59e0b;
  margin-top: 0.5rem;
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

  .categories-grid {
    grid-template-columns: 1fr;
  }

  .color-picker {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
