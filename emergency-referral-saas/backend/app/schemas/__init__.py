"""
Schemas package - exports all Pydantic schemas.
"""
from app.schemas.user import UserBase, UserCreate, UserLogin, UserResponse, Token
from app.schemas.patient import PatientBase, PatientCreate, PatientUpdate, PatientResponse
from app.schemas.referral import ReferralBase, ReferralCreate, ReferralUpdate, ReferralResponse, ReferralWithPatient

__all__ = [
    "UserBase", "UserCreate", "UserLogin", "UserResponse", "Token",
    "PatientBase", "PatientCreate", "PatientUpdate", "PatientResponse",
    "ReferralBase", "ReferralCreate", "ReferralUpdate", "ReferralResponse", "ReferralWithPatient"
]

