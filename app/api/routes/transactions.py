from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date
from decimal import Decimal

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction, TxStatus, TxType
from app.dtos.transaction import TransactionCreate, TransactionPatch, TransactionOut
from app.services.categories import ensure_category_belongs_to_user
from app.services.transactions import compute_signed_amount

router = APIRouter(prefix="/transactions", tags=["transactions"])

def month_bounds(month: str) -> tuple[date, date]:
    # month formato "YYYY-MM"
    y, m = month.split("-")
    y, m = int(y), int(m)
    start = date(y, m, 1)
    if m == 12:
        end = date(y + 1, 1, 1)
    else:
        end = date(y, m + 1, 1)
    return start, end

@router.get("", response_model=list[TransactionOut])
async def list_transactions(
    month: str | None = Query(default=None, description="YYYY-MM"),
    status: TxStatus | None = None,
    category_id: int | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    filters = [Transaction.user_id == user.id]
    if month:
        start, end = month_bounds(month)
        filters.append(and_(Transaction.date >= start, Transaction.date < end))
    if status:
        filters.append(Transaction.status == status)
    if category_id is not None:
        filters.append(Transaction.category_id == category_id)

    res = await db.execute(select(Transaction).where(and_(*filters)).order_by(Transaction.date.desc(), Transaction.id.desc()))
    txs = res.scalars().all()
    return [
        TransactionOut(
            id=t.id,
            date=t.date,
            type=t.type,
            status=t.status,
            amount=Decimal(str(t.amount)),
            signed_amount=Decimal(str(t.signed_amount)),
            description=t.description,
            category_id=t.category_id,
            payment_method=t.payment_method,
        )
        for t in txs
    ]

@router.post("", response_model=TransactionOut, status_code=201)
async def create_transaction(payload: TransactionCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if payload.category_id is not None:
        await ensure_category_belongs_to_user(db, user.id, payload.category_id)

    try:
        signed = compute_signed_amount(payload.type, payload.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    t = Transaction(
        user_id=user.id,
        category_id=payload.category_id,
        date=payload.date,
        type=payload.type,
        status=payload.status,
        amount=payload.amount,
        signed_amount=signed,
        description=payload.description.strip(),
        payment_method=payload.payment_method,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)

    return TransactionOut(
        id=t.id,
        date=t.date,
        type=t.type,
        status=t.status,
        amount=Decimal(str(t.amount)),
        signed_amount=Decimal(str(t.signed_amount)),
        description=t.description,
        category_id=t.category_id,
        payment_method=t.payment_method,
    )

@router.patch("/{tx_id}", response_model=TransactionOut)
async def patch_transaction(tx_id: int, payload: TransactionPatch, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Transaction).where(Transaction.id == tx_id, Transaction.user_id == user.id))
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if payload.category_id is not None:
        await ensure_category_belongs_to_user(db, user.id, payload.category_id)

    # aplicar campos
    if payload.date is not None:
        t.date = payload.date
    if payload.type is not None:
        t.type = payload.type
    if payload.status is not None:
        t.status = payload.status
    if payload.description is not None:
        t.description = payload.description.strip()
    if payload.category_id is not None or payload.category_id is None:
        # permite setar null explicitamente
        t.category_id = payload.category_id
    if payload.payment_method is not None:
        t.payment_method = payload.payment_method
    if payload.amount is not None:
        t.amount = payload.amount

    # recalcular signed_amount se type/amount mudou
    amount_dec = Decimal(str(t.amount))
    t.signed_amount = compute_signed_amount(t.type, amount_dec)

    await db.commit()
    await db.refresh(t)

    return TransactionOut(
        id=t.id,
        date=t.date,
        type=t.type,
        status=t.status,
        amount=Decimal(str(t.amount)),
        signed_amount=Decimal(str(t.signed_amount)),
        description=t.description,
        category_id=t.category_id,
        payment_method=t.payment_method,
    )

@router.delete("/{tx_id}", status_code=204)
async def delete_transaction(tx_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Transaction).where(Transaction.id == tx_id, Transaction.user_id == user.id))
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await db.delete(t)
    await db.commit()
