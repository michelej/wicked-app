import axios from 'axios'

const getPublicApiURL = () => {
  const configuredApiUrl = import.meta.env.VITE_API_URL?.trim()
  return configuredApiUrl || null
}

// Construir la URL del backend dinámicamente basada en el host actual
const getBackendURL = () => {
  // Si hay una URL publica configurada, usarla
  const publicApiUrl = getPublicApiURL()
  if (publicApiUrl) {
    return publicApiUrl
  }

  // En desarrollo, usar el proxy de Vite (/api)
  if (import.meta.env.DEV) {
    return ''
  }
  
  // En producción, usar el hostname actual con puerto 8000
  const protocol = window.location.protocol
  const hostname = window.location.hostname
  return `${protocol}//${hostname}:8000`
}

const apiClient = axios.create({
  baseURL: getBackendURL(),
  headers: {
    'Content-Type': 'application/json'
  }
})

export default apiClient
