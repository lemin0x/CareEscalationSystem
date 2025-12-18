"""
Pydantic schemas for Patient model.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PatientBase(BaseModel):
    """Base patient schema."""
    first_name: str
    last_name: str
    age: int
    gender: str  # "M", "F", or "Other"
    national_id: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class PatientCreate(PatientBase):
    """Schema for creating a new patient."""
    health_center_id: int
    oxygen_saturation: Optional[float] = None
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    temperature: Optional[float] = None
    chest_pain: bool = False
    chief_complaint: Optional[str] = None
    notes: Optional[str] = None


class PatientUpdate(BaseModel):
    """Schema for updating patient information."""
    oxygen_saturation: Optional[float] = None
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    temperature: Optional[float] = None
    chest_pain: Optional[bool] = None
    triage_level: Optional[str] = None
    chief_complaint: Optional[str] = None
    notes: Optional[str] = None


class PatientResponse(PatientBase):
    """Schema for patient response."""
    id: int
    oxygen_saturation: Optional[float] = None
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    temperature: Optional[float] = None
    chest_pain: bool = False
    triage_level: Optional[str] = None
    chief_complaint: Optional[str] = None
    notes: Optional[str] = None
    health_center_id: int
    registered_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

