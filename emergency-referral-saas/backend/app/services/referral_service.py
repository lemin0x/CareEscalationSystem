"""
Referral service for managing patient referrals.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.referral import Referral
from app.models.patient import Patient
from app.models.health_center import HealthCenter
from app.services.triage_service import TriageService


class ReferralService:
    """Service for managing referral lifecycle."""
    
    @staticmethod
    def create_referral(
        db: Session,
        patient_id: int,
        to_center_id: int,
        created_by: int,
        reason: str = None,
        clinical_notes: str = None
    ) -> Referral:
        """
        Create a new referral for a patient.
        
        Args:
            db: Database session
            patient_id: Patient ID
            to_center_id: Destination CHU ID
            created_by: User ID who created the referral
            reason: Optional reason for referral
            clinical_notes: Optional clinical notes
            
        Returns:
            Created Referral object
        """
        # Get patient and verify
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        # Get source and destination centers
        from_center = db.query(HealthCenter).filter(
            HealthCenter.id == patient.health_center_id
        ).first()
        
        to_center = db.query(HealthCenter).filter(
            HealthCenter.id == to_center_id
        ).first()
        
        if not from_center or not to_center:
            raise ValueError("Invalid health center ID")
        
        # Verify destination is CHU
        if to_center.center_type != "CHU":
            raise ValueError("Destination must be a CHU")
        
        # Determine priority from patient triage level
        priority = patient.triage_level or "CRITICAL"
        
        # Create referral
        referral = Referral(
            patient_id=patient_id,
            from_center_id=from_center.id,
            to_center_id=to_center_id,
            status="CREATED",
            priority=priority,
            reason=reason or f"Critical case requiring CHU care",
            clinical_notes=clinical_notes,
            created_by=created_by
        )
        
        db.add(referral)
        db.commit()
        db.refresh(referral)
        
        return referral
    
    @staticmethod
    def auto_create_referral_for_critical_patient(
        db: Session,
        patient_id: int,
        created_by: int
    ) -> Optional[Referral]:
        """
        Automatically create a referral for a critical patient from Centre de Santé.
        
        This is called when a patient is triaged as CRITICAL at a Centre de Santé.
        
        Args:
            db: Database session
            patient_id: Patient ID
            created_by: User ID who created the referral
            
        Returns:
            Created Referral object or None if not applicable
        """
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return None
        
        # Check if referral should be created
        if not TriageService.should_create_referral(patient, db):
            return None
        
        # Find a CHU to refer to (simplified: get first available CHU)
        chu = db.query(HealthCenter).filter(
            HealthCenter.center_type == "CHU"
        ).first()
        
        if not chu:
            # No CHU available - log this in production
            return None
        
        # Create referral
        return ReferralService.create_referral(
            db=db,
            patient_id=patient_id,
            to_center_id=chu.id,
            created_by=created_by,
            reason="Auto-referral: Critical case from Centre de Santé",
            clinical_notes=f"Patient triage level: {patient.triage_level}"
        )
    
    @staticmethod
    def send_referral(db: Session, referral_id: int) -> Referral:
        """
        Mark referral as SENT (notifies destination CHU).
        
        Args:
            db: Database session
            referral_id: Referral ID
            
        Returns:
            Updated Referral object
        """
        referral = db.query(Referral).filter(Referral.id == referral_id).first()
        if not referral:
            raise ValueError(f"Referral with ID {referral_id} not found")
        
        if referral.status != "CREATED":
            raise ValueError(f"Cannot send referral with status {referral.status}")
        
        referral.status = "SENT"
        referral.sent_at = datetime.utcnow()
        
        db.commit()
        db.refresh(referral)
        
        return referral
    
    @staticmethod
    def accept_referral(db: Session, referral_id: int, accepted_by: int) -> Referral:
        """
        Accept a referral (CHU accepts the patient).
        
        Args:
            db: Database session
            referral_id: Referral ID
            accepted_by: User ID who accepted the referral
            
        Returns:
            Updated Referral object
        """
        referral = db.query(Referral).filter(Referral.id == referral_id).first()
        if not referral:
            raise ValueError(f"Referral with ID {referral_id} not found")
        
        if referral.status not in ["CREATED", "SENT"]:
            raise ValueError(f"Cannot accept referral with status {referral.status}")
        
        referral.status = "ACCEPTED"
        referral.accepted_at = datetime.utcnow()
        referral.accepted_by = accepted_by
        
        db.commit()
        db.refresh(referral)
        
        return referral
    
    @staticmethod
    def mark_transferred(db: Session, referral_id: int) -> Referral:
        """
        Mark referral as TRANSFERRED (patient has been transferred).
        
        Args:
            db: Database session
            referral_id: Referral ID
            
        Returns:
            Updated Referral object
        """
        referral = db.query(Referral).filter(Referral.id == referral_id).first()
        if not referral:
            raise ValueError(f"Referral with ID {referral_id} not found")
        
        if referral.status != "ACCEPTED":
            raise ValueError(f"Cannot transfer referral with status {referral.status}")
        
        referral.status = "TRANSFERRED"
        referral.transferred_at = datetime.utcnow()
        
        db.commit()
        db.refresh(referral)
        
        return referral
    
    @staticmethod
    def get_referrals_by_status(db: Session, status: str = None):
        """
        Get referrals filtered by status.
        
        Args:
            db: Database session
            status: Optional status filter
            
        Returns:
            Query result of referrals
        """
        query = db.query(Referral)
        if status:
            query = query.filter(Referral.status == status)
        return query.order_by(Referral.created_at.desc()).all()
    
    @staticmethod
    def get_referrals_for_center(db: Session, center_id: int, direction: str = "to"):
        """
        Get referrals for a specific health center.
        
        Args:
            db: Database session
            center_id: Health center ID
            direction: "to" (incoming) or "from" (outgoing)
            
        Returns:
            List of referrals
        """
        query = db.query(Referral)
        if direction == "to":
            query = query.filter(Referral.to_center_id == center_id)
        else:
            query = query.filter(Referral.from_center_id == center_id)
        
        return query.order_by(Referral.created_at.desc()).all()

