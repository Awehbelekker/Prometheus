import React, { createContext, useContext, useState, useEffect } from 'react';
import './RealWorldIntelligenceProvider.css';
import { apiCall } from '../config/api';


// Interface definitions for market intelligence data
interface NewsEvent {
  id: string;
  title: string;
  source: string;
  timestamp: string;
  impact: 'high' | 'medium' | 'low';
  description: string;
  relatedAssets: string[];
}

interface EconomicEvent {
  id: string;
  name: string;
  actual: number;
  forecast: number;
  previous: number;
  impact: 'high' | 'medium' | 'low';
  timestamp: string;
}

interface RegulatoryEvent {
  id: string;
  title: string;
  authority: string;
  region: string;
  timestamp: string;
  description: string;
  affectedSectors: string[];
}

interface WhaleMovement {
  symbol: string;
  amount: number;
  fromExchange: string;
  toExchange: string;
  timestamp: string;
  impact: 'bullish' | 'bearish' | 'neutral';
}

interface ExchangeFlow {
  exchange: string;
  netFlow: number;
  timestamp: string;
}

interface MarketIntelligence {
  sentiment: {
    twitter: number;         // -1 to 1
    reddit: number;          // -1 to 1
    news: number;           // -1 to 1
    overall: number;        // -1 to 1
  };
  economic: {
    inflation: number;
    unemployment: number;
    interestRates: number;
    dollarIndex: number;
  };
  crypto: {
    whaleMovements: WhaleMovement[];
    exchangeFlows: ExchangeFlow[];
    fearGreedIndex: number;
    regulatorySentiment: number;
  };
  events: {
    majorNews: NewsEvent[];
    economicReleases: EconomicEvent[];
    regulatoryChanges: RegulatoryEvent[];
  };
}

// Create context for market intelligence
const RealWorldIntelligenceContext = createContext<{
  intelligence: MarketIntelligence | null;
  isLoading: boolean;
  lastUpdate: string;
}>({
  intelligence: null,
  isLoading: true,
  lastUpdate: ''
});

// Define mock data for development
const generateMockData = (): MarketIntelligence => {
  const now = new Date().toISOString();

  // Generate random value between min and max
  const randomRange = (min: number, max: number) => min + Math.random() * (max - min);

  // Randomize sentiment values between -1 and 1
  const twitterSentiment = randomRange(-0.8, 0.8);
  const redditSentiment = randomRange(-0.7, 0.7);
  const newsSentiment = randomRange(-0.5, 0.5);

  // Calculate overall sentiment as weighted average
  const overallSentiment = (twitterSentiment * 0.3 + redditSentiment * 0.3 + newsSentiment * 0.4);

  // Generate mock whale movements (0-8 movements)
  const whaleCount = Math.floor(randomRange(0, 8));
  const whaleMovements: WhaleMovement[] = [];

  for (let i = 0; i < whaleCount; i++) {
    const symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'AVAX', 'LINK'];
    const exchanges = ['Binance', 'Coinbase', 'Kraken', 'FTX', 'Wallet'];

    whaleMovements.push({
      symbol: symbols[Math.floor(Math.random() * symbols.length)],
      amount: randomRange(100, 5000) * 1000, // $100k to $5M
      fromExchange: exchanges[Math.floor(Math.random() * exchanges.length)],
      toExchange: exchanges[Math.floor(Math.random() * exchanges.length)],
      timestamp: now,
      impact: Math.random() > 0.6 ? 'bullish' : Math.random() > 0.5 ? 'bearish' : 'neutral'
    });
  }

  return {
    sentiment: {
      twitter: twitterSentiment,
      reddit: redditSentiment,
      news: newsSentiment,
      overall: overallSentiment
    },
    economic: {
      inflation: randomRange(0.02, 0.08), // 2% to 8%
      unemployment: randomRange(0.03, 0.06), // 3% to 6%
      interestRates: randomRange(0.02, 0.05), // 2% to 5%
      dollarIndex: randomRange(90, 110) // 90 to 110
    },
    crypto: {
      whaleMovements: whaleMovements,
      exchangeFlows: [
        {
          exchange: 'Binance',
          netFlow: randomRange(-2000, 2000) * 1000, // -$2M to $2M
          timestamp: now
        },
        {
          exchange: 'Coinbase',
          netFlow: randomRange(-1500, 1500) * 1000, // -$1.5M to $1.5M
          timestamp: now
        }
      ],
      fearGreedIndex: Math.floor(randomRange(10, 90)), // 10 to 90
      regulatorySentiment: randomRange(-0.5, 0.5) // -0.5 to 0.5
    },
    events: {
      majorNews: [
        {
          id: 'news1',
          title: Math.random() > 0.5 ? 'Market Rally Continues Amid Economic Recovery' : 'Markets Pull Back Following Central Bank Announcement',
          source: 'Financial Times',
          timestamp: now,
          impact: 'medium',
          description: 'Latest market movements based on economic data and central bank policy.',
          relatedAssets: ['SPY', 'QQQ', 'BTC', 'USD']
        }
      ],
      economicReleases: [
        {
          id: 'econ1',
          name: 'CPI Data',
          actual: randomRange(0.02, 0.07), // 2% to 7%
          forecast: 0.04, // 4%
          previous: 0.038, // 3.8%
          impact: 'high',
          timestamp: now
        },
        {
          id: 'econ2',
          name: 'Non-Farm Payrolls',
          actual: randomRange(150, 350) * 1000, // 150k to 350k
          forecast: 220000, // 220k
          previous: 210000, // 210k
          impact: 'medium',
          timestamp: now
        }
      ],
      regulatoryChanges: []
    }
  };
};

export const RealWorldIntelligenceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [intelligence, setIntelligence] = useState<MarketIntelligence | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIntelligence = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Get the auth token if available (preserve header source)
        const token = localStorage.getItem('auth_token');
        const data = await apiCall('/api/intelligence/real-time', {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined
        });

        // Basic shape check
        if (!data || typeof data !== 'object' || !data.sentiment || !data.economic || !data.crypto || !data.events) {
          throw new Error('API returned unexpected data shape');
        }

        setIntelligence(data);
        setLastUpdate(new Date().toISOString());
        setIsLoading(false);

      } catch (err: any) {
        console.error('Failed to fetch market intelligence from API, using mock data:', err);

        // Show a less technical error message
        let errorMessage = 'Live market data unavailable. Showing simulated data.';
        if (err.message.includes('Failed to fetch') || err.name === 'AbortError') {
          errorMessage = 'Could not connect to market intelligence server. Showing simulated data.';
        }
        setError(errorMessage);

        try {
          const mockData = generateMockData();
          setIntelligence(mockData);
          setLastUpdate(new Date().toISOString());
        } catch (mockErr) {
          setError('Unable to load market intelligence data. Please try again later.');
          setIntelligence(null);
        }
        setIsLoading(false);
      }
    };
    fetchIntelligence();
    const interval = setInterval(fetchIntelligence, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <RealWorldIntelligenceContext.Provider value={{ intelligence, isLoading, lastUpdate }}>
      {error && (
        <div className="intelligence-warning">
          {error}
        </div>
      )}
      {children}
    </RealWorldIntelligenceContext.Provider>
  );
};

export const useRealWorldIntelligence = () => useContext(RealWorldIntelligenceContext);
