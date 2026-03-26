# Prometheus Frontend API Documentation

## Overview

This document describes all API endpoints used by the Prometheus Trading Platform frontend.

## Base Configuration

- **Development API URL**: `http://localhost:8000`
- **WebSocket URL**: `ws://localhost:8000`
- **Production**: Uses environment variable `REACT_APP_API_URL` or current origin

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
```text
Authorization: Bearer <token>

```

Tokens are stored in `localStorage` as `authToken` and automatically included in API requests.

## API Endpoints

### Authentication Endpoints

#### POST `/api/auth/login`

Authenticate user and receive JWT token.

**Request Body:**

```json

{
  "username": "user@example.com",
  "password": "password123"
}

```

**Response:**

```json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

```

#### POST `/api/auth/register`

Register a new user account.

**Request Body:**

```json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}

```

#### GET `/api/auth/me`

Get current authenticated user information.

**Response:**

```json

{
  "user": {
    "user_id": "user_123",
    "email": "user@example.com",
    "tier": "demo",
    "role": "user"
  }
}

```

#### POST `/api/auth/logout`

Logout current user and invalidate token.

#### GET `/api/auth/validate-invitation`

Validate an invitation token.

**Query Parameters:**

- `token`: Invitation token string

---

### Trading Endpoints

#### POST `/api/trading/start-trial`

Start a 48-hour paper trading trial.

**Request Body:**

```json

{
  "starting_capital": 10000
}

```

#### POST `/api/trading/start`

Start a trading session.

**Request Body:**

```json

{
  "mode": "paper",
  "auto_trading": true
}

```

#### GET `/api/trading/orders`

Get all trading orders for current user.

**Response:**

```json

{
  "orders": [
    {
      "id": "order_123",
      "symbol": "AAPL",
      "side": "buy",
      "quantity": 10,
      "status": "filled",
      "filled_at": "2024-01-15T10:30:00Z"
    }
  ]
}

```

---

### Live Trading Endpoints

#### GET `/api/live-trading/status`

Get current live trading status.

**Response:**

```json

{
  "isActive": true,
  "activePositions": 5,
  "dailyPnL": 1250.50,
  "winRate": 68.5,
  "canActivate": true
}

```

#### POST `/api/live-trading/start`

Start live trading engine.

**Request Body:**

```json

{
  "fund_allocation": 50000
}

```

#### POST `/api/live-trading/start-engine`

Start the live trading engine (admin only).

---

### Alpaca Trading Endpoints

#### Paper Trading

##### GET `/api/trading/alpaca/paper/account`

Get Alpaca paper trading account information.

**Response:**

```json

{
  "id": "account_id",
  "status": "ACTIVE",
  "currency": "USD",
  "cash": 50000.00,
  "portfolio_value": 52500.00,
  "buying_power": 100000.00,
  "equity": 52500.00
}

```

##### GET `/api/trading/alpaca/paper/positions`

Get current paper trading positions.

**Response:**

```json

{
  "positions": [
    {
      "symbol": "AAPL",
      "qty": 10,
      "market_value": 1500.00,
      "unrealized_pl": 50.00,
      "current_price": 150.00
    }
  ]
}

```

##### GET `/api/trading/alpaca/paper/orders`

Get paper trading order history.

##### GET `/api/trading/alpaca/portfolio/history`

Get portfolio history for paper trading.

**Query Parameters:**

- `period`: `1D`, `1W`, `1M`, `1Y`
- `timeframe`: `1Min`, `5Min`, `15Min`, `1Hour`, `1Day`

#### Live Trading

##### GET `/api/trading/alpaca/live/account`

Get Alpaca live trading account information.

##### GET `/api/trading/alpaca/live/positions`

Get current live trading positions.

##### GET `/api/trading/alpaca/live/orders`

Get live trading order history.

##### GET `/api/trading/alpaca/live/portfolio`

Get live trading portfolio data.

---

### User Endpoints

#### GET `/api/user/{userId}/dashboard`

Get user dashboard data.

**Response:**

```json

{
  "active_sessions": [],
  "portfolio_value": 10000.00,
  "total_return": 500.00
}

```

