from sqlalchemy import (
    String, ForeignKey, Date, Enum, Numeric, DateTime, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.core.database import Base

class TxType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class TxStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELED = "CANCELED"

class PaymentMethod(str, enum.Enum):
    PIX = "PIX"
    CASH = "CASH"
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    TRANSFER = "TRANSFER"

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), index=True, nullable=True)

    date: Mapped[str] = mapped_column(Date, index=True, nullable=False)
    type: Mapped[TxType] = mapped_column(Enum(TxType), nullable=False)
    status: Mapped[TxStatus] = mapped_column(Enum(TxStatus), nullable=False, default=TxStatus.PENDING)

    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)        # sempre positivo
    signed_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False) # expense negativo

    description: Mapped[str] = mapped_column(String(255), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), nullable=False, default=PaymentMethod.PIX)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
