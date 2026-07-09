from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

if TYPE_CHECKING:
    from .allocation import SeatAllocation

class Seat(Base):
    __tablename__ = "seats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    floor: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    zone: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    bay: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="Available") # Available, Occupied, Reserved, Maintenance
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Unique constraint: Duplicate seat number on the same floor/zone is not allowed
    __table_args__ = (
        UniqueConstraint('floor', 'zone', 'seat_number', name='uq_floor_zone_seat_number'),
    )

    # Relationships
    allocations: Mapped[List["SeatAllocation"]] = relationship("SeatAllocation", back_populates="seat")
