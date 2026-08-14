"""Budget queries. One budget per category, stored as integer cents."""

from app.core.db import get_conn

# Budgets are meaningless without the category name, and a budget can only
# exist for a category that exists, so this is a plain INNER JOIN — unlike the
# expenses queries, where the category is optional.
SELECT_BUDGET = """
    SELECT b.category_id, c.name AS category_name, b.limit_cents
      FROM budgets b
      JOIN categories c ON c.id = b.category_id
"""


def list_budgets() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(SELECT_BUDGET + " ORDER BY c.name").fetchall()
    return [dict(row) for row in rows]


def get_budget(category_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            SELECT_BUDGET + " WHERE b.category_id = ?", (category_id,)
        ).fetchone()
    return dict(row) if row else None


def set_budget(category_id: int, limit_cents: int) -> dict | None:
    """Create or update a budget. None if there's no category with that id."""
    with get_conn() as conn:
        exists = conn.execute(
            "SELECT 1 FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        if exists is None:
            return None

        # An upsert, because "set the budget for Food" should work whether or
        # not one already exists. The ON CONFLICT target is the primary key.
        conn.execute(
            "INSERT INTO budgets (category_id, limit_cents) VALUES (?, ?)"
            " ON CONFLICT(category_id) DO UPDATE SET limit_cents = excluded.limit_cents",
            (category_id, limit_cents),
        )

    return get_budget(category_id)


def delete_budget(category_id: int) -> bool:
    """True if a budget was removed, False if there wasn't one."""
    with get_conn() as conn:
        return (
            conn.execute(
                "DELETE FROM budgets WHERE category_id = ?", (category_id,)
            ).rowcount
            > 0
        )
