import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  Chip,
  Divider,
  CircularProgress,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Card,
  CardContent,
  Avatar,
  Tooltip
} from '@mui/material';
import {
  Send as SendIcon,
  Start as StartIcon,
  Chat as ChatIcon,
  AutoAwesome as AIIcon,
  Code as CodeIcon,
  Build as BuildIcon,
  Close as CloseIcon,
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon
} from '@mui/icons-material';

import { apiCall } from '../config/api';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'text' | 'workflow' | 'code' | 'error';
  metadata?: any;
}

interface AICapability {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  examples: string[];
}

const AIChat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m MASS AI, your intelligent development assistant. I can help you create workflows, generate code, analyze projects, and much more. What would you like to build today?',
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const aiCapabilities: AICapability[] = [
    {
      id: 'workflows',
      name: 'Create Workflows',
      description: 'Generate intelligent workflows from natural language',
      icon: <BuildIcon />,
      examples: [
        'Create a code review workflow',
        'Build a deployment pipeline',
        'Set up testing automation'
      ]
    },
    {
      id: 'code',
      name: 'Generate Code',
      description: 'AI-powered code generation and optimization',
      icon: <CodeIcon />,
      examples: [
        'Generate a REST API for user management',
        'Create unit tests for my function',
        'Refactor this code for better performance'
      ]
    },
    {
      id: 'analysis',
      name: 'Project Analysis',
      description: 'Intelligent project insights and recommendations',
      icon: <StartIcon />,
      examples: [
        'Analyze my project structure',
        'Find security vulnerabilities',
        'Suggest performance improvements'
      ]
    }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send message to AI chat API via centralized helper
      const data = await apiCall('/api/ai/chat', {
        method: 'POST',
        body: JSON.stringify({
          message: inputMessage,
          conversation_history: messages.slice(-10) // Send last 10 messages for context
        })
      });

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'I apologize, but I couldn\'t process your request.',
        timestamp: new Date(),
        type: data.type || 'text',
        metadata: data.metadata
      };

      setMessages(prev => [...prev, aiMessage]);

      // If AI suggests creating a workflow, handle it
      if (data.workflow_suggestion) {
        handleWorkflowSuggestion(data.workflow_suggestion);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I\'m experiencing technical difficulties. Please try again.',
        timestamp: new Date(),
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleWorkflowSuggestion = (workflow: any) => {
    // Handle workflow creation suggestion
    console.log('Workflow suggestion:', workflow);
    // You could automatically create the workflow or show a confirmation dialog
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const handleCapabilityClick = (example: string) => {
    setInputMessage(example);
  };

  const formatMessage = (message: ChatMessage) => {
    const isUser = message.role === 'user';

    return (
      <ListItem
        key={message.id}
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 1
        }}
      >
        <Card
          sx={{
            inlineSize: '80%',
            backgroundColor: isUser ? 'primary.main' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary'
          }}
        >
          <CardContent sx={{ pb: '16px !important' }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
              {!isUser && (
                <Avatar sx={{ inlineSize: 24, blockSize: 24, bgcolor: 'secondary.main' }}>
                  <AIIcon sx={{ fontSize: 16 }} />
                </Avatar>
              )}
              <Box sx={{ flex: 1 }}>
                <Typography
                  variant="body1"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}
                >
                  {message.content}
                </Typography>

                {message.type === 'workflow' && message.metadata && (
                  <Box sx={{ mt: 2 }}>
                    <Chip
                      label="Workflow Created"
                      color="success"
                      size="small"
                      icon={<BuildIcon />}
                    />
                  </Box>
                )}

                {message.type === 'code' && (
                  <Box sx={{ mt: 2 }}>
                    <Chip
                      label="Code Generated"
                      color="info"
                      size="small"
                      icon={<CodeIcon />}
                    />
                  </Box>
                )}

                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    mt: 1,
                    opacity: 0.7
                  }}
                >
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </ListItem>
    );
  };

  const renderCapabilities = () => (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        AI Capabilities
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
        Click on any example to get started:
      </Typography>

      {aiCapabilities.map((capability) => (
        <Card key={capability.id} sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              {capability.icon}
              <Typography variant="subtitle1" sx={{ ml: 1 }}>
                {capability.name}
              </Typography>
            </Box>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              {capability.description}
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {capability.examples.map((example, index) => (
                <Chip
                  key={index}
                  label={example}
                  variant="outlined"
                  size="small"
                  clickable
                  onClick={() => handleCapabilityClick(example)}
                />
              ))}
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );

  // Floating action button for opening chat
  if (!isOpen) {
    return (
      <Tooltip title="AI Assistant">
        <Fab
          color="primary"
          sx={{
            position: 'fixed',
            insetBlockEnd: 24,
            insetInlineEnd: 24,
            zIndex: 1000
          }}
          onClick={() => setIsOpen(true)}
        >
          <ChatIcon />
        </Fab>
      </Tooltip>
    );
  }

  // Chat dialog
  return (
    <Dialog
      open={isOpen}
      onClose={() => setIsOpen(false)}
      maxWidth={isFullscreen ? false : "md"}
      fullWidth
      fullScreen={isFullscreen}
      PaperProps={{
        sx: {
          blockSize: isFullscreen ? '100vh' : '80vh',
          maxBlockSize: isFullscreen ? '100vh' : '80vh'
        }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AIIcon color="primary" />
            <Typography variant="h6">
              MASS AI Assistant
            </Typography>
            <Chip label="BETA" size="small" color="secondary" />
          </Box>
          <Box>
            <IconButton onClick={() => setIsFullscreen(!isFullscreen)}>
              {isFullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
            </IconButton>
            <IconButton onClick={() => setIsOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column' }}>
        {messages.length === 1 ? (
          // Show capabilities when no conversation has started
          renderCapabilities()
        ) : (
          // Show chat messages
          <List sx={{ flex: 1, overflow: 'auto', p: 1 }}>
            {messages.map(formatMessage)}
            {isLoading && (
              <ListItem sx={{ display: 'flex', justifyContent: 'flex-start' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ inlineSize: 24, blockSize: 24, bgcolor: 'secondary.main' }}>
                    <AIIcon sx={{ fontSize: 16 }} />
                  </Avatar>
                  <CircularProgress size={20} />
                  <Typography variant="body2" color="textSecondary">
                    AI is thinking...
                  </Typography>
                </Box>
              </ListItem>
            )}
            <div ref={messagesEndRef} />
          </List>
        )}

        <Divider />

        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask me anything about workflows, code generation, or project analysis..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              variant="outlined"
              size="small"
            />
            <IconButton
              color="primary"
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              sx={{ blockSize: 'fit-content' }}
            >
              <SendIcon />
            </IconButton>
          </Box>

          <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
            Powered by advanced AI models • Press Enter to send, Shift+Enter for new line
          </Typography>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default AIChat;
