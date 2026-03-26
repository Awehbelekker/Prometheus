import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  IconButton,
  Fab
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  StopCircle as StopIcon,
  Delete as DeleteIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { apiCall } from '../config/api';

interface Task {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  priority: number;
  assigned_agent?: string;
}

interface Workflow {
  id: string;
  name: string;
  status: 'created' | 'running' | 'completed' | 'failed';
  task_count: number;
  created_at: string;
  tasks?: Task[];
}

const WorkflowsPage: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newWorkflowName, setNewWorkflowName] = useState('');
  const [newWorkflowTasks, setNewWorkflowTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWorkflows = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('auth_token');
        const data = await apiCall('/workflows/', {
          headers: token ? { 'Authorization': `Bearer ${token}` } : undefined
        });
        setWorkflows(data.workflows || []);
      } catch (error) {
        console.error('Error fetching workflows:', error);
        setError('Failed to load workflows');
      } finally {
        setLoading(false);
      }
    };

    fetchWorkflows();
  }, []);

  const handleCreateWorkflow = async (workflowData: any) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('auth_token');
      const newWorkflow = await apiCall('/workflows/', {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : undefined,
        body: JSON.stringify(workflowData)
      });
      setWorkflows(prev => [...prev, newWorkflow]);
      setCreateDialogOpen(false);
      setNewWorkflowName('');
      setNewWorkflowTasks([]);
    } catch (error) {
      console.error('Error creating workflow:', error);
      setError('Failed to create workflow');
    } finally {
      setLoading(false);
    }
  };

  const addTask = () => {
    const newTask: Task = {
      id: `task_${Date.now()}`,
      name: `Task ${newWorkflowTasks.length + 1}`,
      description: 'New task description',
      status: 'pending',
      priority: 1
    };
    setNewWorkflowTasks([...newWorkflowTasks, newTask]);
  };

  const removeTask = (taskId: string) => {
    setNewWorkflowTasks(newWorkflowTasks.filter(task => task.id !== taskId));
  };

  const updateTask = (taskId: string, field: keyof Task, value: any) => {
    setNewWorkflowTasks(newWorkflowTasks.map(task => 
      task.id === taskId ? { ...task, [field]: value } : task
    ));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'primary';
      case 'completed': return 'success';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Workflows</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Workflow
        </Button>
      </Box>

      {/* Workflows List */}
      <Grid container spacing={3}>
        {workflows.map((workflow) => (
          <Grid item xs={12} md={6} lg={4} key={workflow.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                  <Typography variant="h6">{workflow.name}</Typography>
                  <Chip 
                    label={workflow.status} 
                    color={getStatusColor(workflow.status) as any}
                    size="small"
                  />
                </Box>
                
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Tasks: {workflow.task_count}
                </Typography>
                
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Created: {new Date(workflow.created_at).toLocaleDateString()}
                </Typography>

                <Box display="flex" gap={1} mt={2}>
                  <Button
                    size="small"
                    startIcon={<PlayIcon />}
                    disabled={workflow.status === 'running'}
                  >
                    Run
                  </Button>
                  <Button
                    size="small"
                    startIcon={<EditIcon />}
                  >
                    Edit
                  </Button>
                  <IconButton size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {workflows.length === 0 && !loading && (
        <Box 
          display="flex" 
          flexDirection="column" 
          alignItems="center" 
          justifyContent="center" 
          minHeight="300px"
        >
          <Typography variant="h6" color="textSecondary" gutterBottom>
            No workflows created yet
          </Typography>
          <Typography variant="body2" color="textSecondary" mb={3}>
            Create your first workflow to start automating development tasks
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Your First Workflow
          </Button>
        </Box>
      )}

      {/* Create Workflow Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New Workflow</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Workflow Name"
            fullWidth
            variant="outlined"
            value={newWorkflowName}
            onChange={(e) => setNewWorkflowName(e.target.value)}
            sx={{ mb: 3 }}
          />

          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Tasks</Typography>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={addTask}
            >
              Add Task
            </Button>
          </Box>

          <List>
            {newWorkflowTasks.map((task, index) => (
              <ListItem key={task.id} divider>
                <Box sx={{ width: '100%' }}>
                  <Box display="flex" gap={2} mb={1}>
                    <TextField
                      label="Task Name"
                      value={task.name}
                      onChange={(e) => updateTask(task.id, 'name', e.target.value)}
                      size="small"
                      sx={{ flex: 1 }}
                    />
                    <TextField
                      label="Priority"
                      type="number"
                      value={task.priority}
                      onChange={(e) => updateTask(task.id, 'priority', parseInt(e.target.value))}
                      size="small"
                      sx={{ width: 100 }}
                    />
                    <IconButton onClick={() => removeTask(task.id)} color="error">
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                  <TextField
                    label="Description"
                    value={task.description}
                    onChange={(e) => updateTask(task.id, 'description', e.target.value)}
                    multiline
                    rows={2}
                    fullWidth
                    size="small"
                  />
                </Box>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={() => handleCreateWorkflow({ name: newWorkflowName, tasks: newWorkflowTasks })} 
            variant="contained"
            disabled={!newWorkflowName.trim() || newWorkflowTasks.length === 0}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkflowsPage;
