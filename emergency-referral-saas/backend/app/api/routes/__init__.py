"""
API routes package.
"""
from app.api.routes import auth, patients, triage, referrals, assignments

__all__ = ["auth", "patients", "triage", "referrals", "assignments"]

