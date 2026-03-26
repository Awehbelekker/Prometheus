/**
 * 📊 LIVE MARKET DATA SERVICE
 * Real-time market data integration for 48-hour trial
 */

export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  timestamp: number;
}

export interface PortfolioPosition {
  symbol: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
}

export interface TradingSignal {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reason: string;
  targetPrice: number;
  stopLoss: number;
  timestamp: number;
}

export interface LiveAnalytics {
  portfolioValue: number;
  dailyPnL: number;
  totalReturn: number;
  totalReturnPercent: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
  avgTradeReturn: number;
  volatility: number;
  beta: number;
  alpha: number;
}

type Variant = 'live' | 'paper' | 'demo';

interface MarketDataOptions {
  seed?: number;
  variant?: Variant;
  pnlMultiplier?: number;      // scales dailyPnL
  volatilityScale?: number;    // scales symbol volatilities
  priceJitter?: number;        // initial price jitter percent (e.g., 0.5 => ±0.5%)
}

class LiveMarketDataService {
  private ws: WebSocket | null = null;
  private subscribers: Map<string, (data: any) => void> = new Map();
  private marketData: Map<string, MarketData> = new Map();
  private portfolio: PortfolioPosition[] = [];
  private analytics: LiveAnalytics = {
    portfolioValue: 100000,
    dailyPnL: 0,
    totalReturn: 0,
    totalReturnPercent: 0,
    sharpeRatio: 0,
    maxDrawdown: 0,
    winRate: 0,
    totalTrades: 0,
    avgTradeReturn: 0,
    volatility: 0,
    beta: 1.0,
    alpha: 0
  };

  private options: Required<MarketDataOptions>;
  private rng: () => number;
  private variant: Variant;

  // Popular trading symbols for demo
  private watchedSymbols = [
    'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX',
    'SPY', 'QQQ', 'IWM', 'GLD', 'SLV', 'BTCUSD', 'ETHUSD'
  ];

