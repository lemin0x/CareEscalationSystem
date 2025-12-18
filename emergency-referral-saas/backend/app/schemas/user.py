"""
Pydantic schemas for User model.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr
    full_name: str
    role: str  # "nurse" or "doctor"
    health_center_id: Optional[int] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

