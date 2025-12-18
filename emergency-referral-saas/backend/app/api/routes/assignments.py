"""
Assignment routes (simplified for MVP - can be expanded later).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.models.referral import Referral
from app.schemas.referral import ReferralResponse
from app.services.assignment_service import AssignmentService

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/{referral_id}/assign", response_model=ReferralResponse)
async def assign_referral(
    referral_id: int,
    chu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    """
    Assign a referral to a specific CHU.
    
    Only doctors can assign referrals.
    
    Args:
        referral_id: Referral ID
        chu_id: CHU health center ID
        db: Database session
        current_user: Current authenticated user (doctor)
        
    Returns:
        Updated referral object
        
    Raises:
        HTTPException: If referral or CHU not found
    """
    try:
        referral = AssignmentService.assign_referral_to_chu(
            db=db,
            referral_id=referral_id,
            chu_id=chu_id
        )
        return referral
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

