"""SQLAlchemy ORM models for Prometheus Trading App (baseline)

Refactored to use timezone-aware UTC at source, but persisted as naive UTC
for compatibility with existing schema/migrations.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Float, Numeric, UniqueConstraint, Index

Base = declarative_base()

def _utc_now_naive() -> datetime:
    """Return current UTC time as a naive datetime (tzinfo stripped).

    SQLAlchemy defaults historically used datetime.utcnow (naive). We migrate
    away from the deprecated call while preserving identical DB representation.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    tenant_id = Column(String, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utc_now_naive)
    last_login = Column(DateTime)
    metadata_json = Column("metadata", Text)
    sessions = relationship("UserSession", back_populates="user", cascade="all,delete")

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=_utc_now_naive)
    is_active = Column(Boolean, default=True)
    user = relationship("User", back_populates="sessions")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=_utc_now_naive)
    revoked = Column(Boolean, default=False)

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    key_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    permissions = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=_utc_now_naive)
    is_active = Column(Boolean, default=True)

class AuthAuditLog(Base):
    __tablename__ = "auth_audit_log"
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    action = Column(String, nullable=False)
    resource = Column(String)
    details = Column(Text)
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=_utc_now_naive)
    success = Column(Boolean, default=True)

class BrokerCredential(Base):
    __tablename__ = "broker_credentials"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    broker = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    api_secret = Column(String, nullable=False)
    account_name = Column(String)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=_utc_now_naive)
    updated_at = Column(DateTime, default=_utc_now_naive)

class AgentActivity(Base):
    __tablename__ = "agent_activities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, nullable=False)
    activity_type = Column(String, nullable=False)
    details = Column(Text)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=_utc_now_naive)
    completed_at = Column(DateTime)

class SystemMetric(Base):
    __tablename__ = "system_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=_utc_now_naive)

class AppConfiguration(Base):
    __tablename__ = "app_configurations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    app_name = Column(String, nullable=False)
    config_key = Column(String, nullable=False)
    config_value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=_utc_now_naive)

class DatabaseMetadata(Base):
    __tablename__ = "database_metadata"
    key = Column(String, primary_key=True)
    value = Column(String)
    updated_at = Column(DateTime, default=_utc_now_naive)

# ------------------------------------------------------------
# Hedge-Fund / Multi-Investor Extension Schema
# ------------------------------------------------------------

class Invitation(Base):
    """Enhanced invitation codes for comprehensive user onboarding.

    Supports both Standard Users (paper trading) and Pool Investors (live trading).
    """
    __tablename__ = "invitations"
    code = Column(String, primary_key=True)
    email = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False, default="investor")
    user_tier = Column(String, nullable=False, default="standard")  # standard|pool_investor
    allocated_capital = Column(Numeric(18, 4), nullable=False, default=0)
    expires_at = Column(DateTime, nullable=True)
    used_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=_utc_now_naive)
    status = Column(String, default="active", index=True)  # active|expired|used|revoked
    access_scope = Column(String, default="full")  # full | trial48
    invitation_token = Column(String, unique=True, nullable=False, index=True)
    invited_name = Column(String, nullable=True)
    invitation_message = Column(Text, nullable=True)
    max_position_size = Column(Numeric(18, 4), default=0)
    daily_loss_limit = Column(Numeric(18, 4), default=0)
    broker_access = Column(Text, nullable=True)  # JSON array of allowed brokers

class CapitalAccount(Base):
    """Per-user capital / equity tracking (direct equity model)."""
    __tablename__ = "capital_accounts"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    starting_capital = Column(Numeric(18, 4), nullable=False)
    cash = Column(Numeric(18, 4), nullable=False, default=0)
    current_equity = Column(Numeric(18, 4), nullable=False, default=0)
    last_valuation = Column(DateTime)
    created_at = Column(DateTime, default=_utc_now_naive)
    updated_at = Column(DateTime, default=_utc_now_naive)
    status = Column(String, default="active")  # active|trial|suspended|closed
    trial_expires_at = Column(DateTime, nullable=True)
    __table_args__ = (
        UniqueConstraint('user_id', name='uq_capital_account_user'),
    )

class Contribution(Base):
    """Capital contributions / withdrawals queued or executed."""
    __tablename__ = "contributions"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    amount = Column(Numeric(18, 4), nullable=False)
    type = Column(String, nullable=False)  # initial|topup|withdrawal_request|withdrawal_settled
    timestamp = Column(DateTime, default=_utc_now_naive, index=True)
    status = Column(String, default="recorded")

class TradeLedger(Base):
    """Executed trades (real or simulated) allocated per user for accounting."""
    __tablename__ = "trade_ledger"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False)  # buy|sell
    qty = Column(Numeric(18, 8), nullable=False)
    fill_price = Column(Numeric(18, 8), nullable=False)
    gross_value = Column(Numeric(18, 4), nullable=False)
    fees = Column(Numeric(18, 4), nullable=False, default=0)
    pnl_realized = Column(Numeric(18, 4), nullable=False, default=0)
    strategy_tag = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, default=_utc_now_naive, index=True)
    __table_args__ = (
        Index('ix_trade_user_symbol_time', 'user_id', 'symbol', 'timestamp'),
    )

