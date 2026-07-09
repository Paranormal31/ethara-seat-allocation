from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .project import ProjectResponse

class EmployeeBase(BaseModel):
    employee_code: str = Field(..., max_length=50, description="Unique alphanumeric code of the employee")
    name: str = Field(..., max_length=100)
    email: EmailStr
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=100)
    joining_date: date
    status: str = Field("Active", description="Status of the employee: Active, Deactivated, Pending")
    project_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None
    project_id: Optional[int] = None

class EmployeeResponse(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project: Optional[ProjectResponse] = None

    model_config = ConfigDict(from_attributes=True)
