import { useCallback, useEffect, useState } from 'react'

import { deleteExpense, listCategories, listExpenses } from '../../api/client.js'
import CategoryManager from './CategoryManager.jsx'
import ExpenseForm from './ExpenseForm.jsx'

const formatMoney = (cents) => (cents / 100).toFixed(2)

export default function ExpensesPanel() {
  const [expenses, setExpenses] = useState([])
  const [categories, setCategories] = useState([])
  const [filter, setFilter] = useState('') // category id, or '' for all
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  // Refetching after every change is the simplest correct option at this size,
  // and it keeps the table from drifting out of step with the database.
  const reload = useCallback(async () => {
    try {
      setError(null)
      setExpenses(await listExpenses(filter || undefined))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [filter])

  const loadCategories = useCallback(async () => {
    try {
      setCategories(await listCategories())
    } catch (err) {
      setError(err.message)
    }
  }, [])

  useEffect(() => {
    loadCategories()
  }, [loadCategories])

  useEffect(() => {
    reload()
  }, [reload])

  async function handleDelete(id) {
    try {
      await deleteExpense(id)
      await reload()
    } catch (err) {
      setError(err.message)
    }
  }

  const shownTotal = expenses.reduce((sum, expense) => sum + expense.amount_cents, 0)

  return (
    <div className="panel">
      <ExpenseForm categories={categories} onCreated={reload} />

      <CategoryManager categories={categories} onCreated={loadCategories} />

      <div className="card">
        <h2>Expenses</h2>

        <div className="toolbar">
          <label className="form__label" htmlFor="category-filter">Filter</label>
          <select
            id="category-filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="">All categories</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          <span className="bar-value">
            {expenses.length} shown · {formatMoney(shownTotal)}
          </span>
        </div>

        {error && <p className="error">{error}</p>}

        {loading ? (
          <p className="loading">Loading…</p>
        ) : expenses.length === 0 ? (
          <p className="empty">No expenses here yet — add one above.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th className="num">Amount</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {expenses.map((expense) => (
                <tr key={expense.id}>
                  <td>{expense.spent_on}</td>
                  <td>{expense.description}</td>
                  <td>{expense.category_name ?? '—'}</td>
                  <td className="num">{formatMoney(expense.amount_cents)}</td>
                  <td className="num">
                    <button
                      className="btn btn--danger"
                      onClick={() => handleDelete(expense.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
