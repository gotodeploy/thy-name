from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class Kanji(Base):
    __tablename__ = "kanji"

    id: Mapped[int] = mapped_column(primary_key=True)
    character: Mapped[str] = mapped_column(String(1), nullable=False, unique=True)
    rating: Mapped[int] = mapped_column(nullable=False, default=0)


class ThyName(Base):
    __tablename__ = "thy_name"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
