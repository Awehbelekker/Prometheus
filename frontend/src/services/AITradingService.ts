/**
 * 🤖 AI Trading Service Integration
 * Frontend service for connecting to PROMETHEUS AI trading endpoints
 */

import { useState } from 'react';
import { getJsonWithRetry } from '../utils/network';


// Ensure this file is treated as a module
export {};

export interface AIMarketSentiment {
  symbol: string;
  sentiment: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  reasoning: string;
  bullish_factors: string[];
  bearish_factors: string[];
  market_data: {
    symbol: string;
    price: number;
    volume: number;
      change_percent: number;
    market_cap: number;
    news_sentiment: number;
  };
  news_count: number;
}

export interface AITradingStrategy {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string;
  price_target: number | null;
  stop_loss: number | null;
  time_horizon: string;
  risk_assessment: string;
  market_sentiment: string;
  strategy_context: string;
}

export interface AITechnicalAnalysis {
  symbol: string;
  patterns: string[];
  indicators: {
    [key: string]: {
      value: number;
      signal: 'bullish' | 'bearish' | 'neutral';
      strength: number;
    };
  };
  support_resistance: {
    support_levels: number[];
    resistance_levels: number[];
  };
  trend_analysis: {
    short_term: string;
    medium_term: string;
    long_term: string;
  };
  confidence: number;
}

export interface AIRiskAssessment {
  risk_level: 'low' | 'medium' | 'high';
  risk_score: number;
  risk_factors: string[];
  recommendations: string[];
  portfolio_positions: number;
  market_condition: string;
}

export interface AITradingResponse<T> {
  success: boolean;
  data: T;
  ai_analysis?: any;
  processing_time: number;
  model_used: string;
  confidence: number;
}

class AITradingService {
  private baseUrl = 'http://localhost:8000/api/ai-trading';
  private isAvailable = false;

  constructor() {
    this.checkAvailability();
  }

  private async checkAvailability(): Promise<void> {
    try {
      await getJsonWithRetry(`${this.baseUrl}/health`);
      this.isAvailable = true;
    } catch (error) {
      this.isAvailable = false;
      console.warn('AI Trading Service not available:', error);
    }
  }

  public async getServiceHealth(): Promise<any> {
    try {
      return await getJsonWithRetry(`${this.baseUrl}/health`);
    } catch (error) {
      console.error('Failed to get AI service health:', error);
      return { ai_trading_service: 'unavailable' };
    }
  }

