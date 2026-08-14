-- The whole data model. Two tables, one optional relationship.

CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS expenses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    description  TEXT    NOT NULL,

    -- Money is cents, stored as INTEGER. A REAL column can't hold 0.10
    -- exactly, and that error compounds as soon as you start summing rows.
    amount_cents INTEGER NOT NULL,

    category_id  INTEGER REFERENCES categories(id),

    -- ISO 'YYYY-MM-DD'. SQLite has no date type; this format sorts correctly
    -- as text and works with strftime().
    spent_on     TEXT    NOT NULL,

    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category_id);
CREATE INDEX IF NOT EXISTS idx_expenses_spent_on ON expenses(spent_on);

-- One monthly spending limit per category. category_id is the PRIMARY KEY
-- rather than a plain column, which is what enforces "at most one budget per
-- category" and lets the write be a single upsert instead of a check-then-write.
CREATE TABLE IF NOT EXISTS budgets (
    category_id INTEGER PRIMARY KEY REFERENCES categories(id),
    limit_cents INTEGER NOT NULL
);