class Position(Base):
    """Current open positions per user & symbol (aggregated)."""
    __tablename__ = "positions"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    qty = Column(Numeric(18, 8), nullable=False)
    avg_price = Column(Numeric(18, 8), nullable=False)
    unrealized_pnl = Column(Numeric(18, 4), nullable=False, default=0)
    last_mark_price = Column(Numeric(18, 8), nullable=True)
    updated_at = Column(DateTime, default=_utc_now_naive)
    __table_args__ = (
        UniqueConstraint('user_id', 'symbol', name='uq_position_user_symbol'),
    )

class NAVHistory(Base):
    """Fund level NAV (simple direct equity aggregation)."""
    __tablename__ = "nav_history"
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=_utc_now_naive, index=True)
    total_equity = Column(Numeric(20, 4), nullable=False)
    total_cash = Column(Numeric(20, 4), nullable=False)
    total_unrealized = Column(Numeric(20, 4), nullable=False)
    nav_per_account = Column(Numeric(20, 6), nullable=True)  # simple average or future share model

class UserPerformance(Base):
    """Daily performance snapshots per user."""
    __tablename__ = "user_performance"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    period_date = Column(DateTime, nullable=False, index=True)
    start_equity = Column(Numeric(18, 4), nullable=False)
    end_equity = Column(Numeric(18, 4), nullable=False)
    rtn_pct = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=True)
    realized_pnl = Column(Numeric(18, 4), nullable=False, default=0)
    updated_at = Column(DateTime, default=_utc_now_naive)
    __table_args__ = (
        UniqueConstraint('user_id', 'period_date', name='uq_user_perf_user_day'),
    )

class UserPermissions(Base):
    """Enhanced user permissions for dual-tier system."""
    __tablename__ = "user_permissions"
    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    permission_type = Column(String, nullable=False, default="standard")  # standard|pool_investor
    allocated_funds = Column(Numeric(18, 4), default=0)
    granted_by = Column(String, nullable=False)
    granted_at = Column(DateTime, default=_utc_now_naive)
    max_position_size = Column(Numeric(18, 4), default=0)
    daily_loss_limit = Column(Numeric(18, 4), default=0)
    broker_access = Column(Text, nullable=True)  # JSON array of allowed brokers
    paper_trading_enabled = Column(Boolean, default=True)
    live_trading_enabled = Column(Boolean, default=False)
    gamification_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=_utc_now_naive, onupdate=_utc_now_naive)

class InvitationTracking(Base):
    """Track invitation events and analytics."""
    __tablename__ = "invitation_tracking"
    id = Column(String, primary_key=True)
    invitation_code = Column(String, ForeignKey('invitations.code'), nullable=False, index=True)
    event_type = Column(String, nullable=False)  # sent|opened|registered|expired
    event_data = Column(Text, nullable=True)  # JSON data
    timestamp = Column(DateTime, default=_utc_now_naive)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

class GamificationProgress(Base):
    """Gamification progress for standard users."""
    __tablename__ = "gamification_progress"
    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    xp_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    badges_earned = Column(Text, nullable=True)  # JSON array
    achievements_unlocked = Column(Text, nullable=True)  # JSON array
    trading_streak = Column(Integer, default=0)
    total_trades = Column(Integer, default=0)
    best_daily_return = Column(Float, default=0.0)
    leaderboard_rank = Column(Integer, nullable=True)
    last_activity = Column(DateTime, default=_utc_now_naive)
    created_at = Column(DateTime, default=_utc_now_naive)
    updated_at = Column(DateTime, default=_utc_now_naive, onupdate=_utc_now_naive)

class RiskEvent(Base):
    """Logged whenever a risk threshold is breached or action taken."""
    __tablename__ = "risk_events"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), index=True, nullable=True)
    event_type = Column(String, nullable=False)  # drawdown_hit | position_limit | global_circuit | other
    threshold = Column(String, nullable=True)
    value = Column(String, nullable=True)
    action_taken = Column(String, nullable=True)
    timestamp = Column(DateTime, default=_utc_now_naive, index=True)
    severity = Column(String, default="info")  # info|warning|critical

class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=_utc_now_naive)

class SystemState(Base):
    __tablename__ = "system_state"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=_utc_now_naive)

class RiskLimit(Base):
    __tablename__ = "risk_limits"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=True, index=True)  # null for global default
    daily_loss_pct = Column(Float, nullable=True)  # percent (e.g. 5 = 5%)
    max_position_pct = Column(Float, nullable=True)  # percent of equity
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utc_now_naive)
    updated_at = Column(DateTime, default=_utc_now_naive)