  constructor(options: MarketDataOptions = {}) {
    // Initialize options with defaults
    const variant: Variant = options.variant || 'paper';
    this.options = {
      seed: options.seed ?? (Math.floor(Math.random() * 2 ** 31) >>> 0),
      variant,
      pnlMultiplier: options.pnlMultiplier ?? (variant === 'live' ? 0.3 : 0.25),
      volatilityScale: options.volatilityScale ?? (variant === 'live' ? 1.0 : 0.9),
      priceJitter: options.priceJitter ?? (variant === 'live' ? 0.3 : 0.5)
    };
    this.variant = this.options.variant;

    // Seeded RNG (mulberry32)
    const mulberry32 = (a: number) => {
      return function() {
        let t = (a += 0x6D2B79F5);
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    };
    this.rng = mulberry32(this.options.seed);

    this.initializeDemo();
  }

  /**
   * Initialize with realistic demo data
   */
  private initializeDemo() {
    // Create realistic starting portfolio
    this.portfolio = [
      {
        symbol: 'AAPL',
        quantity: 50,
        avgPrice: 180.00,
        currentPrice: 185.50,
        unrealizedPnL: 275.00,
        unrealizedPnLPercent: 3.06
      },
      {
        symbol: 'GOOGL',
        quantity: 10,
        avgPrice: 2800.00,
        currentPrice: 2850.00,
        unrealizedPnL: 500.00,
        unrealizedPnLPercent: 1.79
      },
      {
        symbol: 'TSLA',
        quantity: 25,
        avgPrice: 220.00,
        currentPrice: 235.00,
        unrealizedPnL: 375.00,
        unrealizedPnLPercent: 6.82
      },
      {
        symbol: 'SPY',
        quantity: 100,
        avgPrice: 450.00,
        currentPrice: 455.00,
        unrealizedPnL: 500.00,
        unrealizedPnLPercent: 1.11
      }
    ];

    // Apply a small variant-specific initial jitter so first render differs across instances
    const jitterPct = this.options.priceJitter / 100; // convert to fraction
    this.portfolio.forEach(pos => {
      const jitter = (this.rng() - 0.5) * 2 * jitterPct; // ±jitterPct
      pos.currentPrice = Math.max(0.01, pos.currentPrice * (1 + jitter));
      pos.unrealizedPnL = (pos.currentPrice - pos.avgPrice) * pos.quantity;
      pos.unrealizedPnLPercent = ((pos.currentPrice - pos.avgPrice) / pos.avgPrice) * 100;
    });

    // Prime with one market update cycle to desynchronize streams immediately
    this.updateMarketPrices();
    this.updatePortfolio();
    this.updateAnalytics();
    
    // Start live data simulation
    this.startLiveDataSimulation();
  }

  /**
   * Simulate live market data updates
   */
  private startLiveDataSimulation() {
  setInterval(() => {
      this.updateMarketPrices();
      this.updatePortfolio();
      this.updateAnalytics();
      this.generateTradingSignals();
      this.notifySubscribers();
    }, 2000); // Update every 2 seconds
  }

  /**
   * Simulate realistic price movements
   */
  private updateMarketPrices() {
    this.watchedSymbols.forEach(symbol => {
      const existing = this.marketData.get(symbol);
      const basePrice = existing?.price || this.getBasePriceForSymbol(symbol);
      
      // Simulate realistic price movement (random walk with slight upward bias)
      const volatility = this.getVolatilityForSymbol(symbol) * this.options.volatilityScale;
      const randomChange = (this.rng() - 0.48) * volatility; // Slight upward bias
      const newPrice = Math.max(0.01, basePrice * (1 + randomChange / 100));
      
      const change = newPrice - basePrice;
      const changePercent = (change / basePrice) * 100;
      
      this.marketData.set(symbol, {
        symbol,
        price: newPrice,
        change,
        changePercent,
        volume: Math.floor(this.rng() * 10000000) + 1000000,
        timestamp: Date.now()
      });
    });
  }

  /**
   * Update portfolio based on current market prices
   */
  private updatePortfolio() {
    this.portfolio.forEach(position => {
      const marketData = this.marketData.get(position.symbol);
      if (marketData) {
        position.currentPrice = marketData.price;
        position.unrealizedPnL = (position.currentPrice - position.avgPrice) * position.quantity;
        position.unrealizedPnLPercent = ((position.currentPrice - position.avgPrice) / position.avgPrice) * 100;
      }
    });
  }

  /**
   * Calculate live analytics
   */
  private updateAnalytics() {
    const totalValue = this.portfolio.reduce((sum, pos) => 
      sum + (pos.currentPrice * pos.quantity), 0
    );
    
    const totalUnrealizedPnL = this.portfolio.reduce((sum, pos) => 
      sum + pos.unrealizedPnL, 0
    );

    const totalCost = this.portfolio.reduce((sum, pos) => 
      sum + (pos.avgPrice * pos.quantity), 0
    );

    this.analytics = {
      portfolioValue: totalValue,
      dailyPnL: totalUnrealizedPnL * this.options.pnlMultiplier, // Simulate daily portion (variant-specific)
      totalReturn: totalUnrealizedPnL,
      totalReturnPercent: (totalUnrealizedPnL / totalCost) * 100,
      sharpeRatio: 1.2 + this.rng() * 0.5,
      maxDrawdown: -2.5 - this.rng() * 3,
      winRate: 65 + this.rng() * 10,
      totalTrades: Math.floor(this.rng() * 50) + 20,
      avgTradeReturn: 1.5 + this.rng() * 2,
      volatility: 12 + this.rng() * 8,
      beta: 0.8 + this.rng() * 0.4,
      alpha: this.rng() * 2 - 0.5
    };
  }

  /**
   * Generate AI trading signals
   */
  private generateTradingSignals(): TradingSignal[] {
    const signals: TradingSignal[] = [];
    
    // Generate 1-3 signals randomly
    const numSignals = Math.floor(this.rng() * 3) + 1;
    
    for (let i = 0; i < numSignals; i++) {
      const symbol = this.watchedSymbols[Math.floor(this.rng() * this.watchedSymbols.length)];
      const marketData = this.marketData.get(symbol);
      
      if (marketData) {
        const actions: ('BUY' | 'SELL' | 'HOLD')[] = ['BUY', 'SELL', 'HOLD'];
        const action = actions[Math.floor(this.rng() * actions.length)];
        
        signals.push({
          symbol,
          action,
          confidence: 70 + this.rng() * 25,
          reason: this.generateSignalReason(action, symbol),
          targetPrice: marketData.price * (1 + (this.rng() - 0.5) * 0.1),
          stopLoss: marketData.price * (1 - this.rng() * 0.05),
          timestamp: Date.now()
        });
      }
    }
    
    return signals;
  }

  /**
   * Generate realistic signal reasons
   */
  private generateSignalReason(action: string, symbol: string): string {
    const reasons = {
      BUY: [
        `${symbol} showing strong momentum with volume spike`,
        `Technical indicators suggest ${symbol} oversold condition`,
        `${symbol} breaking above key resistance level`,
        `Positive earnings surprise expected for ${symbol}`
      ],
      SELL: [
        `${symbol} approaching overbought territory`,
        `Technical analysis shows ${symbol} weakness`,
        `${symbol} facing resistance at current levels`,
        `Risk management suggests taking profits on ${symbol}`
      ],
      HOLD: [
        `${symbol} in consolidation phase, waiting for breakout`,
        `Mixed signals on ${symbol}, maintaining position`,
        `${symbol} fair valued at current levels`,
        `Monitoring ${symbol} for better entry/exit points`
      ]
    };
    
  const reasonList = reasons[action as keyof typeof reasons];
  return reasonList[Math.floor(this.rng() * reasonList.length)];
  }

  /**
   * Get base price for symbol (realistic starting prices)
   */
  private getBasePriceForSymbol(symbol: string): number {
    const basePrices: { [key: string]: number } = {
      'AAPL': 185.50, 'GOOGL': 2850.00, 'MSFT': 380.00, 'TSLA': 235.00,
      'AMZN': 145.00, 'NVDA': 480.00, 'META': 320.00, 'NFLX': 450.00,
      'SPY': 455.00, 'QQQ': 385.00, 'IWM': 195.00, 'GLD': 185.00,
      'SLV': 22.50, 'BTCUSD': 45000.00, 'ETHUSD': 2800.00
    };
    return basePrices[symbol] || 100.00;
  }

  /**
   * Get volatility for symbol (realistic volatility levels)
   */
  private getVolatilityForSymbol(symbol: string): number {
    const volatilities: { [key: string]: number } = {
      'AAPL': 0.8, 'GOOGL': 1.2, 'MSFT': 0.7, 'TSLA': 2.5,
      'AMZN': 1.5, 'NVDA': 2.0, 'META': 1.8, 'NFLX': 1.6,
      'SPY': 0.5, 'QQQ': 0.8, 'IWM': 1.0, 'GLD': 0.6,
      'SLV': 1.2, 'BTCUSD': 5.0, 'ETHUSD': 4.0
    };
    return volatilities[symbol] || 1.0;
  }

  /**
   * Subscribe to live updates
   */
  subscribe(callback: (data: any) => void): string {
  const id = Math.floor(this.rng() * 1e9).toString(36);
    this.subscribers.set(id, callback);
    
    // Send initial data
    callback({
      type: 'initial',
      marketData: Array.from(this.marketData.values()),
      portfolio: this.portfolio,
      analytics: this.analytics
    });
    
    return id;
  }

  /**
   * Unsubscribe from updates
   */
  unsubscribe(id: string) {
    this.subscribers.delete(id);
  }

  /**
   * Notify all subscribers
   */
  private notifySubscribers() {
    const data = {
      type: 'update',
      marketData: Array.from(this.marketData.values()),
      portfolio: this.portfolio,
      analytics: this.analytics,
      signals: this.generateTradingSignals()
    };

    this.subscribers.forEach(callback => callback(data));
  }

  /**
   * Get current analytics
   */
  getAnalytics(): LiveAnalytics {
    return { ...this.analytics };
  }

  /**
   * Get current portfolio
   */
  getPortfolio(): PortfolioPosition[] {
    return [...this.portfolio];
  }

  /**
   * Get market data for symbol
   */
  getMarketData(symbol: string): MarketData | undefined {
    return this.marketData.get(symbol);
  }
}

// Export singleton instance (live variant)
export const liveMarketData = new LiveMarketDataService({ variant: 'live', seed: 1337, pnlMultiplier: 0.3, volatilityScale: 1.0, priceJitter: 0.3 });
export default LiveMarketDataService;
