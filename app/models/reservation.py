from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_phone: Mapped[str] = mapped_column(String(100))
    user_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
