/**
 * useRealtimePortfolio Hook
 * Integrates WebSocket for real-time portfolio updates
 */

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from './useWebSocket';

export const useRealtimePortfolio = (userId: string) => {
  const queryClient = useQueryClient();
  const { lastMessage, isConnected } = useWebSocket(
    `/ws/portfolio/${userId}`,
    userId
  );

  useEffect(() => {
    if (!lastMessage) return;

    // Handle portfolio updates
    if (lastMessage.type === 'portfolio_update') {
      queryClient.setQueryData(
        ['portfolio', userId],
        (old: any) => ({
          ...old,
          ...lastMessage.data
        })
      );
    }

    // Handle trade notifications
    if (lastMessage.type === 'trade_notification') {
      console.log('📊 New trade:', lastMessage.data);
      
      // Invalidate portfolio to refetch
      queryClient.invalidateQueries({ queryKey: ['portfolio', userId] });
    }

    // Handle position updates
    if (lastMessage.type === 'position_update') {
      queryClient.setQueryData(
        ['portfolio', userId],
        (old: any) => {
          if (!old) return old;
          
          const updatedPositions = old.positions.map((pos: any) => {
            if (pos.symbol === lastMessage.data.symbol) {
              return {
                ...pos,
                ...lastMessage.data
              };
            }
            return pos;
          });
          
          return {
            ...old,
            positions: updatedPositions
          };
        }
      );
    }
  }, [lastMessage, userId, queryClient]);

  return { isConnected };
};

