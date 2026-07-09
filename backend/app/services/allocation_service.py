from typing import List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_, func
from ..models.employee import Employee
from ..models.seat import Seat
from ..models.allocation import SeatAllocation

class AllocationService:
    @staticmethod
    def get_suggested_seats(db: Session, employee_id: int, limit: int = 5) -> List[Seat]:
        """
        Suggest available seats near the employee's project team members based on proximity rules:
        1. Same floor, same zone, same bay
        2. Same floor, same zone, adjacent bays
        3. Same floor, different zones
        4. Different floors, starting from the closest floors
        """
        # 1. Fetch employee to find project_id
        employee = db.scalar(select(Employee).where(Employee.id == employee_id))
        if not employee or not employee.project_id:
            # Fallback: Just return any available seats if employee or project not found
            return list(db.scalars(
                select(Seat)
                .where(Seat.status == "Available")
                .order_by(Seat.floor, Seat.zone, Seat.bay, Seat.seat_number)
                .limit(limit)
            ).all())

        project_id = employee.project_id

        # 2. Find seats occupied by teammates on the same project
        teammate_allocs = db.scalars(
            select(SeatAllocation)
            .options(joinedload(SeatAllocation.seat))
            .where(
                and_(
                    SeatAllocation.project_id == project_id,
                    SeatAllocation.allocation_status == "Active"
                )
            )
        ).all()

        available_seats = db.scalars(
            select(Seat).where(Seat.status == "Available")
        ).all()

        if not available_seats:
            return []

        if not teammate_allocs:
            # No teammates allocated yet: Suggest seats starting from Floor 1
            available_seats.sort(key=lambda s: (s.floor, s.zone, s.bay, s.seat_number))
            return available_seats[:limit]

        # 3. Score each available seat based on proximity to teammates
        # Lower score = Closer proximity (better)
        scored_seats: List[Tuple[Seat, float]] = []

        for seat in available_seats:
            min_distance = float('inf')
            for alloc in teammate_allocs:
                t_seat = alloc.seat
                # Calculate distance metrics:
                # - Floor difference: weight of 1000 (very high penalty for changing floors)
                # - Zone difference: weight of 100 (high penalty for changing zones)
                # - Bay difference: weight of 10
                floor_diff = abs(seat.floor - t_seat.floor)
                zone_diff = 0 if seat.zone == t_seat.zone else 1
                bay_diff = abs(seat.bay - t_seat.bay)

                # Composite score to teammates
                distance = (floor_diff * 1000) + (zone_diff * 100) + (bay_diff * 10)
                if distance < min_distance:
                    min_distance = distance
            
            scored_seats.append((seat, min_distance))

        # Sort by distance score, and sub-sort by natural coordinates to ensure stable suggestions
        scored_seats.sort(key=lambda x: (x[1], x[0].floor, x[0].zone, x[0].bay, x[0].seat_number))

        return [item[0] for item in scored_seats[:limit]]
