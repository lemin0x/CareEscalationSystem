"""
Pydantic schemas for Health Centers.
"""
from pydantic import BaseModel
from typing import Optional


class HealthCenterBase(BaseModel):
    name: str
    center_type: str  # "CENTRE" or "CHU"
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None


class HealthCenterCreate(HealthCenterBase):
    pass


class HealthCenter(HealthCenterBase):
    id: int
    
    class Config:
        from_attributes = True  # For SQLAlchemy compatibility (replaces orm_mode)


class HealthCenterUpdate(BaseModel):
    name: Optional[str] = None
    center_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None