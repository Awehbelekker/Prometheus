"""
🚀 PROMETHEUS Trading Platform - Unified Invitation & Permission Service
Consolidates all invitation functionality with best practices
"""

import asyncio
import logging
import secrets
import smtplib
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os
import json

from sqlalchemy.orm import Session
from core.models import Invitation, UserPermissions, InvitationTracking, GamificationProgress, User
from core.database_manager import DatabaseManager
from core.auth.unified_auth_service import UnifiedAuthService

logger = logging.getLogger(__name__)

class UserTier(Enum):
    STANDARD = "standard"  # Internal Paper Trading + Gamification
    POOL_INVESTOR = "pool_investor"  # Live Trading with Allocated Funds

class InvitationStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    USED = "used"
    REVOKED = "revoked"

@dataclass
class InvitationRequest:
    """Request to create a new invitation"""
    email: str
    name: str
    user_tier: UserTier
    allocated_funds: float = 0.0
    max_position_size: float = 0.0
    daily_loss_limit: float = 0.0
    broker_access: List[str] = None
    invitation_message: str = ""
    expires_hours: int = 168  # 7 days default

@dataclass
class InvitationResponse:
    """Response from invitation creation"""
    success: bool
    invitation_code: str = ""
    invitation_token: str = ""
    expires_at: datetime = None
    registration_link: str = ""
    error_message: str = ""

