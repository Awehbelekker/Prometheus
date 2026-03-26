"""
📧 PROMETHEUS Trading Platform - Enhanced Notification Service
Customizable notification system with user preferences and frequency controls
"""

import logging
import json
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session

from core.models import User, UserPermissions
from core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    TRADE_CONFIRMATION = "trade_confirmation"
    PERFORMANCE_UPDATE = "performance_update"
    PROFIT_ALERT = "profit_alert"
    LOSS_ALERT = "loss_alert"
    GAMIFICATION_ACHIEVEMENT = "gamification_achievement"
    MARKET_ALERT = "market_alert"
    SYSTEM_NOTIFICATION = "system_notification"
    INVITATION_RECEIVED = "invitation_received"

class NotificationFrequency(Enum):
    INSTANT = "instant"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NEVER = "never"

@dataclass
class NotificationPreference:
    """User notification preference"""
    user_id: str
    notification_type: NotificationType
    frequency: NotificationFrequency
    email_enabled: bool = True
    push_enabled: bool = False
    threshold: Optional[float] = None  # For profit/loss alerts

@dataclass
class NotificationMessage:
    """Notification message"""
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    data: Dict[str, Any]
    priority: str = "normal"  # low, normal, high, urgent
    created_at: datetime = None

class EnhancedNotificationService:
    """Enhanced notification service with user preferences"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.user_preferences = {}
        self.pending_notifications = {}
        self.smtp_config = self._load_smtp_config()
        
        logger.info("📧 Enhanced Notification Service initialized")

    def _load_smtp_config(self) -> Dict[str, str]:
        """Load SMTP configuration"""
        return {
            "smtp_server": "smtp.gmail.com",  # Configure as needed
            "smtp_port": 587,
            "username": "",  # Configure from environment
            "password": "",  # Configure from environment
            "from_email": "noreply@prometheus-trading.com"
        }

    async def set_user_preferences(self, user_id: str, preferences: List[NotificationPreference]) -> Dict[str, Any]:
        """Set user notification preferences"""
        try:
            self.user_preferences[user_id] = {
                pref.notification_type.value: pref for pref in preferences
            }
            
            # Save to database (extend User model to include notification preferences)
            with self.db_manager.get_session() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if user:
                    # Store preferences as JSON in user profile
                    prefs_json = json.dumps({
                        pref.notification_type.value: {
                            "frequency": pref.frequency.value,
                            "email_enabled": pref.email_enabled,
                            "push_enabled": pref.push_enabled,
                            "threshold": pref.threshold
                        }
                        for pref in preferences
                    })
                    # This would require adding notification_preferences column to User model
                    # user.notification_preferences = prefs_json
                    session.commit()
            
            logger.info(f"[CHECK] Updated notification preferences for user {user_id}")
            
            return {
                "success": True,
                "preferences_updated": len(preferences),
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to set user preferences: {e}")
            return {"success": False, "error": str(e)}

    async def send_notification(self, notification: NotificationMessage) -> Dict[str, Any]:
        """Send notification based on user preferences"""
        try:
            user_prefs = self.user_preferences.get(notification.user_id, {})
            pref = user_prefs.get(notification.notification_type.value)
            
            if not pref or pref.frequency == NotificationFrequency.NEVER:
                return {"success": True, "skipped": "User preferences disabled"}
            
            # Check frequency limits
            if not self._should_send_now(notification.user_id, notification.notification_type, pref.frequency):
                # Queue for later
                await self._queue_notification(notification)
                return {"success": True, "queued": True}
            
            # Send based on enabled channels
            results = {}
            
            if pref.email_enabled:
                email_result = await self._send_email_notification(notification)
                results["email"] = email_result
            
            if pref.push_enabled:
                push_result = await self._send_push_notification(notification)
                results["push"] = push_result
            
            # Record notification sent
            await self._record_notification_sent(notification)
            
            logger.info(f"📧 Sent notification to user {notification.user_id}: {notification.title}")
            
            return {
                "success": True,
                "notification_sent": True,
                "channels": results
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to send notification: {e}")
            return {"success": False, "error": str(e)}

    async def send_trade_confirmation(self, user_id: str, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send trade confirmation notification"""
        notification = NotificationMessage(
            user_id=user_id,
            notification_type=NotificationType.TRADE_CONFIRMATION,
            title=f"Trade Executed: {trade_data.get('symbol', 'Unknown')}",
            message=f"Your {trade_data.get('side', 'trade')} order for {trade_data.get('quantity', 0)} shares of {trade_data.get('symbol', 'Unknown')} has been executed at ${trade_data.get('price', 0):.2f}",
            data=trade_data,
            priority="normal",
            created_at=datetime.utcnow()
        )
        
        return await self.send_notification(notification)

    async def send_performance_update(self, user_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send performance update notification"""
        notification = NotificationMessage(
            user_id=user_id,
            notification_type=NotificationType.PERFORMANCE_UPDATE,
            title="Portfolio Performance Update",
            message=f"Your portfolio is {performance_data.get('change_direction', 'up')} {performance_data.get('change_percent', 0):.2f}% today. Total value: ${performance_data.get('total_value', 0):,.2f}",
            data=performance_data,
            priority="normal",
            created_at=datetime.utcnow()
        )
        
        return await self.send_notification(notification)

    async def send_gamification_achievement(self, user_id: str, achievement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send gamification achievement notification"""
        notification = NotificationMessage(
            user_id=user_id,
            notification_type=NotificationType.GAMIFICATION_ACHIEVEMENT,
            title=f"🏆 Achievement Unlocked: {achievement_data.get('name', 'Unknown')}",
            message=f"Congratulations! You've earned the '{achievement_data.get('name', 'Unknown')}' badge and {achievement_data.get('xp_reward', 0)} XP points!",
            data=achievement_data,
            priority="high",
            created_at=datetime.utcnow()
        )
        
        return await self.send_notification(notification)

    def _should_send_now(self, user_id: str, notification_type: NotificationType, frequency: NotificationFrequency) -> bool:
        """Check if notification should be sent now based on frequency"""
        if frequency == NotificationFrequency.INSTANT:
            return True
        
        # Check last sent time for this user and notification type
        last_sent_key = f"{user_id}_{notification_type.value}_last_sent"
        last_sent = self.pending_notifications.get(last_sent_key)
        
        if not last_sent:
            return True
        
        now = datetime.utcnow()
        time_diff = now - last_sent
        
        if frequency == NotificationFrequency.HOURLY:
            return time_diff >= timedelta(hours=1)
        elif frequency == NotificationFrequency.DAILY:
            return time_diff >= timedelta(days=1)
        elif frequency == NotificationFrequency.WEEKLY:
            return time_diff >= timedelta(weeks=1)
        elif frequency == NotificationFrequency.MONTHLY:
            return time_diff >= timedelta(days=30)
        
        return False

    async def _send_email_notification(self, notification: NotificationMessage) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Get user email
            with self.db_manager.get_session() as session:
                user = session.query(User).filter_by(id=notification.user_id).first()
                if not user or not user.email:
                    return {"success": False, "error": "User email not found"}
                
                # Create email
                msg = MIMEMultipart()
                msg['From'] = self.smtp_config['from_email']
                msg['To'] = user.email
                msg['Subject'] = notification.title
                
                # Create HTML email body
                html_body = self._create_email_template(notification)
                msg.attach(MIMEText(html_body, 'html'))
                
                # Send email (if SMTP configured)
                if self.smtp_config.get('username') and self.smtp_config.get('password'):
                    server = smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port'])
                    server.starttls()
                    server.login(self.smtp_config['username'], self.smtp_config['password'])
                    server.send_message(msg)
                    server.quit()
                    
                    return {"success": True, "email_sent": True}
                else:
                    logger.info(f"📧 Email notification created (SMTP not configured): {notification.title}")
                    return {"success": True, "email_created": True, "smtp_configured": False}
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to send email: {e}")
            return {"success": False, "error": str(e)}

    async def _send_push_notification(self, notification: NotificationMessage) -> Dict[str, Any]:
        """Send push notification (placeholder for future implementation)"""
        logger.info(f"📱 Push notification: {notification.title}")
        return {"success": True, "push_sent": True}

    def _create_email_template(self, notification: NotificationMessage) -> str:
        """Create HTML email template"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #1a1a2e; color: white; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 10px; padding: 30px;">
                <h1 style="color: #00d4ff; text-align: center;">🚀 PROMETHEUS Trading Platform</h1>
                <h2 style="color: #ff6b35;">{notification.title}</h2>
                <p style="font-size: 16px; line-height: 1.6;">{notification.message}</p>
                
                <div style="background: rgba(0, 212, 255, 0.1); border-left: 4px solid #00d4ff; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Notification Type:</strong> {notification.notification_type.value.replace('_', ' ').title()}</p>
                    <p style="margin: 5px 0 0 0;"><strong>Time:</strong> {notification.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if notification.created_at else 'Now'}</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://prometheus-trading.com/dashboard" style="background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%); color: #000; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Dashboard</a>
                </div>
                
                <p style="font-size: 12px; color: #aaa; text-align: center; margin-top: 30px;">
                    You can manage your notification preferences in your account settings.
                </p>
            </div>
        </body>
        </html>
        """

    async def _queue_notification(self, notification: NotificationMessage):
        """Queue notification for later sending"""
        queue_key = f"{notification.user_id}_{notification.notification_type.value}_queue"
        if queue_key not in self.pending_notifications:
            self.pending_notifications[queue_key] = []
        self.pending_notifications[queue_key].append(notification)

    async def _record_notification_sent(self, notification: NotificationMessage):
        """Record that notification was sent"""
        sent_key = f"{notification.user_id}_{notification.notification_type.value}_last_sent"
        self.pending_notifications[sent_key] = datetime.utcnow()

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        try:
            prefs = self.user_preferences.get(user_id, {})
            return {
                "success": True,
                "user_id": user_id,
                "preferences": {
                    pref_type: {
                        "frequency": pref.frequency.value,
                        "email_enabled": pref.email_enabled,
                        "push_enabled": pref.push_enabled,
                        "threshold": pref.threshold
                    }
                    for pref_type, pref in prefs.items()
                }
            }
        except Exception as e:
            logger.error(f"[ERROR] Failed to get user preferences: {e}")
            return {"success": False, "error": str(e)}

# Global service instance
notification_service = None

def get_notification_service() -> EnhancedNotificationService:
    """Get global notification service instance"""
    global notification_service
    if notification_service is None:
        from core.database_manager import db_manager
        notification_service = EnhancedNotificationService(db_manager)
    return notification_service
