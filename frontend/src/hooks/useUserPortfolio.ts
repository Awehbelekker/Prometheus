/**
 * useUserPortfolio Hook
 * Fetches real user portfolio data from backend
 */

import { useQuery } from '@tanstack/react-query';
import { apiCall } from '../config/api';

export interface Position {
  symbol: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  totalValue: number;
  profitLoss: number;
  profitLossPercentage: number;
}

export interface Portfolio {
  totalValue: number;
  totalInvested: number;
  totalReturn: number;
  returnPercentage: number;
  currency: string;
  positions: Position[];
  totalTrades: number;
  winningTrades?: number;
  losingTrades?: number;
  winRate?: number;
  lastUpdated?: string;
}

export const useUserPortfolio = (userId: string, enabled: boolean = true) => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['portfolio', userId],
    queryFn: async () => {
      try {
        // Try primary endpoint
        const response = await apiCall(`/api/user/portfolio/${userId}`);
        return response as Portfolio;
      } catch (err) {
        console.warn('Primary portfolio endpoint failed, trying fallback:', err);
        
        // Fallback: Try to get data from Alpaca paper account
        try {
          const alpacaAccount = await apiCall('/api/trading/alpaca/paper/account');
          const alpacaPositions = await apiCall('/api/trading/alpaca/paper/positions');
          
          // Transform Alpaca data to Portfolio format
          const positions: Position[] = alpacaPositions.map((pos: any) => ({
            symbol: pos.symbol,
            quantity: parseFloat(pos.qty),
            averagePrice: parseFloat(pos.avg_entry_price),
            currentPrice: parseFloat(pos.current_price),
            totalValue: parseFloat(pos.market_value),
            profitLoss: parseFloat(pos.unrealized_pl),
            profitLossPercentage: parseFloat(pos.unrealized_plpc) * 100
          }));
          
          const totalValue = parseFloat(alpacaAccount.portfolio_value || 0);
          const cash = parseFloat(alpacaAccount.cash || 0);
          const totalInvested = totalValue - positions.reduce((sum, pos) => sum + pos.profitLoss, 0);
          const totalReturn = totalValue - totalInvested;
          
          return {
            totalValue,
            totalInvested,
            totalReturn,
            returnPercentage: totalInvested > 0 ? (totalReturn / totalInvested) * 100 : 0,
            currency: 'USD',
            positions,
            totalTrades: 0,
            lastUpdated: new Date().toISOString()
          } as Portfolio;
        } catch (fallbackErr) {
          console.error('Fallback portfolio fetch failed:', fallbackErr);
          
          // Return empty portfolio if all fails
          return {
            totalValue: 0,
            totalInvested: 0,
            totalReturn: 0,
            returnPercentage: 0,
            currency: 'USD',
            positions: [],
            totalTrades: 0
          } as Portfolio;
        }
      }
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
    refetchOnWindowFocus: true,
    retry: 3,
    enabled
  });

  return {
    portfolio: data,
    isLoading,
    error,
    refetch
  };
};

