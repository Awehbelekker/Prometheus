import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import {
  Activity,
  Brain,
  Zap,
  TrendingUp,
  Shield,
  Target,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';

import { apiCall } from '../config/api';

interface QuantumOptimizationResult {
  optimization_id: string;
  optimal_weights: number[];
  expected_return: number;
  sharpe_ratio: number;
  quantum_advantage: boolean;
  execution_time_ms: number;
  confidence: number;
}

interface QuantumStatus {
  connected: boolean;
  total_optimizations: number;
  quantum_advantages: number;
  advantage_rate: number;
  algorithms_used: string[];
}

interface QuantumTradeRequest {
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  order_type: 'market' | 'limit' | 'stop' | 'stop_limit';
  price?: number;
  stop_price?: number;
  broker: 'interactive_brokers' | 'alpaca';
  time_in_force: 'day' | 'gtc' | 'ioc' | 'fok';
}

const QuantumTrading: React.FC = () => {
  const [quantumStatus, setQuantumStatus] = useState<QuantumStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<QuantumOptimizationResult | null>(null);
  const [tradeRequest, setTradeRequest] = useState<QuantumTradeRequest>({
    symbol: '',
    side: 'buy',
    quantity: 0,
    order_type: 'market',
    price: undefined,
    stop_price: undefined,
    broker: 'interactive_brokers',
    time_in_force: 'day'
  });
  const [executingTrade, setExecutingTrade] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sample assets for portfolio optimization
  const sampleAssets = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX'];
  const sampleReturns = Array.from({ length: 252 }, () =>
    sampleAssets.map(() => (Math.random() - 0.5) * 0.1)
  );

  useEffect(() => {
    checkQuantumStatus();
  }, []);

  const checkQuantumStatus = async () => {
    try {
      const status = await apiCall('/api/quantum/status');
      setQuantumStatus(status);
      setIsConnected(status.connected);
    } catch (error) {
      console.error('Failed to check quantum status:', error);
    }
  };

  const connectQuantum = async () => {
    try {
      setError(null);
      await apiCall('/api/quantum/connect', { method: 'POST' });
      setIsConnected(true);
      await checkQuantumStatus();
    } catch (error) {
      setError('Connection error: ' + error);
    }
  };

  const optimizePortfolio = async () => {
    try {
      setError(null);
      setIsOptimizing(true);

      const result = await apiCall('/api/quantum/portfolio/optimize', {
        method: 'POST',
        body: JSON.stringify({
          assets: sampleAssets,
          returns_data: sampleReturns,
          risk_free_rate: 0.02,
          optimization_target: 'sharpe_ratio'
        })
      });

      setOptimizationResult(result);
    } catch (error) {
      setError('Optimization error: ' + error);
    } finally {
      setIsOptimizing(false);
    }
  };

  const executeQuantumTrade = async () => {
    if (!tradeRequest.symbol || tradeRequest.quantity <= 0) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setError(null);
      setExecutingTrade(true);

      const result = await apiCall('/api/quantum/trade/execute', {
        method: 'POST',
        body: JSON.stringify(tradeRequest)
      });

      setError(null);
      // Reset form
      setTradeRequest({
        symbol: '',
        side: 'buy',
        quantity: 0,
        order_type: 'market',
        price: undefined,
        stop_price: undefined,
        broker: 'interactive_brokers',
        time_in_force: 'day'
      });
    } catch (error) {
      setError('Trade execution error: ' + error);
    } finally {
      setExecutingTrade(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Quantum Trading Engine</h1>
          <p className="text-gray-400">Advanced quantum computing for trading optimization</p>
        </div>
        <Badge variant={isConnected ? "default" : "danger"} className="flex items-center gap-2">
          {isConnected ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          {isConnected ? 'Connected' : 'Disconnected'}
        </Badge>
      </div>

      {/* Connection Status */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Zap className="h-5 w-5" />
            Quantum System Status
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {!isConnected ? (
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400">Quantum computing resources not connected</p>
                <p className="text-sm text-gray-500">Connect to enable quantum optimization</p>
              </div>
              <Button onClick={connectQuantum} className="bg-blue-600 hover:bg-blue-700">
                Connect Quantum
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-white">{quantumStatus?.total_optimizations || 0}</p>
                <p className="text-sm text-gray-400">Total Optimizations</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-400">{quantumStatus?.quantum_advantages || 0}</p>
                <p className="text-sm text-gray-400">Quantum Advantages</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-400">
                  {((quantumStatus?.advantage_rate || 0) * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-gray-400">Advantage Rate</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-400">
                  {quantumStatus?.algorithms_used?.length || 0}
                </p>
                <p className="text-sm text-gray-400">Algorithms Used</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Portfolio Optimization */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Brain className="h-5 w-5" />
            Quantum Portfolio Optimization
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400">Optimize portfolio using quantum algorithms</p>
              <p className="text-sm text-gray-500">QAOA algorithm for optimal asset allocation</p>
            </div>
            <Button
              onClick={optimizePortfolio}
              disabled={!isConnected || isOptimizing}
              className="bg-purple-600 hover:bg-purple-700"
            >
              {isOptimizing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Optimizing...
                </>
              ) : (
                <>
                  <Target className="mr-2 h-4 w-4" />
                  Optimize Portfolio
                </>
              )}
            </Button>
          </div>

          {optimizationResult && (
            <div className="space-y-4 p-4 bg-gray-800 rounded-lg">
              <h3 className="text-lg font-semibold text-white">Optimization Results</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-400">Expected Return</p>
                  <p className="text-lg font-bold text-green-400">
                    {(optimizationResult.expected_return * 100).toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Sharpe Ratio</p>
                  <p className="text-lg font-bold text-blue-400">
                    {optimizationResult.sharpe_ratio.toFixed(3)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Confidence</p>
                  <p className="text-lg font-bold text-yellow-400">
                    {(optimizationResult.confidence * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Execution Time</p>
                  <p className="text-lg font-bold text-purple-400">
                    {optimizationResult.execution_time_ms.toFixed(0)}ms
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={optimizationResult.quantum_advantage ? "default" : "default"}>
                  {optimizationResult.quantum_advantage ? 'Quantum Advantage' : 'Classical Equivalent'}
                </Badge>
                <span className="text-sm text-gray-400">
                  Optimization ID: {optimizationResult.optimization_id.slice(0, 8)}...
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quantum Trade Execution */}
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Activity className="h-5 w-5" />
            Quantum Trade Execution
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="symbol" className="text-white">Symbol</Label>
              <Input
                id="symbol"
                value={tradeRequest.symbol}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTradeRequest({...tradeRequest, symbol: e.target.value})}
                placeholder="e.g., AAPL"
                className="bg-gray-800 border-gray-600 text-white"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="quantity" className="text-white">Quantity</Label>
              <Input
                id="quantity"
                type="number"
                value={tradeRequest.quantity}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTradeRequest({...tradeRequest, quantity: parseFloat(e.target.value) || 0})}
                placeholder="100"
                className="bg-gray-800 border-gray-600 text-white"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="side" className="text-white">Side</Label>
              <Select
                value={tradeRequest.side}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setTradeRequest({...tradeRequest, side: e.target.value as 'buy' | 'sell'})}
              >
                <SelectTrigger className="bg-gray-800 border-gray-600 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="buy">Buy</SelectItem>
                  <SelectItem value="sell">Sell</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="order_type" className="text-white">Order Type</Label>
              <Select
                value={tradeRequest.order_type}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setTradeRequest({...tradeRequest, order_type: e.target.value as 'market' | 'limit'})}
              >
                <SelectTrigger className="bg-gray-800 border-gray-600 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="market">Market</SelectItem>
                  <SelectItem value="limit">Limit</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {tradeRequest.order_type === 'limit' && (
            <div className="space-y-2">
              <Label htmlFor="price" className="text-white">Price</Label>
              <Input
                id="price"
                type="number"
                value={tradeRequest.price || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTradeRequest({...tradeRequest, price: parseFloat(e.target.value) || undefined})}
                placeholder="150.00"
                className="bg-gray-800 border-gray-600 text-white"
              />
            </div>
          )}

          <Button
            onClick={executeQuantumTrade}
            disabled={!isConnected || executingTrade || !tradeRequest.symbol || tradeRequest.quantity <= 0}
            className="w-full bg-green-600 hover:bg-green-700"
          >
            {executingTrade ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Executing Quantum Trade...
              </>
            ) : (
              <>
                <Zap className="mr-2 h-4 w-4" />
                Execute Quantum Trade
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert variant="danger">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Quantum Statistics */}
      {quantumStatus && (
        <Card className="bg-gray-900 border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <TrendingUp className="h-5 w-5" />
              Quantum Performance Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm text-gray-400 mb-1">
                  <span>Quantum Advantage Rate</span>
                  <span>{((quantumStatus.advantage_rate || 0) * 100).toFixed(1)}%</span>
                </div>
                <Progress value={quantumStatus.advantage_rate * 100} className="h-2" />
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-400">Algorithms Used</p>
                  <p className="text-white font-medium">
                    {quantumStatus.algorithms_used?.join(', ') || 'None'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400">Total Optimizations</p>
                  <p className="text-white font-medium">{quantumStatus.total_optimizations}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default QuantumTrading;