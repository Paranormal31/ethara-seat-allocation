from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, select, and_, outerjoin
from ..database import get_db
from ..models.employee import Employee
from ..models.seat import Seat
from ..models.allocation import SeatAllocation
from ..models.project import Project

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    # 1. Base counts
    total_employees = db.scalar(select(func.count(Employee.id)).where(Employee.status == "Active")) or 0
    total_seats = db.scalar(select(func.count(Seat.id))) or 0
    occupied_seats = db.scalar(select(func.count(Seat.id)).where(Seat.status == "Occupied")) or 0
    available_seats = db.scalar(select(func.count(Seat.id)).where(Seat.status == "Available")) or 0
    reserved_seats = db.scalar(select(func.count(Seat.id)).where(Seat.status == "Reserved")) or 0
    maintenance_seats = db.scalar(select(func.count(Seat.id)).where(Seat.status == "Maintenance")) or 0

    # 2. Project-wise seat allocation
    # Join projects with seat allocations to count active allocations per project
    project_allocs = db.execute(
        select(Project.name, func.count(SeatAllocation.id))
        .select_from(outerjoin(Project, SeatAllocation, and_(Project.id == SeatAllocation.project_id, SeatAllocation.allocation_status == "Active")))
        .group_by(Project.name)
    ).all()
    project_wise = [{"project_name": row[0], "count": row[1]} for row in project_allocs]

    # 3. Floor-wise occupancy
    # Calculate occupied and total seats per floor
    floor_totals = db.execute(
        select(Seat.floor, func.count(Seat.id))
        .group_by(Seat.floor)
    ).all()
    floor_occupied = db.execute(
        select(Seat.floor, func.count(Seat.id))
        .where(Seat.status == "Occupied")
        .group_by(Seat.floor)
    ).all()
    
    occupied_map = {row[0]: row[1] for row in floor_occupied}
    floor_wise = []
    for floor, total in floor_totals:
        occ = occupied_map.get(floor, 0)
        floor_wise.append({
            "floor": floor,
            "occupied": occ,
            "total": total,
            "occupancy_rate": round((occ / total) * 100, 1) if total > 0 else 0.0
        })
    floor_wise.sort(key=lambda x: x["floor"])

    # 4. New joiners pending allocation
    # Employees who are Active and have no active SeatAllocation record
    subq = select(SeatAllocation.employee_id).where(SeatAllocation.allocation_status == "Active").subquery()
    pending_allocs = db.scalar(
        select(func.count(Employee.id))
        .where(
            and_(
                Employee.status == "Active",
                Employee.id.not_in(select(subq.c.employee_id))
            )
        )
    ) or 0

    return {
        "summary": {
            "total_employees": total_employees,
            "total_seats": total_seats,
            "occupied_seats": occupied_seats,
            "available_seats": available_seats,
            "reserved_seats": reserved_seats,
            "maintenance_seats": maintenance_seats,
            "pending_allocations_count": pending_allocs
        },
        "project_wise_allocations": project_wise,
        "floor_wise_occupancy": floor_wise
    }
