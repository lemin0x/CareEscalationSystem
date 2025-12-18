"""
Health Centers API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.health_center import HealthCenter
from app.schemas.health_center import HealthCenterCreate, HealthCenter as HealthCenterSchema

router = APIRouter()


@router.post("/health-centers", response_model=HealthCenterSchema)
async def create_health_center(
    health_center: HealthCenterCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new health center.
    """
    db_health_center = HealthCenter(**health_center.model_dump())
    db.add(db_health_center)
    db.commit()
    db.refresh(db_health_center)
    return db_health_center


@router.get("/health-centers", response_model=List[HealthCenterSchema])
async def get_health_centers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Get all health centers.
    """
    health_centers = db.query(HealthCenter).offset(skip).limit(limit).all()
    return health_centers