import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Dialog,
  DialogContent,
  TextField,
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Chip,
  Paper,
  InputAdornment,
  alpha
} from '@mui/material';
import {
  Search,
  Close,
  TrendingUp,
  People,
  Assessment,
  Dashboard,
  AdminPanelSettings,
  AccountBalance,
  Psychology
} from '@mui/icons-material';

interface SearchResult {
  id: string;
  title: string;
  description: string;
  category: 'user' | 'trade' | 'symbol' | 'page' | 'feature';
  icon: React.ElementType;
  action: () => void;
  metadata?: Record<string, any>;
}

interface GlobalSearchProps {
  open: boolean;
  onClose: () => void;
  onNavigate?: (path: string) => void;
}

/**
 * Global Search Component
 * Provides unified search across users, trades, symbols, and pages
 */
const GlobalSearch: React.FC<GlobalSearchProps> = ({ open, onClose, onNavigate }) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Mock search results - in production, this would fetch from API
  const allResults: SearchResult[] = useMemo(() => [
    // Pages
    {
      id: 'dashboard',
      title: 'Dashboard',
      description: 'Go to user dashboard',
      category: 'page',
      icon: Dashboard,
      action: () => {
        if (onNavigate) onNavigate('/dashboard');
        onClose();
      }
    },
    {
      id: 'trading',
      title: 'Trading Dashboard',
      description: 'Open trading interface',
      category: 'page',
      icon: TrendingUp,
      action: () => {
        if (onNavigate) onNavigate('/trading');
        onClose();
      }
    },
    {
      id: 'admin',
      title: 'Admin Cockpit',
      description: 'Open admin dashboard',
      category: 'page',
      icon: AdminPanelSettings,
      action: () => {
        if (onNavigate) onNavigate('/cockpit');
        onClose();
      }
    },
    {
      id: 'portfolio',
      title: 'Portfolio',
      description: 'View portfolio',
      category: 'page',
      icon: AccountBalance,
      action: () => {
        if (onNavigate) onNavigate('/dashboard');
        onClose();
      }
    },
    // Symbols (would be fetched from API)
    {
      id: 'AAPL',
      title: 'AAPL',
      description: 'Apple Inc. - View details',
      category: 'symbol',
      icon: TrendingUp,
      action: () => {
        console.log('Navigate to AAPL');
        onClose();
      },
      metadata: { symbol: 'AAPL', price: 185.50 }
    },
    {
      id: 'GOOGL',
      title: 'GOOGL',
      description: 'Alphabet Inc. - View details',
      category: 'symbol',
      icon: TrendingUp,
      action: () => {
        console.log('Navigate to GOOGL');
        onClose();
      },
      metadata: { symbol: 'GOOGL', price: 2850.00 }
    },
    {
      id: 'MSFT',
      title: 'MSFT',
      description: 'Microsoft Corporation - View details',
      category: 'symbol',
      icon: TrendingUp,
      action: () => {
        console.log('Navigate to MSFT');
        onClose();
      },
      metadata: { symbol: 'MSFT', price: 380.00 }
    },
  ], [onNavigate, onClose]);

  // Filter results based on query
  const filteredResults = useMemo(() => {
    if (!query.trim()) {
      return allResults.slice(0, 5); // Show top 5 when no query
    }

    const lowerQuery = query.toLowerCase();
    return allResults.filter(result => 
      result.title.toLowerCase().includes(lowerQuery) ||
      result.description.toLowerCase().includes(lowerQuery) ||
      (result.metadata?.symbol?.toLowerCase().includes(lowerQuery))
    ).slice(0, 10); // Limit to 10 results
  }, [query, allResults]);

  // Reset selected index when results change
  useEffect(() => {
    setSelectedIndex(0);
  }, [filteredResults]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, filteredResults.length - 1));
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (filteredResults[selectedIndex]) {
        filteredResults[selectedIndex].action();
      }
    } else if (event.key === 'Escape') {
      onClose();
    }
  }, [filteredResults, selectedIndex, onClose]);

  // Close on outside click
  useEffect(() => {
    if (open) {
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose();
        }
      };
      window.addEventListener('keydown', handleEscape);
      return () => window.removeEventListener('keydown', handleEscape);
    }
  }, [open, onClose]);

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      page: '#00d4ff',
      symbol: '#4caf50',
      user: '#ff9800',
      trade: '#9c27b0',
      feature: '#f44336'
    };
    return colors[category] || '#666';
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      page: 'Page',
      symbol: 'Symbol',
      user: 'User',
      trade: 'Trade',
      feature: 'Feature'
    };
    return labels[category] || category;
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: 'rgba(26, 26, 46, 0.98)',
          border: '1px solid rgba(0, 212, 255, 0.3)',
          borderRadius: 2,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
          maxHeight: '80vh'
        }
      }}
      onKeyDown={handleKeyDown}
    >
      <DialogContent sx={{ p: 0 }}>
        {/* Search Input */}
        <Box sx={{ p: 2, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <TextField
            autoFocus
            fullWidth
            placeholder="Search users, trades, symbols, pages..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            variant="outlined"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search sx={{ color: 'rgba(255, 255, 255, 0.5)' }} />
                </InputAdornment>
              ),
              endAdornment: query && (
                <InputAdornment position="end">
                  <Chip
                    label={filteredResults.length}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.7rem',
                      backgroundColor: 'rgba(0, 212, 255, 0.2)',
                      color: '#00d4ff'
                    }}
                  />
                </InputAdornment>
              ),
              sx: {
                color: 'white',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(0, 212, 255, 0.3)'
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(0, 212, 255, 0.5)'
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#00d4ff'
                }
              }
            }}
            sx={{
              '& .MuiInputBase-input::placeholder': {
                color: 'rgba(255, 255, 255, 0.5)'
              }
            }}
          />
        </Box>

        {/* Results List */}
        <Box sx={{ maxHeight: '60vh', overflow: 'auto' }}>
          {filteredResults.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                No results found for "{query}"
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {filteredResults.map((result, index) => {
                const Icon = result.icon;
                const isSelected = index === selectedIndex;
                const categoryColor = getCategoryColor(result.category);

                return (
                  <React.Fragment key={result.id}>
                    <ListItem
                      disablePadding
                      sx={{
                        backgroundColor: isSelected ? alpha(categoryColor, 0.1) : 'transparent',
                        '&:hover': {
                          backgroundColor: alpha(categoryColor, 0.15)
                        },
                        transition: 'background-color 0.15s ease'
                      }}
                    >
                      <ListItemButton
                        onClick={result.action}
                        sx={{ py: 1.5, px: 2 }}
                      >
                        <ListItemIcon sx={{ minWidth: 40 }}>
                          <Icon sx={{ color: categoryColor }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body1" sx={{ color: '#fff', fontWeight: 600 }}>
                                {result.title}
                              </Typography>
                              <Chip
                                label={getCategoryLabel(result.category)}
                                size="small"
                                sx={{
                                  height: 18,
                                  fontSize: '0.65rem',
                                  backgroundColor: alpha(categoryColor, 0.2),
                                  color: categoryColor,
                                  border: `1px solid ${alpha(categoryColor, 0.3)}`
                                }}
                              />
                            </Box>
                          }
                          secondary={
                            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                              {result.description}
                              {result.metadata?.price && (
                                <span style={{ marginLeft: 8, fontFamily: 'monospace' }}>
                                  ${result.metadata.price}
                                </span>
                              )}
                            </Typography>
                          }
                        />
                      </ListItemButton>
                    </ListItem>
                    {index < filteredResults.length - 1 && (
                      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.05)' }} />
                    )}
                  </React.Fragment>
                );
              })}
            </List>
          )}
        </Box>

        {/* Footer Hint */}
        <Box sx={{ 
          p: 1.5, 
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.4)' }}>
            Use ↑↓ to navigate, Enter to select, Esc to close
          </Typography>
          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.4)' }}>
            Press ? for all shortcuts
          </Typography>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default GlobalSearch;

