/**
 * 📊 PAPER MARKET DATA SERVICE
 * Uses REAL live market data from backend APIs (Yahoo Finance, Alpaca, Polygon)
 * This provides actual market prices for paper trading, not simulated data.
 * 
 * Paper Trading = Real Market Data + Simulated Money (No Real Capital at Risk)
 */
import RealPaperMarketDataService, {
  MarketData,
  PortfolioPosition,
  TradingSignal,
  LiveAnalytics
} from './RealPaperMarketData';

// Use REAL market data service for paper trading
// This fetches actual live prices from Yahoo Finance, Alpaca, Polygon, etc.
export const paperMarketData = new RealPaperMarketDataService();

// Re-export types for convenience
export type { MarketData, PortfolioPosition, TradingSignal, LiveAnalytics };

export default paperMarketData;
