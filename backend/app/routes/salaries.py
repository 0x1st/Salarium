from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from ..models import SalaryRecord, Person, SalaryField, CustomSalaryValue
from ..schemas.salary import SalaryCreate, SalaryUpdate, SalaryOut
from ..services.payroll import compute_payroll
from ..utils.auth import get_current_user


router = APIRouter()


async def get_custom_fields_for_record(record_id: int) -> dict:
    """Load custom field values for a salary record."""
    values = await CustomSalaryValue.filter(salary_record_id=record_id).prefetch_related(
        "salary_field"
    ).all()
    return {v.salary_field.field_key: float(v.amount) for v in values}


async def get_custom_fields_for_payroll(record_id: int) -> list:
    """Load custom field info for payroll calculation."""
    values = await CustomSalaryValue.filter(salary_record_id=record_id).prefetch_related(
        "salary_field"
    ).all()
    return [
        {
            "field_type": v.salary_field.field_type,
            "is_non_cash": v.salary_field.is_non_cash,
            "amount": float(v.amount),
        }
        for v in values
    ]


async def save_custom_fields(
    record_id: int, user_id: int, custom_fields: dict
) -> None:
    """Save custom field values for a salary record."""
    if not custom_fields:
        return

    # Get user's field definitions
    field_defs = await SalaryField.filter(user_id=user_id, is_active=True).all()
    field_map = {f.field_key: f for f in field_defs}

    # Delete existing custom values for this record
    await CustomSalaryValue.filter(salary_record_id=record_id).delete()

    # Create new custom values
    for field_key, amount in custom_fields.items():
        if field_key in field_map and amount != 0:
            await CustomSalaryValue.create(
                salary_record_id=record_id,
                salary_field_id=field_map[field_key].id,
                amount=amount,
            )


async def to_out(rec: SalaryRecord) -> SalaryOut:
    custom_fields_data = await get_custom_fields_for_record(rec.id)
    custom_fields_payroll = await get_custom_fields_for_payroll(rec.id)

    data = compute_payroll(
        base_salary=rec.base_salary,
        performance_salary=rec.performance_salary,
        high_temp_allowance=rec.high_temp_allowance,
        low_temp_allowance=rec.low_temp_allowance,
        computer_allowance=rec.computer_allowance,
        communication_allowance=rec.communication_allowance,
        meal_allowance=rec.meal_allowance,
        mid_autumn_benefit=rec.mid_autumn_benefit,
        dragon_boat_benefit=rec.dragon_boat_benefit,
        spring_festival_benefit=rec.spring_festival_benefit,
        other_income=rec.other_income,
        comprehensive_allowance=rec.comprehensive_allowance,
        pension_insurance=rec.pension_insurance,
        medical_insurance=rec.medical_insurance,
        unemployment_insurance=rec.unemployment_insurance,
        critical_illness_insurance=rec.critical_illness_insurance,
        enterprise_annuity=rec.enterprise_annuity,
        housing_fund=rec.housing_fund,
        other_deductions=rec.other_deductions,
        labor_union_fee=rec.labor_union_fee,
        performance_deduction=rec.performance_deduction,
        tax=rec.tax,
        custom_fields=custom_fields_payroll,
    )
    return SalaryOut(
        id=rec.id,
        year=rec.year,
        month=rec.month,
        base_salary=rec.base_salary,
        performance_salary=rec.performance_salary,
        high_temp_allowance=rec.high_temp_allowance,
        low_temp_allowance=rec.low_temp_allowance,
        computer_allowance=rec.computer_allowance,
        communication_allowance=rec.communication_allowance,
        meal_allowance=rec.meal_allowance,
        mid_autumn_benefit=rec.mid_autumn_benefit,
        dragon_boat_benefit=rec.dragon_boat_benefit,
        spring_festival_benefit=rec.spring_festival_benefit,
        other_income=rec.other_income,
        comprehensive_allowance=rec.comprehensive_allowance,
        pension_insurance=rec.pension_insurance,
        medical_insurance=rec.medical_insurance,
        unemployment_insurance=rec.unemployment_insurance,
        critical_illness_insurance=rec.critical_illness_insurance,
        enterprise_annuity=rec.enterprise_annuity,
        housing_fund=rec.housing_fund,
        other_deductions=rec.other_deductions,
        labor_union_fee=rec.labor_union_fee,
        performance_deduction=rec.performance_deduction,
        tax=data["tax"],
        total_income=data["total_income"],
        total_deductions=data["total_deductions"],
        gross_income=data["gross_income"],
        net_income=data["net_income"],
        actual_take_home=data["actual_take_home"],
        non_cash_benefits=data["non_cash_benefits"],
        note=rec.note,
        custom_fields=custom_fields_data,
    )


@router.get("/", response_model=List[SalaryOut])
async def list_salaries(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
):
    q = SalaryRecord.filter(person__user_id=user.id)
    if person_id:
        q = q.filter(person_id=person_id)
    if year:
        q = q.filter(year=year)
    if month:
        q = q.filter(month=month)
    records = await q.all()
    return [await to_out(r) for r in records]


@router.post("/{person_id}", response_model=SalaryOut)
async def create_salary(person_id: int, payload: SalaryCreate, user=Depends(get_current_user)):
    person = await Person.filter(id=person_id, user_id=user.id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")

    rec = await SalaryRecord.create(
        person_id=person_id,
        year=payload.year,
        month=payload.month,
        base_salary=payload.base_salary,
        performance_salary=payload.performance_salary,
        high_temp_allowance=payload.high_temp_allowance,
        low_temp_allowance=payload.low_temp_allowance,
        computer_allowance=payload.computer_allowance,
        communication_allowance=payload.communication_allowance,
        meal_allowance=payload.meal_allowance,
        mid_autumn_benefit=payload.mid_autumn_benefit,
        dragon_boat_benefit=payload.dragon_boat_benefit,
        spring_festival_benefit=payload.spring_festival_benefit,
        other_income=payload.other_income,
        comprehensive_allowance=payload.comprehensive_allowance,
        pension_insurance=payload.pension_insurance,
        medical_insurance=payload.medical_insurance,
        unemployment_insurance=payload.unemployment_insurance,
        critical_illness_insurance=payload.critical_illness_insurance,
        enterprise_annuity=payload.enterprise_annuity,
        housing_fund=payload.housing_fund,
        other_deductions=payload.other_deductions,
        labor_union_fee=payload.labor_union_fee,
        performance_deduction=payload.performance_deduction,
        tax=payload.tax,
        note=payload.note,
    )

    # Save custom fields
    if payload.custom_fields:
        await save_custom_fields(rec.id, user.id, payload.custom_fields)

    return await to_out(rec)


@router.get("/{record_id}", response_model=SalaryOut)
async def get_salary(record_id: int, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    return await to_out(rec)


@router.put("/{record_id}", response_model=SalaryOut)
async def update_salary(record_id: int, payload: SalaryUpdate, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")

    # Update fixed fields
    update_data = payload.model_dump(exclude_unset=True, exclude={"custom_fields"})
    for field, value in update_data.items():
        setattr(rec, field, value)
    await rec.save()

    # Update custom fields if provided
    if payload.custom_fields is not None:
        await save_custom_fields(rec.id, user.id, payload.custom_fields)

    return await to_out(rec)


@router.delete("/{record_id}")
async def delete_salary(record_id: int, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")

    # Delete custom values first (cascade)
    await CustomSalaryValue.filter(salary_record_id=rec.id).delete()

    await rec.delete()
    return {"ok": True}
