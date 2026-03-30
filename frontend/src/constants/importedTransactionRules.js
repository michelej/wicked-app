const normalizeRuleText = (value) => {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9\s/-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const splitMovementLabels = (value) => {
  return String(value || '')
    .split('/')
    .map((part) => part.trim())
    .filter(Boolean)
}

const CATEGORY_RELATION_RULES = [
  {
    id: 'supermarket-merchants',
    category: 'Supermercado',
    types: ['expense'],
    matchAny: [
      'mercadona',
      'carrefour'
    ]
  },
  {
    id: 'digi-subscription',
    category: 'DIGI',
    types: ['expense'],
    matchAny: ['digi']
  },
  {
    id: 'disney-subscription',
    category: 'Disney plus',
    types: ['expense'],
    matchAny: ['disney']
  },
  {
    id: 'spotify-subscription',
    category: 'Spotify',
    types: ['expense'],
    matchAny: ['spotify']
  },
  {
    id: 'netflix-subscription',
    category: 'Netflix',
    types: ['expense'],
    matchAny: ['netflix']
  },
  {
    id: 'hbo-subscription',
    category: 'HBO',
    types: ['expense'],
    matchAny: ['hbo']
  },
  {
    id: 'alimentacion-to-chino',
    category: 'Alimentacion Chino',
    types: ['expense'],
    matchAny: ['alimentacion']
  },
  {
    id: 'salary-income',
    category: 'Salario',
    types: ['income'],
    matchAny: [
      'nomina',
      'nómina',
      'payroll'
    ]
  },
  {
    id: 'rent-expense',
    category: 'Alquiler',
    types: ['expense'],
    matchAny: ['alquiler']
  },
  {
    id: 'electricity-expense',
    category: 'Luz',
    types: ['expense'],
    matchAny: ['luz']
  },
  {
    id: 'water-expense',
    category: 'Agua',
    types: ['expense'],
    matchAny: ['agua']
  },
  {
    id: 'bizum-income',
    category: 'Otros Ingresos',
    types: ['income'],
    matchAny: [
      'bizum recibido',
      'bizum ingreso',
      'ingreso bizum'
    ]
  },
  {
    id: 'bizum-expense',
    category: 'Otros Gastos',
    types: ['expense'],
    matchAny: [
      'bizum enviado',
      'bizum pago',
      'pago bizum'
    ]
  },
  {
    id: 'amazon-prime',
    category: 'Amazon Prime',
    types: ['expense'],
    matchAny: [
      'amazon prime',
      'amazon'
    ]
  },
  {
    id: 'transport-services',
    category: 'Transporte',
    types: ['expense'],
    matchAny: [
      'uber',
      'cabify',
      'renfe',
      'metro'
    ]
  },
  {
    id: 'fuel-stations',
    category: 'Gasolina',
    types: ['expense'],
    matchAny: [
      'repsol',
      'cepsa',
      'bp'
    ]
  },
  {
    id: 'restaurant-platforms',
    category: 'Restaurante',
    types: ['expense'],
    matchAny: [
      'just eat',
      'glovo',
      'burger king',
      'mcdonalds',
      'mcdonald'
    ]
  },
  {
    id: 'transfer-relations',
    category: 'Transferido Cuentas',
    types: ['income', 'expense'],
    matchAny: [
      'transferido cuentas',
      'traspaso entre cuentas',
      'transferencia entre cuentas',
      'transferencia a cuenta',
      'transferencia desde cuenta',
      'transferencia emitida',
      'transferencia recibida'
    ]
  }
]

const importedCategoryRules = [
  {
    id: 'category-relations',
    resolve: (context) => {
      for (const relation of CATEGORY_RELATION_RULES) {
        if (relation.types?.length && !relation.types.includes(context.item.type)) {
          continue
        }

        if (relation.banks?.length && !relation.banks.includes(context.bankLabel)) {
          continue
        }

        const relationMatched = relation.matchAny.some((term) => {
          return context.searchableText.includes(normalizeRuleText(term))
        })

        if (!relationMatched) {
          continue
        }

        const category = context.categoriesByNormalizedName.get(normalizeRuleText(relation.category))
        if (category) {
          return category.name
        }
      }

      return null
    }
  },
  {
    id: 'exact-import-label-match',
    resolve: (context) => {
      for (const candidate of context.labelCandidates) {
        const category = context.categoriesByNormalizedName.get(normalizeRuleText(candidate))
        if (category) {
          return category.name
        }
      }

      return null
    }
  }
]

const buildCategoryContext = ({ item, categories, bankLabel }) => {
  const payload = item?.raw_payload || {}
  const labelCandidates = [
    payload.subcategory,
    payload.category,
    ...splitMovementLabels(item?.raw_movement),
    item?.raw_concept
  ].filter(Boolean)

  const searchableParts = [
    ...labelCandidates,
    item?.raw_observations,
    item?.comment_suggestion
  ].filter(Boolean)

  return {
    item,
    bankLabel,
    labelCandidates,
    searchableText: normalizeRuleText(searchableParts.join(' | ')),
    categoriesByNormalizedName: new Map(
      categories.map((category) => [normalizeRuleText(category.name), category])
    )
  }
}

export const findImportedTransactionCategoryMatch = ({ item, categories, bankLabel }) => {
  if (!item || !Array.isArray(categories) || categories.length === 0) {
    return null
  }

  const context = buildCategoryContext({ item, categories, bankLabel })

  for (const rule of importedCategoryRules) {
    const categoryName = rule.resolve(context)
    if (categoryName) {
      return categoryName
    }
  }

  return null
}

export const getImportedTransactionCategoryRules = () => importedCategoryRules
