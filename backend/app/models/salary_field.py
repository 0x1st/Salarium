from tortoise import fields
from tortoise.models import Model


# Income categories
INCOME_CATEGORIES = [
    ("base_salary", "基本工资"),
    ("performance", "绩效"),
    ("allowance", "补贴"),
    ("bonus", "奖金"),
    ("welfare", "福利"),
    ("other_income", "其他收入"),
]

# Deduction categories
DEDUCTION_CATEGORIES = [
    ("insurance", "保险"),
    ("housing_fund", "公积金"),
    ("tax", "税"),
    ("other_deduction", "其他扣款"),
]

ALL_CATEGORIES = {
    "income": INCOME_CATEGORIES,
    "deduction": DEDUCTION_CATEGORIES,
}


class SalaryField(Model):
    """User-defined salary field definition."""

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="salary_fields")
    name = fields.CharField(max_length=64)  # Display name, e.g., "春节奖金"
    field_key = fields.CharField(max_length=64)  # Unique key, e.g., "spring_bonus"
    field_type = fields.CharField(max_length=16)  # "income" or "deduction"
    category = fields.CharField(max_length=32)  # e.g., "bonus", "allowance", "insurance"
    is_non_cash = fields.BooleanField(default=False)  # Excluded from actual_take_home
    display_order = fields.IntField(default=0)  # For UI ordering
    is_active = fields.BooleanField(default=True)  # Soft delete
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "salary_fields"
        unique_together = ("user_id", "field_key")


class CustomSalaryValue(Model):
    """Custom field value for a salary record."""

    id = fields.IntField(pk=True)
    salary_record = fields.ForeignKeyField(
        "models.SalaryRecord", related_name="custom_values"
    )
    salary_field = fields.ForeignKeyField("models.SalaryField", related_name="values")
    amount = fields.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        table = "custom_salary_values"
        unique_together = ("salary_record_id", "salary_field_id")
