from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from decimal import Decimal
from datetime import date

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction, TxStatus
from app.dtos.stats import SummaryOut

router = APIRouter(prefix="/stats", tags=["stats"])

def month_bounds(month: str) -> tuple[date, date]:
    y, m = month.split("-")
    y, m = int(y), int(m)
    start = date(y, m, 1)
    if m == 12:
        end = date(y + 1, 1, 1)
    else:
        end = date(y, m + 1, 1)
    return start, end

@router.get("/summary", response_model=SummaryOut)
async def summary(
    month: str = Query(..., description="YYYY-MM"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start, end = month_bounds(month)
    base = and_(Transaction.user_id == user.id, Transaction.date >= start, Transaction.date < end)

    # pagos (realizado)
    income_paid_q = select(func.coalesce(func.sum(Transaction.signed_amount), 0)).where(
        base, Transaction.status == TxStatus.PAID, Transaction.signed_amount > 0
    )
    expense_paid_q = select(func.coalesce(func.sum(Transaction.signed_amount), 0)).where(
        base, Transaction.status == TxStatus.PAID, Transaction.signed_amount < 0
    )

    # todos (previsto)
    income_all_q = select(func.coalesce(func.sum(Transaction.signed_amount), 0)).where(base, Transaction.signed_amount > 0)
    expense_all_q = select(func.coalesce(func.sum(Transaction.signed_amount), 0)).where(base, Transaction.signed_amount < 0)

    income_paid = (await db.execute(income_paid_q)).scalar_one()
    expense_paid = (await db.execute(expense_paid_q)).scalar_one()
    income_all = (await db.execute(income_all_q)).scalar_one()
    expense_all = (await db.execute(expense_all_q)).scalar_one()

    # expense_* já vem negativo; aqui mantenho como negativo e calculo balance somando
    return SummaryOut(
        month=month,
        income_paid=Decimal(str(income_paid)),
        expense_paid=Decimal(str(expense_paid)),
        balance_paid=Decimal(str(income_paid + expense_paid)),
        income_all=Decimal(str(income_all)),
        expense_all=Decimal(str(expense_all)),
        balance_all=Decimal(str(income_all + expense_all)),
    )
