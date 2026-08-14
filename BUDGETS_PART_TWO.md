# Budgets — part two: spend against budget

Part one is already on `main`: you can set, list and remove a monthly limit per category. It works,
but it only shows the limit — it never tells you how much of it you've actually used.

That's part two, and it's yours.

**Everything below has been written and tested end to end.** Paste it in, rebuild, and it works.

---

## What you're building

The Budgets table currently reads:

```
Category     Monthly limit
Food              1000.00     [Remove]
Rent               500.00     [Remove]
```

After your half:

```
Category     Monthly limit    Spent      Used
Food              1000.00     10.00     [=...........]   [Remove]
Rent               500.00   2400.00     [############]   [Remove]   <- red, 480%
Holidays           400.00      0.00     [............]   [Remove]
```

## Files you touch — 1 new, 4 edited

```
frontend/src/features/budgets/BudgetProgress.jsx   NEW
backend/app/features/budgets/service.py            append one function
backend/app/features/budgets/router.py             append a model + endpoint
frontend/src/api/client.js                         append one call
frontend/src/features/budgets/BudgetsPanel.jsx     4 small edits
```

Nothing outside `features/budgets/` except the one line in `client.js`. `main.py`, `schema.sql`
and the expenses feature are untouched.

---

# ▼▼▼ PART TWO STARTS HERE ▼▼▼

## 1. `backend/app/features/budgets/service.py`

**Append to the end of the file.** Don't modify anything above it.

```python
# ===========================================================================
# PART TWO — spend against budget
# ===========================================================================


def budget_status(month: str) -> list[dict]:
    """Every budget with the amount spent against it in `month` (YYYY-MM).

    The month filter sits in the ON clause, not in WHERE. That distinction is
    the whole query: in a WHERE clause it would be applied after the join, so
    any budget with no spending this month would be filtered out entirely and
    silently vanish from the list — exactly the budgets you most want to see.
    In the ON clause it only limits which expenses attach, and the budget row
    survives with a zero.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT b.category_id,
                   c.name AS category_name,
                   b.limit_cents,
                   COALESCE(SUM(e.amount_cents), 0) AS spent_cents
              FROM budgets b
              JOIN categories c ON c.id = b.category_id
              LEFT JOIN expenses e
                     ON e.category_id = b.category_id
                    AND strftime('%Y-%m', e.spent_on) = ?
             GROUP BY b.category_id, c.name, b.limit_cents
             ORDER BY c.name
            """,
            (month,),
        ).fetchall()
    return [dict(row) for row in rows]
```

**If you read one thing in this document, make it that docstring.** Moving `AND strftime(...)` from
the `ON` clause into a `WHERE` clause turns the LEFT JOIN back into an inner join in effect, and
every budget you haven't spent against this month disappears from the screen. It looks fine in
testing because your test budgets always have spending.

`COALESCE` is the same guard the reports feature needs: `SUM` over no matching rows returns NULL,
not 0, and the frontend would render `NaN`.

## 2. `backend/app/features/budgets/router.py`

**Add the import** at the top:

```python
from datetime import date
```

**Add the response model**, just after the existing `BudgetOut`:

```python
class BudgetStatus(BudgetOut):
    spent_cents: int
    pct_used: float
```

It inherits `BudgetOut`, so it picks up `category_id`, `category_name` and `limit_cents` without
repeating them.

**Add the endpoint.** Put it directly after `list_budgets` and *before* the `/{category_id}`
routes:

```python
# ===========================================================================
# PART TWO — spend against budget
# ===========================================================================
#
# Declared before the /{category_id} routes on purpose. FastAPI matches in
# declaration order, so a literal path has to come first or a later
# path-parameter route could swallow it. Nothing here collides today, but the
# ordering is what keeps that true when someone adds GET /budgets/{id}.


@router.get("/status", response_model=list[BudgetStatus])
def budget_status():
    month = date.today().strftime("%Y-%m")
    return [
        {
            **row,
            # Guard the divide: a limit can't be zero today (the model requires
            # > 0) but this endpoint shouldn't be the thing that breaks if that
            # ever changes.
            "pct_used": (
                round(row["spent_cents"] * 100 / row["limit_cents"], 1)
                if row["limit_cents"]
                else 0.0
            ),
        }
        for row in service.budget_status(month)
    ]
```

The percentage is computed here rather than in SQL, for the same reason the reports feature does
it: you need a second value to divide by, and the guard is easier to see in Python.

## 3. `frontend/src/api/client.js`

**Append** after `deleteBudget`:

```js
// ---- part two -------------------------------------------------------------

export const getBudgetStatus = () => request('/budgets/status')
```

## 4. `frontend/src/features/budgets/BudgetProgress.jsx` — new file

```jsx
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
```

`.bar-track`, `.bar-fill` and `--danger` are already in `styles.css`. **You don't need to write any
CSS.**

## 5. `frontend/src/features/budgets/BudgetsPanel.jsx` — four edits

**a. Swap the import.** `listBudgets` becomes `getBudgetStatus`, and add `BudgetProgress`:

```jsx
import { deleteBudget, getBudgetStatus, listCategories } from '../../api/client.js'
import BudgetForm from './BudgetForm.jsx'
import BudgetProgress from './BudgetProgress.jsx'
```

**b. Change what `reload` fetches** — inside the `useCallback`:

```jsx
      setError(null)
      // part two: /status returns the same rows plus this month's spend
      setBudgets(await getBudgetStatus())
```

**c. Add two column headers**, between `Monthly limit` and the empty one:

```jsx
                <th>Category</th>
                <th className="num">Monthly limit</th>
                <th className="num">Spent</th>
                <th>Used</th>
                <th />
```

**d. Add the two matching cells**, between the limit cell and the Remove cell:

```jsx
                  <td className="num">{formatMoney(budget.limit_cents)}</td>
                  <td className="num">{formatMoney(budget.spent_cents)}</td>
                  <td>
                    <BudgetProgress pctUsed={budget.pct_used} />
                  </td>
                  <td className="num">
```

Nothing else in the file changes — the state, the delete handler and the form all stay as they are.

# ▲▲▲ PART TWO ENDS HERE ▲▲▲

---

## Check it worked

```powershell
cd frontend; npm run build
cd ..\backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --port 8000
```

Open <http://127.0.0.1:8000>, go to **Budgets**, and:

1. Set a budget on a category you've spent on — the bar fills and Spent shows a figure.
2. Set a small budget on a category with lots of spend — the bar goes full width and **red**, and
   the percentage reads over 100.
3. **The one that matters:** create a brand-new category on the Expenses tab, spend nothing on it,
   then set a budget for it. It must still appear in the list with `0.00` spent. If it's missing,
   your month filter ended up in a `WHERE` clause.

`/api/budgets/status` should return one row per budget:

```json
[{ "category_id": 1, "category_name": "Food", "limit_cents": 100000,
   "spent_cents": 1000, "pct_used": 1.0 }]
```

## Merging

Part one doesn't touch any of these lines after this point, so your push should merge cleanly.
`BudgetsPanel.jsx` is the only file where both halves have written — if git does stop there, the
resolution is to keep both sides: your new columns alongside the existing ones.
