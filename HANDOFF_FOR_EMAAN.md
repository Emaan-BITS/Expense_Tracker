# Adding the reports feature

Everything the reports feature needs already exists in the repo — the database schema, the
connection helper, the shared stylesheet, and the router auto-discovery. You're filling in files,
not wiring up plumbing.

## Setup

```powershell
git clone <repo-url>
cd <repo>

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py                 # 5 categories, 30 sample expenses
uvicorn app.main:app --reload  # leave running

# second terminal
cd frontend
npm install
npm run dev                    # leave running
```

Open <http://localhost:5173>. You should see one tab, **Expenses**, working.

## Files to add — 5 new, 2 shared

### New (nobody else touches these)

```
backend/app/features/reports/__init__.py        empty file, makes it a package
backend/app/features/reports/router.py          3 endpoints
backend/app/features/reports/service.py         the SQL
frontend/src/features/reports/ReportsPanel.jsx  fetching + layout
frontend/src/features/reports/SummaryCards.jsx  stat tiles + bars
```

### Shared (2 small edits)

**`frontend/src/api/client.js`** — append:

```js
export const getSummary = () => request('/reports/summary')

export const getMonthly = () => request('/reports/monthly')

// A plain URL, not a request() call — this one goes straight to an <a download>
// and is fetched by the browser, so it needs the /api prefix here.
export const CSV_EXPORT_URL = '/api/reports/export.csv'
```

**`frontend/src/App.jsx`** — one import, one array entry:

```jsx
import ReportsPanel from './features/reports/ReportsPanel'

const TABS = [
  { id: 'expenses', label: 'Expenses', Panel: ExpensesPanel },
  { id: 'reports', label: 'Reports', Panel: ReportsPanel },   // <- add this
]
```

**`backend/app/main.py` needs no change at all.** It scans `app/features/` and mounts whatever it
finds, so your router registers itself the moment the folder exists.

## Things already done for you

- **The CSS is in the repo.** `styles.css` already has `.stat-grid`, `.stat`, `.stat__label`,
  `.stat__value`, `.bar-row`, `.bar-label`, `.bar-track`, `.bar-fill` and `.stack`. Use those class
  names and it'll look right with no CSS from you.
- **`get_conn()`** in `app/core/db.py` gives a connection that commits, rolls back on error, and
  closes. Use `with get_conn() as conn:`.
- **Rows behave like dicts** — `row["total_cents"]`, not `row[2]`.

## Four things that will bite you

1. **`SUM()` over an empty table returns NULL, not 0.** Wrap it: `COALESCE(SUM(amount_cents), 0)`.
   Otherwise the frontend renders `NaN`.
2. **Guard the divisions.** Average is `total / count` and percentage is `total / grand_total` —
   both blow up on an empty database.
3. **Use `LEFT JOIN` onto categories.** `category_id` is nullable, so an inner join silently drops
   uncategorised expenses and your category totals won't add up to the grand total.
4. **Money is integer cents everywhere.** 19.99 is stored as 1999. Only divide by 100 at the point
   of display. The CSV export is the exception — write decimals there, since a person opens it in a
   spreadsheet.

## API shape the frontend expects

```
GET /api/reports/summary
{ "total_cents": 577788, "count": 30, "average_cents": 19260,
  "by_category": [ { "category_id": 3, "category_name": "Rent",
                     "total_cents": 480000, "pct": 83.1 }, ... ] }

GET /api/reports/monthly
[ { "month": "2026-06", "total_cents": 61000, "count": 10 }, ... ]

GET /api/reports/export.csv
text/csv, header: Content-Disposition: attachment; filename=expenses.csv
columns: id,spent_on,description,category,amount
```

`spent_on` is stored as an ISO `YYYY-MM-DD` string, so `strftime('%Y-%m', spent_on)` works for the
monthly grouping and plain text ordering sorts chronologically.

## Before you push

```powershell
cd frontend; npm run build
cd ..\backend; uvicorn app.main:app --port 8000
```

Open <http://127.0.0.1:8000> — that's how it runs in production, one port serving both the API and
the UI. Check both tabs work and the browser console is clean.

Then push to `main`. Nothing on the expenses side touches your files, and the two lines you add to
`App.jsx` and `client.js` are in places nobody else is editing, so it should merge cleanly.
