"""
Patient model for emergency cases.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Patient(Base):
    """Patient model for emergency cases."""
    
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)  # "M", "F", or "Other"
    national_id = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    
    # Emergency vitals
    oxygen_saturation = Column(Float, nullable=True)  # SpO2 percentage
    heart_rate = Column(Integer, nullable=True)  # BPM
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)  # Celsius
    chest_pain = Column(Boolean, default=False)
    
    # Triage information
    triage_level = Column(String, nullable=True)  # "CRITICAL", "URGENT", "NORMAL"
    chief_complaint = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    # Relationships
    health_center_id = Column(Integer, ForeignKey("health_centers.id"), nullable=False)
    registered_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    health_center = relationship("HealthCenter", backref="patients")
    referrals = relationship("Referral", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.first_name} {self.last_name}, triage={self.triage_level})>"

