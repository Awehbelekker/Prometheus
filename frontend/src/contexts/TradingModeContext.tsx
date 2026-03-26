import React, { createContext, useContext, useState, useEffect } from 'react';
import { getApiUrl } from '../config/api';
import { getJsonWithRetry } from '../utils/network';


export type TradingMode = 'paper' | 'live' | 'demo';

interface TradingModeContextType {
  tradingMode: TradingMode;
  setTradingMode: (mode: TradingMode) => void;
  isLiveTrading: boolean;
  isPaperTrading: boolean;
  isDemoMode: boolean;
  canSwitchToLive: boolean;
  userTier: string;
  accountBalance: {
    paper: number;
    live: number;
    demo: number;
  };
  switchTradingMode: (mode: TradingMode) => Promise<boolean>;
}

const TradingModeContext = createContext<TradingModeContextType | undefined>(undefined);

export const useTradingMode = () => {
  const context = useContext(TradingModeContext);
  if (!context) {
    throw new Error('useTradingMode must be used within a TradingModeProvider');
  }
  return context;
};

interface TradingModeProviderProps {
  children: React.ReactNode;
  user?: any;
}

export const TradingModeProvider: React.FC<TradingModeProviderProps> = ({ children, user }) => {
  const [tradingMode, setTradingModeState] = useState<TradingMode>('paper');
  const [accountBalance, setAccountBalance] = useState({
    paper: 100000, // $100k virtual money for paper trading
    live: 0,       // Real money balance
    demo: 10000    // $10k for 48-hour demo
  });

  const userTier = user?.tier || user?.role || 'demo';

  // Determine what trading modes are available based on user tier
  const canSwitchToLive = userTier === 'admin' || userTier === 'premium';

  // Check if backend has ALWAYS_LIVE enabled and force live mode
  useEffect(() => {
    const checkBackendLiveMode = async () => {
      try {
        const debugStatus = await getJsonWithRetry<any>(getApiUrl('/api/alpaca/debug-status'), {}, { retries: 3, backoffMs: 400, maxBackoffMs: 4000, timeoutMs: 6000 });
        if (debugStatus.always_live === true) {
          console.log('🔴 Backend ALWAYS_LIVE detected - forcing frontend to live mode');
          setTradingModeState('live');
          return; // Skip normal user tier logic
        }
      } catch (error) {
        console.warn('Could not check backend live mode:', error);
      }

      // Normal user tier logic if ALWAYS_LIVE is not enabled
      if (userTier === 'demo') {
        setTradingModeState('demo');
      } else if (userTier === 'admin') {
        setTradingModeState('live'); // Admins default to live trading
      } else {
        setTradingModeState('paper'); // Premium users default to paper
      }
    };

    checkBackendLiveMode();
  }, [userTier]);

  const switchTradingMode = async (mode: TradingMode): Promise<boolean> => {
    try {
      // Validate mode switch permissions
      if (mode === 'live' && !canSwitchToLive) {
        throw new Error('Live trading requires Premium or Admin tier');
      }

      // For demo users, only allow demo mode
      if (userTier === 'demo' && mode !== 'demo') {
        throw new Error('Demo users can only use demo trading mode');
      }

      // API call to switch trading mode
      await getJsonWithRetry(getApiUrl('/api/trading/switch-mode'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({ mode, user_id: user?.id })
      }, { retries: 3, backoffMs: 400, maxBackoffMs: 4000, timeoutMs: 8000 });

      setTradingModeState(mode);

      // Load account balances for the new mode
      await loadAccountBalances();

      return true;
    } catch (error) {
      console.error('Error switching trading mode:', error);
      return false;
    }
  };

  const loadAccountBalances = async () => {
    try {
      const data = await getJsonWithRetry<any>(getApiUrl('/api/account/balances'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      }, { retries: 3, backoffMs: 400, maxBackoffMs: 4000, timeoutMs: 8000 });

      setAccountBalance({
        paper: data.paper_balance || 100000,
        live: data.live_balance || 0,
        demo: data.demo_balance || 10000
      });
    } catch (error) {
      console.error('Failed to load account balances:', error);
    }
  };

  const setTradingMode = (mode: TradingMode) => {
    switchTradingMode(mode);
  };

  const value: TradingModeContextType = {
    tradingMode,
    setTradingMode,
    isLiveTrading: tradingMode === 'live',
    isPaperTrading: tradingMode === 'paper',
    isDemoMode: tradingMode === 'demo',
    canSwitchToLive,
    userTier,
    accountBalance,
    switchTradingMode
  };

  return (
    <TradingModeContext.Provider value={value}>
      {children}
    </TradingModeContext.Provider>
  );
};

export default TradingModeContext;
