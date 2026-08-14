import { useState } from 'react'

import BudgetsPanel from './features/budgets/BudgetsPanel'
import ExpensesPanel from './features/expenses/ExpensesPanel'

/* Features register themselves in TABS rather than being hardcoded into the
 * markup below, so adding one is a single line here and a folder under
 * src/features/. */
const TABS = [
  { id: 'expenses', label: 'Expenses', Panel: ExpensesPanel },
  { id: 'budgets', label: 'Budgets', Panel: BudgetsPanel },
]

export default function App() {
  // The ?. and ?? keep this safe if TABS is ever empty.
  const [active, setActive] = useState(TABS[0]?.id ?? null)

  const current = TABS.find((tab) => tab.id === active)
  const Panel = current?.Panel

  return (
    <div className="app">
      <h1>Expense Tracker</h1>

      <nav className="tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={tab.id === active ? 'tab tab--active' : 'tab'}
            onClick={() => setActive(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main>
        {Panel ? (
          <Panel />
        ) : (
          <p className="empty">
            No features registered yet — add yours to the <code>TABS</code> array above.
          </p>
        )}
      </main>
    </div>
  )
}
