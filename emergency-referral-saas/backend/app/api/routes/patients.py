"""
Patient routes for patient registration and management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.models.patient import Patient
from app.models.health_center import HealthCenter
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.services.triage_service import TriageService
from app.services.referral_service import ReferralService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Register a new patient (POST /patients).
    
    After registration:
    - Assesses triage level
    - If CRITICAL and from Centre de Santé → auto-creates referral to CHU
    
    Args:
        patient_data: Patient registration data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created patient object
        
    Raises:
        HTTPException: If health center not found
    """
    # Verify health center exists
    health_center = db.query(HealthCenter).filter(
        HealthCenter.id == patient_data.health_center_id
    ).first()
    
    if not health_center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Health center with ID {patient_data.health_center_id} not found"
        )
    
    # Create patient
    new_patient = Patient(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        age=patient_data.age,
        gender=patient_data.gender,
        national_id=patient_data.national_id,
        phone=patient_data.phone,
        address=patient_data.address,
        oxygen_saturation=patient_data.oxygen_saturation,
        heart_rate=patient_data.heart_rate,
        blood_pressure_systolic=patient_data.blood_pressure_systolic,
        blood_pressure_diastolic=patient_data.blood_pressure_diastolic,
        temperature=patient_data.temperature,
        chest_pain=patient_data.chest_pain,
        chief_complaint=patient_data.chief_complaint,
        notes=patient_data.notes,
        health_center_id=patient_data.health_center_id,
        registered_by=current_user.id
    )
    
    db.add(new_patient)
    db.flush()  # Flush to get patient ID
    
    # Assess triage level
    triage_level = TriageService.assess_triage_level(new_patient)
    new_patient.triage_level = triage_level
    
    db.commit()
    db.refresh(new_patient)
    
    # Auto-create referral if CRITICAL and from Centre de Santé
    referral = None
    if TriageService.should_create_referral(new_patient, db):
        try:
            referral = ReferralService.auto_create_referral_for_critical_patient(
                db=db,
                patient_id=new_patient.id,
                created_by=current_user.id
            )
            
            # Send notification for new referral
            if referral:
                await NotificationService.notify_new_referral({
                    "referral_id": referral.id,
                    "patient_id": new_patient.id,
                    "patient_name": f"{new_patient.first_name} {new_patient.last_name}",
                    "from_center": health_center.name,
                    "priority": referral.priority,
                    "status": referral.status
                })
        except Exception as e:
            # Log error but don't fail patient creation
            print(f"Error creating auto-referral: {e}")
    
    return new_patient


@router.get("", response_model=List[PatientResponse])
async def list_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all patients with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of patient objects
    """
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific patient by ID.
    
    Args:
        patient_id: Patient ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Patient object
        
    Raises:
        HTTPException: If patient not found
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("nurse", "doctor"))
):
    """
    Update patient information and vitals.
    
    If vitals are updated, triage level is reassessed.
    If triage becomes CRITICAL and from Centre de Santé → auto-creates referral.
    
    Args:
        patient_id: Patient ID
        patient_update: Patient update data
        db: Database session
        current_user: Current authenticated user (nurse or doctor)
        
    Returns:
        Updated patient object
        
    Raises:
        HTTPException: If patient not found
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    # Update fields
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    # Reassess triage level if vitals were updated
    if any(key in update_data for key in [
        "oxygen_saturation", "heart_rate", "blood_pressure_systolic",
        "blood_pressure_diastolic", "temperature", "chest_pain"
    ]):
        triage_level = TriageService.assess_triage_level(patient)
        patient.triage_level = triage_level
        
        # Auto-create referral if now CRITICAL and from Centre de Santé
        if TriageService.should_create_referral(patient, db):
            try:
                referral = ReferralService.auto_create_referral_for_critical_patient(
                    db=db,
                    patient_id=patient.id,
                    created_by=current_user.id
                )
                
                # Send notification
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
    
    db.commit()
    db.refresh(patient)
    
    return patient

