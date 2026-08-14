"""Report queries. Read-only: SELECT and GROUP BY, never a write."""

from app.core.db import get_conn


def get_totals() -> dict:
    with get_conn() as conn:
        # COALESCE matters: SUM() over an empty table returns NULL, not 0,
        # and the frontend would render that as "NaN".
        row = conn.execute(
            "SELECT COALESCE(SUM(amount_cents), 0) AS total_cents,"
            "       COUNT(*) AS count"
            "  FROM expenses"
        ).fetchone()

    total_cents = row["total_cents"]
    count = row["count"]
    return {
        "total_cents": total_cents,
        "count": count,
        # The one place a division can blow up, so the guard lives here.
        "average_cents": round(total_cents / count) if count else 0,
    }


def get_by_category() -> list[dict]:
    """Totals per category, biggest first. Uncategorised rows group under NULL."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT e.category_id,
                   c.name AS category_name,
                   SUM(e.amount_cents) AS total_cents
              FROM expenses e
              LEFT JOIN categories c ON c.id = e.category_id
             GROUP BY e.category_id, c.name
             ORDER BY total_cents DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_monthly() -> list[dict]:
    """Totals per calendar month, oldest first.

    strftime works here only because spent_on is stored as an ISO
    'YYYY-MM-DD' string — SQLite has no real date type.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT strftime('%Y-%m', spent_on) AS month,
                   SUM(amount_cents) AS total_cents,
                   COUNT(*) AS count
              FROM expenses
             GROUP BY month
             ORDER BY month
            """
        ).fetchall()
    return [dict(row) for row in rows]


def expense_rows() -> list[dict]:
    """Every expense, flattened for the CSV export.

    Returns a list rather than yielding: the connection closes when this
    function returns, so a lazy generator would be reading from a dead cursor
    by the time the response streamed.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT e.id,
                   e.spent_on,
                   e.description,
                   COALESCE(c.name, '') AS category,
                   e.amount_cents
              FROM expenses e
              LEFT JOIN categories c ON c.id = e.category_id
             ORDER BY e.spent_on, e.id
            """
        ).fetchall()
    return [dict(row) for row in rows]
