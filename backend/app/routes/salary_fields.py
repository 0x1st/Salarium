from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..models import SalaryField, INCOME_CATEGORIES, DEDUCTION_CATEGORIES, ALL_CATEGORIES
from ..schemas.salary_field import (
    SalaryFieldCreate,
    SalaryFieldUpdate,
    SalaryFieldOut,
    CategoryOut,
)
from ..utils.auth import get_current_user


router = APIRouter()


@router.get("/categories")
async def list_categories():
    """List all available categories for income and deduction fields."""
    return {
        "income": [CategoryOut(key=k, label=v) for k, v in INCOME_CATEGORIES],
        "deduction": [CategoryOut(key=k, label=v) for k, v in DEDUCTION_CATEGORIES],
    }


@router.get("/", response_model=List[SalaryFieldOut])
async def list_salary_fields(
    field_type: str = None,
    include_inactive: bool = False,
    user=Depends(get_current_user),
):
    """List all salary field definitions for the current user."""
    filters = {"user_id": user.id}
    if field_type:
        filters["field_type"] = field_type
    if not include_inactive:
        filters["is_active"] = True

    fields = await SalaryField.filter(**filters).order_by("display_order", "id").all()
    return [
        SalaryFieldOut(
            id=f.id,
            name=f.name,
            field_key=f.field_key,
            field_type=f.field_type,
            category=f.category,
            is_non_cash=f.is_non_cash,
            display_order=f.display_order,
            is_active=f.is_active,
            created_at=f.created_at,
        )
        for f in fields
    ]


@router.post("/", response_model=SalaryFieldOut)
async def create_salary_field(
    payload: SalaryFieldCreate, user=Depends(get_current_user)
):
    """Create a new salary field definition."""
    # Validate category
    valid_categories = [c[0] for c in ALL_CATEGORIES.get(payload.field_type, [])]
    if payload.category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"无效的类别 '{payload.category}'，有效类别: {valid_categories}",
        )

    # Check for duplicate field_key
    existing = await SalaryField.filter(
        user_id=user.id, field_key=payload.field_key
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"字段标识 '{payload.field_key}' 已存在")

    f = await SalaryField.create(
        user_id=user.id,
        name=payload.name,
        field_key=payload.field_key,
        field_type=payload.field_type,
        category=payload.category,
        is_non_cash=payload.is_non_cash,
        display_order=payload.display_order,
    )
    return SalaryFieldOut(
        id=f.id,
        name=f.name,
        field_key=f.field_key,
        field_type=f.field_type,
        category=f.category,
        is_non_cash=f.is_non_cash,
        display_order=f.display_order,
        is_active=f.is_active,
        created_at=f.created_at,
    )


@router.put("/{field_id}", response_model=SalaryFieldOut)
async def update_salary_field(
    field_id: int, payload: SalaryFieldUpdate, user=Depends(get_current_user)
):
    """Update a salary field definition."""
    f = await SalaryField.filter(id=field_id, user_id=user.id).first()
    if not f:
        raise HTTPException(status_code=404, detail="字段不存在")

    if payload.name is not None:
        f.name = payload.name
    if payload.category is not None:
        valid_categories = [c[0] for c in ALL_CATEGORIES.get(f.field_type, [])]
        if payload.category not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"无效的类别 '{payload.category}'，有效类别: {valid_categories}",
            )
        f.category = payload.category
    if payload.is_non_cash is not None:
        f.is_non_cash = payload.is_non_cash
    if payload.display_order is not None:
        f.display_order = payload.display_order
    if payload.is_active is not None:
        f.is_active = payload.is_active

    await f.save()
    return SalaryFieldOut(
        id=f.id,
        name=f.name,
        field_key=f.field_key,
        field_type=f.field_type,
        category=f.category,
        is_non_cash=f.is_non_cash,
        display_order=f.display_order,
        is_active=f.is_active,
        created_at=f.created_at,
    )


@router.delete("/{field_id}")
async def delete_salary_field(field_id: int, user=Depends(get_current_user)):
    """Soft delete a salary field (set is_active=False)."""
    f = await SalaryField.filter(id=field_id, user_id=user.id).first()
    if not f:
        raise HTTPException(status_code=404, detail="字段不存在")

    f.is_active = False
    await f.save()
    return {"ok": True}
