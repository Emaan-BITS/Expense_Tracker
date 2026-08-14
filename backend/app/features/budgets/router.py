"""Budgets API.

Paths here are relative; main.py adds the /api prefix.

    GET    /budgets                 every budget
    PUT    /budgets/{category_id}   set or update one   -> 200, or 404
    DELETE /budgets/{category_id}   remove one          -> 204, or 404

PUT rather than POST because there is at most one budget per category, so the
call is idempotent — sending it twice leaves the same single row.

SQL lives in service.py.
"""

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


@router.get("", response_model=list[BudgetOut])
def list_budgets():
    return service.list_budgets()


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
