from decimal import Decimal
from app.models.transaction import TxType

def compute_signed_amount(tx_type: TxType, amount: Decimal) -> Decimal:
    if amount <= 0:
        raise ValueError("amount must be > 0")
    return -amount if tx_type == TxType.EXPENSE else amount
