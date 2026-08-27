from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)   # BOOK / MAGAZINE
    genre: Mapped[str] = mapped_column(String, nullable=False)  # e.g. CRIME, FANTASY, FICTION
    author: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String, nullable=True)  # e.g. /static/covers/clean_code.jpg
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    borrowings: Mapped[list["Borrowing"]] = relationship("Borrowing", back_populates="item")
