// Small helper layer for talking to the Django API.
//
// In development the Vite dev server proxies /api to Django (see vite.config.js).
// For a deployed frontend, set VITE_API_URL to the backend's API address,
// for example: VITE_API_URL=https://my-backend.example.com/api
const API_BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

export class ApiError extends Error {
  constructor(status, data) {
    super(`API request failed with status ${status}`)
    this.name = 'ApiError'
    this.status = status
    // For 400 responses this is the field-error object sent by DRF,
    // e.g. { duration: ['Ensure this value is greater than or equal to 1.'] }
    this.data = data
  }
}

async function request(path, { method = 'GET', body, params } = {}) {
  const query = params
    ? '?' + new URLSearchParams(
        Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== ''),
      )
    : ''

  const response = await fetch(`${API_BASE_URL}${path}${query}`, {
    method,
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  // DELETE returns 204 with no body.
  const data = response.status === 204 ? null : await response.json().catch(() => null)

  if (!response.ok) {
    throw new ApiError(response.status, data)
  }
  return data
}

// Categories
export const getCategories = () => request('/categories/')
export const createCategory = (category) => request('/categories/', { method: 'POST', body: category })

// Entries. Filters: { date, from, to, category } (dates as YYYY-MM-DD)
export const getEntries = (filters) => request('/entries/', { params: filters })
export const createEntry = (entry) => request('/entries/', { method: 'POST', body: entry })
export const updateEntry = (id, changes) => request(`/entries/${id}/`, { method: 'PATCH', body: changes })
export const deleteEntry = (id) => request(`/entries/${id}/`, { method: 'DELETE' })
