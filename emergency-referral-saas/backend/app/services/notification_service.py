"""
Notification service for WebSocket real-time alerts.
"""
from typing import Dict, Any
from app.websocket.manager import websocket_manager


class NotificationService:
    """Service for sending real-time notifications via WebSocket."""
    
    @staticmethod
    async def notify_new_referral(referral_data: Dict[str, Any]):
        """
        Send WebSocket notification for a new referral.
        
        Args:
            referral_data: Dictionary containing referral information
        """
        await websocket_manager.broadcast({
            "event": "new_referral",
            "data": referral_data
        })
    
    @staticmethod
    async def notify_referral_accepted(referral_data: Dict[str, Any]):
        """
        Send WebSocket notification when a referral is accepted.
        
        Args:
            referral_data: Dictionary containing referral information
        """
        await websocket_manager.broadcast({
            "event": "referral_accepted",
            "data": referral_data
        })
    
    @staticmethod
    async def notify_referral_status_change(
        referral_id: int,
        new_status: str,
        referral_data: Dict[str, Any]
    ):
        """
        Send WebSocket notification for any referral status change.
        
        Args:
            referral_id: Referral ID
            new_status: New status
            referral_data: Dictionary containing referral information
        """
        await websocket_manager.broadcast({
            "event": "referral_status_changed",
            "data": {
                "referral_id": referral_id,
                "status": new_status,
                **referral_data
            }
        })

