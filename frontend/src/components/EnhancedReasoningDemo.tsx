import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  Chip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControlLabel,
  Switch
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { apiService } from '../services/enhancedApiService';

interface ReasoningResult {
  content: string;
  confidence: number;
  strategy_used: string;
  verified: boolean;
  tokens_used: number;
  processing_time: number;
  enhanced: boolean;
}

interface AnalysisResult {
  status: string;
  analysis: string;
  confidence: number;
  strategy_used: string;
  verified: boolean;
  tokens_used: number;
  processing_time: number;
  enhanced: boolean;
  error?: string;
}

export const EnhancedReasoningDemo: React.FC = () => {
  const [prompt, setPrompt] = useState('Should I buy AAPL stock given current market conditions?');
  const [marketContext, setMarketContext] = useState(JSON.stringify({
    "current_price": 175.50,
    "volume": 45000000,
    "trend": "bullish",
    "rsi": 58.2,
    "moving_average_20": 172.30
  }, null, 2));
  const [riskParams, setRiskParams] = useState(JSON.stringify({
    "max_position_size": 1000,
    "max_risk_per_trade": 0.02,
    "stop_loss_percentage": 0.05
  }, null, 2));
  
  const [useAdvanced, setUseAdvanced] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!prompt.trim()) {
      setError('Please enter a trading prompt');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const marketData = JSON.parse(marketContext);
      const riskData = JSON.parse(riskParams);

      const response = await apiService.request({
        method: 'POST',
        url: '/api/ai/reasoning/analyze-trading-decision',
        data: {
          prompt: prompt.trim(),
          market_context: marketData,
          risk_parameters: riskData,
          use_advanced_reasoning: useAdvanced
        }
      });

      if (response.success) {
        setResult(response.analysis_result);
      } else {
        setError('Analysis failed: ' + (response.error || 'Unknown error'));
      }
    } catch (err: any) {
      setError('Error: ' + (err.response?.data?.detail || err.message || 'Network error'));
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getConfidenceText = (confidence: number) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Enhanced AI Reasoning Demo
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Test the ThinkMesh integration for enhanced trading decision analysis with confidence gating and parallel reasoning.
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Trading Decision Analysis
          </Typography>
          
          <TextField
            fullWidth
            label="Trading Prompt"
            multiline
            rows={3}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            sx={{ mb: 2 }}
            placeholder="e.g., Should I buy AAPL stock given current market conditions?"
          />

          <Accordion sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Market Context (JSON)</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TextField
                fullWidth
                multiline
                rows={6}
                value={marketContext}
                onChange={(e) => setMarketContext(e.target.value)}
                variant="outlined"
                placeholder="Market data in JSON format"
              />
            </AccordionDetails>
          </Accordion>

          <Accordion sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Risk Parameters (JSON)</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TextField
                fullWidth
                multiline
                rows={4}
                value={riskParams}
                onChange={(e) => setRiskParams(e.target.value)}
                variant="outlined"
                placeholder="Risk management parameters in JSON format"
              />
            </AccordionDetails>
          </Accordion>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={useAdvanced}
                  onChange={(e) => setUseAdvanced(e.target.checked)}
                />
              }
              label="Use Enhanced Reasoning (ThinkMesh)"
            />
            
            <Button
              variant="contained"
              onClick={handleAnalyze}
              disabled={loading}
              size="large"
            >
              {loading ? 'Analyzing...' : 'Analyze Decision'}
            </Button>
          </Box>

          {loading && <LinearProgress sx={{ mb: 2 }} />}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Analysis Result
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip
                  label={result.enhanced ? 'Enhanced' : 'Standard'}
                  color={result.enhanced ? 'primary' : 'default'}
                  size="small"
                />
                <Chip
                  label={`${getConfidenceText(result.confidence)} Confidence`}
                  color={getConfidenceColor(result.confidence)}
                  size="small"
                />
                {result.verified && (
                  <Chip
                    label="Verified"
                    color="success"
                    size="small"
                  />
                )}
              </Box>
            </Box>

            <Typography variant="body1" sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
              {result.analysis}
            </Typography>

            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Strategy Used
                </Typography>
                <Typography variant="body2">
                  {result.strategy_used}
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Confidence Score
                </Typography>
                <Typography variant="body2">
                  {(result.confidence * 100).toFixed(1)}%
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Processing Time
                </Typography>
                <Typography variant="body2">
                  {result.processing_time?.toFixed(2)}s
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Tokens Used
                </Typography>
                <Typography variant="body2">
                  {result.tokens_used || 'N/A'}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};
