"""Expense queries. Every SQL statement for this feature lives here."""

import sqlite3

from app.core.db import get_conn

# LEFT JOIN, not INNER: category_id is nullable, and an inner join would
# silently hide every uncategorised expense.
SELECT_EXPENSE = """
    SELECT e.id, e.description, e.amount_cents, e.category_id,
           c.name AS category_name, e.spent_on
      FROM expenses e
      LEFT JOIN categories c ON c.id = e.category_id
"""

# Whitelist for PATCH. Column names can't be bound as SQL parameters, so the
# UPDATE below builds its SET clause by string formatting — that's only safe
# because the names can only ever come from this set. Values stay parameterised.
UPDATABLE_COLUMNS = {"description", "amount_cents", "category_id", "spent_on"}


def list_expenses(category_id: int | None = None) -> list[dict]:
    sql = SELECT_EXPENSE
    params: tuple = ()
    if category_id is not None:
        sql += " WHERE e.category_id = ?"
        params = (category_id,)
    sql += " ORDER BY e.spent_on DESC, e.id DESC"

    with get_conn() as conn:
        return [dict(row) for row in conn.execute(sql, params)]


def get_expense(expense_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(SELECT_EXPENSE + " WHERE e.id = ?", (expense_id,)).fetchone()
    return dict(row) if row else None


def create_expense(
    description: str, amount_cents: int, category_id: int | None, spent_on: str
) -> dict:
    with get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO expenses (description, amount_cents, category_id, spent_on)"
            " VALUES (?, ?, ?, ?)",
            (description, amount_cents, category_id, spent_on),
        )
        new_id = cursor.lastrowid
    # Re-read so the caller gets category_name filled in by the join.
    return get_expense(new_id)


def update_expense(expense_id: int, fields: dict) -> dict | None:
    """Returns the updated row, or None if there's no expense with that id."""
    fields = {k: v for k, v in fields.items() if k in UPDATABLE_COLUMNS}
    if not fields:
        return get_expense(expense_id)

    assignments = ", ".join(f"{column} = ?" for column in fields)
    params = [*fields.values(), expense_id]

    with get_conn() as conn:
        cursor = conn.execute(
            f"UPDATE expenses SET {assignments} WHERE id = ?", params
        )
        if cursor.rowcount == 0:
            return None
    return get_expense(expense_id)


def delete_expense(expense_id: int) -> bool:
    """True if a row was deleted, False if the id didn't exist."""
    with get_conn() as conn:
        return conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,)).rowcount > 0


def list_categories() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name FROM categories ORDER BY name")
        return [dict(row) for row in rows]


def get_category(category_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
    return dict(row) if row else None


def create_category(name: str) -> dict | None:
    """Returns the new category, or None if that name is already taken.

    The UNIQUE constraint in schema.sql does the checking — asking first and
    then inserting would leave a gap where a concurrent request could slip in.
    """
    try:
        with get_conn() as conn:
            cursor = conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            return {"id": cursor.lastrowid, "name": name}
    except sqlite3.IntegrityError:
        return None
