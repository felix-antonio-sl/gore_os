from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal


# ============================================================
# TP-02: Subvención 8% Funds
# ============================================================

class Subv8FundItem(BaseModel):
    id: UUID
    code: str
    name: str
    budget_regular: Decimal | None = None
    budget_special: Decimal | None = None
    budget_total: Decimal | None = None
    is_exclusive: bool
    sort_order: int
    is_active: bool


class Subv8FundCreate(BaseModel):
    code: str
    name: str
    budget_regular: Decimal | None = None
    budget_special: Decimal | None = None
    budget_total: Decimal | None = None
    is_exclusive: bool = False
    sort_order: int = 0


class Subv8FundUpdate(BaseModel):
    name: str | None = None
    budget_regular: Decimal | None = None
    budget_special: Decimal | None = None
    budget_total: Decimal | None = None
    is_exclusive: bool | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class Subv8CeilingItem(BaseModel):
    id: UUID
    fund_id: UUID
    fund_code: str | None = None
    fund_name: str | None = None
    institution_type: str
    area: str | None = None
    max_amount: Decimal
    notes: str | None = None


class Subv8CeilingCreate(BaseModel):
    institution_type: str
    area: str | None = None
    max_amount: Decimal
    notes: str | None = None


class Subv8CeilingUpdate(BaseModel):
    institution_type: str | None = None
    area: str | None = None
    max_amount: Decimal | None = None
    notes: str | None = None


# ============================================================
# TP-04: FRIL Categories
# ============================================================

class FrilCategoryItem(BaseModel):
    id: UUID
    code: str
    name: str
    group_code: str
    group_name: str
    description: str | None = None
    examples: str | None = None
    max_utm: Decimal
    is_exempt_commune_limit: bool
    is_active: bool
    sort_order: int


class FrilCategoryCreate(BaseModel):
    code: str
    name: str
    group_code: str
    group_name: str
    description: str | None = None
    examples: str | None = None
    max_utm: Decimal = Decimal("4545")
    is_exempt_commune_limit: bool = False
    sort_order: int = 0


class FrilCategoryUpdate(BaseModel):
    name: str | None = None
    group_code: str | None = None
    group_name: str | None = None
    description: str | None = None
    examples: str | None = None
    max_utm: Decimal | None = None
    is_exempt_commune_limit: bool | None = None
    is_active: bool | None = None
    sort_order: int | None = None
