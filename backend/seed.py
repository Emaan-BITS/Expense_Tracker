"""Sample data, so there's something in the table to work against.

Run once from the backend/ directory:

    python seed.py

The random seed is fixed, so every run produces the same rows and the numbers
are reproducible. Only the dates move, since they're relative to today.
"""

import random
from datetime import date, timedelta

from app.core.db import get_conn, init_db

random.seed(42)

CATEGORIES = ["Food", "Transport", "Rent", "Entertainment", "Utilities"]

DESCRIPTIONS = {
    "Food": ["Groceries", "Coffee", "Lunch", "Takeaway", "Bakery"],
    "Transport": ["Bus pass", "Fuel", "Cab ride", "Train ticket"],
    "Rent": ["Monthly rent"],
    "Entertainment": ["Cinema", "Concert", "Streaming subscription", "Books"],
    "Utilities": ["Electricity", "Internet", "Water", "Mobile bill"],
}

# In cents. Rent is fixed and large so one category clearly dominates —
# otherwise the sorted bar chart is five equal bars and you can't tell whether
# the sorting works.
AMOUNT_RANGES = {
    "Food": (300, 6_000),
    "Transport": (500, 4_000),
    "Rent": (80_000, 80_000),
    "Entertainment": (800, 5_000),
    "Utilities": (1_500, 9_000),
}

EXPENSE_COUNT = 30
DAYS_OF_HISTORY = 90  # about 3 months, so the monthly report has real buckets


def seed() -> None:
    init_db()

    with get_conn() as conn:
        # Start clean so re-running doesn't stack up duplicates.
        conn.execute("DELETE FROM expenses")
        conn.execute("DELETE FROM categories")

        category_ids = {}
        for name in CATEGORIES:
            cursor = conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            category_ids[name] = cursor.lastrowid

        today = date.today()
        rows = []
        for _ in range(EXPENSE_COUNT):
            name = random.choice(CATEGORIES)
            low, high = AMOUNT_RANGES[name]
            rows.append(
                (
                    random.choice(DESCRIPTIONS[name]),
                    random.randint(low, high),
                    category_ids[name],
                    (today - timedelta(days=random.randrange(DAYS_OF_HISTORY))).isoformat(),
                )
            )

        conn.executemany(
            "INSERT INTO expenses (description, amount_cents, category_id, spent_on)"
            " VALUES (?, ?, ?, ?)",
            rows,
        )

    total = sum(row[1] for row in rows)
    print(f"Seeded {len(CATEGORIES)} categories and {len(rows)} expenses.")
    print(f"Total spend: {total / 100:.2f}  (total_cents = {total})")


if __name__ == "__main__":
    seed()
