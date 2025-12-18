"""
Seed script for initializing health centers and demo users.
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.health_center import HealthCenter
from app.models.user import User
from app.core.security import get_password_hash


def seed_health_centers(db: Session):
    """Seed health centers (Centres de Santé and CHU)."""
    
    # Check if centers already exist
    existing = db.query(HealthCenter).first()
    if existing:
        print("Health centers already seeded, skipping...")
        return
    
    centers = [
        HealthCenter(
            name="Centre de Santé Ibn Sina",
            center_type="Centre de Santé",
            address="123 Avenue Mohammed V",
            city="Casablanca",
            phone="+212 522-123456"
        ),
        HealthCenter(
            name="Centre de Santé Al Kindi",
            center_type="Centre de Santé",
            address="456 Boulevard Zerktouni",
            city="Casablanca",
            phone="+212 522-234567"
        ),
        HealthCenter(
            name="CHU Ibn Rochd",
            center_type="CHU",
            address="789 Boulevard de la Corniche",
            city="Casablanca",
            phone="+212 522-345678"
        ),
        HealthCenter(
            name="CHU Mohammed VI",
            center_type="CHU",
            address="321 Avenue Allal Ben Abdellah",
            city="Rabat",
            phone="+212 537-123456"
        ),
    ]
    
    for center in centers:
        db.add(center)
    
    db.commit()
    print(f"✅ Seeded {len(centers)} health centers")


def seed_demo_users(db: Session):
    """Seed demo users (nurse and doctor)."""
    
    # Check if users already exist
    existing = db.query(User).first()
    if existing:
        print("Demo users already seeded, skipping...")
        return
    
    # Get health centers
    center_1 = db.query(HealthCenter).filter(
        HealthCenter.center_type == "Centre de Santé"
    ).first()
    
    chu_1 = db.query(HealthCenter).filter(
        HealthCenter.center_type == "CHU"
    ).first()
    
    if not center_1 or not chu_1:
        print("⚠️  Warning: Health centers not found. Run seed_health_centers first.")
        return
    
    users = [
        User(
            username="nurse1",
            email="nurse1@demo.com",
            hashed_password=get_password_hash("nurse123"),
            full_name="Fatima Alami",
            role="nurse",
            health_center_id=center_1.id,
            is_active=True
        ),
        User(
            username="doctor1",
            email="doctor1@demo.com",
            hashed_password=get_password_hash("doctor123"),
            full_name="Dr. Ahmed Benali",
            role="doctor",
            health_center_id=chu_1.id,
            is_active=True
        ),
    ]
    
    for user in users:
        db.add(user)
    
    db.commit()
    print(f"✅ Seeded {len(users)} demo users")
    print("\n📝 Demo credentials:")
    print("   Nurse: nurse1 / nurse123")
    print("   Doctor: doctor1 / doctor123")


def main():
    """Run all seed functions."""
    print("🌱 Starting database seeding...\n")
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    try:
        seed_health_centers(db)
        seed_demo_users(db)
        print("\n✅ Seeding complete!")
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

