/**
 * One progress bar, sized from the data.
 *
 * The width is capped at 100% so an overspend doesn't push the fill outside
 * its track, and the colour flips to the danger token instead — the number
 * beside it still shows the true figure.
 */
export default function BudgetProgress({ pctUsed }) {
  const over = pctUsed > 100

  return (
    <div className="bar-track" title={`${pctUsed}% used`}>
      <div
        className="bar-fill"
        style={{
          width: `${Math.min(pctUsed, 100)}%`,
          background: over ? 'var(--danger)' : undefined,
        }}
      />
    </div>
  )
}
