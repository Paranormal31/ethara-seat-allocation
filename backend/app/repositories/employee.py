from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from ..models.employee import Employee
from ..schemas.employee import EmployeeCreate, EmployeeUpdate

class EmployeeRepository:
    @staticmethod
    def get_by_id(db: Session, employee_id: int) -> Optional[Employee]:
        return db.scalar(
            select(Employee)
            .options(joinedload(Employee.project))
            .where(Employee.id == employee_id)
        )

    @staticmethod
    def get_by_code(db: Session, employee_code: str) -> Optional[Employee]:
        return db.scalar(
            select(Employee)
            .options(joinedload(Employee.project))
            .where(Employee.employee_code == employee_code)
        )

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Employee]:
        return db.scalar(
            select(Employee)
            .options(joinedload(Employee.project))
            .where(Employee.email == email)
        )

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
        return list(
            db.scalars(
                select(Employee)
                .options(joinedload(Employee.project))
                .offset(skip)
                .limit(limit)
            ).all()
        )

    @staticmethod
    def create(db: Session, schema: EmployeeCreate) -> Employee:
        db_employee = Employee(
            employee_code=schema.employee_code,
            name=schema.name,
            email=schema.email,
            department=schema.department,
            role=schema.role,
            joining_date=schema.joining_date,
            status=schema.status,
            project_id=schema.project_id
        )
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee

    @staticmethod
    def update(db: Session, db_employee: Employee, schema: EmployeeUpdate) -> Employee:
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
        return db_employee
