# Emergency Referral System - Frontend

React + Vite frontend for the Emergency Referral SaaS system connecting Centres de Santé and CHUs in Morocco.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **WebSockets** - Real-time updates

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Backend Requirements

Make sure the backend is running on `http://localhost:8000` before starting the frontend.

## Features

### Login Page
- Simple username/password authentication
- Role-based routing (nurse → Centre de Santé, doctor → CHU)

### Centre de Santé Dashboard
- Patient registration form with vitals
- Urgency indicator (green/yellow/red) based on triage level
- Referral status badges
- Real-time updates via WebSocket

### CHU Dashboard
- List of incoming referrals
- Accept referral button (doctors only)
- Live updates when new referrals arrive
- Real-time notifications

## API Integration

The frontend integrates with these backend endpoints:
- `POST /api/auth/login` - User authentication
- `POST /api/patients` - Register new patient
- `POST /api/triage/{patient_id}/assess` - Assess patient triage
- `GET /api/referrals` - List referrals
- `POST /api/referrals/{id}/accept` - Accept referral

## WebSocket Events

The app listens for these WebSocket events:
- `new_referral` - When a new referral is created
- `referral_accepted` - When a referral is accepted
- `referral_status_changed` - When referral status changes

## Project Structure

```
src/
├── components/       # Reusable UI components
├── context/         # React context (Auth)
├── pages/           # Page components
├── services/        # API and WebSocket services
├── App.tsx          # Main app component with routing
└── main.tsx         # Entry point
```

