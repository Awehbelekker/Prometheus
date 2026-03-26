"""
PROMETHEUS Trading Platform - Security & Authentication Unit Tests
Comprehensive tests for security and authentication systems
"""

import pytest
import jwt
import hashlib
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from core.auth.unified_auth_service import UnifiedAuthService
from core.dual_tier_permission_system import DualTierPermissionSystem
from core.audit_logger import AuditLogger


class TestUnifiedAuthService:
    """Test suite for Unified Authentication Service."""
    
    @pytest.fixture
    def auth_service(self, temp_db):
        """Create auth service instance for testing."""
        return UnifiedAuthService(database_path=temp_db)
    
    @pytest.mark.unit
    def test_auth_service_initialization(self, auth_service):
        """Test auth service initializes correctly."""
        assert auth_service is not None
        assert hasattr(auth_service, 'jwt_secret')
        assert hasattr(auth_service, 'token_expiry')
    
    @pytest.mark.unit
    async def test_user_registration(self, auth_service):
        """Test user registration functionality."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "role": "trader"
        }
        
        result = await auth_service.register_user(user_data)
        
        assert result["status"] == "success"
        assert "user_id" in result
        assert "password" not in result  # Password should not be returned
    
    @pytest.mark.unit
    async def test_user_login(self, auth_service):
        """Test user login functionality."""
        # First register a user
        user_data = {
            "username": "logintest",
            "email": "login@example.com",
            "password": "SecurePassword123!",
            "role": "trader"
        }
        await auth_service.register_user(user_data)
        
        # Now test login
        login_result = await auth_service.authenticate_user("logintest", "SecurePassword123!")
        
        assert login_result["status"] == "success"
        assert "access_token" in login_result
        assert "refresh_token" in login_result
        assert login_result["user"]["username"] == "logintest"
    
    @pytest.mark.unit
    async def test_invalid_login(self, auth_service):
        """Test invalid login attempts."""
        # Test with non-existent user
        result = await auth_service.authenticate_user("nonexistent", "password")
        assert result["status"] == "error"
        assert "invalid credentials" in result["message"].lower()
        
        # Test with wrong password
        user_data = {
            "username": "wrongpasstest",
            "email": "wrong@example.com",
            "password": "CorrectPassword123!",
            "role": "trader"
        }
        await auth_service.register_user(user_data)
        
        result = await auth_service.authenticate_user("wrongpasstest", "WrongPassword")
        assert result["status"] == "error"
    
    @pytest.mark.unit
    def test_jwt_token_generation(self, auth_service):
        """Test JWT token generation and validation."""
        user_data = {
            "user_id": "test_123",
            "username": "testuser",
            "role": "trader"
        }
        
        token = auth_service.generate_jwt_token(user_data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Validate token
        decoded = auth_service.validate_jwt_token(token)
        assert decoded["user_id"] == "test_123"
        assert decoded["username"] == "testuser"
    
    @pytest.mark.unit
    def test_expired_token_handling(self, auth_service):
        """Test expired token handling."""
        user_data = {
            "user_id": "test_123",
            "username": "testuser",
            "role": "trader"
        }
        
        # Generate token with very short expiry
        with patch.object(auth_service, 'token_expiry', timedelta(seconds=-1)):
            token = auth_service.generate_jwt_token(user_data)
            
            # Token should be invalid due to expiry
            decoded = auth_service.validate_jwt_token(token)
            assert decoded is None
    
    @pytest.mark.unit
    def test_password_hashing(self, auth_service):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        
        hashed = auth_service.hash_password(password)
        
        assert hashed != password  # Should be hashed
        assert len(hashed) > 50  # Should be long hash
        
        # Verify password
        assert auth_service.verify_password(password, hashed) == True
        assert auth_service.verify_password("WrongPassword", hashed) == False


class TestDualTierPermissionSystem:
    """Test suite for Dual Tier Permission System."""
    
    @pytest.fixture
    def permission_system(self, temp_db):
        """Create permission system instance for testing."""
        return DualTierPermissionSystem(database_path=temp_db)
    
    @pytest.mark.unit
    def test_permission_system_initialization(self, permission_system):
        """Test permission system initializes correctly."""
        assert permission_system is not None
        assert hasattr(permission_system, 'paper_tier_permissions')
        assert hasattr(permission_system, 'live_tier_permissions')
    
    @pytest.mark.unit
    async def test_paper_tier_user_creation(self, permission_system):
        """Test paper tier user creation."""
        user_data = {
            "user_id": "paper_user_123",
            "username": "papertrader",
            "tier": "paper"
        }
        
        result = await permission_system.create_user_permissions(user_data)
        
        assert result["status"] == "success"
        assert result["tier"] == "paper"
        assert result["permissions"]["live_trading"] == False
        assert result["permissions"]["paper_trading"] == True
    
    @pytest.mark.unit
    async def test_live_tier_user_creation(self, permission_system):
        """Test live tier user creation with admin approval."""
        user_data = {
            "user_id": "live_user_123",
            "username": "livetrader",
            "tier": "live",
            "admin_approved": True,
            "fund_allocation": 50000.0
        }
        
        result = await permission_system.create_user_permissions(user_data)
        
        assert result["status"] == "success"
        assert result["tier"] == "live"
        assert result["permissions"]["live_trading"] == True
        assert result["permissions"]["paper_trading"] == True
        assert result["fund_allocation"] == 50000.0
    
    @pytest.mark.unit
    async def test_permission_validation(self, permission_system):
        """Test permission validation for different actions."""
        # Create paper tier user
        paper_user = {
            "user_id": "paper_123",
            "username": "paperuser",
            "tier": "paper"
        }
        await permission_system.create_user_permissions(paper_user)
        
        # Test paper trading permission
        can_paper_trade = await permission_system.check_permission("paper_123", "paper_trading")
        assert can_paper_trade == True
        
        # Test live trading permission (should be denied)
        can_live_trade = await permission_system.check_permission("paper_123", "live_trading")
        assert can_live_trade == False
    
    @pytest.mark.unit
    async def test_fund_allocation_tracking(self, permission_system):
        """Test fund allocation tracking."""
        user_data = {
            "user_id": "funded_user_123",
            "username": "fundedtrader",
            "tier": "live",
            "admin_approved": True,
            "fund_allocation": 100000.0
        }
        
        await permission_system.create_user_permissions(user_data)
        
        # Test fund allocation retrieval
        allocation = await permission_system.get_fund_allocation("funded_user_123")
        assert allocation == 100000.0
        
        # Test fund usage tracking
        await permission_system.track_fund_usage("funded_user_123", 5000.0)
        remaining = await permission_system.get_remaining_funds("funded_user_123")
        assert remaining == 95000.0
    
    @pytest.mark.unit
    async def test_tier_upgrade_process(self, permission_system):
        """Test tier upgrade from paper to live."""
        # Create paper user
        paper_user = {
            "user_id": "upgrade_user_123",
            "username": "upgradeuser",
            "tier": "paper"
        }
        await permission_system.create_user_permissions(paper_user)
        
        # Request tier upgrade
        upgrade_request = {
            "user_id": "upgrade_user_123",
            "requested_tier": "live",
            "fund_allocation": 25000.0,
            "admin_approval": True
        }
        
        result = await permission_system.process_tier_upgrade(upgrade_request)
        
        assert result["status"] == "success"
        assert result["new_tier"] == "live"
        assert result["fund_allocation"] == 25000.0


class TestAuditLogger:
    """Test suite for Audit Logger."""
    
    @pytest.fixture
    def audit_logger(self, temp_db):
        """Create audit logger instance for testing."""
        return AuditLogger(database_path=temp_db)
    
    @pytest.mark.unit
    async def test_audit_log_creation(self, audit_logger):
        """Test audit log entry creation."""
        log_entry = {
            "user_id": "test_user_123",
            "action": "login",
            "details": {"ip_address": "192.168.1.1", "user_agent": "TestAgent"},
            "timestamp": datetime.now().isoformat()
        }
        
        result = await audit_logger.log_action(log_entry)
        
        assert result["status"] == "success"
        assert "log_id" in result
    
    @pytest.mark.unit
    async def test_trading_action_logging(self, audit_logger):
        """Test trading action audit logging."""
        trading_log = {
            "user_id": "trader_123",
            "action": "place_order",
            "details": {
                "symbol": "AAPL",
                "quantity": 100,
                "price": 150.0,
                "order_type": "buy"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        result = await audit_logger.log_trading_action(trading_log)
        
        assert result["status"] == "success"
        assert result["action_type"] == "trading"
    
    @pytest.mark.unit
    async def test_security_event_logging(self, audit_logger):
        """Test security event logging."""
        security_event = {
            "user_id": "potential_threat_123",
            "event_type": "failed_login_attempt",
            "severity": "medium",
            "details": {
                "ip_address": "suspicious.ip.address",
                "attempt_count": 5,
                "time_window": "5_minutes"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        result = await audit_logger.log_security_event(security_event)
        
        assert result["status"] == "success"
        assert result["severity"] == "medium"
    
    @pytest.mark.unit
    async def test_audit_log_retrieval(self, audit_logger):
        """Test audit log retrieval and filtering."""
        # Log several entries
        for i in range(5):
            log_entry = {
                "user_id": f"user_{i}",
                "action": "test_action",
                "details": {"test": f"data_{i}"},
                "timestamp": datetime.now().isoformat()
            }
            await audit_logger.log_action(log_entry)
        
        # Retrieve logs
        logs = await audit_logger.get_audit_logs(
            user_id="user_1",
            action="test_action",
            limit=10
        )
        
        assert len(logs) >= 1
        assert logs[0]["user_id"] == "user_1"
        assert logs[0]["action"] == "test_action"
