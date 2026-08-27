from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Silver, Gold, Platinum
    max_books: Mapped[int] = mapped_column(Integer, nullable=False)
    max_magazines: Mapped[int] = mapped_column(Integer, nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="subscription_plan")
