from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.borrowing import Borrowing
    from app.models.plan import SubscriptionPlan
    from app.models.transaction import Transaction


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    subscription_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subscription_plans.id"), nullable=False
    )

    subscription_plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan", back_populates="users"
    )
    borrowings: Mapped[list["Borrowing"]] = relationship("Borrowing", back_populates="user")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user")
