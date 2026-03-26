import React, { useState, useEffect, useRef } from 'react';
import { Box, Card, CardContent, Typography, Button, TextField, LinearProgress, Chip, List, ListItem, ListItemText, Dialog, DialogTitle, DialogContent, DialogActions, ListItemIcon } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import CodeIcon from '@mui/icons-material/Code';
import { OrchestrationWebSocket } from '../utils/websocket';
import { apiCall } from '../config/api';


interface SubTask {
  id: string;
  description: string;
  assigned_agent: string;
  status: string;
  has_result: boolean;
  result?: string;
  error?: string;
}

interface Orchestration {
  orchestration_id: string;
  status: string;
  progress: number;
  subtasks: SubTask[];
}

const agentIcons: Record<string, JSX.Element> = {
  code_analyzer: <CodeIcon color="primary" />,
  ai_code_generator: <PersonIcon color="secondary" />,
};

const MultiAgentOrchestrator: React.FC = () => {
  const [taskDescription, setTaskDescription] = useState('');
  const [requirements, setRequirements] = useState('{}');
  const [activeOrchestration, setActiveOrchestration] = useState<Orchestration | null>(null);
  const [loading, setLoading] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const wsRef = useRef<OrchestrationWebSocket | null>(null);

  const startOrchestration = async () => {
    if (!taskDescription.trim()) return;
    setLoading(true);
    try {
      const result = await apiCall('/api/ai/orchestrate-task', {
        method: 'POST',
        body: JSON.stringify({
          task_description: taskDescription,
          requirements: JSON.parse(requirements || '{}')
        })
      });
      if (result?.status === 'success') {
        monitorOrchestration(result.orchestration_id);
      }
    } catch (error) {
      console.error('Orchestration failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const monitorOrchestration = async (orchestrationId: string) => {
    const checkStatus = async () => {
      try {
        const status = await apiCall(`/api/ai/orchestration/${orchestrationId}/status`);
        setActiveOrchestration(status);
        if (status.status === 'in_progress') {
          setTimeout(checkStatus, 2000);
        }
      } catch (error) {
        console.error('Status check failed:', error);
      }
    };
    checkStatus();
  };

  useEffect(() => {
    wsRef.current = new OrchestrationWebSocket();
    wsRef.current.connect('orchestrator-ui');
    wsRef.current.onMessage((data) => {
      if (data.type === 'orchestration_update' && data.data) {
        setActiveOrchestration((prev) => prev && prev.orchestration_id === data.data.orchestration_id ? { ...prev, ...data.data } : prev);
      }
    });
    return () => wsRef.current?.close();
  }, []);

  return (
    <Box p={3}>
      <Typography variant="h5" gutterBottom>Multi-Agent Orchestration</Typography>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            label="Task Description"
            value={taskDescription}
            onChange={e => setTaskDescription(e.target.value)}
            fullWidth
            multiline
            sx={{ mb: 2 }}
          />
          <TextField
            label="Requirements (JSON)"
            value={requirements}
            onChange={e => setRequirements(e.target.value)}
            fullWidth
            multiline
            sx={{ mb: 2 }}
          />
          <Button variant="contained" onClick={startOrchestration} disabled={loading}>
            {loading ? 'Starting...' : 'Start Orchestration'}
          </Button>
        </CardContent>
      </Card>
      {activeOrchestration && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Active Orchestration</Typography>
              <Button onClick={() => setDetailsOpen(true)}>View Details</Button>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Progress: {Math.round(activeOrchestration.progress * 100)}%
              </Typography>
              <LinearProgress variant="determinate" value={activeOrchestration.progress * 100} sx={{ height: 8, borderRadius: 4 }} />
            </Box>
            <Typography variant="body2" gutterBottom>
              Status: <Chip label={activeOrchestration.status} size="small" sx={{ ml: 1 }} />
            </Typography>
            <Typography variant="body2" gutterBottom>
              Subtasks: {activeOrchestration.subtasks.length}
            </Typography>
          </CardContent>
        </Card>
      )}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Orchestration Details</DialogTitle>
        <DialogContent>
          {activeOrchestration && (
            <List>
              {activeOrchestration.subtasks.map((subtask) => (
                <ListItem key={subtask.id}>
                  <ListItemIcon>
                    {agentIcons[subtask.assigned_agent] || <PersonIcon />}
                  </ListItemIcon>
                  <ListItemText
                    primary={subtask.description}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          Agent: {subtask.assigned_agent}
                        </Typography>
                        <Chip label={subtask.status} size="small" color={subtask.status === 'completed' ? 'success' : subtask.status === 'pending' ? 'warning' : 'default'} />
                        {subtask.result && (
                          <Typography variant="caption" color="success.main" display="block">Result: {subtask.result}</Typography>
                        )}
                        {subtask.error && (
                          <Typography variant="caption" color="error" display="block">Error: {subtask.error}</Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MultiAgentOrchestrator;
