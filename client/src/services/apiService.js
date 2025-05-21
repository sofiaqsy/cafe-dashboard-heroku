import axios from 'axios';

// Base URL para las solicitudes API
const API_URL = process.env.REACT_APP_API_URL || '/api';

// Crear instancia de axios con configuración común
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para manejo de errores global
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Aquí se podrían implementar manejo global de errores,
    // como mostrar notificaciones o redirigir a páginas de error
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Funciones para comunicarse con el backend
export const apiService = {
  // Obtener resumen general (para el dashboard principal)
  async getSummary(startDate, endDate) {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await apiClient.get('/summary', { params });
    return response.data;
  },
  
  // Obtener datos diarios (para gráficos de tendencias)
  async getDailyData(startDate, endDate) {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await apiClient.get('/daily', { params });
    return response.data;
  },
  
  // Obtener resumen de tipos de café
  async getCoffeeTypes() {
    const response = await apiClient.get('/coffee-types');
    return response.data;
  },
  
  // Obtener datos crudos de cada colección
  async getRawData(collection) {
    if (!['compras', 'ventas', 'gastos', 'proceso', 'almacen'].includes(collection)) {
      throw new Error(`Colección inválida: ${collection}`);
    }
    
    const response = await apiClient.get(`/raw/${collection}`);
    return response.data;
  }
};

// Función auxiliar para formatear fechas para la API
function formatDate(date) {
  if (!date) return null;
  
  // Asegurarse de que date sea un objeto Date
  const d = date instanceof Date ? date : new Date(date);
  
  // Formato YYYY-MM-DD
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export default apiService;
