import axios from 'axios'

// Construir la URL del backend dinámicamente basada en el host actual
const getBackendURL = () => {
  // Si hay una variable de entorno, usarla
  if (import.meta.env.VITE_BACKEND_URL) {
    return import.meta.env.VITE_BACKEND_URL
  }
  
  // Si hay VITE_API_URL, usarla
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
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
