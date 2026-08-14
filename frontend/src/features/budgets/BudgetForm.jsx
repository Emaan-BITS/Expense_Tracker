import { useState } from 'react'

import { setBudget } from '../../api/client.js'

export default function BudgetForm({ categories, onSaved }) {
  const [categoryId, setCategoryId] = useState('')
  const [amount, setAmount] = useState('')
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setSaving(true)

    try {
      // Same conversion as the expense form: the user types decimals, the API
      // stores integer cents, and Math.round is what stops 19.99 arriving as
      // 1998.9999999999998.
      await setBudget(Number(categoryId), Math.round(parseFloat(amount) * 100))
      setAmount('')
      await onSaved()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="card">
      <h2>Set a budget</h2>

      <form className="form" onSubmit={handleSubmit}>
        <div className="form__field">
          <label className="form__label" htmlFor="budget-category">Category</label>
          <select
            id="budget-category"
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            required
          >
            <option value="">Choose one</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form__field">
          <label className="form__label" htmlFor="budget-amount">Monthly limit</label>
          <input
            id="budget-amount"
            type="number"
            step="0.01"
            min="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="250.00"
            required
          />
        </div>

        <button className="btn btn--primary" type="submit" disabled={saving}>
          {saving ? 'Saving…' : 'Save'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}
    </div>
  )
}
