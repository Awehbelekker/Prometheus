/**
 * AI Assistant Component
 * Interactive AI trading assistant with chat interface
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  CircularProgress,
  Fab
} from '@mui/material';
import {
  Send,
  SmartToy,
  Close,
  TrendingUp,
  Assessment,
  Lightbulb
} from '@mui/icons-material';
import { useMutation } from '@tanstack/react-query';
import { apiCall } from '../../config/api';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggestions?: string[];
}

interface AIAssistantProps {
  userId: string;
}

const AIAssistant: React.FC<AIAssistantProps> = ({ userId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your AI trading assistant. I can help you analyze markets, suggest strategies, and answer questions about trading. How can I help you today?",
      timestamp: new Date(),
      suggestions: [
        'Analyze AAPL stock',
        'What are trending stocks?',
        'Suggest a trading strategy'
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await apiCall('/api/ai/chat', {
        method: 'POST',
        body: JSON.stringify({
          userId,
          message,
          conversationHistory: messages.slice(-5) // Last 5 messages for context
        })
      });
      return response;
    },
    onSuccess: (response: any) => {
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        suggestions: response.suggestions
      };
      setMessages(prev => [...prev, assistantMessage]);
    },
    onError: () => {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  });

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    sendMessageMutation.mutate(input);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            style={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 1000
            }}
          >
            <Fab
              color="primary"
              onClick={() => setIsOpen(true)}
              sx={{
                background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                color: '#000',
                width: 64,
                height: 64,
                '&:hover': {
                  background: 'linear-gradient(45deg, #33ddff, #00b3e6)',
                  transform: 'scale(1.1)'
                }
              }}
            >
              <SmartToy sx={{ fontSize: 32 }} />
            </Fab>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            style={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 1000,
              width: 400,
              maxWidth: 'calc(100vw - 48px)'
            }}
          >
            <Card
              sx={{
                background: 'rgba(26, 26, 26, 0.98)',
                border: '1px solid rgba(0, 212, 255, 0.3)',
                borderRadius: 3,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
                height: 600,
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              {/* Header */}
              <Box
                sx={{
                  p: 2,
                  background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                  color: '#000',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  borderRadius: '12px 12px 0 0'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SmartToy sx={{ fontSize: 28 }} />
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    AI Assistant
                  </Typography>
                </Box>
                <IconButton onClick={() => setIsOpen(false)} sx={{ color: '#000' }}>
                  <Close />
                </IconButton>
              </Box>

              {/* Messages */}
              <Box
                sx={{
                  flex: 1,
                  overflowY: 'auto',
                  p: 2,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 2
                }}
              >
                {messages.map((message) => (
                  <Box
                    key={message.id}
                    sx={{
                      display: 'flex',
                      justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                      gap: 1
                    }}
                  >
                    {message.role === 'assistant' && (
                      <Avatar
                        sx={{
                          bgcolor: 'rgba(0, 212, 255, 0.2)',
                          width: 32,
                          height: 32
                        }}
                      >
                        <SmartToy sx={{ fontSize: 20, color: '#00d4ff' }} />
                      </Avatar>
                    )}

                    <Box sx={{ maxWidth: '75%' }}>
                      <Box
                        sx={{
                          p: 1.5,
                          borderRadius: 2,
                          bgcolor:
                            message.role === 'user'
                              ? 'rgba(0, 212, 255, 0.2)'
                              : 'rgba(255, 255, 255, 0.05)',
                          border:
                            message.role === 'user'
                              ? '1px solid rgba(0, 212, 255, 0.3)'
                              : '1px solid rgba(255, 255, 255, 0.1)'
                        }}
                      >
                        <Typography variant="body2" sx={{ color: '#fff' }}>
                          {message.content}
                        </Typography>
                      </Box>

                      {/* Suggestions */}
                      {message.suggestions && message.suggestions.length > 0 && (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                          {message.suggestions.map((suggestion, index) => (
                            <Chip
                              key={index}
                              label={suggestion}
                              size="small"
                              onClick={() => handleSuggestionClick(suggestion)}
                              sx={{
                                bgcolor: 'rgba(0, 212, 255, 0.1)',
                                color: '#00d4ff',
                                border: '1px solid rgba(0, 212, 255, 0.3)',
                                cursor: 'pointer',
                                '&:hover': {
                                  bgcolor: 'rgba(0, 212, 255, 0.2)'
                                }
                              }}
                            />
                          ))}
                        </Box>
                      )}

                      <Typography
                        variant="caption"
                        sx={{ color: '#666', display: 'block', mt: 0.5 }}
                      >
                        {message.timestamp.toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </Typography>
                    </Box>

                    {message.role === 'user' && (
                      <Avatar
                        sx={{
                          bgcolor: 'rgba(255, 107, 53, 0.2)',
                          width: 32,
                          height: 32
                        }}
                      >
                        <Typography variant="caption" sx={{ color: '#ff6b35' }}>
                          You
                        </Typography>
                      </Avatar>
                    )}
                  </Box>
                ))}

                {sendMessageMutation.isPending && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Avatar
                      sx={{
                        bgcolor: 'rgba(0, 212, 255, 0.2)',
                        width: 32,
                        height: 32
                      }}
                    >
                      <SmartToy sx={{ fontSize: 20, color: '#00d4ff' }} />
                    </Avatar>
                    <CircularProgress size={20} sx={{ color: '#00d4ff' }} />
                  </Box>
                )}

                <div ref={messagesEndRef} />
              </Box>

              {/* Input */}
              <Box
                sx={{
                  p: 2,
                  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                  display: 'flex',
                  gap: 1
                }}
              >
                <TextField
                  fullWidth
                  multiline
                  maxRows={3}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything..."
                  disabled={sendMessageMutation.isPending}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: '#fff',
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.2)'
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(0, 212, 255, 0.5)'
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#00d4ff'
                      }
                    }
                  }}
                />
                <IconButton
                  onClick={handleSend}
                  disabled={!input.trim() || sendMessageMutation.isPending}
                  sx={{
                    bgcolor: 'rgba(0, 212, 255, 0.2)',
                    color: '#00d4ff',
                    '&:hover': {
                      bgcolor: 'rgba(0, 212, 255, 0.3)'
                    },
                    '&:disabled': {
                      bgcolor: 'rgba(255, 255, 255, 0.05)',
                      color: '#666'
                    }
                  }}
                >
                  <Send />
                </IconButton>
              </Box>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default AIAssistant;

