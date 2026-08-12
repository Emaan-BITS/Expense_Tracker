import { useEffect, useState } from 'react'

import { CSV_EXPORT_URL, getMonthly, getSummary } from '../../api/client.js'
import SummaryCards from './SummaryCards.jsx'

const formatMoney = (cents) => (cents / 100).toFixed(2)

export default function ReportsPanel() {
  const [summary, setSummary] = useState(null)
  const [monthly, setMonthly] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  // Switching tabs unmounts this component, so coming back here refetches —
  // which is why the totals pick up anything added on the Expenses tab.
  useEffect(() => {
    Promise.all([getSummary(), getMonthly()])
      .then(([summaryData, monthlyData]) => {
        setSummary(summaryData)
        setMonthly(monthlyData)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="loading">Loading…</p>
  if (error) return <p className="error">{error}</p>

  return (
    <div className="panel">
      <SummaryCards summary={summary} />

      <div className="card">
        <h2>By month</h2>

        {monthly.length === 0 ? (
          <p className="empty">No expenses recorded yet.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Month</th>
                <th className="num">Expenses</th>
                <th className="num">Total</th>
              </tr>
            </thead>
            <tbody>
              {monthly.map((month) => (
                <tr key={month.month}>
                  <td>{month.month}</td>
                  <td className="num">{month.count}</td>
                  <td className="num">{formatMoney(month.total_cents)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="toolbar">
        {/* A plain link, not a fetch-and-Blob dance. The browser already
            handles Content-Disposition: attachment. */}
        <a className="btn btn--primary" href={CSV_EXPORT_URL} download>
          Export CSV
        </a>
      </div>
    </div>
  )
}
