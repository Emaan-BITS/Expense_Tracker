"""Reports API.

This router sets its own /reports prefix and main.py adds /api on top.

    GET /reports/summary       totals plus a per-category breakdown
    GET /reports/monthly       totals per calendar month
    GET /reports/export.csv    every expense, as a download

Everything here is read-only. SQL lives in service.py.
"""

import csv
import io

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.features.reports import service

router = APIRouter(prefix="/reports", tags=["reports"])


class CategoryTotal(BaseModel):
    category_id: int | None
    category_name: str | None
    total_cents: int
    pct: float


class Summary(BaseModel):
    total_cents: int
    count: int
    average_cents: int
    by_category: list[CategoryTotal]


class MonthTotal(BaseModel):
    month: str
    total_cents: int
    count: int


@router.get("/summary", response_model=Summary)
def summary():
    totals = service.get_totals()
    grand_total = totals["total_cents"]

    by_category = [
        {
            **row,
            # An empty database gives a grand total of 0, so guard the divide.
            "pct": round(row["total_cents"] * 100 / grand_total, 1) if grand_total else 0.0,
        }
        for row in service.get_by_category()
    ]

    return {**totals, "by_category": by_category}


@router.get("/monthly", response_model=list[MonthTotal])
def monthly():
    return service.get_monthly()


@router.get("/export.csv")
def export_csv():
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "spent_on", "description", "category", "amount"])

    for row in service.expense_rows():
        writer.writerow(
            [
                row["id"],
                row["spent_on"],
                row["description"],
                row["category"],
                # Decimals here, not cents — a person is going to open this
                # in a spreadsheet.
                f"{row['amount_cents'] / 100:.2f}",
            ]
        )

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"},
    )
