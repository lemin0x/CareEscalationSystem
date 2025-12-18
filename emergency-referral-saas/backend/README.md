# Emergency Referral SaaS - Backend

FastAPI backend for emergency referral system in Morocco. Centres de Santé handle basic emergencies, and CRITICAL cases are digitally referred to CHU (Centre Hospitalier Universitaire).

## Tech Stack

- **FastAPI** (Python web framework)
- **SQLite** (Database)
- **SQLAlchemy** (ORM)
- **JWT Authentication** (Roles: nurse, doctor)
- **WebSockets** (Real-time alerts)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Database

The SQLite database (`emergency_referral.db`) will be automatically created on first run.

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user (nurse or doctor)
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Patients

- `POST /api/patients` - Register a new patient
- `GET /api/patients` - List all patients
- `GET /api/patients/{id}` - Get patient by ID
- `PATCH /api/patients/{id}` - Update patient information

### Triage

- `POST /api/triage/{patient_id}/assess` - Assess patient triage level

**Triage Rules:**
- Chest pain OR oxygen saturation < 90% → **CRITICAL**
- Other vitals may also trigger CRITICAL status

### Referrals

- `POST /api/referrals` - Create a referral manually
- `GET /api/referrals` - List all referrals (optional `?status_filter=CREATED`)
- `GET /api/referrals/{id}` - Get referral by ID
- `POST /api/referrals/{id}/send` - Send referral (mark as SENT)
- `POST /api/referrals/{id}/accept` - Accept referral (doctor only)
- `POST /api/referrals/{id}/transfer` - Mark as TRANSFERRED

**Referral Lifecycle:**
```
CREATED → SENT → ACCEPTED → TRANSFERRED
```

### Assignments

- `POST /api/assignments/{referral_id}/assign?chu_id={id}` - Assign referral to CHU

## WebSocket

Connect to `/ws` for real-time notifications:

**Events:**
- `new_referral` - When a new referral is created
- `referral_accepted` - When a referral is accepted
- `referral_status_changed` - When referral status changes

## Auto-Referral Logic

When a patient is registered or updated:

1. **Triage Assessment**: Patient vitals are assessed
2. **If CRITICAL** and patient is at a **Centre de Santé**:
   - Automatically creates a referral to the first available CHU
   - Sends WebSocket notification

## Example Usage

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nurse1",
    "email": "nurse1@example.com",
    "password": "password123",
    "full_name": "Nurse One",
    "role": "nurse",
    "health_center_id": 1
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=nurse1&password=password123"
```

### 3. Register a Patient (with JWT token)

```bash
curl -X POST "http://localhost:8000/api/patients" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Ahmed",
    "last_name": "Benali",
    "age": 45,
    "gender": "M",
    "health_center_id": 1,
    "oxygen_saturation": 85.0,
    "chest_pain": true,
    "chief_complaint": "Severe chest pain"
  }'
```

This will automatically:
- Assess triage as **CRITICAL** (chest pain + low oxygen)
- Create referral to CHU if patient is at Centre de Santé
- Send WebSocket notification

## Project Structure

```
backend/
└─ app/
   ├─ main.py                 # FastAPI app entry point
   ├─ core/                   # Configuration, database, security
   ├─ models/                 # SQLAlchemy models
   ├─ schemas/                # Pydantic schemas
   ├─ services/              # Business logic
   │   ├─ triage_service.py
   │   ├─ referral_service.py
   │   ├─ assignment_service.py
   │   └─ notification_service.py
   ├─ api/routes/            # API endpoints
   │   ├─ auth.py
   │   ├─ patients.py
   │   ├─ triage.py
   │   └─ referrals.py
   └─ websocket/             # WebSocket manager
      └─ manager.py
```

## Environment Variables


## Notes

- This is an MVP for hackathon purposes
- Database is SQLite (simple, no setup required)
- JWT tokens expire after 30 minutes (configurable)
- WebSocket connections are managed in-memory (for MVP)
- Auto-referral assigns to first available CHU (simplified)

## Testing

Use the interactive docs at `/docs` to test all endpoints with authentication.

