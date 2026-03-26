# PROMETHEUS Trading Platform - API Documentation

## 🌐 **API Overview**

The PROMETHEUS Trading Platform provides a comprehensive RESTful API for trading operations, market data access, and system management.

**Base URL**: `https://prometheus-trade.com/api` (Production)  
**Base URL**: `http://localhost:8000/api` (Development)

## 🔐 **Authentication**

### JWT Token Authentication

All API endpoints require authentication using JWT tokens.

#### Login

```http

POST /api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}

```

**Response:**

```json

{
  "status": "success",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "username": "trader",
    "role": "trader",
    "tier": "live"
  }
}

```

#### Using Authentication

Include the JWT token in the Authorization header:

```http

Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

```

## 📊 **Market Data Endpoints**

### Get Real-Time Price

```http

GET /api/market-data/price/{symbol}

```

**Parameters:**

- `symbol` (string): Stock symbol (e.g., "AAPL")

**Response:**

```json

{
  "symbol": "AAPL",
  "price": 150.25,
  "timestamp": "2024-01-01T12:00:00Z",
  "source": "polygon"
}

```

### Get Market Data

```http

GET /api/market-data/{symbol}

```

**Response:**

```json

{
  "symbol": "AAPL",
  "price": 150.25,
  "volume": 1000000,
  "change": 2.50,
  "change_percent": 1.69,
  "bid": 150.20,
  "ask": 150.30,
  "high": 152.00,
  "low": 148.50,
  "timestamp": "2024-01-01T12:00:00Z"
}

```

### Get Historical Data

```http

GET /api/market-data/{symbol}/history?period=1d&interval=1m

```

**Parameters:**

- `period`: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
- `interval`: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

## 💰 **Paper Trading Endpoints**

### Get Portfolio

```http

GET /api/paper-trading/portfolio

```

**Response:**

```json

{
  "total_value": 15000.00,
  "cash": 5000.00,
  "buying_power": 10000.00,
  "positions": {
    "AAPL": {
      "quantity": 50,
      "average_price": 148.00,
      "current_price": 150.25,
      "market_value": 7512.50,
      "unrealized_pnl": 112.50,
      "unrealized_pnl_percent": 1.52
    }
  },
  "performance": {
    "total_return": 500.00,
    "total_return_percent": 3.45,
    "today_return": 25.00,
    "today_return_percent": 0.17
  }
}

```

### Place Order

```http

POST /api/paper-trading/orders
Content-Type: application/json

{
  "symbol": "AAPL",
  "quantity": 10,
  "order_type": "buy",
  "price": 150.00,
  "order_style": "limit"
}

```

**Response:**

```json

{
  "status": "success",
  "order": {
    "id": "order_123456",
    "symbol": "AAPL",
    "quantity": 10,
    "order_type": "buy",
    "price": 150.00,
    "status": "pending",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}

```

### Get Order History

```http

GET /api/paper-trading/orders/history?limit=50&offset=0

```

**Response:**

```json

{
  "orders": [
    {
      "id": "order_123456",
      "symbol": "AAPL",
      "quantity": 10,
      "order_type": "buy",
      "price": 150.00,
      "filled_price": 150.25,
      "status": "filled",
      "timestamp": "2024-01-01T12:00:00Z",
      "filled_at": "2024-01-01T12:00:05Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}

```

## 🚀 **Revolutionary Trading Engines**

### Crypto Trading (24/7)

```http

POST /api/revolutionary/crypto/order
Content-Type: application/json

{
  "pair": "BTC/USD",
  "quantity": 0.1,
  "order_type": "buy",
  "price": 50000.00
}

```

### Options Trading

```http

POST /api/revolutionary/options/multi-leg
Content-Type: application/json

{
  "strategy": "iron_condor",
  "underlying": "AAPL",
  "expiration": "2024-12-20",
  "legs": [
    {
      "action": "sell",
      "type": "call",
      "strike": 155,
      "quantity": 1
    },
    {
      "action": "buy",
      "type": "call",
      "strike": 160,
      "quantity": 1
    }
  ]
}

```

### Advanced Trading (DMA/VWAP/TWAP)

```http

POST /api/revolutionary/advanced/vwap
Content-Type: application/json

{
  "symbol": "AAPL",
  "target_quantity": 10000,
  "time_horizon": 60,
  "participation_rate": 0.1
}

```

## 🤖 **AI Trading Intelligence**

### Market Sentiment Analysis

```http

GET /api/ai/sentiment/{symbol}

```

**Response:**

