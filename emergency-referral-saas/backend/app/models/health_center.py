"""
Health Center model for Centres de Santé and CHU.
"""
from sqlalchemy import Column, Integer, String
from app.core.database import Base


class HealthCenter(Base):
    """Health Center model representing Centres de Santé and CHU."""
    
    __tablename__ = "health_centers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    center_type = Column(String, nullable=False)  # "Centre de Santé" or "CHU"
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<HealthCenter(id={self.id}, name={self.name}, type={self.center_type})>"

