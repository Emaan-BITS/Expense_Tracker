const formatMoney = (cents) => (cents / 100).toFixed(2)

export default function SummaryCards({ summary }) {
  if (!summary) return null

  return (
    <>
      <div className="stat-grid">
        <div className="stat">
          <p className="stat__label">Total</p>
          <p className="stat__value">{formatMoney(summary.total_cents)}</p>
        </div>
        <div className="stat">
          <p className="stat__label">Expenses</p>
          <p className="stat__value">{summary.count}</p>
        </div>
        <div className="stat">
          <p className="stat__label">Average</p>
          <p className="stat__value">{formatMoney(summary.average_cents)}</p>
        </div>
      </div>

      <div className="card">
        <h2>By category</h2>

        {summary.by_category.length === 0 ? (
          <p className="empty">Nothing to report yet.</p>
        ) : (
          <div className="stack">
            {/* Already sorted by the backend — don't re-sort here, or there
                are two places deciding the order. */}
            {summary.by_category.map((row) => (
              <div className="bar-row" key={row.category_id ?? 'uncategorised'}>
                <span className="bar-label">
                  {row.category_name ?? 'Uncategorised'}
                </span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${row.pct}%` }} />
                </div>
                <span className="bar-value">{formatMoney(row.total_cents)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}
