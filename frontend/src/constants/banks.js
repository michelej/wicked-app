export const BUDGET_BANK_OPTIONS = [
  { label: 'BBVA', value: 'BBVA', shortLabel: 'BBVA' },
  { label: 'ING Direct', value: 'ING Direct', shortLabel: 'ING' }
]

const DEFAULT_BANK_BRAND = {
  key: 'default',
  label: 'Sin banco',
  shortLabel: 'N/A',
  logoText: 'BANK',
  accent: '#64748b',
  accentSoft: '#cbd5e1',
  surface: 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)',
  shadow: 'rgba(100, 116, 139, 0.2)',
  glow: 'rgba(148, 163, 184, 0.2)',
  pillBackground: 'rgba(100, 116, 139, 0.12)',
  pillColor: '#475569'
}

const BANK_BRANDS = {
  BBVA: {
    key: 'bbva',
    label: 'BBVA',
    shortLabel: 'BBVA',
    logoText: 'BBVA',
    accent: '#0a4abf',
    accentSoft: '#8ac7ff',
    surface: 'linear-gradient(135deg, #0a4abf 0%, #34a3ff 100%)',
    shadow: 'rgba(10, 74, 191, 0.22)',
    glow: 'rgba(52, 163, 255, 0.18)',
    pillBackground: 'rgba(10, 74, 191, 0.1)',
    pillColor: '#0a3b97'
  },
  'ING Direct': {
    key: 'ing-direct',
    label: 'ING Direct',
    shortLabel: 'ING',
    logoText: 'ING',
    accent: '#f97316',
    accentSoft: '#fdba74',
    surface: 'linear-gradient(135deg, #f97316 0%, #fb923c 100%)',
    shadow: 'rgba(249, 115, 22, 0.22)',
    glow: 'rgba(251, 146, 60, 0.2)',
    pillBackground: 'rgba(249, 115, 22, 0.12)',
    pillColor: '#c2410c'
  }
}

export const getBankBrand = (bank) => {
  if (!bank) {
    return DEFAULT_BANK_BRAND
  }

  return BANK_BRANDS[bank] || {
    ...DEFAULT_BANK_BRAND,
    label: bank,
    shortLabel: bank.slice(0, 3).toUpperCase(),
    logoText: bank.slice(0, 4).toUpperCase()
  }
}

export const formatBudgetOptionLabel = (budget) => {
  if (!budget?.bank) {
    return budget?.name || 'Presupuesto'
  }

  return `${budget.name} - ${budget.bank}`
}
