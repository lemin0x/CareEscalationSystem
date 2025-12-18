"""
Triage routes for patient triage assessment.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.models.patient import Patient
from app.schemas.patient import PatientResponse
from app.services.triage_service import TriageService
from app.services.referral_service import ReferralService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/triage", tags=["triage"])


@router.post("/{patient_id}/assess", response_model=PatientResponse)
async def assess_triage(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("nurse", "doctor"))
):
    """
    Assess and update patient triage level based on current vitals.
    
    Rule-based triage:
    - Chest pain OR oxygen saturation < 90% → CRITICAL
    - Other vitals may also trigger CRITICAL
    
    If CRITICAL and from Centre de Santé → auto-creates referral to CHU.
    
    Args:
        patient_id: Patient ID
        db: Database session
        current_user: Current authenticated user (nurse or doctor)
        
    Returns:
        Updated patient object with triage level
        
    Raises:
        HTTPException: If patient not found
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    # Assess triage level
    triage_level = TriageService.assess_triage_level(patient)
    patient.triage_level = triage_level
    
    db.commit()
    db.refresh(patient)
    
    # Auto-create referral if CRITICAL and from Centre de Santé
    referral = None
    if TriageService.should_create_referral(patient, db):
        try:
            referral = ReferralService.auto_create_referral_for_critical_patient(
                db=db,
                patient_id=patient.id,
                created_by=current_user.id
            )
            
            # Send notification for new referral
            if referral:
                await NotificationService.notify_new_referral({
                    "referral_id": referral.id,
                    "patient_id": patient.id,
                    "patient_name": f"{patient.first_name} {patient.last_name}",
                    "priority": referral.priority,
                    "status": referral.status
                })
        except Exception as e:
            print(f"Error creating auto-referral: {e}")
    
    return patient

