"""
Assignment service for managing patient assignments (simplified for MVP).
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.referral import Referral
from app.models.health_center import HealthCenter


class AssignmentService:
    """
    Service for assigning referrals to CHU centers.
    
    Simplified for MVP: assigns to first available CHU.
    In production, this would consider capacity, specialization, distance, etc.
    """
    
    @staticmethod
    def find_available_chu(db: Session) -> Optional[HealthCenter]:
        """
        Find an available CHU for referral.
        
        Simplified: returns first CHU found.
        In production, would consider:
        - Current capacity
        - Specialization match
        - Geographic proximity
        - Current workload
        
        Args:
            db: Database session
            
        Returns:
            HealthCenter object or None if no CHU found
        """
        chu = db.query(HealthCenter).filter(
            HealthCenter.center_type == "CHU"
        ).first()
        
        return chu
    
    @staticmethod
    def assign_referral_to_chu(
        db: Session,
        referral_id: int,
        chu_id: int
    ) -> Referral:
        """
        Assign a referral to a specific CHU.
        
        Args:
            db: Database session
            referral_id: Referral ID
            chu_id: CHU health center ID
            
        Returns:
            Updated Referral object
        """
        referral = db.query(Referral).filter(Referral.id == referral_id).first()
        if not referral:
            raise ValueError(f"Referral with ID {referral_id} not found")
        
        # Verify destination is CHU
        chu = db.query(HealthCenter).filter(HealthCenter.id == chu_id).first()
        if not chu or chu.center_type != "CHU":
            raise ValueError("Destination must be a CHU")
        
        referral.to_center_id = chu_id
        db.commit()
        db.refresh(referral)
        
        return referral

