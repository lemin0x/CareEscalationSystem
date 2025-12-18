"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.router import api_router
from app.websocket.manager import websocket_manager

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Emergency Referral SaaS for Morocco - MVP",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("Database initialized")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Emergency Referral SaaS API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications.
    
    Events:
    - new_referral: When a new referral is created
    - referral_accepted: When a referral is accepted
    - referral_status_changed: When referral status changes
    """
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back (can be extended for bidirectional communication)
            await websocket_manager.send_personal_message(
                {"message": "Connection active", "received": data},
                websocket
            )
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        print("WebSocket client disconnected")

