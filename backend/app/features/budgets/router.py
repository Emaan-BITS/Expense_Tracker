"""Budgets API.

Paths here are relative; main.py adds the /api prefix.

    GET    /budgets                 every budget
    GET    /budgets/status          every budget + this month's spend
    PUT    /budgets/{category_id}   set or update one   -> 200, or 404
    DELETE /budgets/{category_id}   remove one          -> 204, or 404

PUT rather than POST because there is at most one budget per category, so the
call is idempotent — sending it twice leaves the same single row.

SQL lives in service.py.
"""

from datetime import date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.features.budgets import service

router = APIRouter(prefix="/budgets", tags=["budgets"])


class BudgetIn(BaseModel):
    limit_cents: int = Field(gt=0)


class BudgetOut(BaseModel):
    category_id: int
    category_name: str
    limit_cents: int


class BudgetStatus(BudgetOut):
    spent_cents: int
    pct_used: float


@router.get("", response_model=list[BudgetOut])
def list_budgets():
    return service.list_budgets()


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


@router.put("/{category_id}", response_model=BudgetOut)
def set_budget(category_id: int, payload: BudgetIn):
    saved = service.set_budget(category_id, payload.limit_cents)
    if saved is None:
        raise HTTPException(status_code=404, detail="No such category")
    return saved


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(category_id: int):
    if not service.delete_budget(category_id):
        raise HTTPException(status_code=404, detail="No budget for that category")