#### GET `/api/user/portfolio/{userId}`

Get user portfolio information.

**Response:**

```json

{
  "totalValue": 10500.00,
  "totalInvested": 10000.00,
  "totalReturn": 500.00,
  "returnPercentage": 5.0,
  "currency": "USD",
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 10,
      "averagePrice": 145.00,
      "currentPrice": 150.00,
      "totalValue": 1500.00,
      "profitLoss": 50.00,
      "profitLossPercentage": 3.45
    }
  ],
  "totalTrades": 25,
  "winningTrades": 17,
  "losingTrades": 8,
  "winRate": 68.0
}

```

#### POST `/api/user/create-session`

Create a new paper trading session.

**Request Body:**

```json

{
  "session_type": "24_hour",
  "starting_capital": 10000,
  "custom_hours": 48
}

```

---

### Gamification Endpoints

#### GET `/api/gamification/progress/{userId}`

Get user gamification progress.

**Response:**

```json

{
  "level": 5,
  "xp_points": 2500,
  "next_level_xp": 3000,
  "xp_to_next_level": 500,
  "current_streak": 7,
  "recent_achievements": [
    {
      "id": "ach_1",
      "name": "First Trade",
      "description": "Completed your first trade",
      "icon": "🎯",
      "points": 100,
      "earned_at": "2024-01-15T10:00:00Z"
    }
  ],
  "skill_ratings": {
    "risk_management": 75,
    "market_analysis": 80,
    "timing": 70,
    "portfolio_management": 85,
    "consistency": 78
  },
  "badges_earned": [],
  "total_achievements": 12
}

```

#### POST `/api/gamification/award-xp`

Award XP to a user.

**Request Body:**

```json

{
  "user_id": "user_123",
  "xp_amount": 50,
  "reason": "Completed a trade"
}

```

**Response:**

```json

{
  "new_xp": 2550,
  "new_level": 5,
  "level_up": false
}

```

#### POST `/api/gamification/unlock-achievement`

Unlock an achievement for a user.

**Request Body:**

```json

{
  "user_id": "user_123",
  "achievement_id": "ach_1"
}

```

---

### System Endpoints

#### GET `/api/system/health`

Get system health metrics.

**Response:**

```json

{
  "system_health": 95,
  "ai_accuracy": 92.5,
  "latency_ms": 2.5,
  "active_strategies": 5,
  "market_status": "OPEN",
  "uptime": 99.9,
  "active_users": 47,
  "active_trades": 12
}

```

#### GET `/api/system/status`

Get system status information.

#### GET `/api/system/performance-metrics`

Get system performance metrics.

#### GET `/api/system/performance`

Get detailed system performance data.

#### GET `/health`

Basic health check endpoint.

**Response:**

```json

{
  "status": "healthy"
}

```

---

### Admin Endpoints

#### GET `/api/admin/users`

Get all users (admin only).

**Response:**

```json

{
  "users": [
    {
      "id": "user_123",
      "username": "john_doe",
      "email": "john@example.com",
      "status": "active",
      "tier": "premium",
      "allocatedFunds": 50000,
      "currentValue": 52500,
      "pnl": 2500,
      "pnlPercentage": 5.0
    }
  ]
}

```

#### POST `/api/admin/users/{userId}/allocate-funds`

Allocate funds to a user (admin only).

**Request Body:**

```json

{
  "amount": 10000,
  "reason": "Initial allocation"
}

```

#### GET `/api/admin/metrics`

Get admin dashboard metrics.

**Response:**

```json

{
  "totalUsers": 150,
  "activeTraders": 47,
  "totalAllocated": 5000000,
  "totalPortfolioValue": 5250000,
  "dailyPnL": 250000,
  "systemUptime": 99.9,
  "pendingApprovals": 3,
  "activeSessions": 47
}

```

---

### Agent Endpoints

#### GET `/api/agents/status`

Get status of all hierarchical trading agents.

**Response:**

