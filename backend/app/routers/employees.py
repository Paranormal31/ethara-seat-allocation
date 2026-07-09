from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from ..repositories.employee import EmployeeRepository
from ..repositories.project import ProjectRepository

router = APIRouter(prefix="/api/employees", tags=["employees"])

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(schema: EmployeeCreate, db: Session = Depends(get_db)):
    # Check employee code unique
    if EmployeeRepository.get_by_code(db, schema.employee_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this code already exists"
        )
    # Check email unique
    if EmployeeRepository.get_by_email(db, schema.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this email already exists"
        )
    # Check project exists if provided
    if schema.project_id:
        if not ProjectRepository.get_by_id(db, schema.project_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned project not found"
            )
    return EmployeeRepository.create(db, schema)

@router.get("/", response_model=List[EmployeeResponse])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return EmployeeRepository.get_all(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=EmployeeResponse)
def read_employee(id: int, db: Session = Depends(get_db)):
    db_employee = EmployeeRepository.get_by_id(db, id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return db_employee

@router.put("/{id}", response_model=EmployeeResponse)
def update_employee(id: int, schema: EmployeeUpdate, db: Session = Depends(get_db)):
    db_employee = EmployeeRepository.get_by_id(db, id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    # Validate unique constraints if email is changing
    if schema.email and schema.email != db_employee.email:
        if EmployeeRepository.get_by_email(db, schema.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use by another employee"
            )
    # Validate project exists if changing
    if schema.project_id:
        if not ProjectRepository.get_by_id(db, schema.project_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned project not found"
            )
    return EmployeeRepository.update(db, db_employee, schema)

@router.delete("/{id}", response_model=EmployeeResponse)
def deactivate_employee(id: int, db: Session = Depends(get_db)):
    db_employee = EmployeeRepository.get_by_id(db, id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    # Deactivate instead of deleting
    deactivate_schema = EmployeeUpdate(status="Deactivated")
    return EmployeeRepository.update(db, db_employee, deactivate_schema)
