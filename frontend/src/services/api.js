import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : '/api',
})

// Injeta o token JWT em todas as requisições se existir
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('adp_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const getProducts = (params = {}) => api.get('/products/', { params }).then((r) => r.data)
export const getProduct = (id) => api.get(`/products/${id}`).then((r) => r.data)
export const registerClick = (id) => api.post(`/products/${id}/click`).then((r) => r.data)
export const createProduct = (data) => api.post('/products/', data).then((r) => r.data)
export const updateProduct = (id, data) => api.put(`/products/${id}`, data).then((r) => r.data)
export const deleteProduct = (id) => api.delete(`/products/${id}`).then((r) => r.data)
export const getCategories = () => api.get('/categories/').then((r) => r.data)
export const createCategory = (data) => api.post('/categories/', data).then((r) => r.data)
export const getTags = () => api.get('/tags/').then((r) => r.data)
export const createTag = (data) => api.post('/tags/', data).then((r) => r.data)
export const fetchShopeeProduct = (url) => api.get('/shopee/fetch', { params: { url } }).then((r) => r.data)
export const getSegments = () => api.get('/segments/').then((r) => r.data)
export const getSegmentCategories = (slug) => api.get(`/segments/${slug}/categories`).then((r) => r.data)

// Auth
export const login = (username, password) =>
  api.post('/auth/login', { username, password }).then((r) => r.data)
export const getMe = () => api.get('/auth/me').then((r) => r.data)
export const getUsers = () => api.get('/auth/users').then((r) => r.data)
export const createUser = (data) => api.post('/auth/users', data).then((r) => r.data)
export const deleteUser = (id) => api.delete(`/auth/users/${id}`).then((r) => r.data)
export const updateUserRole = (id, role) => api.patch(`/auth/users/${id}`, { role }).then((r) => r.data)

export default api
