export function useFormatters() {
  /**
   * Format a number as Euro currency
   */
  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '€0.00'
    
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount)
  }

  /**
   * Format a date string to localized format
   */
  const formatDate = (dateString, options = {}) => {
    if (!dateString) return ''
    
    const date = new Date(dateString)
    const defaultOptions = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      ...options
    }
    
    return new Intl.DateTimeFormat('es-ES', defaultOptions).format(date)
  }

  /**
   * Format a date string to include time
   */
  const formatDateTime = (dateString) => {
    return formatDate(dateString, {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  /**
   * Format a date to short format (e.g., "15 Mar")
   */
  const formatShortDate = (dateString) => {
    return formatDate(dateString, {
      day: 'numeric',
      month: 'short'
    })
  }

  /**
   * Format a date range
   */
  const formatDateRange = (startDate, endDate) => {
    return `${formatDate(startDate)} - ${formatDate(endDate)}`
  }

  /**
   * Get relative time (e.g., "hace 2 días")
   */
  const getRelativeTime = (dateString) => {
    if (!dateString) return ''
    
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return 'Hoy'
    if (diffDays === 1) return 'Ayer'
    if (diffDays < 7) return `Hace ${diffDays} días`
    if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`
    if (diffDays < 365) return `Hace ${Math.floor(diffDays / 30)} meses`
    return `Hace ${Math.floor(diffDays / 365)} años`
  }

  /**
   * Parse a number from currency string
   */
  const parseCurrency = (currencyString) => {
    if (typeof currencyString === 'number') return currencyString
    if (!currencyString) return 0
    
    // Remove currency symbol, spaces, and convert comma to dot
    const cleaned = currencyString
      .replace(/[€\s]/g, '')
      .replace(',', '.')
    
    return parseFloat(cleaned) || 0
  }

  /**
   * Format payment method to display text
   */
  const formatPaymentMethod = (method) => {
    const methods = {
      cash: 'Efectivo',
      credit: 'Crédito',
      debit: 'Débito'
    }
    return methods[method] || method
  }

  /**
   * Format transaction type to display text
   */
  const formatTransactionType = (type) => {
    const types = {
      income: 'Ingreso',
      expense: 'Egreso'
    }
    return types[type] || type
  }

  /**
   * Format frequency to display text
   */
  const formatFrequency = (frequency) => {
    const frequencies = {
      monthly: 'Mensual',
      annual: 'Anual',
      quarterly: 'Trimestral',
      'one-time': 'Único'
    }
    return frequencies[frequency] || frequency
  }

  /**
   * Format budget status to display text
   */
  const formatBudgetStatus = (status) => {
    const statuses = {
      active: 'Activo',
      closed: 'Cerrado',
      draft: 'Borrador'
    }
    return statuses[status] || status
  }

  /**
   * Get severity class for budget balance
   */
  const getBalanceSeverity = (balance) => {
    if (balance > 0) return 'success'
    if (balance === 0) return 'info'
    return 'danger'
  }

  /**
   * Get icon for transaction type
   */
  const getTransactionIcon = (type) => {
    return type === 'income' ? 'pi-arrow-down' : 'pi-arrow-up'
  }

  /**
   * Get color class for transaction type
   */
  const getTransactionColor = (type) => {
    return type === 'income' ? 'text-green-600' : 'text-red-600'
  }

  return {
    formatCurrency,
    formatDate,
    formatDateTime,
    formatShortDate,
    formatDateRange,
    getRelativeTime,
    parseCurrency,
    formatPaymentMethod,
    formatTransactionType,
    formatFrequency,
    formatBudgetStatus,
    getBalanceSeverity,
    getTransactionIcon,
    getTransactionColor
  }
}
