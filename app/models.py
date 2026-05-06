from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Technician(Base):
    __tablename__ = "technicians"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(80), default="Tecnico")
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    withdrawals: Mapped[list["Withdrawal"]] = relationship(back_populates="technician")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    unit: Mapped[str] = mapped_column(String(30), default="unidade")
    stock: Mapped[int] = mapped_column(Integer, default=0)
    minimum_stock: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    withdrawals: Mapped[list["Withdrawal"]] = relationship(back_populates="item")


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    technician_id: Mapped[int] = mapped_column(ForeignKey("technicians.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("inventory_items.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    withdrawn_at: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    technician: Mapped[Technician] = relationship(back_populates="withdrawals")
    item: Mapped[InventoryItem] = relationship(back_populates="withdrawals")
