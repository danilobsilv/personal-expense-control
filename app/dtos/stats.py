from decimal import Decimal
from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class SummaryOut:
    month: str
    income_paid: Decimal
    expense_paid: Decimal
    balance_paid: Decimal
    income_all: Decimal
    expense_all: Decimal
    balance_all: Decimal
