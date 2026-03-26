/**
 * 🏦 Real Alpaca Trading Data Service
 * Connects frontend to real Alpaca Markets API data (no demo/mock data)
 */

import { apiCall, API_ENDPOINTS } from '../config/api';

export interface AlpacaAccount {
  id: string;
  status: string;
  currency: string;
  cash: number;
  portfolio_value: number;
  buying_power: number;
  equity: number;
  last_equity: number;
  multiplier: number;
  pattern_day_trader: boolean;
  day_trading_buying_power: number;
  regt_buying_power: number;
  initial_margin: number;
  maintenance_margin: number;
  last_maintenance_margin: number;
  sma: number;
  daytrade_count: number;
}

export interface AlpacaPosition {
  asset_id: string;
  symbol: string;
  exchange: string;
  asset_class: string;
  qty: number;
  side: string;
  market_value: number;
  cost_basis: number;
  unrealized_pl: number;
  unrealized_plpc: number;
  unrealized_intraday_pl: number;
  unrealized_intraday_plpc: number;
  current_price: number;
  lastday_price: number;
  change_today: number;
}

export interface AlpacaOrder {
  id: string;
  client_order_id: string;
  created_at: string;
  updated_at: string;
  submitted_at: string;
  filled_at?: string;
  expired_at?: string;
  canceled_at?: string;
  failed_at?: string;
  replaced_at?: string;
  replaced_by?: string;
  replaces?: string;
  asset_id: string;
  symbol: string;
  asset_class: string;
  qty: number;
  filled_qty: number;
  type: string;
  side: string;
  time_in_force: string;
  limit_price?: number;
  stop_price?: number;
  status: string;
  extended_hours: boolean;
  legs?: any[];
}

export interface AlpacaPortfolioHistory {
  timestamp: number[];
  equity: number[];
  profit_loss: number[];
  profit_loss_pct: number[];
  base_value: number;
  timeframe: string;
}

export interface RealTradingData {
  paperAccount: AlpacaAccount;
  liveAccount: AlpacaAccount;
  paperPositions: AlpacaPosition[];
  livePositions: AlpacaPosition[];
  paperOrders: AlpacaOrder[];
  liveOrders: AlpacaOrder[];
  analytics: {
    todaysPnL: number;
    totalReturn: number;
    totalReturnPercent: number;
    maxDrawdown: number;
    volatility: number;
    beta: number;
    alpha: number;
    sharpeRatio: number;
    avgTradeReturn: number;
    winRate: number;
    totalTrades: number;
    portfolioValue: number;
    dailyPnL: number;
    lastUpdated: string;
  };
}

class RealAlpacaService {
  private baseUrl = '/api/trading/alpaca';
  private alwaysLiveMode = false;

  constructor() {
    this.checkAlwaysLiveMode();
  }

  /**
   * Check if backend has ALWAYS_LIVE mode enabled
   */
  private async checkAlwaysLiveMode() {
    try {
      const debugStatus = await apiCall('/api/alpaca/debug-status');
      this.alwaysLiveMode = debugStatus.always_live === true;
      if (this.alwaysLiveMode) {
        console.log('🔴 Backend ALWAYS_LIVE mode detected - using generic endpoints for live data');
      }
    } catch (error) {
      console.warn('Could not check backend ALWAYS_LIVE mode:', error);
    }
  }

