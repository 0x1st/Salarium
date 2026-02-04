from decimal import Decimal, ROUND_HALF_UP


def compute_payroll(
    *,
    base_salary,
    performance_salary,
    high_temp_allowance,
    low_temp_allowance,
    computer_allowance,
    communication_allowance,
    meal_allowance,
    mid_autumn_benefit,
    dragon_boat_benefit,
    spring_festival_benefit,
    other_income,
    comprehensive_allowance,
    pension_insurance,
    medical_insurance,
    unemployment_insurance,
    critical_illness_insurance,
    enterprise_annuity,
    housing_fund,
    other_deductions,
    labor_union_fee,
    performance_deduction,
    tax,
    custom_fields=None,  # List of dicts: [{field_type, is_non_cash, amount}, ...]
):
    D = lambda v: v if isinstance(v, Decimal) else Decimal(str(v or 0))
    q = Decimal("0.01")

    base_salary = D(base_salary)
    performance_salary = D(performance_salary)
    high_temp_allowance = D(high_temp_allowance)
    low_temp_allowance = D(low_temp_allowance)
    computer_allowance = D(computer_allowance)
    communication_allowance = D(communication_allowance)
    meal_allowance = D(meal_allowance)
    mid_autumn_benefit = D(mid_autumn_benefit)
    dragon_boat_benefit = D(dragon_boat_benefit)
    spring_festival_benefit = D(spring_festival_benefit)
    other_income = D(other_income)
    comprehensive_allowance = D(comprehensive_allowance)

    pension_insurance = D(pension_insurance)
    medical_insurance = D(medical_insurance)
    unemployment_insurance = D(unemployment_insurance)
    critical_illness_insurance = D(critical_illness_insurance)
    enterprise_annuity = D(enterprise_annuity)
    housing_fund = D(housing_fund)
    other_deductions = D(other_deductions)
    labor_union_fee = D(labor_union_fee)
    performance_deduction = D(performance_deduction)
    tax = D(tax)

    # Process custom fields
    custom_income = Decimal("0")
    custom_deductions = Decimal("0")
    custom_non_cash = Decimal("0")
    custom_cash_income = Decimal("0")

    if custom_fields:
        for cf in custom_fields:
            amount = D(cf.get("amount", 0))
            field_type = cf.get("field_type", "income")
            is_non_cash = cf.get("is_non_cash", False)

            if field_type == "income":
                custom_income += amount
                if is_non_cash:
                    custom_non_cash += amount
                else:
                    custom_cash_income += amount
            elif field_type == "deduction":
                custom_deductions += amount

    # Non-cash benefits (not included in actual take-home)
    non_cash_benefits = (
        meal_allowance
        + mid_autumn_benefit
        + dragon_boat_benefit
        + spring_festival_benefit
        + custom_non_cash
    ).quantize(q, rounding=ROUND_HALF_UP)

    # Total income includes everything
    total_income = (
        base_salary
        + performance_salary
        + high_temp_allowance
        + low_temp_allowance
        + computer_allowance
        + communication_allowance
        + comprehensive_allowance
        + meal_allowance
        + mid_autumn_benefit
        + dragon_boat_benefit
        + spring_festival_benefit
        + other_income
        + custom_income
    ).quantize(q, rounding=ROUND_HALF_UP)

    total_deductions = (
        pension_insurance
        + medical_insurance
        + unemployment_insurance
        + critical_illness_insurance
        + enterprise_annuity
        + housing_fund
        + other_deductions
        + labor_union_fee
        + performance_deduction
        + custom_deductions
    ).quantize(q, rounding=ROUND_HALF_UP)

    gross_income = total_income
    net_income = (gross_income - total_deductions - tax).quantize(q, rounding=ROUND_HALF_UP)

    # Actual take-home = cash income - deductions - tax
    # Excludes non-cash benefits (meal, festival benefits)
    actual_take_home = (
        base_salary
        + performance_salary
        + high_temp_allowance
        + low_temp_allowance
        + computer_allowance
        + communication_allowance
        + comprehensive_allowance
        + other_income
        + custom_cash_income
        - total_deductions
    ).quantize(q, rounding=ROUND_HALF_UP)

    return {
        "total_income": total_income,
        "total_deductions": total_deductions,
        "gross_income": gross_income,
        "tax": tax.quantize(q, rounding=ROUND_HALF_UP),
        "net_income": net_income,
        "actual_take_home": actual_take_home,
        "non_cash_benefits": non_cash_benefits,
    }
