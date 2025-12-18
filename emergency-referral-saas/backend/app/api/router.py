"""
Main API router that combines all route modules.
"""
from fastapi import APIRouter
from app.api.routes import (
    auth, 
    patients, 
    triage, 
    referrals, 
    assignments, 
    health_centers  # Add this import
)

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(health_centers.router)  # Add this line first
api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(triage.router)
api_router.include_router(referrals.router)
api_router.include_router(assignments.router)