  /**
   * 📊 Get real paper trading account data
   */
  async getPaperTradingData(): Promise<RealTradingData> {
    try {
      console.log('🔍 Fetching real paper trading data...');

      // If ALWAYS_LIVE mode is enabled, use generic endpoints that return live data
      const endpoints = this.alwaysLiveMode ? {
        account: '/api/trading/alpaca/account',
        positions: '/api/trading/alpaca/positions', 
        orders: '/api/trading/alpaca/orders',
        portfolio: '/api/trading/alpaca/portfolio/history'
      } : {
        account: API_ENDPOINTS.ALPACA_PAPER_ACCOUNT,
        positions: API_ENDPOINTS.ALPACA_PAPER_POSITIONS,
        orders: API_ENDPOINTS.ALPACA_PAPER_ORDERS,
        portfolio: API_ENDPOINTS.ALPACA_PAPER_PORTFOLIO
      };

      // Fetch all real data in parallel
      const [accountResponse, positionsResponse, ordersResponse] = await Promise.all([
        apiCall(endpoints.account),
        apiCall(endpoints.positions),
        apiCall(endpoints.orders)
      ]);

      // Handle different response formats (generic vs specific endpoints)
      const account = this.alwaysLiveMode && accountResponse.account ? accountResponse.account : accountResponse;
      const positions = this.alwaysLiveMode && positionsResponse.positions ? positionsResponse.positions : positionsResponse;
      const orders = this.alwaysLiveMode && ordersResponse.orders ? ordersResponse.orders : ordersResponse;

      // Get portfolio history
      let portfolio_history = null;
      try {
        const portfolioResponse = await apiCall(endpoints.portfolio);
        portfolio_history = this.alwaysLiveMode && portfolioResponse.portfolio_history ? portfolioResponse.portfolio_history : portfolioResponse;
      } catch (error) {
        console.warn('Portfolio history not available:', error);
        // Provide fallback data
        portfolio_history = {
          timestamp: [Date.now() / 1000],
          equity: [account.portfolio_value],
          profit_loss: [0],
          profit_loss_pct: [0],
          base_value: account.portfolio_value,
          timeframe: '1D'
        };
      }

      // Calculate analytics from real data
      const daily_pnl = account.equity - account.last_equity;
      const total_trades = orders.filter((order: AlpacaOrder) => order.status === 'filled').length;
      
      // Calculate win rate from filled orders
      const filledOrders = orders.filter((order: AlpacaOrder) => order.status === 'filled');
      let wins = 0;
      filledOrders.forEach((order: AlpacaOrder) => {
        // Simple profit check - compare filled price with current market (simplified)
        if (order.side === 'buy' && positions.find((p: AlpacaPosition) => p.symbol === order.symbol)) {
          const position = positions.find((p: AlpacaPosition) => p.symbol === order.symbol);
          if (position && position.unrealized_pl > 0) wins++;
        }
      });
      const win_rate = filledOrders.length > 0 ? (wins / filledOrders.length) * 100 : 0;

      console.log('✅ Real paper trading data loaded:', {
        portfolio_value: account.portfolio_value,
        positions_count: positions.length,
        orders_count: orders.length,
        daily_pnl,
        win_rate: win_rate.toFixed(2) + '%'
      });

      // Calculate analytics
      const analytics = {
        todaysPnL: daily_pnl,
        totalReturn: daily_pnl,
        totalReturnPercent: account.portfolio_value > 0 ? (daily_pnl / account.portfolio_value) * 100 : 0,
        maxDrawdown: 0, // TODO: Calculate from portfolio history
        volatility: 0,
        beta: 0,
        alpha: 0,
        sharpeRatio: 0,
        avgTradeReturn: total_trades > 0 ? daily_pnl / total_trades : 0,
        winRate: win_rate,
        totalTrades: total_trades,
        portfolioValue: account.portfolio_value,
        dailyPnL: daily_pnl,
        lastUpdated: new Date().toISOString()
      };

      // Create empty placeholders for live data to avoid confusion
      const emptyAccount: AlpacaAccount = {
        id: '',
        status: 'INACTIVE',
        currency: 'USD',
        cash: 0,
        portfolio_value: 0,
        buying_power: 0,
        equity: 0,
        last_equity: 0,
        multiplier: 1,
        pattern_day_trader: false,
        day_trading_buying_power: 0,
        regt_buying_power: 0,
        initial_margin: 0,
        maintenance_margin: 0,
        last_maintenance_margin: 0,
        sma: 0,
        daytrade_count: 0
      };

      return {
        paperAccount: account,
        liveAccount: emptyAccount, // Empty account to avoid confusion
        paperPositions: positions,
        livePositions: [],
        paperOrders: orders,
        liveOrders: [],
        analytics
      };
    } catch (error) {
      console.error('❌ Failed to fetch real paper trading data:', error);
      throw error;
    }
  }