```json

{
  "symbol": "AAPL",
  "sentiment_score": 0.75,
  "sentiment_label": "BULLISH",
  "confidence": 0.85,
  "factors": [
    "Strong earnings report",
    "Positive analyst upgrades",
    "Market momentum"
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}

```

### Generate Trading Signal

```http

POST /api/ai/signal
Content-Type: application/json

{
  "symbol": "AAPL",
  "timeframe": "1d",
  "strategy": "momentum"
}

```

**Response:**

```json

{
  "symbol": "AAPL",
  "action": "buy",
  "confidence": 0.92,
  "target_price": 155.00,
  "stop_loss": 145.00,
  "reasoning": "Strong momentum with bullish technical indicators",
  "risk_score": 0.3,
  "timestamp": "2024-01-01T12:00:00Z"
}

```

## 👥 **User Management (Admin)**

### Get All Users

```http

GET /api/admin/users?limit=50&offset=0

```

### Create User

```http

POST /api/admin/users
Content-Type: application/json

{
  "username": "newtrader",
  "email": "trader@example.com",
  "password": "SecurePassword123!",
  "role": "trader",
  "tier": "paper"
}

```

### Fund Allocation

```http

POST /api/admin/fund-allocation
Content-Type: application/json

{
  "user_id": "user_123",
  "amount": 50000.00,
  "approved": true,
  "notes": "Approved for live trading"
}

```

## 📈 **System Monitoring**

### System Status

```http

GET /api/system/status

```

**Response:**

```json

{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "database": "healthy",
    "market_data": "healthy",
    "trading_engines": "healthy",
    "ai_services": "healthy"
  },
  "performance": {
    "cpu_usage": 25.5,
    "memory_usage": 45.2,
    "disk_usage": 30.1
  }
}

```

### Health Check

```http

GET /health

```

**Response:**

```json

{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}

```

## 📊 **Analytics & Reporting**

### Performance Analytics

```http

GET /api/analytics/performance?period=30d

```

### Trading Statistics

```http

GET /api/analytics/trading-stats?user_id=user_123

```

### Risk Metrics

```http

GET /api/analytics/risk-metrics?portfolio_id=portfolio_123

```

## 🔒 **Security Endpoints**

### Audit Logs

```http

GET /api/security/audit-logs?user_id=user_123&limit=100

```

### Security Events

```http

GET /api/security/events?severity=high&limit=50

```

## 📝 **Error Handling**

### Standard Error Response

```json

{
  "status": "error",
  "error_code": "INVALID_SYMBOL",
  "message": "The provided symbol is not valid",
  "details": {
    "symbol": "INVALID",
    "valid_symbols": ["AAPL", "MSFT", "GOOGL"]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}

```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

## 🔄 **Rate Limiting**

### Default Limits
- **General API**: 1000 requests per hour per user
- **Market Data**: 500 requests per minute per user
- **Trading Orders**: 100 requests per minute per user
- **Admin Endpoints**: 200 requests per hour per admin

### Rate Limit Headers

```http

X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200

```

## 📚 **SDKs & Libraries**

### Python SDK

```python

from prometheus_trading import PrometheusClient

client = PrometheusClient(
    api_key="your_api_key",
    base_url="https://prometheus-trade.com/api"
)

# Get market data

price = client.market_data.get_price("AAPL")

# Place order

order = client.paper_trading.place_order(
    symbol="AAPL",
    quantity=10,
    order_type="buy",
    price=150.00
)

```

### JavaScript SDK

```javascript

import { PrometheusClient } from '@prometheus-trading/sdk';

const client = new PrometheusClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://prometheus-trade.com/api'
});

// Get portfolio
const portfolio = await client.paperTrading.getPortfolio();

// Place order
const order = await client.paperTrading.placeOrder({
  symbol: 'AAPL',
  quantity: 10,
  orderType: 'buy',
  price: 150.00
});

```

## 🔧 **Webhooks**

### Order Status Updates

```http

POST https://your-webhook-url.com/order-updates
Content-Type: application/json

{
  "event": "order.filled",
  "order_id": "order_123456",
  "symbol": "AAPL",
  "quantity": 10,
  "filled_price": 150.25,
  "timestamp": "2024-01-01T12:00:05Z"
}

```

### Portfolio Updates

```http

POST https://your-webhook-url.com/portfolio-updates
Content-Type: application/json

{
  "event": "portfolio.updated",
  "user_id": "user_123",
  "total_value": 15000.00,
  "change": 125.50,
  "change_percent": 0.84,
  "timestamp": "2024-01-01T12:00:00Z"
}

```

---

**© 2024 PROMETHEUS Trading Platform. All rights reserved.**
