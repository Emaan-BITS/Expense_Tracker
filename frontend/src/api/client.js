/**
 * Shared plumbing for every call below.
 *
 * The bare `/api` prefix has no host or port: the browser requests it from its
 * own origin and Vite's proxy forwards it to FastAPI. That's why there's no
 * CORS config anywhere in this project. See vite.config.js.
 */
async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!res.ok) {
    // FastAPI puts errors in a `detail` field, but don't let error handling
    // itself throw when the body isn't JSON.
    let detail = ''
    try {
      detail = (await res.json())?.detail ?? ''
    } catch {
      /* no JSON body — fall back to the status line */
    }
    throw new Error(detail || `${res.status} ${res.statusText}`)
  }

  // 204 has an empty body, and .json() would throw on it.
  return res.status === 204 ? null : res.json()
}

export const listCategories = () => request('/categories')

export const createCategory = (name) =>
  request('/categories', { method: 'POST', body: JSON.stringify({ name }) })

export const listExpenses = (categoryId) =>
  request(categoryId ? `/expenses?category_id=${categoryId}` : '/expenses')

export const createExpense = (data) =>
  request('/expenses', { method: 'POST', body: JSON.stringify(data) })

export const deleteExpense = (id) => request(`/expenses/${id}`, { method: 'DELETE' })



// No updateExpense helper here on purpose. PATCH /api/expenses/{id} exists,
// but editing isn't one of the user stories, so nothing in the UI calls it.
// Add the helper back the day you build an edit button.

export const listBudgets = () => request('/budgets')

export const setBudget = (categoryId, limitCents) =>
  request(`/budgets/${categoryId}`, {
    method: 'PUT',
    body: JSON.stringify({ limit_cents: limitCents }),
  })

export const deleteBudget = (categoryId) =>
  request(`/budgets/${categoryId}`, { method: 'DELETE' })

export const getSummary = () => request('/reports/summary')

export const getMonthly = () => request('/reports/monthly')

// A plain URL, not a request() call — this one goes straight to an <a download>
// and is fetched by the browser, so it needs the /api prefix here.
export const CSV_EXPORT_URL = '/api/reports/export.csv'
