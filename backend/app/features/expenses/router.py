"""Expenses API.

Paths here are relative; main.py adds the /api prefix.

    GET    /expenses          list, optional ?category_id=
    POST   /expenses          create             -> 201
    PATCH  /expenses/{id}     partial update     -> 200, or 404
    DELETE /expenses/{id}     delete             -> 204, or 404
    GET    /categories        list
    POST   /categories        create             -> 201, or 409 if duplicate

SQL lives in service.py — this file is HTTP and validation only.
"""

from datetime import date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.features.expenses import service

router = APIRouter(tags=["expenses"])


class ExpenseIn(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    amount_cents: int = Field(gt=0)
    category_id: int | None = None
    spent_on: date  # Pydantic rejects anything that isn't a real ISO date


class ExpensePatch(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=200)
    amount_cents: int | None = Field(default=None, gt=0)
    category_id: int | None = None
    spent_on: date | None = None


class ExpenseOut(BaseModel):
    id: int
    description: str
    amount_cents: int
    category_id: int | None
    category_name: str | None
    spent_on: date


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class CategoryOut(BaseModel):
    id: int
    name: str


@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(category_id: int | None = None):
    return service.list_expenses(category_id)


@router.post("/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseIn):
    if payload.category_id is not None and service.get_category(payload.category_id) is None:
        raise HTTPException(status_code=400, detail="No such category")

    return service.create_expense(
        payload.description.strip(),
        payload.amount_cents,
        payload.category_id,
        # The column is TEXT, so hand SQLite the ISO string rather than a date.
        payload.spent_on.isoformat(),
    )


@router.patch("/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, payload: ExpensePatch):
    # exclude_unset so an omitted field stays as it is, rather than being
    # overwritten with None.
    fields = payload.model_dump(exclude_unset=True)
    if isinstance(fields.get("spent_on"), date):
        fields["spent_on"] = fields["spent_on"].isoformat()

    updated = service.update_expense(expense_id, fields)
    if updated is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int):
    if not service.delete_expense(expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")


@router.get("/categories", response_model=list[CategoryOut])
def list_categories():
    return service.list_categories()


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryIn):
    created = service.create_category(payload.name.strip())
    if created is None:
        raise HTTPException(status_code=409, detail="Category already exists")
    return created
