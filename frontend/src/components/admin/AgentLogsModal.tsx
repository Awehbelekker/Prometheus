/**
 * 📋 AGENT LOGS MODAL
 * 
 * Displays detailed logs for a specific agent:
 * - Recent actions and decisions
 * - Trade executions
 * - Errors and warnings
 * - Performance metrics
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
  IconButton,
  Tabs,
  Tab,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  Close,
  CheckCircle,
  Error as ErrorIcon,
  Warning,
  Info,
  Search,
  Refresh,
  Download
} from '@mui/icons-material';
import { getApiUrl } from '../../config/api';
import { getJsonWithRetry } from '../../utils/network';

interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'success';
  message: string;
  details?: string;
  action?: string;
  result?: string;
}

interface AgentLogsModalProps {
  open: boolean;
  onClose: () => void;
  agentId: string;
  agentName: string;
}

const AgentLogsModal: React.FC<AgentLogsModalProps> = ({ open, onClose, agentId, agentName }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (open) {
      fetchLogs();
    }
  }, [open, agentId, activeTab]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);

      // Determine log level filter based on active tab
      const levelFilter = activeTab === 0 ? 'all' :
                         activeTab === 1 ? 'error' :
                         activeTab === 2 ? 'warning' : 'info';

      // Fetch real logs from backend
      const response = await getJsonWithRetry<{
        success: boolean;
        agent_id: string;
        agent_name: string;
        logs: Array<{
          timestamp: string;
          level: 'info' | 'warning' | 'error' | 'success';
          message: string;
          details?: string;
          action?: string;
          result?: string;
        }>;
        total_logs: number;
        note?: string;
      }>(
        getApiUrl(`/api/agents/${agentId}/logs?limit=100&level=${levelFilter}`),
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        },
        { retries: 3, backoffMs: 500, maxBackoffMs: 4000, timeoutMs: 8000 }
      );

      setLogs(response.logs || []);
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to fetch agent logs:', err);
      setError(err.message || 'Failed to load agent logs');
      setLoading(false);
    }
  };

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'success': return <CheckCircle sx={{ color: '#4caf50' }} />;
      case 'error': return <ErrorIcon sx={{ color: '#f44336' }} />;
      case 'warning': return <Warning sx={{ color: '#ff9800' }} />;
      default: return <Info sx={{ color: '#2196f3' }} />;
    }
  };

  const getLogColor = (level: string) => {
    switch (level) {
      case 'success': return '#4caf50';
      case 'error': return '#f44336';
      case 'warning': return '#ff9800';
      default: return '#2196f3';
    }
  };

  const filteredLogs = logs.filter(log => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return log.message.toLowerCase().includes(query) ||
           log.details?.toLowerCase().includes(query) ||
           log.action?.toLowerCase().includes(query);
  });

  const logsByLevel = {
    all: filteredLogs,
    info: filteredLogs.filter(l => l.level === 'info'),
    success: filteredLogs.filter(l => l.level === 'success'),
    warning: filteredLogs.filter(l => l.level === 'warning'),
    error: filteredLogs.filter(l => l.level === 'error')
  };

  const currentLogs = activeTab === 0 ? logsByLevel.all :
                      activeTab === 1 ? logsByLevel.info :
                      activeTab === 2 ? logsByLevel.success :
                      activeTab === 3 ? logsByLevel.warning :
                      logsByLevel.error;

  const downloadLogs = () => {
    const logsText = currentLogs.map(log => 
      `[${new Date(log.timestamp).toLocaleString()}] [${log.level.toUpperCase()}] ${log.message}\n` +
      (log.details ? `  Details: ${log.details}\n` : '') +
      (log.result ? `  Result: ${log.result}\n` : '')
    ).join('\n');

    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${agentName}_logs_${new Date().toISOString().split('T')[0]}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
          border: '1px solid rgba(0, 212, 255, 0.3)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)'
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        borderBottom: '1px solid rgba(0, 212, 255, 0.2)',
        pb: 2
      }}>
        <Box>
          <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 700 }}>
            📋 {agentName} Logs
          </Typography>
          <Typography variant="caption" sx={{ color: '#999' }}>
            Recent activity and system events
          </Typography>
        </Box>
        <IconButton onClick={onClose} sx={{ color: '#999' }}>
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'rgba(0, 212, 255, 0.2)' }}>
          <Tabs 
            value={activeTab} 
            onChange={(_, newValue) => setActiveTab(newValue)}
            sx={{
              '& .MuiTab-root': { color: '#999' },
              '& .Mui-selected': { color: '#00d4ff' }
            }}
          >
            <Tab label={`All (${logsByLevel.all.length})`} />
            <Tab label={`Info (${logsByLevel.info.length})`} />
            <Tab label={`Success (${logsByLevel.success.length})`} />
            <Tab label={`Warnings (${logsByLevel.warning.length})`} />
            <Tab label={`Errors (${logsByLevel.error.length})`} />
          </Tabs>
        </Box>

        {/* Search and Actions */}
        <Box sx={{ p: 2, display: 'flex', gap: 2, borderBottom: '1px solid rgba(0, 212, 255, 0.2)' }}>
          <TextField
            size="small"
            placeholder="Search logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            fullWidth
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search sx={{ color: '#999' }} />
                </InputAdornment>
              ),
              sx: {
                color: '#fff',
                '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(0, 212, 255, 0.3)' }
              }
            }}
          />
          <IconButton onClick={fetchLogs} sx={{ color: '#00d4ff' }}>
            <Refresh />
          </IconButton>
          <IconButton onClick={downloadLogs} sx={{ color: '#4caf50' }}>
            <Download />
          </IconButton>
        </Box>

        {/* Logs List */}
        <Box sx={{ maxHeight: 400, overflow: 'auto', p: 2 }}>
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {!loading && !error && currentLogs.length === 0 && (
            <Typography sx={{ color: '#999', textAlign: 'center', p: 4 }}>
              No logs found
            </Typography>
          )}

          {!loading && !error && currentLogs.length > 0 && (
            <List sx={{ p: 0 }}>
              {currentLogs.map((log, index) => (
                <React.Fragment key={index}>
                  <ListItem
                    sx={{
                      flexDirection: 'column',
                      alignItems: 'flex-start',
                      backgroundColor: 'rgba(0, 212, 255, 0.05)',
                      borderRadius: 1,
                      mb: 1,
                      border: `1px solid ${getLogColor(log.level)}33`
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, width: '100%' }}>
                      {getLogIcon(log.level)}
                      <Typography variant="body2" sx={{ color: '#fff', flex: 1 }}>
                        {log.message}
                      </Typography>
                      <Chip 
                        label={log.level.toUpperCase()} 
                        size="small" 
                        sx={{ 
                          backgroundColor: `${getLogColor(log.level)}22`,
                          color: getLogColor(log.level),
                          fontWeight: 600
                        }}
                      />
                    </Box>
                    <Typography variant="caption" sx={{ color: '#999', mb: 0.5 }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </Typography>
                    {log.details && (
                      <Typography variant="caption" sx={{ color: '#ccc', fontStyle: 'italic' }}>
                        {log.details}
                      </Typography>
                    )}
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ borderTop: '1px solid rgba(0, 212, 255, 0.2)', p: 2 }}>
        <Button onClick={onClose} sx={{ color: '#999' }}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AgentLogsModal;

