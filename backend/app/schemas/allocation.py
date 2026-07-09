from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .project import ProjectResponse
from .seat import SeatResponse

# Avoid circular dependencies by using a simpler Employee representation
class EmployeeMinResponse(BaseModel):
    id: int
    employee_code: str
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class SeatAllocationBase(BaseModel):
    employee_id: int
    seat_id: int
    project_id: int
    allocation_status: str = Field("Active", description="Status: Active, Released")

class SeatAllocationCreate(SeatAllocationBase):
    pass

class SeatAllocationRequest(BaseModel):
    employee_id: int
    seat_id: int

class SeatAllocationResponse(SeatAllocationBase):
    id: int
    allocation_date: datetime
    released_date: Optional[datetime] = None
    employee: EmployeeMinResponse
    seat: SeatResponse
    project: ProjectResponse

    model_config = ConfigDict(from_attributes=True)
