"""
Referral routes for managing patient referrals.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.models.referral import Referral
from app.schemas.referral import ReferralCreate, ReferralUpdate, ReferralResponse, ReferralWithPatient
from app.services.referral_service import ReferralService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.post("", response_model=ReferralResponse, status_code=status.HTTP_201_CREATED)
async def create_referral(
    referral_data: ReferralCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("nurse"))
):
    """
    Manually create a referral for a patient.
    
    Args:
        referral_data: Referral creation data
        db: Database session
        current_user: Current authenticated user (nurse or doctor)
        
    Returns:
        Created referral object
        
    Raises:
        HTTPException: If patient or health center not found
    """
    try:
        referral = ReferralService.create_referral(
            db=db,
            patient_id=referral_data.patient_id,
            to_center_id=referral_data.to_center_id,
            created_by=current_user.id,
            reason=referral_data.reason,
            clinical_notes=referral_data.clinical_notes
        )
        
        # Send notification
        await NotificationService.notify_new_referral({
            "referral_id": referral.id,
            "patient_id": referral.patient_id,
            "status": referral.status,
            "priority": referral.priority
        })
        
        return referral
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[ReferralResponse])
async def list_referrals(
    status_filter: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List referrals with role-based filtering.
    
    - Nurses see referrals from their health center
    - Doctors see referrals to their CHU
    
    Args:
        status_filter: Optional status filter (CREATED, SENT, ACCEPTED, TRANSFERRED)
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of referral objects
    """
    from app.models.referral import Referral
    
    query = db.query(Referral)
    
    # Role-based filtering
    if current_user.role == "nurse" and current_user.health_center_id:
        # Nurses see referrals FROM their center
        query = query.filter(Referral.from_center_id == current_user.health_center_id)
    elif current_user.role == "doctor" and current_user.health_center_id:
        # Doctors see referrals TO their CHU
        query = query.filter(Referral.to_center_id == current_user.health_center_id)
    
    # Apply status filter if provided
    if status_filter:
        query = query.filter(Referral.status == status_filter)
    
    referrals = query.order_by(Referral.created_at.desc()).offset(skip).limit(limit).all()
    return referrals


@router.get("/{referral_id}", response_model=ReferralWithPatient)
async def get_referral(
    referral_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific referral by ID with patient details.
    
    Args:
        referral_id: Referral ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Referral object with patient details
        
    Raises:
        HTTPException: If referral not found
    """
    referral = db.query(Referral).filter(Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Referral with ID {referral_id} not found"
        )
    
    # Role-based access check
    if current_user.role == "nurse" and current_user.health_center_id:
        if referral.from_center_id != current_user.health_center_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: This referral does not belong to your health center"
            )
    elif current_user.role == "doctor" and current_user.health_center_id:
        if referral.to_center_id != current_user.health_center_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: This referral is not for your CHU"
            )
    
    return referral


@router.post("/{referral_id}/send", response_model=ReferralResponse)
async def send_referral(
    referral_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("nurse", "doctor"))
):
    """
    Send a referral (mark as SENT) - notifies destination CHU.
    
    Args:
        referral_id: Referral ID
        db: Database session
        current_user: Current authenticated user (nurse or doctor)
        
    Returns:
        Updated referral object
        
    Raises:
        HTTPException: If referral not found or invalid status
    """
    try:
        referral = ReferralService.send_referral(db, referral_id)
        
        # Send notification
        await NotificationService.notify_referral_status_change(
            referral_id=referral.id,
            new_status=referral.status,
            referral_data={
                "referral_id": referral.id,
                "patient_id": referral.patient_id,
                "status": referral.status
            }
        )
        
        return referral
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{referral_id}/accept", response_model=ReferralResponse)
async def accept_referral(
    referral_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    """
    Accept a referral (CHU accepts the patient).
    
    Only doctors can accept referrals.
    
    Args:
        referral_id: Referral ID
        db: Database session
        current_user: Current authenticated user (doctor)
        
    Returns:
        Updated referral object
        
    Raises:
        HTTPException: If referral not found or invalid status
    """
    try:
        referral = ReferralService.accept_referral(db, referral_id, current_user.id)
        
        # Send notification
        await NotificationService.notify_referral_accepted({
            "referral_id": referral.id,
            "patient_id": referral.patient_id,
            "accepted_by": current_user.full_name,
            "status": referral.status
        })
        
        return referral
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{referral_id}/transfer", response_model=ReferralResponse)
async def mark_transferred(
    referral_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("nurse", "doctor"))
):
    """
    Mark referral as TRANSFERRED (patient has been transferred).
    
    Args:
        referral_id: Referral ID
        db: Database session
        current_user: Current authenticated user (nurse or doctor)
        
    Returns:
        Updated referral object
        
    Raises:
        HTTPException: If referral not found or invalid status
    """
    try:
        referral = ReferralService.mark_transferred(db, referral_id)
        
        # Send notification
        await NotificationService.notify_referral_status_change(
            referral_id=referral.id,
            new_status=referral.status,
            referral_data={
                "referral_id": referral.id,
                "patient_id": referral.patient_id,
                "status": referral.status
            }
        )
        
        return referral
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

