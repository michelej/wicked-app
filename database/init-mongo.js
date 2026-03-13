// MongoDB initialization script for Finance App
// This script runs when the MongoDB container is first created

db = db.getSiblingDB('wicked_db');

// Create collections
db.createCollection('categories');
db.createCollection('budgets');
db.createCollection('transactions');
db.createCollection('budget_templates');
db.createCollection('recurring_expenses');

// Insert default categories
db.categories.insertMany([
  {
    name: 'Agua',
    type: 'expense',
    icon: 'pi-tint',
    color: '#3B82F6',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Luz',
    type: 'expense',
    icon: 'pi-bolt',
    color: '#F59E0B',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Gas',
    type: 'expense',
    icon: 'pi-fire',
    color: '#EF4444',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Internet',
    type: 'expense',
    icon: 'pi-wifi',
    color: '#8B5CF6',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Netflix',
    type: 'expense',
    icon: 'pi-play',
    color: '#E50914',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Spotify',
    type: 'expense',
    icon: 'pi-headphones',
    color: '#1DB954',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Supermercado',
    type: 'expense',
    icon: 'pi-shopping-cart',
    color: '#10B981',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Restaurante',
    type: 'expense',
    icon: 'pi-book',
    color: '#F97316',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Transporte',
    type: 'expense',
    icon: 'pi-car',
    color: '#6366F1',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Gasolina',
    type: 'expense',
    icon: 'pi-directions',
    color: '#14B8A6',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Salud',
    type: 'expense',
    icon: 'pi-heart',
    color: '#EC4899',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Gimnasio',
    type: 'expense',
    icon: 'pi-star',
    color: '#A855F7',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Ropa',
    type: 'expense',
    icon: 'pi-tag',
    color: '#F43F5E',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Educación',
    type: 'expense',
    icon: 'pi-book',
    color: '#0EA5E9',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Entretenimiento',
    type: 'expense',
    icon: 'pi-ticket',
    color: '#FB923C',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Alquiler',
    type: 'expense',
    icon: 'pi-home',
    color: '#64748B',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Teléfono',
    type: 'expense',
    icon: 'pi-phone',
    color: '#06B6D4',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Seguros',
    type: 'expense',
    icon: 'pi-shield',
    color: '#84CC16',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Salario',
    type: 'income',
    icon: 'pi-money-bill',
    color: '#22C55E',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Freelance',
    type: 'income',
    icon: 'pi-briefcase',
    color: '#3B82F6',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Inversiones',
    type: 'income',
    icon: 'pi-chart-line',
    color: '#10B981',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Otros Ingresos',
    type: 'income',
    icon: 'pi-wallet',
    color: '#8B5CF6',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Otros Gastos',
    type: 'expense',
    icon: 'pi-ellipsis-h',
    color: '#6B7280',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Varios',
    type: 'both',
    icon: 'pi-box',
    color: '#9CA3AF',
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  }
]);

// Create indexes
db.budgets.createIndex({ "start_date": 1 });
db.budgets.createIndex({ "status": 1 });
db.transactions.createIndex({ "budget_ids": 1 });
db.transactions.createIndex({ "timestamp": -1 });
db.transactions.createIndex({ "category": 1 });
db.transactions.createIndex({ "type": 1 });
db.transactions.createIndex({ "is_charged": 1 });
db.recurring_expenses.createIndex({ "is_active": 1 });
db.recurring_expenses.createIndex({ "frequency": 1 });
db.categories.createIndex({ "name": 1 }, { unique: true });
db.categories.createIndex({ "type": 1 });
db.categories.createIndex({ "is_active": 1 });

print('Database initialized successfully with default categories and indexes!');
