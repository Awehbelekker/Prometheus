import React, { useState, useEffect } from 'react';
import './MultiAgentCollaboration.css';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import AssignmentIcon from '@mui/icons-material/Assignment';
import SyncIcon from '@mui/icons-material/Sync';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';

import { apiCall } from '../config/api';

interface CollaborationSession {
  session_id: string;
  status: string;
  main_task: string;
  participating_agents: string[];
  total_subtasks: number;
  completed_subtasks: number;
  created_at: string;
  completed_at?: string;
  final_result?: any;
}

interface SubTask {
  id: string;
  description: string;
  assigned_agent: string;
  status: string;
  result?: any;
}

const MultiAgentCollaboration: React.FC = () => {
  const [sessions, setSessions] = useState<CollaborationSession[]>([]);
  const [activeSession, setActiveSession] = useState<CollaborationSession | null>(null);
  const [taskDescription, setTaskDescription] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [templates, setTemplates] = useState<any>({});
  const [context, setContext] = useState('{}');
  const [loading, setLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    fetchSessions();
    fetchTemplates();
    const interval = setInterval(fetchSessions, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSessions = async () => {
    try {
      const data = await apiCall('/api/collaboration/sessions');
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const data = await apiCall('/api/collaboration/templates');
      setTemplates(data.templates || {});
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const fetchSessionDetails = async (sessionId: string) => {
    try {
      const data = await apiCall(`/api/collaboration/status/${sessionId}`);
      setActiveSession(data);
    } catch (error) {
      console.error('Failed to fetch session details:', error);
    }
  };

  const startCollaboration = async () => {
    if (!taskDescription.trim()) {
      alert('Please enter a task description');
      return;
    }

    setIsCreating(true);
    try {
      let parsedContext = {};
      try {
        parsedContext = JSON.parse(context);
      } catch (e) {
        console.warn('Invalid JSON context, using empty object');
      }

      const data = await apiCall('/api/collaboration/orchestrate', {
        method: 'POST',
        body: JSON.stringify({
          task_description: taskDescription,
          context: parsedContext,
          template: selectedTemplate || undefined
        }),
      });

      setTaskDescription('');
      setContext('{}');
      setSelectedTemplate('');
      fetchSessions();
      if (data?.session_id) fetchSessionDetails(data.session_id);
    } catch (error: any) {
      console.error('Failed to start collaboration:', error);
      alert(`Failed to start collaboration${error?.message ? `: ${error.message}` : ''}`);
    } finally {
      setIsCreating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#4CAF50';
      case 'executing': return '#FF9800';
      case 'planning': return '#2196F3';
      case 'aggregating': return '#9C27B0';
      case 'failed': return '#F44336';
      default: return '#757575';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon sx={{ color: '#4CAF50', fontSize: 16 }} />;
      case 'executing': return <FlashOnIcon sx={{ color: '#FF9800', fontSize: 16 }} />;
      case 'planning': return <AssignmentIcon sx={{ color: '#2196F3', fontSize: 16 }} />;
      case 'aggregating': return <SyncIcon sx={{ color: '#9C27B0', fontSize: 16 }} />;
      case 'failed': return <ErrorIcon sx={{ color: '#F44336', fontSize: 16 }} />;
      default: return <HourglassEmptyIcon sx={{ color: '#757575', fontSize: 16 }} />;
    }
  };

  const formatAgentName = (agentId: string) => {
    return agentId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const renderSessionCard = (session: CollaborationSession) => (
    <div
      key={session.session_id}
      className={`session-card ${activeSession?.session_id === session.session_id ? 'active' : ''}`}
      onClick={() => fetchSessionDetails(session.session_id)}
    >
      <div className="session-header">
        <div className="session-status">
          <span className="status-icon">{getStatusIcon(session.status)}</span>
          <span
            className="status-text"
            style={{ '--status-color': getStatusColor(session.status) } as React.CSSProperties}
          >
            {session.status.toUpperCase()}
          </span>
        </div>
        <div className="session-time">
          {new Date(session.created_at).toLocaleString()}
        </div>
      </div>

      <div className="session-task">
        <h4>{session.main_task}</h4>
      </div>

      <div className="session-progress">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              '--progress-width': `${session.total_subtasks > 0 ? (session.completed_subtasks / session.total_subtasks) * 100 : 0}%`,
              '--progress-color': getStatusColor(session.status)
            } as React.CSSProperties}
          />
        </div>
        <span className="progress-text">
          {session.completed_subtasks}/{session.total_subtasks} subtasks
        </span>
      </div>

      <div className="session-agents">
        <span className="agents-label">Agents:</span>
        {session.participating_agents.map(agent => (
          <span key={agent} className="agent-badge">
            {formatAgentName(agent)}
          </span>
        ))}
      </div>
    </div>
  );

  const renderSessionDetails = () => {
    if (!activeSession) return null;

    return (
      <div className="session-details">
        <div className="details-header">
          <h3>Session Details</h3>
          <button
            className="refresh-btn"
            onClick={() => fetchSessionDetails(activeSession.session_id)}
          >
            🔄 Refresh
          </button>
        </div>

        <div className="session-info">
          <div className="info-item">
            <strong>Status:</strong>
            <span style={{ '--status-color': getStatusColor(activeSession.status) } as React.CSSProperties}>
              {getStatusIcon(activeSession.status)} {activeSession.status.toUpperCase()}
            </span>
          </div>
          <div className="info-item">
            <strong>Task:</strong> {activeSession.main_task}
          </div>
          <div className="info-item">
            <strong>Created:</strong> {new Date(activeSession.created_at).toLocaleString()}
          </div>
          {activeSession.completed_at && (
            <div className="info-item">
              <strong>Completed:</strong> {new Date(activeSession.completed_at).toLocaleString()}
            </div>
          )}
        </div>

        <div className="agents-section">
          <h4>Participating Agents</h4>
          <div className="agents-grid">
            {activeSession.participating_agents.map(agent => (
              <div key={agent} className="agent-card">
                <div className="agent-name">{formatAgentName(agent)}</div>
                <div className="agent-status">Active</div>
              </div>
            ))}
          </div>
        </div>

        {activeSession.final_result && (
          <div className="results-section">
            <h4>Final Results</h4>
            <div className="results-content">
              {typeof activeSession.final_result === 'string' ? (
                <pre className="result-text">{activeSession.final_result}</pre>
              ) : (
                <pre className="result-json">
                  {JSON.stringify(activeSession.final_result, null, 2)}
                </pre>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="multi-agent-collaboration">
      <div className="collaboration-header">
        <h2>🤖 SynergyCore™ Collaboration</h2>
        <p>Orchestrate complex tasks across multiple AI agents</p>
      </div>

      <div className="collaboration-content">
        <div className="left-panel">
          <div className="create-session">
            <h3>Start New Collaboration</h3>

            <div className="form-group">
              <label>Task Description</label>
              <textarea
                value={taskDescription}
                onChange={(e) => setTaskDescription(e.target.value)}
                placeholder="Describe the task you want SynergyCore™ agents to collaborate on..."
                rows={4}
                disabled={isCreating}
              />
            </div>

            <div className="form-group">
              <label htmlFor="collaboration-template">Collaboration Template</label>
              <select
                id="collaboration-template"
                name="collaboration-template"
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                disabled={isCreating}
                aria-label="Select collaboration template"
                title="Choose a collaboration template"
              >
                <option value="">Custom (no template)</option>
                {Object.keys(templates).map(template => (
                  <option key={template} value={template}>
                    {template.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
              </select>
            </div>

            {selectedTemplate && templates[selectedTemplate] && (
              <div className="template-info">
                <h4>Template: {selectedTemplate.replace(/_/g, ' ')}</h4>
                <p>{templates[selectedTemplate].description}</p>
                <div className="template-stages">
                  {templates[selectedTemplate].stages?.map((stage: any, index: number) => (
                    <div key={index} className="stage-item">
                      <strong>{stage.name}:</strong> {stage.agents.join(', ')}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="form-group">
              <label>Context (JSON)</label>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder='{"project_path": "/path/to/project", "language": "python"}'
                rows={3}
                disabled={isCreating}
              />
            </div>

            <button
              className="start-btn"
              onClick={startCollaboration}
              disabled={isCreating || !taskDescription.trim()}
            >
              {isCreating ? '🔄 Starting...' : '🚀 Start Collaboration'}
            </button>
          </div>

          <div className="sessions-list">
            <h3>Active Sessions</h3>
            {sessions.length === 0 ? (
              <div className="no-sessions">
                <p>No active collaboration sessions</p>
              </div>
            ) : (
              <div className="sessions-grid">
                {sessions.map(renderSessionCard)}
              </div>
            )}
          </div>
        </div>

        <div className="right-panel">
          {renderSessionDetails()}
        </div>
      </div>
    </div>
  );
};

export default MultiAgentCollaboration;
