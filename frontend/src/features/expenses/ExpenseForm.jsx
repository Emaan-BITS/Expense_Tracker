import { useState } from 'react'

import { createExpense } from '../../api/client.js'

const todayISO = () => new Date().toISOString().slice(0, 10)

export default function ExpenseForm({ categories, onCreated }) {
  const [description, setDescription] = useState('')
  const [amount, setAmount] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [spentOn, setSpentOn] = useState(todayISO)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setSaving(true)

    try {
      await createExpense({
        description: description.trim(),
        // The form deals in decimals, the API in integer cents. The rounding
        // isn't optional. Plenty of ordinary prices don't survive the multiply:
        // 19.99 * 100 is 1998.9999999999998 and 0.29 * 100 is 28.999999999999996,
        // because neither value is exactly representable in binary floating
        // point. The API rejects a non-integer, and truncating instead of
        // rounding would quietly lose a cent on every one of them.
        amount_cents: Math.round(parseFloat(amount) * 100),
        category_id: categoryId ? Number(categoryId) : null,
        spent_on: spentOn,
      })
      setDescription('')
      setAmount('')
      await onCreated()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="card">
      <h2>Add an expense</h2>

      <form className="form" onSubmit={handleSubmit}>
        <div className="form__field">
          <label className="form__label" htmlFor="description">Description</label>
          <input
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Coffee"
            required
          />
        </div>

        <div className="form__field">
          <label className="form__label" htmlFor="amount">Amount</label>
          <input
            id="amount"
            type="number"
            step="0.01"
            min="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="4.50"
            required
          />
        </div>

        <div className="form__field">
          <label className="form__label" htmlFor="category">Category</label>
          <select
            id="category"
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
          >
            <option value="">Uncategorised</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form__field">
          <label className="form__label" htmlFor="spent-on">Date</label>
          <input
            id="spent-on"
            type="date"
            value={spentOn}
            onChange={(e) => setSpentOn(e.target.value)}
            required
          />
        </div>

        <button className="btn btn--primary" type="submit" disabled={saving}>
          {saving ? 'Saving…' : 'Add'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}
    </div>
  )
}
