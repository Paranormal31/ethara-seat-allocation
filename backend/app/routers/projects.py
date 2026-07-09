from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from ..schemas.employee import EmployeeResponse
from ..repositories.project import ProjectRepository
from sqlalchemy import select
from ..models.employee import Employee

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(schema: ProjectCreate, db: Session = Depends(get_db)):
    db_project = ProjectRepository.get_by_name(db, schema.name)
    if db_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists"
        )
    return ProjectRepository.create(db, schema)

@router.get("/", response_model=List[ProjectResponse])
def read_projects(db: Session = Depends(get_db)):
    return ProjectRepository.get_all(db)

@router.get("/{id}", response_model=ProjectResponse)
def read_project(id: int, db: Session = Depends(get_db)):
    db_project = ProjectRepository.get_by_id(db, id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return db_project

@router.get("/{id}/employees", response_model=List[EmployeeResponse])
def read_project_employees(id: int, db: Session = Depends(get_db)):
    db_project = ProjectRepository.get_by_id(db, id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    # Modern SQLAlchemy 2.0 select statement for relationships
    employees = db.scalars(select(Employee).where(Employee.project_id == id)).all()
    return list(employees)
