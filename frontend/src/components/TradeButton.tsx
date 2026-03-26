import React, { useState } from 'react';
import { Button, CircularProgress, Alert } from '@mui/material';
import { executeTrade } from '../api/trade';

const TradeButton: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTrade = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const tradeData = { symbol: 'AAPL', quantity: 1, action: 'buy' };
      const res = await executeTrade(tradeData);
      setResult(res);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Button variant="contained" onClick={handleTrade} disabled={loading}>
        {loading ? <CircularProgress size={24} /> : 'Execute Trade'}
      </Button>
      {result && <Alert severity="success">Trade Success: {JSON.stringify(result)}</Alert>}
      {error && <Alert severity="error">{error}</Alert>}
    </div>
  );
};

export default TradeButton; 