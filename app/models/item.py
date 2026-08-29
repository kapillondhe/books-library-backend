from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SAEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ItemType

if TYPE_CHECKING:
    from app.models.borrowing import Borrowing


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[ItemType] = mapped_column(
        SAEnum(ItemType, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    genre: Mapped[str] = mapped_column(String, nullable=False)  # free text, e.g. CRIME, FANTASY, FICTION
    author: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    borrowings: Mapped[list["Borrowing"]] = relationship("Borrowing", back_populates="item")
