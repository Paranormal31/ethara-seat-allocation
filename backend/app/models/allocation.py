from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

if TYPE_CHECKING:
    from .employee import Employee
    from .seat import Seat
    from .project import Project

class SeatAllocation(Base):
    __tablename__ = "seat_allocations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), nullable=True, index=True)
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"), nullable=False, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    allocation_status: Mapped[str] = mapped_column(String(50), default="Active", index=True) # Active, Released, Reserved
    allocation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    released_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    employee: Mapped[Optional["Employee"]] = relationship("Employee", back_populates="allocations")
    seat: Mapped["Seat"] = relationship("Seat", back_populates="allocations")
    project: Mapped["Project"] = relationship("Project", back_populates="allocations")
