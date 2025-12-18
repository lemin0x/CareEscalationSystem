"""
Triage service for determining patient priority levels.
"""
from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.models.health_center import HealthCenter


class TriageService:
    """Service for triage logic and patient priority assessment."""
    
    # Critical thresholds
    CRITICAL_OXYGEN_THRESHOLD = 90.0  # SpO2 below 90% is critical
    
    @staticmethod
    def assess_triage_level(patient: Patient) -> str:
        """
        Assess patient triage level based on vitals and symptoms.
        
        Rules:
        - Chest pain OR oxygen saturation < 90% → CRITICAL
        - Otherwise → URGENT or NORMAL (simplified for MVP)
        
        Args:
            patient: Patient object with vitals
            
        Returns:
            Triage level: "CRITICAL", "URGENT", or "NORMAL"
        """
        # Rule 1: Chest pain → CRITICAL
        if patient.chest_pain:
            return "CRITICAL"
        
        # Rule 2: Low oxygen saturation → CRITICAL
        if patient.oxygen_saturation is not None:
            if patient.oxygen_saturation < TriageService.CRITICAL_OXYGEN_THRESHOLD:
                return "CRITICAL"
        
        # Additional critical indicators (can be expanded)
        # Very high heart rate (> 150) or very low (< 40)
        if patient.heart_rate is not None:
            if patient.heart_rate > 150 or patient.heart_rate < 40:
                return "CRITICAL"
        
        # Very high or very low blood pressure
        if patient.blood_pressure_systolic is not None:
            if patient.blood_pressure_systolic > 180 or patient.blood_pressure_systolic < 80:
                return "CRITICAL"
        
        # Default to URGENT for emergency cases (can be refined)
        return "URGENT"
    
    @staticmethod
    def update_patient_triage(db: Session, patient_id: int) -> Patient:
        """
        Update patient triage level based on current vitals.
        
        Args:
            db: Database session
            patient_id: Patient ID
            
        Returns:
            Updated Patient object
        """
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        triage_level = TriageService.assess_triage_level(patient)
        patient.triage_level = triage_level
        db.commit()
        db.refresh(patient)
        
        return patient
    
    @staticmethod
    def should_create_referral(patient: Patient, db: Session) -> bool:
        """
        Determine if a referral should be created for this patient.
        
        Rule: If CRITICAL and center_type == "Centre de Santé" → auto-create referral
        
        Args:
            patient: Patient object
            db: Database session
            
        Returns:
            True if referral should be created, False otherwise
        """
        # Check if patient is CRITICAL
        if patient.triage_level != "CRITICAL":
            return False
        
        # Get patient's health center
        health_center = db.query(HealthCenter).filter(
            HealthCenter.id == patient.health_center_id
        ).first()
        
        if not health_center:
            return False
        
        # Only create referral if from "Centre de Santé"
        if health_center.center_type == "Centre de Santé":
            return True
        
        return False

