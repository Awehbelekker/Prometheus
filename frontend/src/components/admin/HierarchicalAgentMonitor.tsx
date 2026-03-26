/**
 * 🤖 HIERARCHICAL AGENT MONITOR
 * 
 * Displays real-time status and performance of all 17 hierarchical trading agents:
 * - 3 Supervisor Agents (Portfolio, Risk, Market Regime)
 * - 5 Arbitrage Agents
 * - 3 Sentiment Analysis Agents
 * - 2 Whale Following Agents
 * - 3 News Reaction Agents
 * - 4 Technical Analysis Agents (Total: 17 execution agents)
 * 
 * Uses secured admin-only endpoints: /api/agents/*
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  CircularProgress,
  Alert,
  Tooltip,
  IconButton,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Collapse,
  LinearProgress,
  Checkbox
} from '@mui/material';
import {
  AccountTree,
  Psychology,
  TrendingUp,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Refresh,
  PlayArrow,
  Pause,
  ExpandMore,
  ExpandLess,
  Speed,
  ShowChart,
  Wifi,
  WifiOff,
  Download,
  FileDownload,
  Article
} from '@mui/icons-material';
import { getApiUrl } from '../../config/api';
import { getJsonWithRetry } from '../../utils/network';
import { useAdminWebSocket } from '../../hooks/useAdminWebSocket';
import AgentPerformanceChart from './AgentPerformanceChart';
import AgentLogsModal from './AgentLogsModal';
import { exportAllAgents } from '../../utils/exportData';

interface Agent {
  id: string;
  name: string;
  type: 'supervisor' | 'arbitrage' | 'sentiment' | 'whale' | 'news' | 'technical';
  status: 'active' | 'inactive' | 'error';
  performance: {
    trades: number;
    winRate: number;
    pnl: number;
    avgProfit: number;
    successRate?: number;
  };
  lastActivity: string;
  uptime?: number;
}

interface AgentStatus {
  success: boolean;
  agents: {
    supervisor_agents: Agent[];
    execution_agents: {
      arbitrage: Agent[];
      sentiment: Agent[];
      whale_following: Agent[];
      news_reaction: Agent[];
      technical: Agent[];
    };
  };
  total_agents: number;
  active_agents: number;
  total_trades: number;
  total_pnl: number;
}

const HierarchicalAgentMonitor: React.FC = () => {
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    supervisors: true,
    arbitrage: true,
    sentiment: false,
    whale: false,
    news: false,
    technical: false
  });
  const [expandedCharts, setExpandedCharts] = useState<Record<string, boolean>>({});
  const [logsModalOpen, setLogsModalOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<{ id: string; name: string } | null>(null);
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set());

  // Use WebSocket for real-time updates
  const { data: wsData, isConnected, error: wsError, reconnect } = useAdminWebSocket<AgentStatus>({
    endpoint: '/ws/agents',
    onData: (data) => {
      setAgentStatus(data);
      setLastUpdate(new Date());
      setLoading(false);
    }
  });

  // Fallback to REST API if WebSocket fails
  useEffect(() => {
    if (wsError && !isConnected) {
      fetchAgentStatus();
      const interval = setInterval(fetchAgentStatus, 30000);
      return () => clearInterval(interval);
    }
  }, [wsError, isConnected]);

  const fetchAgentStatus = async () => {
    try {
      setError(null);
      const data = await getJsonWithRetry(
        getApiUrl('/api/agents/status'),
        {},
        { retries: 3, backoffMs: 500, maxBackoffMs: 4000, timeoutMs: 8000 }
      );

      setAgentStatus(data);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to fetch agent status:', err);
      setError(err.message || 'Failed to load agent status');
      setLoading(false);
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const handleActivateAgent = async (agentId: string, agentName: string) => {
    if (!window.confirm(`Are you sure you want to ACTIVATE agent "${agentName}"?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(getApiUrl(`/api/agents/${agentId}/activate`), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to activate agent');
      }

      // Refresh agent status
      if (isConnected) {
        reconnect();
      } else {
        fetchAgentStatus();
      }

      alert(`✅ Agent "${agentName}" activated successfully!`);
    } catch (err: any) {
      console.error('Failed to activate agent:', err);
      alert(`❌ Failed to activate agent: ${err.message}`);
    }
  };

  const handleDeactivateAgent = async (agentId: string, agentName: string) => {
    if (!window.confirm(`Are you sure you want to DEACTIVATE agent "${agentName}"?\n\nThis will stop the agent from making new trades.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(getApiUrl(`/api/agents/${agentId}/deactivate`), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to deactivate agent');
      }

      // Refresh agent status
      if (isConnected) {
        reconnect();
      } else {
        fetchAgentStatus();
      }

      alert(`✅ Agent "${agentName}" deactivated successfully!`);
    } catch (err: any) {
      console.error('Failed to deactivate agent:', err);
      alert(`❌ Failed to deactivate agent: ${err.message}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle fontSize="small" />;
      case 'inactive': return <Pause fontSize="small" />;
      case 'error': return <ErrorIcon fontSize="small" />;
      default: return <Warning fontSize="small" />;
    }
  };

  const toggleChart = (agentId: string) => {
    setExpandedCharts(prev => ({ ...prev, [agentId]: !prev[agentId] }));
  };

  const openLogsModal = (agentId: string, agentName: string) => {
    setSelectedAgent({ id: agentId, name: agentName });
    setLogsModalOpen(true);
  };

  const closeLogsModal = () => {
    setLogsModalOpen(false);
    setSelectedAgent(null);
  };

  const toggleAgentSelection = (agentId: string) => {
    setSelectedAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agentId)) {
        newSet.delete(agentId);
      } else {
        newSet.add(agentId);
      }
      return newSet;
    });
  };

  const selectAllAgents = (agents: Agent[]) => {
    setSelectedAgents(new Set(agents.map(a => a.id)));
  };

  const deselectAllAgents = () => {
    setSelectedAgents(new Set());
  };

  const handleBatchActivate = async () => {
    if (selectedAgents.size === 0) return;

    if (!window.confirm(`Activate ${selectedAgents.size} selected agent(s)?`)) {
      return;
    }

    let successCount = 0;
    let failCount = 0;

    for (const agentId of selectedAgents) {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(getApiUrl(`/api/agents/${agentId}/activate`), {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          successCount++;
        } else {
          failCount++;
        }
      } catch (err) {
        failCount++;
      }
    }

    alert(`✅ Activated: ${successCount}\n❌ Failed: ${failCount}`);

    // Refresh data
    if (isConnected) {
      reconnect();
    } else {
      fetchAgentStatus();
    }

    deselectAllAgents();
  };

  const handleBatchDeactivate = async () => {
    if (selectedAgents.size === 0) return;

    if (!window.confirm(`Deactivate ${selectedAgents.size} selected agent(s)?\n\nThis will stop them from making new trades.`)) {
      return;
    }

    let successCount = 0;
    let failCount = 0;

    for (const agentId of selectedAgents) {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(getApiUrl(`/api/agents/${agentId}/deactivate`), {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          successCount++;
        } else {
          failCount++;
        }
      } catch (err) {
        failCount++;
      }
    }

    alert(`✅ Deactivated: ${successCount}\n❌ Failed: ${failCount}`);

    // Refresh data
    if (isConnected) {
      reconnect();
    } else {
      fetchAgentStatus();
    }

    deselectAllAgents();
  };

  const renderAgentTable = (agents: Agent[], title: string, sectionKey: string) => {
    if (!agents || agents.length === 0) return null;

    return (
      <Card sx={{ mb: 2, background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <CardContent>
          <Box
            sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
            onClick={() => toggleSection(sectionKey)}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <AccountTree sx={{ color: '#9c27b0' }} />
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#fff' }}>
                {title}
              </Typography>
              <Chip
                label={`${agents.filter(a => a.status === 'active').length}/${agents.length} Active`}
                size="small"
                color="success"
                variant="outlined"
              />
            </Box>
            <IconButton size="small">
              {expandedSections[sectionKey] ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>

          <Collapse in={expandedSections[sectionKey]}>
            {/* Batch Controls */}
            {selectedAgents.size > 0 && (
              <Box sx={{ mt: 2, mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
                <Chip
                  label={`${selectedAgents.size} selected`}
                  color="primary"
                  size="small"
                />
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<PlayArrow />}
                  onClick={handleBatchActivate}
                  sx={{
                    backgroundColor: '#4caf50',
                    '&:hover': { backgroundColor: '#45a049' }
                  }}
                >
                  Activate Selected
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<Pause />}
                  onClick={handleBatchDeactivate}
                  sx={{
                    backgroundColor: '#f44336',
                    '&:hover': { backgroundColor: '#da190b' }
                  }}
                >
                  Deactivate Selected
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={deselectAllAgents}
                  sx={{ color: '#999', borderColor: '#999' }}
                >
                  Clear Selection
                </Button>
              </Box>
            )}

            <TableContainer sx={{ mt: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>
                      <Checkbox
                        size="small"
                        checked={agents.every(a => selectedAgents.has(a.id))}
                        indeterminate={agents.some(a => selectedAgents.has(a.id)) && !agents.every(a => selectedAgents.has(a.id))}
                        onChange={(e) => {
                          if (e.target.checked) {
                            selectAllAgents(agents);
                          } else {
                            deselectAllAgents();
                          }
                        }}
                        sx={{ color: '#9c27b0' }}
                      />
                    </TableCell>
                    <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Agent Name</TableCell>
                    <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Status</TableCell>
                    <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Trades</TableCell>
                    <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Win Rate</TableCell>
                    <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>P&L</TableCell>
                    <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Last Activity</TableCell>
                    <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Controls</TableCell>
                    <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Chart</TableCell>
                    <TableCell sx={{ color: '#9c27b0', fontWeight: 600 }}>Logs</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {agents.map((agent) => (
                    <React.Fragment key={agent.id}>
                      <TableRow hover>
                        <TableCell>
                          <Checkbox
                            size="small"
                            checked={selectedAgents.has(agent.id)}
                            onChange={() => toggleAgentSelection(agent.id)}
                            sx={{ color: '#9c27b0' }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#fff' }}>{agent.name}</TableCell>
                        <TableCell>
                          <Chip
                            label={agent.status.toUpperCase()}
                            color={getStatusColor(agent.status) as any}
                            size="small"
                            icon={getStatusIcon(agent.status)}
                          />
                        </TableCell>
                        <TableCell sx={{ color: '#fff' }}>{agent.performance.trades}</TableCell>
                        <TableCell sx={{ color: '#4caf50' }}>{agent.performance.winRate.toFixed(1)}%</TableCell>
                        <TableCell sx={{ color: agent.performance.pnl >= 0 ? '#4caf50' : '#f44336' }}>
                          ${agent.performance.pnl.toLocaleString()}
                        </TableCell>
                        <TableCell sx={{ color: '#999', fontSize: '0.85rem' }}>
                          {new Date(agent.lastActivity).toLocaleTimeString()}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="Activate Agent">
                              <span>
                                <IconButton
                                  size="small"
                                  onClick={() => handleActivateAgent(agent.id, agent.name)}
                                  disabled={agent.status === 'active'}
                                  sx={{
                                    color: agent.status === 'active' ? '#666' : '#4caf50',
                                    '&:hover': { backgroundColor: 'rgba(76, 175, 80, 0.1)' }
                                  }}
                                >
                                  <PlayArrow fontSize="small" />
                                </IconButton>
                              </span>
                            </Tooltip>
                            <Tooltip title="Deactivate Agent">
                              <span>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeactivateAgent(agent.id, agent.name)}
                                  disabled={agent.status === 'inactive'}
                                  sx={{
                                    color: agent.status === 'inactive' ? '#666' : '#f44336',
                                    '&:hover': { backgroundColor: 'rgba(244, 67, 54, 0.1)' }
                                  }}
                                >
                                  <Pause fontSize="small" />
                                </IconButton>
                              </span>
                            </Tooltip>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Tooltip title={expandedCharts[agent.id] ? "Hide Chart" : "Show Performance Chart"}>
                            <IconButton
                              size="small"
                              onClick={() => toggleChart(agent.id)}
                              sx={{ color: '#00d4ff' }}
                            >
                              {expandedCharts[agent.id] ? <ExpandLess /> : <ShowChart />}
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View Agent Logs">
                            <IconButton
                              size="small"
                              onClick={() => openLogsModal(agent.id, agent.name)}
                              sx={{ color: '#9c27b0' }}
                            >
                              <Article />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                      {/* Expandable Chart Row */}
                      <TableRow>
                        <TableCell colSpan={10} sx={{ p: 0, border: 'none' }}>
                          <Collapse in={expandedCharts[agent.id]} timeout="auto" unmountOnExit>
                            <Box sx={{ p: 2 }}>
                              <AgentPerformanceChart agentId={agent.id} agentName={agent.name} />
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Collapse>
        </CardContent>
      </Card>
    );
  };

  if (loading && !agentStatus) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#9c27b0', mb: 1 }}>
            🤖 Hierarchical Agent System
          </Typography>
          <Typography variant="body2" sx={{ color: '#ccc' }}>
            Real-time monitoring of all 17 trading agents (3 supervisors + 14 execution agents)
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          {isConnected ? (
            <Tooltip title="WebSocket Connected - Real-time updates">
              <Chip
                icon={<Wifi />}
                label="Live"
                size="small"
                color="success"
                sx={{ fontWeight: 600 }}
              />
            </Tooltip>
          ) : (
            <Tooltip title="WebSocket Disconnected - Using polling">
              <Chip
                icon={<WifiOff />}
                label="Polling"
                size="small"
                color="warning"
                sx={{ fontWeight: 600 }}
              />
            </Tooltip>
          )}
          <Typography variant="caption" sx={{ color: '#999' }}>
            Last updated: {lastUpdate.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Export as CSV">
            <IconButton
              onClick={() => agentStatus && exportAllAgents(agentStatus, 'csv')}
              size="small"
              sx={{ color: '#4caf50' }}
              disabled={!agentStatus}
            >
              <FileDownload />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export as JSON">
            <IconButton
              onClick={() => agentStatus && exportAllAgents(agentStatus, 'json')}
              size="small"
              sx={{ color: '#00d4ff' }}
              disabled={!agentStatus}
            >
              <Download />
            </IconButton>
          </Tooltip>
          <Tooltip title={isConnected ? "Reconnect WebSocket" : "Refresh Data"}>
            <IconButton onClick={isConnected ? reconnect : fetchAgentStatus} size="small" sx={{ color: '#9c27b0' }}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Overall Metrics */}
      {agentStatus && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card sx={{ background: 'linear-gradient(135deg, rgba(156, 39, 176, 0.1), rgba(156, 39, 176, 0.05))' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ color: '#999', mb: 1 }}>Total Agents</Typography>
                <Typography variant="h3" sx={{ fontWeight: 700, color: '#9c27b0' }}>
                  {agentStatus.total_agents}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.05))' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ color: '#999', mb: 1 }}>Active Agents</Typography>
                <Typography variant="h3" sx={{ fontWeight: 700, color: '#4caf50' }}>
                  {agentStatus.active_agents}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 212, 255, 0.05))' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ color: '#999', mb: 1 }}>Total Trades</Typography>
                <Typography variant="h3" sx={{ fontWeight: 700, color: '#00d4ff' }}>
                  {agentStatus.total_trades?.toLocaleString() || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1), rgba(255, 152, 0, 0.05))' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ color: '#999', mb: 1 }}>Total P&L</Typography>
                <Typography
                  variant="h3"
                  sx={{
                    fontWeight: 700,
                    color: (agentStatus.total_pnl || 0) >= 0 ? '#4caf50' : '#f44336'
                  }}
                >
                  ${agentStatus.total_pnl?.toLocaleString() || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Agent Tables */}
      {agentStatus && (
        <>
          {/* Supervisor Agents */}
          {renderAgentTable(agentStatus.agents.supervisor_agents, '👑 Supervisor Agents', 'supervisors')}

          {/* Execution Agents */}
          {renderAgentTable(agentStatus.agents.execution_agents.arbitrage, '💰 Arbitrage Agents', 'arbitrage')}
          {renderAgentTable(agentStatus.agents.execution_agents.sentiment, '😊 Sentiment Analysis Agents', 'sentiment')}
          {renderAgentTable(agentStatus.agents.execution_agents.whale_following, '🐋 Whale Following Agents', 'whale')}
          {renderAgentTable(agentStatus.agents.execution_agents.news_reaction, '📰 News Reaction Agents', 'news')}
          {renderAgentTable(agentStatus.agents.execution_agents.technical, '📊 Technical Analysis Agents', 'technical')}
        </>
      )}

      {/* No Data Message */}
      {!loading && !agentStatus && (
        <Alert severity="info" sx={{ mt: 3 }}>
          No agent data available. The system may still be initializing.
        </Alert>
      )}

      {/* Agent Logs Modal */}
      {selectedAgent && (
        <AgentLogsModal
          open={logsModalOpen}
          onClose={closeLogsModal}
          agentId={selectedAgent.id}
          agentName={selectedAgent.name}
        />
      )}
    </Box>
  );
};

export default HierarchicalAgentMonitor;

