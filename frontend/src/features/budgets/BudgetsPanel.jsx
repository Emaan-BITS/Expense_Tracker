import { useCallback, useEffect, useState } from 'react'

import { deleteBudget, getBudgetStatus, listCategories } from '../../api/client.js'
import BudgetForm from './BudgetForm.jsx'
import BudgetProgress from './BudgetProgress.jsx'

const formatMoney = (cents) => (cents / 100).toFixed(2)

export default function BudgetsPanel() {
  const [budgets, setBudgets] = useState([])
  const [categories, setCategories] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const reload = useCallback(async () => {
    try {
      setError(null)
      // part two: /status returns the same rows plus this month's spend
      setBudgets(await getBudgetStatus())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    listCategories().then(setCategories).catch((err) => setError(err.message))
    reload()
  }, [reload])

  async function handleDelete(categoryId) {
    try {
      await deleteBudget(categoryId)
      await reload()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="panel">
      <BudgetForm categories={categories} onSaved={reload} />

      <div className="card">
        <h2>Budgets</h2>

        {error && <p className="error">{error}</p>}

        {loading ? (
          <p className="loading">Loading…</p>
        ) : budgets.length === 0 ? (
          <p className="empty">No budgets set yet — add one above.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Category</th>
                <th className="num">Monthly limit</th>
                <th className="num">Spent</th>
                <th>Used</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {budgets.map((budget) => (
                <tr key={budget.category_id}>
                  <td>{budget.category_name}</td>
                  <td className="num">{formatMoney(budget.limit_cents)}</td>
                  <td className="num">{formatMoney(budget.spent_cents)}</td>
                  <td>
                    <BudgetProgress pctUsed={budget.pct_used} />
                  </td>
                  <td className="num">
                    <button
                      className="btn btn--danger"
                      onClick={() => handleDelete(budget.category_id)}
                    >
                      Remove
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