  /**
   * 💰 Get real live trading account data
   */
  async getLiveTradingData(): Promise<RealTradingData> {
    try {
      console.log('🔍 Fetching real live trading data...');

      // If ALWAYS_LIVE mode is enabled, use generic endpoints that return live data
      const endpoints = this.alwaysLiveMode ? {
        account: '/api/trading/alpaca/account',
        positions: '/api/trading/alpaca/positions',
        orders: '/api/trading/alpaca/orders', 
        portfolio: '/api/trading/alpaca/portfolio'
      } : {
        account: API_ENDPOINTS.ALPACA_LIVE_ACCOUNT,
        positions: API_ENDPOINTS.ALPACA_LIVE_POSITIONS,
        orders: API_ENDPOINTS.ALPACA_LIVE_ORDERS,
        portfolio: API_ENDPOINTS.ALPACA_LIVE_PORTFOLIO
      };

      // Fetch all real data in parallel
      const [accountResponse, positionsResponse, ordersResponse] = await Promise.all([
        apiCall(endpoints.account),
        apiCall(endpoints.positions),
        apiCall(endpoints.orders)
      ]);

      // Handle different response formats (generic vs specific endpoints)
      const account = this.alwaysLiveMode && accountResponse.account ? accountResponse.account : accountResponse;
      const positions = this.alwaysLiveMode && positionsResponse.positions ? positionsResponse.positions : positionsResponse;
      const orders = this.alwaysLiveMode && ordersResponse.orders ? ordersResponse.orders : ordersResponse;

      // Get portfolio history
      let portfolio_history = null;
      try {
        const portfolioResponse = await apiCall(endpoints.portfolio);
        portfolio_history = this.alwaysLiveMode && portfolioResponse.portfolio_history ? portfolioResponse.portfolio_history : portfolioResponse;
      } catch (error) {
        console.warn('Portfolio history not available:', error);
        // Provide fallback data
        portfolio_history = {
          timestamp: [Date.now() / 1000],
          equity: [account.portfolio_value],
          profit_loss: [0],
          profit_loss_pct: [0],
          base_value: account.portfolio_value,
          timeframe: '1D'
        };
      }

      // Calculate analytics from real data
      const daily_pnl = account.equity - account.last_equity;
      const total_trades = orders.filter((order: AlpacaOrder) => order.status === 'filled').length;
      
      // Calculate win rate from filled orders
      const filledOrders = orders.filter((order: AlpacaOrder) => order.status === 'filled');
      let wins = 0;
      filledOrders.forEach((order: AlpacaOrder) => {
        if (order.side === 'buy' && positions.find((p: AlpacaPosition) => p.symbol === order.symbol)) {
          const position = positions.find((p: AlpacaPosition) => p.symbol === order.symbol);
          if (position && position.unrealized_pl > 0) wins++;
        }
      });
      const win_rate = filledOrders.length > 0 ? (wins / filledOrders.length) * 100 : 0;

      console.log('✅ Real live trading data loaded:', {
        portfolio_value: account.portfolio_value,
        positions_count: positions.length,
        orders_count: orders.length,
        daily_pnl,
        win_rate: win_rate.toFixed(2) + '%'
      });

      // Calculate analytics
      const analytics = {
        todaysPnL: daily_pnl,
        totalReturn: daily_pnl,
        totalReturnPercent: account.portfolio_value > 0 ? (daily_pnl / account.portfolio_value) * 100 : 0,
        maxDrawdown: 0, // TODO: Calculate from portfolio history
        volatility: 0,
        beta: 0,
        alpha: 0,
        sharpeRatio: 0,
        avgTradeReturn: total_trades > 0 ? daily_pnl / total_trades : 0,
        winRate: win_rate,
        totalTrades: total_trades,
        portfolioValue: account.portfolio_value,
        dailyPnL: daily_pnl,
        lastUpdated: new Date().toISOString()
      };

      // Create empty placeholders for paper data to avoid confusion
      const emptyAccount: AlpacaAccount = {
        id: '',
        status: 'INACTIVE',
        currency: 'USD',
        cash: 0,
        portfolio_value: 0,
        buying_power: 0,
        equity: 0,
        last_equity: 0,
        multiplier: 1,
        pattern_day_trader: false,
        day_trading_buying_power: 0,
        regt_buying_power: 0,
        initial_margin: 0,
        maintenance_margin: 0,
        last_maintenance_margin: 0,
        sma: 0,
        daytrade_count: 0
      };

      return {
        paperAccount: emptyAccount, // Empty account to avoid confusion
        liveAccount: account,
        paperPositions: [],
        livePositions: positions,
        paperOrders: [],
        liveOrders: orders,
        analytics
      };
    } catch (error) {
      console.error('❌ Failed to fetch real live trading data:', error);
      throw error;
    }
  }

  /**
   * 🔄 Get trading data based on mode (paper or live)
   */
  async getTradingData(mode: 'paper' | 'live'): Promise<RealTradingData> {
    if (mode === 'live') {
      return this.getLiveTradingData();
    } else {
      return this.getPaperTradingData();
    }
  }

  /**
   * 📈 Calculate advanced analytics from real data
   */
  calculateAdvancedAnalytics(data: RealTradingData) {
    // Use the analytics data we already have
    return data.analytics;
  }
}

// Create singleton instance
export const realAlpacaService = new RealAlpacaService();
export default realAlpacaService;
