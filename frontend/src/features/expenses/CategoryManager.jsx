import { useState } from 'react'

import { createCategory } from '../../api/client.js'

/**
 * Category creation.
 *
 * Props: categories (current list), onCreated (so the parent reloads).
 */
export default function CategoryManager({ categories, onCreated }) {
  const [name, setName] = useState('')
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setSaving(true)

    try {
      await createCategory(name.trim())
      setName('')
      await onCreated()
    } catch (err) {
      // A duplicate name comes back as 409, and client.js surfaces the
      // backend's `detail` string — so this reads "Category already exists".
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="card">
      <h2>Categories</h2>

      <div className="toolbar">
        {categories.length === 0 ? (
          <span className="bar-value">None yet</span>
        ) : (
          categories.map((category) => (
            <span key={category.id} className="bar-value">
              {category.name}
            </span>
          ))
        )}
      </div>

      <form className="form" onSubmit={handleSubmit}>
        <div className="form__field">
          <label className="form__label" htmlFor="new-category">New category</label>
          <input
            id="new-category"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Groceries"
            required
          />
        </div>
        <button className="btn" type="submit" disabled={saving}>
          {saving ? 'Adding…' : 'Add category'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}
    </div>
  )
}
