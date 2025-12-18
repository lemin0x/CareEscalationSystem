"""
Pydantic schemas for Referral model.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.patient import PatientResponse


class ReferralBase(BaseModel):
    """Base referral schema."""
    patient_id: int
    to_center_id: int
    reason: Optional[str] = None
    clinical_notes: Optional[str] = None


class ReferralCreate(ReferralBase):
    """Schema for creating a new referral."""
    pass


class ReferralUpdate(BaseModel):
    """Schema for updating referral status."""
    status: Optional[str] = None
    clinical_notes: Optional[str] = None


class ReferralResponse(ReferralBase):
    """Schema for referral response."""
    id: int
    from_center_id: int
    status: str
    priority: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    transferred_at: Optional[datetime] = None
    created_by: int
    accepted_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class ReferralWithPatient(ReferralResponse):
    """Schema for referral with patient details."""
    patient: PatientResponse
    
    class Config:
        from_attributes = True

