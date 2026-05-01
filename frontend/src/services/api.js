import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export const getProducts = (params = {}) =>
  api.get('/products/', { params }).then((r) => r.data)

export const getProduct = (id) =>
  api.get(`/products/${id}`).then((r) => r.data)

export const registerClick = (id) =>
  api.post(`/products/${id}/click`).then((r) => r.data)

export const createProduct = (data) =>
  api.post('/products/', data).then((r) => r.data)

export const updateProduct = (id, data) =>
  api.put(`/products/${id}`, data).then((r) => r.data)

export const deleteProduct = (id) =>
  api.delete(`/products/${id}`).then((r) => r.data)

// Categories
export const getCategories = () =>
  api.get('/categories/').then((r) => r.data)

export const createCategory = (data) =>
  api.post('/categories/', data).then((r) => r.data)

// Tags
export const getTags = () =>
  api.get('/tags/').then((r) => r.data)

export const createTag = (data) =>
  api.post('/tags/', data).then((r) => r.data)

// Shopee scraper
export const fetchShopeeProduct = (url) =>
  api.get('/shopee/fetch', { params: { url } }).then((r) => r.data)

// Segments
export const getSegments = () =>
  api.get('/segments/').then((r) => r.data)

export const getSegmentCategories = (slug) =>
  api.get(`/segments/${slug}/categories`).then((r) => r.data)

export default api

