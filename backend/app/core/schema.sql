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