```json

{
  "success": true,
  "agents": {
    "supervisor_agents": [
      {
        "id": "supervisor_1",
        "name": "Portfolio Supervisor",
        "type": "supervisor",
        "status": "active",
        "performance": {
          "trades": 150,
          "winRate": 68.5,
          "pnl": 12500.50,
          "avgProfit": 83.34
        }
      }
    ],
    "execution_agents": {
      "arbitrage": [],
      "sentiment": [],
      "whale_following": [],
      "news_reaction": [],
      "technical": []
    }
  },
  "total_agents": 17,
  "active_agents": 15,
  "total_trades": 500,
  "total_pnl": 25000.00
}

```

#### POST `/api/agents/{agentId}/activate`

Activate a trading agent (admin only).

#### POST `/api/agents/{agentId}/deactivate`

Deactivate a trading agent (admin only).

---

### Revolutionary AI Endpoints

#### GET `/api/revolutionary/status`

Get status of all revolutionary AI engines.

**Response:**

```json

{
  "overall_status": "active",
  "engines": [
    {
      "name": "Crypto Trading Engine",
      "type": "crypto",
      "status": "active",
      "performance": {
        "accuracy": 87.5,
        "trades": 200,
        "winRate": 70.0,
        "pnl": 15000.00,
        "avgProfit": 75.00,
        "sharpeRatio": 1.85
      },
      "capabilities": ["crypto_spot", "crypto_futures"],
      "lastUpdate": "2024-01-15T10:30:00Z",
      "uptime": 99.5
    }
  ],
  "total_trades": 1000,
  "total_pnl": 75000.00,
  "avg_win_rate": 68.5,
  "system_uptime": 99.9
}

```

---

### WebSocket Endpoints

#### `/ws/dashboard-client`

WebSocket connection for real-time dashboard updates.

**Connection:**

```
```text
ws://localhost:8000/ws/dashboard-client?token=<jwt_token>

```

**Message Format:**

```json

{
  "type": "portfolio_update",
  "data": {
    "portfolio_value": 10500.00,
    "positions": []
  }
}

```

#### `/ws/revolutionary-ai`

WebSocket connection for revolutionary AI status updates (admin only).

#### `/ws/agents`

WebSocket connection for agent status updates (admin only).

---

### Broker Endpoints

#### GET `/api/broker-credentials`

Get broker account credentials (admin only).

#### POST `/api/broker-credentials`

Update broker account credentials (admin only).

---

### Workflow Endpoints

#### GET `/api/workflows`

Get all workflows.

#### GET `/api/workflow-templates`

Get workflow templates.

#### POST `/api/workflows/{id}/execute`

Execute a workflow.

#### POST `/api/workflows/{id}/cancel`

Cancel a running workflow.

---

### Feature Flags

#### GET `/api/features/flags`

Get available feature flags.

**Response:**

```json

{
  "flags": {
    "holographic_ui": true,
    "quantum_trading": false,
    "predictive_oracle": true,
    "nanosecond_execution": false,
    "hierarchical_agents": true,
    "multi_agent_orchestrator": true
  }
}

```

---

### Strategy & Risk Endpoints

#### POST `/api/strategy/persona/apply`

Apply a trading persona/strategy.

#### GET `/api/strategy/persona/active`

Get active trading persona.

#### GET `/api/risk/profile`

Get user risk profile.

---

### Audit Endpoints

#### GET `/api/audit/recent`

Get recent audit logs.

**Query Parameters:**

- `limit`: Number of logs to return (default: 50)
- `action_type`: Filter by action type
- `user_id`: Filter by user ID

#### GET `/api/audit/export`

Export audit logs.

**Query Parameters:**

- `start_date`: Start date (ISO format)
- `end_date`: End date (ISO format)
- `format`: `json` or `csv`

---

## Error Handling

All API endpoints follow standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**

```json

{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}

```

## Rate Limiting

API endpoints may be rate-limited. Rate limit headers are included in responses:

- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when rate limit resets

## WebSocket Reconnection

WebSocket connections automatically reconnect on disconnect with exponential backoff:

- Initial delay: 1 second
- Max delay: 30 seconds
- Max retries: 10

## Notes

- All timestamps are in ISO 8601 format (UTC)
- All monetary values are in USD
- All quantities are in shares/units
- Pagination may be implemented for list endpoints (check response for `page`, `limit`, `total` fields)

