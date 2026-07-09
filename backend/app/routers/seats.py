from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from ..database import get_db
from ..schemas.seat import SeatCreate, SeatUpdate, SeatResponse
from ..schemas.allocation import SeatAllocationRequest, SeatAllocationResponse
from ..repositories.seat import SeatRepository
from ..models.seat import Seat
from ..models.employee import Employee
from ..models.allocation import SeatAllocation

router = APIRouter(prefix="/api/seats", tags=["seats"])

@router.post("/", response_model=SeatResponse, status_code=status.HTTP_201_CREATED)
def create_seat(schema: SeatCreate, db: Session = Depends(get_db)):
    db_seat = SeatRepository.get_by_number(db, schema.floor, schema.zone, schema.seat_number)
    if db_seat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Seat {schema.seat_number} already exists on Floor {schema.floor} in {schema.zone}"
        )
    return SeatRepository.create(db, schema)

@router.get("/", response_model=List[SeatResponse])
def read_seats(db: Session = Depends(get_db)):
    return SeatRepository.get_all(db)

@router.get("/available", response_model=List[SeatResponse])
def read_available_seats(db: Session = Depends(get_db)):
    return SeatRepository.get_available(db)

@router.post("/allocate", response_model=SeatAllocationResponse)
def allocate_seat(schema: SeatAllocationRequest, db: Session = Depends(get_db)):
    # 1. Fetch employee
    employee = db.scalar(select(Employee).where(Employee.id == schema.employee_id))
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    # 2. Check employee status
    if employee.status != "Active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee is not active")
        
    # 3. Check employee project mapping
    if not employee.project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee must be assigned to an active project before seat allocation"
        )
    
    # 4. Check if employee already has an active seat allocation
    existing_alloc = db.scalar(
        select(SeatAllocation).where(
            and_(
                SeatAllocation.employee_id == schema.employee_id,
                SeatAllocation.allocation_status == "Active"
            )
        )
    )
    if existing_alloc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already has an active seat allocation"
        )

    # 5. Fetch seat with pessimistic write lock (prevents concurrent double-allocations)
    seat = db.scalar(
        select(Seat)
        .with_for_update()
        .where(Seat.id == schema.seat_id)
    )
    if not seat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
        
    if seat.status != "Available":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Seat is not available (status: {seat.status})"
        )

    # 6. Perform allocation
    seat.status = "Occupied"
    
    allocation = SeatAllocation(
        employee_id=employee.id,
        seat_id=seat.id,
        project_id=employee.project_id,
        allocation_status="Active",
        allocation_date=datetime.utcnow()
    )
    
    db.add(allocation)
    db.commit()
    
    # Refresh to load relationships (employee, seat, project) for response
    # We use a select statement with joined loads to fetch relationships cleanly
    refreshed_allocation = db.scalar(
        select(SeatAllocation)
        .options(
            joinedload(SeatAllocation.employee),
            joinedload(SeatAllocation.seat),
            joinedload(SeatAllocation.project)
        )
        .where(SeatAllocation.id == allocation.id)
    )
    
    return refreshed_allocation

from pydantic import BaseModel
class SeatReleaseRequest(BaseModel):
    employee_id: int

from sqlalchemy.orm import joinedload

@router.post("/release", response_model=SeatAllocationResponse)
def release_seat(schema: SeatReleaseRequest, db: Session = Depends(get_db)):
    # 1. Find active allocation
    allocation = db.scalar(
        select(SeatAllocation)
        .options(
            joinedload(SeatAllocation.employee),
            joinedload(SeatAllocation.seat),
            joinedload(SeatAllocation.project)
        )
        .where(
            and_(
                SeatAllocation.employee_id == schema.employee_id,
                SeatAllocation.allocation_status == "Active"
            )
        )
    )
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active seat allocation found for this employee"
        )
    
    # 2. Release seat
    seat = db.scalar(select(Seat).with_for_update().where(Seat.id == allocation.seat_id))
    if seat:
        seat.status = "Available"
        
    allocation.allocation_status = "Released"
    allocation.released_date = datetime.utcnow()
    
    db.commit()
    db.refresh(allocation)
    return allocation

class ReservationReleaseRequest(BaseModel):
    seat_id: int

@router.post("/release-reservation", response_model=SeatResponse)
def release_reservation(schema: ReservationReleaseRequest, db: Session = Depends(get_db)):
    seat = db.scalar(select(Seat).with_for_update().where(Seat.id == schema.seat_id))
    if not seat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
    if seat.status != "Reserved":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seat is not reserved")
    
    seat.status = "Available"
    
    # Mark allocation as Released
    allocation = db.scalar(
        select(SeatAllocation)
        .where(
            and_(
                SeatAllocation.seat_id == seat.id,
                SeatAllocation.allocation_status == "Reserved"
            )
        )
    )
    if allocation:
        allocation.allocation_status = "Released"
        allocation.released_date = datetime.utcnow()
        
    db.commit()
    db.refresh(seat)
    return seat

from ..services.allocation_service import AllocationService

@router.get("/suggest/{employee_id}", response_model=List[SeatResponse])
def suggest_seats_for_employee(employee_id: int, limit: int = 5, db: Session = Depends(get_db)):
    employee = db.scalar(select(Employee).where(Employee.id == employee_id))
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return AllocationService.get_suggested_seats(db, employee_id, limit=limit)

class SeatReserveRequest(BaseModel):
    seat_id: int
    project_id: int

@router.post("/reserve", response_model=SeatResponse)
def reserve_seat(schema: SeatReserveRequest, db: Session = Depends(get_db)):
    seat = db.scalar(select(Seat).with_for_update().where(Seat.id == schema.seat_id))
    if not seat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
    if seat.status != "Available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Seat is not available (status: {seat.status})")
    
    seat.status = "Reserved"
    
    allocation = SeatAllocation(
        employee_id=None,
        seat_id=seat.id,
        project_id=schema.project_id,
        allocation_status="Reserved",
        allocation_date=datetime.utcnow()
    )
    db.add(allocation)
    db.commit()
    
    # Reload seat to get relationships populated
    db.refresh(seat)
    return seat
