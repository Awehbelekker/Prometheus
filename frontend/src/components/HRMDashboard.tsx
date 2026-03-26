import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Extension as ExtensionIcon,
  Route as RouteIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiCall } from '../config/api';


interface HRMPersona {
  type: string;
  risk_tolerance: number;
  reasoning_style: string;
  preferred_assets: string[];
  max_position_size: number;
  stop_loss_percentage: number;
  take_profit_percentage: number;
  trading_frequency: string;
  hrm_weights: Record<string, number>;
  performance: {
    total_decisions: number;
    success_rate: number;
    last_decision_time?: string;
  };
}

interface HRMAnalysis {
  action: string;
  confidence: number;
  position_size: number;
  risk_level: number;
  persona_type: string;
  persona_confidence: number;
  risk_adjusted_action: string;
  reasoning_levels: {
    high_level: number[];
    low_level: number[];
    arc_level: number[];
    patterns: number[];
  };
  timestamp: string;
  hrm_version: string;
}

const HRMDashboard: React.FC = () => {
  const [personas, setPersonas] = useState<Record<string, HRMPersona>>({});
  const [selectedPersona, setSelectedPersona] = useState<string>('balanced_hrm');
  const [analysis, setAnalysis] = useState<HRMAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPersonas();
    loadSystemStatus();
  }, []);

  const loadPersonas = async () => {
    try {
      const data = await apiCall('/api/hrm/personas');
      if (data.success) {
        setPersonas(data.personas);
      }
    } catch (err) {
      setError('Failed to load HRM personas');
    }
  };

  const loadSystemStatus = async () => {
    try {
      const data = await apiCall('/api/hrm/status');
      setSystemStatus(data);
    } catch (err) {
      setError('Failed to load HRM system status');
    }
  };

  const runAnalysis = async () => {
    setIsAnalyzing(true);
    setError(null);

    try {
      // Sample market data for demo
      const marketData = {
        prices: [100.0, 101.5, 99.8, 102.3, 103.1],
        volumes: [1000000, 1200000, 800000, 1500000, 1100000],
        indicators: {
          rsi: 65.5,
          macd: 0.8,
          bollinger_upper: 105.0,
          bollinger_lower: 98.0
        },
        sentiment: {
          positive: 0.6,
          negative: 0.2,
          neutral: 0.2
        }
      };

      const userContext = {
        profile: {
          risk_tolerance: 0.5,
          investment_goal: 'growth',
          time_horizon: 'medium'
        },
        trading_history: [],
        portfolio: {
          total_value: 50000,
          cash: 10000,
          positions: {}
        },
        risk_preferences: {
          max_drawdown: 0.1,
          target_return: 0.15,
          volatility_tolerance: 0.2
        }
      };

      const data = await apiCall('/api/hrm/persona/analyze', {
        method: 'POST',
        body: JSON.stringify({
          market_data: marketData,
          user_context: userContext,
          persona_type: selectedPersona
        })
      });

      if (data.success) {
        setAnalysis(data.decision);
      }
    } catch (err) {
      setError('Failed to run HRM analysis');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getPersonaIcon = (personaType: string) => {
    switch (personaType) {
      case 'conservative_hrm':
        return <PsychologyIcon sx={{ color: '#4caf50' }} />;
      case 'aggressive_hrm':
        return <TrendingUpIcon sx={{ color: '#f44336' }} />;
      case 'balanced_hrm':
        return <SpeedIcon sx={{ color: '#2196f3' }} />;
      case 'quantum_hrm':
        return <ExtensionIcon sx={{ color: '#9c27b0' }} />;
      case 'arbitrage_hrm':
        return <RouteIcon sx={{ color: '#ff9800' }} />;
      default:
        return <PsychologyIcon />;
    }
  };

  const getReasoningLevelColor = (level: string) => {
    switch (level) {
      case 'high_level':
        return '#4caf50';
      case 'low_level':
        return '#f44336';
      case 'arc_level':
        return '#2196f3';
      case 'sudoku_level':
        return '#9c27b0';
      case 'maze_level':
        return '#ff9800';
      default:
        return '#757575';
    }
  };

  return (
    <Box sx={{ p: 3, background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)', minHeight: '100vh' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" sx={{ color: '#00d4ff', mb: 3, fontWeight: 600 }}>
          🤖 HRM Hierarchical Reasoning Dashboard
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* System Status */}
          <Grid item xs={12} md={6}>
            <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid #333' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
                  🚀 HRM System Status
                </Typography>
                {systemStatus && (
                  <Box>
                    <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                      Version: {systemStatus.hrm_version}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                      Status: {systemStatus.status}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                      Total Decisions: {systemStatus.engine_metrics?.total_decisions || 0}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#888' }}>
                      Average Confidence: {((systemStatus.engine_metrics?.average_confidence || 0) * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Analysis Controls */}
          <Grid item xs={12} md={6}>
            <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid #333' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
                  🎯 Analysis Controls
                </Typography>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel sx={{ color: '#888' }}>Select HRM Persona</InputLabel>
                  <Select
                    value={selectedPersona}
                    onChange={(e) => setSelectedPersona(e.target.value)}
                    sx={{ color: '#fff' }}
                  >
                    {Object.keys(personas).map((personaType) => (
                      <MenuItem key={personaType} value={personaType}>
                        {personaType.replace('_hrm', '').toUpperCase()} HRM
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <Button
                  variant="contained"
                  onClick={runAnalysis}
                  disabled={isAnalyzing}
                  startIcon={isAnalyzing ? <StopIcon /> : <PlayArrowIcon />}
                  sx={{
                    background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #00b8e6, #e55a2b)'
                    }
                  }}
                >
                  {isAnalyzing ? 'Analyzing...' : 'Run HRM Analysis'}
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Analysis Results */}
          {analysis && (
            <Grid item xs={12}>
              <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid #333' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
                    📊 HRM Analysis Results
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Action: <Box component="span" sx={{ color: '#fff' }}>{analysis.action}</Box>
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Confidence: <Box component="span" sx={{ color: '#fff' }}>{(analysis.confidence * 100).toFixed(1)}%</Box>
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Position Size: <Box component="span" sx={{ color: '#fff' }}>{(analysis.position_size * 100).toFixed(1)}%</Box>
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Risk Level: <Box component="span" sx={{ color: '#fff' }}>{(analysis.risk_level * 100).toFixed(1)}%</Box>
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Persona: <Box component="span" sx={{ color: '#fff' }}>{analysis.persona_type}</Box>
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Persona Confidence: <Box component="span" sx={{ color: '#fff' }}>{(analysis.persona_confidence * 100).toFixed(1)}%</Box>
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Risk Adjusted Action: <Box component="span" sx={{ color: '#fff' }}>{analysis.risk_adjusted_action}</Box>
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#888' }}>
                        HRM Version: <Box component="span" sx={{ color: '#fff' }}>{analysis.hrm_version}</Box>
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* HRM Personas */}
          <Grid item xs={12}>
            <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid #333' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
                  🤖 HRM-Enhanced AI Personas
                </Typography>
                <Grid container spacing={2}>
                  {Object.entries(personas).map(([personaType, persona]) => (
                    <Grid item xs={12} md={6} lg={4} key={personaType}>
                      <Card sx={{ background: 'rgba(40, 40, 40, 0.8)', border: '1px solid #444' }}>
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            {getPersonaIcon(personaType)}
                            <Typography variant="subtitle1" sx={{ color: '#fff', ml: 1 }}>
                              {personaType.replace('_hrm', '').toUpperCase()}
                            </Typography>
                          </Box>
                          <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                            Risk Tolerance: {(persona.risk_tolerance * 100).toFixed(0)}%
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                            Success Rate: {(persona.performance.success_rate * 100).toFixed(1)}%
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                            Total Decisions: {persona.performance.total_decisions}
                          </Typography>
                          <Box sx={{ mt: 1 }}>
                            {Object.entries(persona.hrm_weights).map(([level, weight]) => (
                              <Chip
                                key={level}
                                label={`${level}: ${(weight * 100).toFixed(0)}%`}
                                size="small"
                                sx={{
                                  mr: 0.5,
                                  mb: 0.5,
                                  background: getReasoningLevelColor(level),
                                  color: '#fff'
                                }}
                              />
                            ))}
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Reasoning Levels */}
          <Grid item xs={12}>
            <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid #333' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
                  🧠 HRM Reasoning Levels
                </Typography>
                <Accordion sx={{ background: 'rgba(40, 40, 40, 0.8)', mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#00d4ff' }} />}>
                    <Typography sx={{ color: '#fff' }}>High-Level Abstract Planning</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" sx={{ color: '#888' }}>
                      Slow, abstract planning like human brain. Responsible for portfolio strategy and risk assessment.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
                <Accordion sx={{ background: 'rgba(40, 40, 40, 0.8)', mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#00d4ff' }} />}>
                    <Typography sx={{ color: '#fff' }}>Low-Level Detailed Execution</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" sx={{ color: '#888' }}>
                      Rapid, detailed computations for specific trade execution and position sizing.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
                <Accordion sx={{ background: 'rgba(40, 40, 40, 0.8)', mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#00d4ff' }} />}>
                    <Typography sx={{ color: '#fff' }}>ARC-Level General Reasoning</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" sx={{ color: '#888' }}>
                      General reasoning capabilities based on ARC benchmark for complex problem solving.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
                <Accordion sx={{ background: 'rgba(40, 40, 40, 0.8)', mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#00d4ff' }} />}>
                    <Typography sx={{ color: '#fff' }}>Sudoku-Level Pattern Recognition</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" sx={{ color: '#888' }}>
                      Complex pattern recognition for market structure analysis and technical patterns.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
                <Accordion sx={{ background: 'rgba(40, 40, 40, 0.8)' }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#00d4ff' }} />}>
                    <Typography sx={{ color: '#fff' }}>Maze-Level Path Finding</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" sx={{ color: '#888' }}>
                      Optimal path finding for arbitrage detection and route optimization.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </motion.div>
    </Box>
  );
};

export default HRMDashboard;