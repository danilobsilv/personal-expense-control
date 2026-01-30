from datetime import date as date_timer
from decimal import Decimal
from typing import Optional
from pydantic.dataclasses import dataclass
from app.models.transaction import TxType, TxStatus, PaymentMethod

@dataclass(frozen=True)
class TransactionCreate:
    date: date_timer
    type: TxType
    amount: Decimal
    description: str
    category_id: Optional[int] = None
    status: TxStatus = TxStatus.PENDING
    payment_method: PaymentMethod = PaymentMethod.PIX


@dataclass(frozen=True)
class TransactionPatch:
    date: Optional[date_timer] = None
    type: Optional[TxType] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[TxStatus] = None
    payment_method: Optional[PaymentMethod] = None


@dataclass(frozen=True)
class TransactionOut:
    id: int
    date: date_timer
    type: TxType
    status: TxStatus
    amount: Decimal
    signed_amount: Decimal
    description: str
    payment_method: PaymentMethod
    category_id: Optional[int] = None
