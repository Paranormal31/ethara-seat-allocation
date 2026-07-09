from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class SeatBase(BaseModel):
    floor: int = Field(..., ge=1, description="Floor number (1-indexed)")
    zone: str = Field(..., max_length=50, description="Zone code (e.g. Zone A, Zone B)")
    bay: int = Field(..., ge=1, description="Bay number")
    seat_number: str = Field(..., max_length=50, description="Seat identifier (unique within floor/zone)")
    status: str = Field("Available", description="Status: Available, Occupied, Reserved, Maintenance")

class SeatCreate(SeatBase):
    pass

class SeatUpdate(BaseModel):
    status: Optional[str] = Field(None)
    floor: Optional[int] = None
    zone: Optional[str] = None
    bay: Optional[int] = None
    seat_number: Optional[str] = None

class EmployeeMinResponse(BaseModel):
    id: int
    employee_code: str
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class SeatAllocationMinResponse(BaseModel):
    id: int
    employee_id: Optional[int] = None
    project_id: int
    allocation_status: str
    allocation_date: datetime
    employee: Optional[EmployeeMinResponse] = None

    model_config = ConfigDict(from_attributes=True)

class SeatResponse(SeatBase):
    id: int
    created_at: datetime
    allocations: List[SeatAllocationMinResponse] = []

    model_config = ConfigDict(from_attributes=True)
