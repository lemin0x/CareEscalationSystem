"""
User model for authentication and authorization.
"""
from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base


class User(Base):
    """User model for nurses and doctors."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "nurse" or "doctor"
    is_active = Column(Boolean, default=True)
    health_center_id = Column(Integer, nullable=True)  # Foreign key to health centers
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

