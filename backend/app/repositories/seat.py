from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from ..models.seat import Seat
from ..models.allocation import SeatAllocation
from ..schemas.seat import SeatCreate, SeatUpdate

class SeatRepository:
    @staticmethod
    def get_by_id(db: Session, seat_id: int) -> Optional[Seat]:
        return db.scalar(
            select(Seat)
            .options(joinedload(Seat.allocations).joinedload(SeatAllocation.employee))
            .where(Seat.id == seat_id)
        )

    @staticmethod
    def get_by_number(db: Session, floor: int, zone: str, seat_number: str) -> Optional[Seat]:
        return db.scalar(
            select(Seat)
            .options(joinedload(Seat.allocations).joinedload(SeatAllocation.employee))
            .where(
                Seat.floor == floor,
                Seat.zone == zone,
                Seat.seat_number == seat_number
            )
        )

    @staticmethod
    def get_all(db: Session) -> List[Seat]:
        return list(
            db.scalars(
                select(Seat).options(
                    joinedload(Seat.allocations).joinedload(SeatAllocation.employee)
                )
            ).unique().all()
        )

    @staticmethod
    def get_available(db: Session) -> List[Seat]:
        return list(db.scalars(select(Seat).where(Seat.status == "Available")).all())

    @staticmethod
    def create(db: Session, schema: SeatCreate) -> Seat:
        db_seat = Seat(
            floor=schema.floor,
            zone=schema.zone,
            bay=schema.bay,
            seat_number=schema.seat_number,
            status=schema.status
        )
        db.add(db_seat)
        db.commit()
        db.refresh(db_seat)
        return db_seat

    @staticmethod
    def update(db: Session, db_seat: Seat, schema: SeatUpdate) -> Seat:
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_seat, key, value)
        db.commit()
        db.refresh(db_seat)
        return db_seat