  public async analyzeSentiment(symbol: string, modelSize: '20b' | '120b' = '20b'): Promise<AITradingResponse<AIMarketSentiment> | null> {
    if (!this.isAvailable) {
      await this.checkAvailability();
      if (!this.isAvailable) return null;
    }

    try {
      return await getJsonWithRetry(`${this.baseUrl}/sentiment-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          include_news: true,
          model_size: modelSize
        })
      });
    } catch (error) {
      console.error('Sentiment analysis failed:', error);
      return null;
    }
  }

  public async generateStrategy(
    symbol: string,
    marketData: any,
    context: string = 'General market analysis',
    timeHorizon: string = 'intraday',
    riskTolerance: string = 'moderate'
  ): Promise<AITradingResponse<AITradingStrategy> | null> {
    if (!this.isAvailable) {
      await this.checkAvailability();
      if (!this.isAvailable) return null;
    }

    try {
      return await getJsonWithRetry(`${this.baseUrl}/trading-strategy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          market_data: marketData,
          strategy_context: context,
          analysis_type: 'technical',
          time_horizon: timeHorizon,
          risk_tolerance: riskTolerance,
          model_size: '120b'
        })
      });
    } catch (error) {
      console.error('Strategy generation failed:', error);
      return null;
    }
  }

  public async analyzeTechnical(
    symbol: string,
    priceData: any[],
    indicators?: any
  ): Promise<AITradingResponse<AITechnicalAnalysis> | null> {
    if (!this.isAvailable) {
      await this.checkAvailability();
      if (!this.isAvailable) return null;
    }

    try {
      return await getJsonWithRetry(`${this.baseUrl}/technical-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          price_data: priceData,
          indicators: indicators || {},
          model_size: '20b'
        })
      });
    } catch (error) {
      console.error('Technical analysis failed:', error);
      return null;
    }
  }

  public async assessRisk(
    portfolio: any,
    marketConditions: any
  ): Promise<AITradingResponse<AIRiskAssessment> | null> {
    if (!this.isAvailable) {
      await this.checkAvailability();
      if (!this.isAvailable) return null;
    }

    try {
      return await getJsonWithRetry(`${this.baseUrl}/risk-assessment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          portfolio,
          market_conditions: marketConditions,
          model_size: '120b'
        })
      });
    } catch (error) {
      console.error('Risk assessment failed:', error);
      return null;
    }
  }

  public async getModelStatus(): Promise<any> {
    try {
      return await getJsonWithRetry(`${this.baseUrl}/models/status`);
    } catch (error) {
      console.error('Failed to get model status:', error);
      return { models: {} };
    }
  }

  public isServiceAvailable(): boolean {
    return this.isAvailable;
  }





  // Batch analysis for multiple symbols
  public async batchAnalysis(
    symbols: string[],
    analysisTypes: string[] = ['sentiment', 'technical', 'risk']
  ): Promise<any> {
    if (!this.isAvailable) {
      await this.checkAvailability();
      if (!this.isAvailable) return null;
    }

    try {
      const marketData: { [key: string]: any } = {};
      symbols.forEach(symbol => {
        marketData[symbol] = {
          price: 150.0 + Math.random() * 100,
          volume: 1000000 + Math.random() * 500000
        };
      });

      return await getJsonWithRetry(`${this.baseUrl}/batch-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbols,
          analysis_types: analysisTypes,
          market_data: marketData
        })
      });
    } catch (error) {
      console.error('Batch analysis failed:', error);
      return null;
    }
  }

  /**
   * 🚀 Get real-time market data with AI enhancement
   */
  async getRealTimeMarketData(symbols: string[]): Promise<any> {
    try {
      const symbolsParam = symbols.join(',');
      const data = await getJsonWithRetry(`http://localhost:8000/api/ai/trading/real-time-data?symbols=${symbolsParam}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
      });
      if (data.success) {
        return data.real_time_data;
      }
      throw new Error('Real-time data request failed');
    } catch (error) {
      console.error('Real-time market data error:', error);
      throw error;
    }
  }

  /**
   * 📊 Get enhanced market sentiment using real data
   */
  async getEnhancedSentiment(symbol: string): Promise<any> {
    try {
      const realTimeData = await this.getRealTimeMarketData([symbol]);

      if (realTimeData[symbol]) {
        const data = realTimeData[symbol];
        return {
          symbol,
          sentiment: data.ai_sentiment || 'neutral',
          confidence: data.ai_confidence || 0.5,
          price: data.price,
          change_percent: data.change_percent,
          volume: data.volume,
          source: data.source,
          real_data: true,
          last_updated: data.last_updated
        };
      } else {
        // Fallback to regular sentiment analysis
        return await this.analyzeSentiment(symbol);
      }
    } catch (error) {
      console.error('Enhanced sentiment error:', error);
      // Fallback to regular sentiment analysis
      return await this.analyzeSentiment(symbol);
    }
  }
}

// Create singleton instance
export const aiTradingService = new AITradingService();

// React hook for AI trading with real-time data
export const useAITrading = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeSymbol = async (symbol: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Use enhanced sentiment analysis with real-time data
      const [sentiment, modelStatus] = await Promise.all([
        aiTradingService.getEnhancedSentiment(symbol),
        aiTradingService.getModelStatus()
      ]);

      return { sentiment, modelStatus };
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const getRealTimeData = async (symbols: string[]) => {
    setIsLoading(true);
    setError(null);

    try {
      const realTimeData = await aiTradingService.getRealTimeMarketData(symbols);
      return realTimeData;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Real-time data unavailable');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const generateTradingStrategy = async (symbol: string, marketData: any) => {
    setIsLoading(true);
    setError(null);

    try {
      const strategy = await aiTradingService.generateStrategy(
        symbol,
        marketData,
        `Analysis for ${symbol} with current market conditions`
      );
      return strategy;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    analyzeSymbol,
    generateTradingStrategy,
    getRealTimeData,
    isLoading,
    error,
    isServiceAvailable: aiTradingService.isServiceAvailable()
  };
};

export default aiTradingService;
