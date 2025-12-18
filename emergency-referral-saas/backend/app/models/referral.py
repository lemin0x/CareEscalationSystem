"""
Referral model for patient transfers from Centres de Santé to CHU.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Referral(Base):
    """
    Referral model tracking patient transfers.
    
    Lifecycle: CREATED → SENT → ACCEPTED → TRANSFERRED
    """
    
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    from_center_id = Column(Integer, ForeignKey("health_centers.id"), nullable=False)
    to_center_id = Column(Integer, ForeignKey("health_centers.id"), nullable=False)
    
    status = Column(
        String,
        nullable=False,
        default="CREATED"
    )  # CREATED, SENT, ACCEPTED, TRANSFERRED
    
    priority = Column(String, nullable=False, default="CRITICAL")  # CRITICAL, URGENT, NORMAL
    reason = Column(Text, nullable=True)  # Reason for referral
    clinical_notes = Column(Text, nullable=True)  # Clinical information
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    transferred_at = Column(DateTime, nullable=True)
    
    # User tracking
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    accepted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="referrals")
    from_center = relationship("HealthCenter", foreign_keys=[from_center_id], backref="referrals_from")
    to_center = relationship("HealthCenter", foreign_keys=[to_center_id], backref="referrals_to")
    
    def __repr__(self):
        return f"<Referral(id={self.id}, patient_id={self.patient_id}, status={self.status})>"

