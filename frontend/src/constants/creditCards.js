export const CREDIT_CARD_OPTIONS = [
  {
    label: 'ING Direct',
    value: 'ING Direct',
    issuerBank: 'ING Direct',
    logoText: 'ING',
    shortLabel: 'ING',
    accent: '#f97316',
    accentSoft: '#fdba74',
    surface: 'linear-gradient(135deg, #f97316 0%, #fb923c 100%)',
    shadow: 'rgba(249, 115, 22, 0.22)',
    glow: 'rgba(251, 146, 60, 0.2)',
    pillBackground: 'rgba(249, 115, 22, 0.14)',
    pillColor: '#c2410c',
    description: 'Tarjeta principal para centralizar compras y movimientos financiados.',
    displayName: 'ING Direct',
    maskedNumber: '**** 4821'
  }
]

const DEFAULT_CREDIT_CARD = {
  label: 'Tarjeta',
  value: 'Tarjeta',
  issuerBank: 'Tarjeta',
  logoText: 'CARD',
  shortLabel: 'CARD',
  accent: '#475569',
  accentSoft: '#94a3b8',
  surface: 'linear-gradient(135deg, #334155 0%, #64748b 100%)',
  shadow: 'rgba(71, 85, 105, 0.22)',
  glow: 'rgba(148, 163, 184, 0.18)',
  pillBackground: 'rgba(71, 85, 105, 0.12)',
  pillColor: '#334155',
  description: 'Tarjeta de credito',
  displayName: 'Tarjeta de credito',
  maskedNumber: '****'
}

export const getCreditCardBrand = (card) => {
  if (!card) {
    return DEFAULT_CREDIT_CARD
  }

  return CREDIT_CARD_OPTIONS.find((item) => item.value === card) || {
    ...DEFAULT_CREDIT_CARD,
    label: card,
    value: card,
    issuerBank: card,
    displayName: card,
    shortLabel: card.slice(0, 3).toUpperCase(),
    logoText: card.slice(0, 4).toUpperCase()
  }
}