class UnifiedInvitationService:
    """Unified invitation and permission management service"""
    
    def __init__(self, db_manager: DatabaseManager, auth_service: UnifiedAuthService):
        self.db_manager = db_manager
        self.auth_service = auth_service
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        self.email_from = os.getenv('EMAIL_FROM', 'noreply@prometheus-trading.com')
        
        logger.info("🚀 Unified Invitation Service initialized")

    async def create_invitation(self, request: InvitationRequest, created_by: str) -> InvitationResponse:
        """Create a new user invitation"""
        try:
            # Check if email already has pending invitation
            existing = self._get_pending_invitation(request.email)
            if existing:
                return InvitationResponse(
                    success=False,
                    error_message="User already has a pending invitation"
                )
            
            # Generate unique codes
            invitation_code = self._generate_invitation_code()
            invitation_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=request.expires_hours)
            
            # Create invitation record
            invitation = Invitation(
                code=invitation_code,
                email=request.email,
                role="investor" if request.user_tier == UserTier.POOL_INVESTOR else "user",
                user_tier=request.user_tier.value,
                allocated_capital=request.allocated_funds,
                expires_at=expires_at,
                created_by=created_by,
                invitation_token=invitation_token,
                invited_name=request.name,
                invitation_message=request.invitation_message,
                max_position_size=request.max_position_size,
                daily_loss_limit=request.daily_loss_limit,
                broker_access=json.dumps(request.broker_access or ["interactive_brokers", "alpaca"])
            )
            
            # Store in database
            with self.db_manager.get_session() as session:
                session.add(invitation)
                session.commit()
            
            # Send invitation email
            registration_link = f"{self.frontend_url}/register?token={invitation_token}"
            await self._send_invitation_email(invitation, registration_link)
            
            # Track invitation event
            self._track_invitation_event(invitation_code, "invitation_sent", {
                "email": request.email,
                "user_tier": request.user_tier.value,
                "created_by": created_by
            })
            
            logger.info(f"[CHECK] Invitation created for {request.email} (tier: {request.user_tier.value})")
            
            return InvitationResponse(
                success=True,
                invitation_code=invitation_code,
                invitation_token=invitation_token,
                expires_at=expires_at,
                registration_link=registration_link
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to create invitation: {e}")
            return InvitationResponse(
                success=False,
                error_message=str(e)
            )

    async def register_from_invitation(self, invitation_token: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register user from invitation token"""
        try:
            # Get invitation by token
            with self.db_manager.get_session() as session:
                invitation = session.query(Invitation).filter_by(
                    invitation_token=invitation_token,
                    status=InvitationStatus.ACTIVE.value
                ).first()
                
                if not invitation:
                    return {"success": False, "error": "Invalid or expired invitation"}
                
                # Check expiration
                if invitation.expires_at and datetime.utcnow() > invitation.expires_at:
                    invitation.status = InvitationStatus.EXPIRED.value
                    session.commit()
                    return {"success": False, "error": "Invitation has expired"}
                
                # Create user account
                user = self.auth_service.create_user(
                    username=user_data["username"],
                    email=invitation.email,
                    password=user_data["password"],
                    role=self.auth_service.UserRole.USER,
                    tenant_id="default",
                    metadata={
                        "invited_by": invitation.created_by,
                        "invitation_code": invitation.code,
                        "user_tier": invitation.user_tier
                    }
                )
                
                # Create user permissions
                permissions = UserPermissions(
                    user_id=user.id,
                    permission_type=invitation.user_tier,
                    allocated_funds=invitation.allocated_capital,
                    granted_by=invitation.created_by,
                    max_position_size=invitation.max_position_size,
                    daily_loss_limit=invitation.daily_loss_limit,
                    broker_access=invitation.broker_access,
                    paper_trading_enabled=True,
                    live_trading_enabled=(invitation.user_tier == UserTier.POOL_INVESTOR.value),
                    gamification_enabled=True
                )
                
                session.add(permissions)
                
                # Create gamification progress for standard users
                if invitation.user_tier == UserTier.STANDARD.value:
                    gamification = GamificationProgress(
                        user_id=user.id,
                        badges_earned=json.dumps([]),
                        achievements_unlocked=json.dumps([])
                    )
                    session.add(gamification)
                
                # Mark invitation as used
                invitation.status = InvitationStatus.USED.value
                invitation.used_at = datetime.utcnow()
                
                session.commit()
                
                # Track registration event
                self._track_invitation_event(invitation.code, "user_registered", {
                    "user_id": user.id,
                    "username": user.username,
                    "user_tier": invitation.user_tier
                })
                
                logger.info(f"[CHECK] User registered from invitation: {user.username} (tier: {invitation.user_tier})")
                
                return {
                    "success": True,
                    "user_id": user.id,
                    "username": user.username,
                    "user_tier": invitation.user_tier,
                    "message": "Registration successful"
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to register from invitation: {e}")
            return {"success": False, "error": str(e)}

    def get_all_invitations(self, admin_id: str) -> List[Dict[str, Any]]:
        """Get all invitations for admin dashboard"""
        try:
            with self.db_manager.get_session() as session:
                invitations = session.query(Invitation).order_by(Invitation.created_at.desc()).all()
                
                result = []
                for inv in invitations:
                    result.append({
                        "code": inv.code,
                        "email": inv.email,
                        "invited_name": inv.invited_name,
                        "user_tier": inv.user_tier,
                        "status": inv.status,
                        "allocated_capital": float(inv.allocated_capital),
                        "created_by": inv.created_by,
                        "created_at": inv.created_at.isoformat(),
                        "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
                        "used_at": inv.used_at.isoformat() if inv.used_at else None
                    })
                
                return result
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to get invitations: {e}")
            return []

    def _generate_invitation_code(self) -> str:
        """Generate unique invitation code"""
        return f"PROM-{uuid.uuid4().hex[:8].upper()}"

    def _get_pending_invitation(self, email: str) -> Optional[Invitation]:
        """Check for existing pending invitation"""
        try:
            with self.db_manager.get_session() as session:
                return session.query(Invitation).filter_by(
                    email=email,
                    status=InvitationStatus.ACTIVE.value
                ).first()
        except Exception:
            return None

    async def _send_invitation_email(self, invitation: Invitation, registration_link: str):
        """Send invitation email with professional template"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("[WARNING]️ SMTP credentials not configured, skipping email")
                return
            
            subject = f"🚀 Welcome to PROMETHEUS Trading Platform - {invitation.user_tier.title()} Invitation"
            
            # Get tier-specific content
            tier_content = self._get_tier_email_content(invitation.user_tier)
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #0a0a0a; color: #ffffff; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); padding: 40px 30px; text-align: center; border-radius: 15px 15px 0 0; }}
                    .content {{ background-color: #1a1a1a; padding: 40px 30px; border-radius: 0 0 15px 15px; border: 1px solid rgba(255, 255, 255, 0.1); }}
                    .button {{ display: inline-block; background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%); color: #000; padding: 18px 35px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 25px 0; font-size: 16px; }}
                    .tier-badge {{ background: linear-gradient(135deg, #9c27b0 0%, #673ab7 100%); color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: bold; display: inline-block; margin: 10px 0; }}
                    .features {{ background: rgba(0, 212, 255, 0.1); padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #00d4ff; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #888; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0; font-size: 28px;">🚀 PROMETHEUS</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Advanced Trading Platform</p>
                        <div class="tier-badge">{invitation.user_tier.replace('_', ' ').title()} Access</div>
                    </div>
                    <div class="content">
                        <h2 style="color: #00d4ff; margin-top: 0;">Welcome, {invitation.invited_name or 'Trader'}!</h2>
                        <p>You've been invited to join PROMETHEUS Trading Platform with <strong>{invitation.user_tier.replace('_', ' ').title()}</strong> access.</p>
                        
                        {tier_content}
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{registration_link}" class="button">Complete Registration</a>
                        </div>
                        
                        <p><strong>⏰ Important:</strong> This invitation expires on {invitation.expires_at.strftime('%B %d, %Y at %I:%M %p UTC')}.</p>
                        
                        {invitation.invitation_message and f'<div style="background: rgba(255, 107, 53, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #ff6b35; margin: 20px 0;"><p><strong>Personal Message:</strong></p><p style="font-style: italic;">{invitation.invitation_message}</p></div>' or ''}
                        
                        <p>Questions? Contact our support team at support@prometheus-trading.com</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 PROMETHEUS Trading Platform. All rights reserved.</p>
                        <p>This invitation was sent to {invitation.email}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = invitation.email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"[CHECK] Invitation email sent to {invitation.email}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to send invitation email: {e}")

    def _get_tier_email_content(self, user_tier: str) -> str:
        """Get tier-specific email content"""
        if user_tier == UserTier.STANDARD.value:
            return """
            <div class="features">
                <h3 style="color: #00d4ff; margin-top: 0;">🎮 Standard User Features:</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>📊 <strong>Internal Paper Trading</strong> - Risk-free trading with real market data</li>
                    <li>🏆 <strong>Gamification System</strong> - Earn points, badges, and climb leaderboards</li>
                    <li>🎯 <strong>Achievement Tracking</strong> - Unlock trading milestones and rewards</li>
                    <li>📈 <strong>Portfolio Analytics</strong> - Professional-grade performance tracking</li>
                    <li>🎓 <strong>Educational Content</strong> - Learn advanced trading strategies</li>
                    <li>🤖 <strong>AI Insights</strong> - Get AI-powered market analysis</li>
                </ul>
            </div>
            """
        else:  # POOL_INVESTOR
            return f"""
            <div class="features">
                <h3 style="color: #ff6b35; margin-top: 0;">💎 Pool Investor Features:</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>💰 <strong>Live Trading Access</strong> - Trade with allocated funds: ${invitation.allocated_capital:,.2f}</li>
                    <li>🏦 <strong>Multi-Broker Support</strong> - Interactive Brokers & Alpaca integration</li>
                    <li>📊 <strong>Advanced Analytics</strong> - Institutional-grade performance metrics</li>
                    <li>🎮 <strong>All Gamification Features</strong> - Plus exclusive investor rewards</li>
                    <li>[LIGHTNING] <strong>Real-Time Execution</strong> - Professional trading infrastructure</li>
                    <li>🛡️ <strong>Risk Management</strong> - Built-in position limits and loss controls</li>
                    <li>📈 <strong>Fund Allocation Tracking</strong> - Monitor your allocated capital performance</li>
                </ul>
            </div>
            """

    def _track_invitation_event(self, invitation_code: str, event_type: str, event_data: Dict[str, Any]):
        """Track invitation events for analytics"""
        try:
            tracking = InvitationTracking(
                id=str(uuid.uuid4()),
                invitation_code=invitation_code,
                event_type=event_type,
                event_data=json.dumps(event_data)
            )
            
            with self.db_manager.get_session() as session:
                session.add(tracking)
                session.commit()
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to track invitation event: {e}")

# Global service instance
unified_invitation_service = None

def get_invitation_service() -> UnifiedInvitationService:
    """Get global invitation service instance"""
    global unified_invitation_service
    if unified_invitation_service is None:
        from core.database_manager import db_manager
        from core.auth.unified_auth_service import unified_auth_service
        unified_invitation_service = UnifiedInvitationService(db_manager, unified_auth_service)
    return unified_invitation_service
