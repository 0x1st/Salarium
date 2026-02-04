from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class SalaryFieldCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    field_key: str = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9_]*$")
    field_type: Literal["income", "deduction"]
    category: str = Field(min_length=1, max_length=32)
    is_non_cash: bool = False
    display_order: int = 0


class SalaryFieldUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=64)
    category: Optional[str] = Field(default=None, min_length=1, max_length=32)
    is_non_cash: Optional[bool] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class SalaryFieldOut(BaseModel):
    id: int
    name: str
    field_key: str
    field_type: str
    category: str
    is_non_cash: bool
    display_order: int
    is_active: bool
    created_at: datetime


class CategoryOut(BaseModel):
    key: str
    label: str
