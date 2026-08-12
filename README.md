# Expense Tracker

A small React + FastAPI app for recording what you spend and organising it into categories.


---

## What it does

**Expenses**
- Add an expense with a description, amount, category and date
- See everything in a table, newest first
- Filter the table to a single category
- Delete an expense
- Create new categories

**Reports** — in progress, built separately
- Totals, a per-category breakdown, monthly spend, and a CSV export

---

## Running it

You need **two terminals**, both left running. Verified on Python 3.13.7, Node 22.20.0, npm 10.9.3.
Python 3.11+ and Node 18+ should be fine.

### Terminal 1 — backend

```powershell
cd backend

# One-time: create the virtual environment
python -m venv .venv

# Activate it. Your prompt should now start with (.venv)
.\.venv\Scripts\Activate.ps1        # Windows PowerShell
# .venv\Scripts\activate.bat        # Windows cmd.exe
# source .venv/bin/activate         # macOS / Linux

# One-time
pip install -r requirements.txt
python seed.py                      # 5 categories, 30 sample expenses

# Every time
uvicorn app.main:app --reload
```

### Terminal 2 — frontend

```powershell
cd frontend
npm install                         # one-time
npm run dev                         # every time
```

Then open **<http://localhost:5173>**.

| Check | Expected |
| --- | --- |
| <http://localhost:5173> | The app |
| <http://127.0.0.1:8000/api/health> | `{"status":"ok"}` |
| <http://127.0.0.1:8000/docs> | Swagger UI for every endpoint |

The frontend calls `/api/...` on its own origin and Vite proxies it to port 8000, so the backend
must be running or every request fails. That proxy is also why there's no CORS setup anywhere.

---

## Deploying

In production FastAPI serves the built React bundle itself, so the whole app is **one process on
one port** — no separate frontend host, and no CORS to configure.

Locally you can run it exactly the way the host does:

```powershell
cd frontend; npm run build
cd ..\backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --port 8000
```

Then everything is on <http://127.0.0.1:8000> — UI at `/`, API under `/api`.

On Render (free tier), create a Web Service pointing at this repo:

- **Build:** `cd frontend && npm ci && npm run build && cd ../backend && pip install -r requirements.txt`
- **Start:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

`frontend/dist/` is gitignored — it's built on the server, never committed.

Free hosts wipe the disk on every redeploy, so `main.py` seeds the database on boot when it finds
the expenses table empty. Without that a fresh deploy would look broken rather than new.

---

## Structure

```
backend/
├── app/
│   ├── main.py                     # entry point; discovers feature routers
│   ├── core/
│   │   ├── db.py                   # sqlite3 helpers, no ORM
│   │   └── schema.sql
│   └── features/
│       └── expenses/
│           ├── router.py           # 6 endpoints + validation
│           └── service.py          # all expense SQL
├── seed.py
└── requirements.txt

frontend/
├── vite.config.js                  # dev-server proxy to the API
└── src/
    ├── App.jsx
    ├── styles.css
    ├── api/client.js               # fetch wrapper
    └── features/
        └── expenses/
            ├── ExpensesPanel.jsx   # state, table, filter
            ├── ExpenseForm.jsx     # add form
            └── CategoryManager.jsx # create categories
```

Routers are discovered rather than listed: `main.py` scans `app/features/`, so adding a feature
means adding a folder, not editing a shared file.

---

## API

| Method | Path | Returns |
| --- | --- | --- |
| `GET` | `/api/expenses` | List; optional `?category_id=` |
| `POST` | `/api/expenses` | `201` |
| `PATCH` | `/api/expenses/{id}` | `200`, or `404` |
| `DELETE` | `/api/expenses/{id}` | `204`, or `404` |
| `GET` | `/api/categories` | List |
| `POST` | `/api/categories` | `201`, or `409` on a duplicate name |

---

