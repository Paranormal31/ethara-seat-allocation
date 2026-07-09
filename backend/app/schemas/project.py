from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ProjectBase(BaseModel):
    name: str = Field(..., max_length=100, description="The unique name of the project")
    description: Optional[str] = Field(None, max_length=500)
    manager_name: Optional[str] = Field(None, max_length=100)
    status: str = Field("Active", description="Status of the project: Active, Inactive, Completed")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    manager_name: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None)

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
