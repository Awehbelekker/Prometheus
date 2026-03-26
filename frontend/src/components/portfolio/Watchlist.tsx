import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  InputAdornment,
  Tooltip,
  alpha,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Add,
  Search,
  TrendingUp,
  TrendingDown,
  Star,
  StarBorder,
  Delete,
  Visibility,
  AddAlert
} from '@mui/icons-material';

interface WatchlistItem {
  id: string;
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: string;
  isWatched: boolean;
  priceAlert?: {
    above?: number;
    below?: number;
  };
}

interface WatchlistProps {
  userId: string;
  onAddToPortfolio?: (symbol: string) => void;
  onSetPriceAlert?: (symbol: string, alert: { above?: number; below?: number }) => void;
}

const Watchlist: React.FC<WatchlistProps> = ({
  userId,
  onAddToPortfolio,
  onSetPriceAlert
}) => {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [newSymbol, setNewSymbol] = useState('');
  const [alertAbove, setAlertAbove] = useState('');
  const [alertBelow, setAlertBelow] = useState('');

  useEffect(() => {
    // Simulate API call to fetch watchlist data
    const fetchWatchlist = async () => {
      setLoading(true);
      
      // Mock data - replace with real API call
      const mockData: WatchlistItem[] = [
        {
          id: '1',
          symbol: 'AAPL',
          name: 'Apple Inc.',
          currentPrice: 175.43,
          change: 2.34,
          changePercent: 1.35,
          volume: 45678900,
          marketCap: '2.7T',
          isWatched: true,
          priceAlert: { above: 180, below: 170 }
        },
        {
          id: '2',
          symbol: 'TSLA',
          name: 'Tesla, Inc.',
          currentPrice: 248.87,
          change: -5.23,
          changePercent: -2.06,
          volume: 67890123,
          marketCap: '789B',
          isWatched: true
        },
        {
          id: '3',
          symbol: 'NVDA',
          name: 'NVIDIA Corporation',
          currentPrice: 875.32,
          change: 12.45,
          changePercent: 1.44,
          volume: 34567890,
          marketCap: '2.1T',
          isWatched: true,
          priceAlert: { above: 900 }
        },
        {
          id: '4',
          symbol: 'MSFT',
          name: 'Microsoft Corporation',
          currentPrice: 378.91,
          change: 1.87,
          changePercent: 0.50,
          volume: 23456789,
          marketCap: '2.8T',
          isWatched: true
        },
        {
          id: '5',
          symbol: 'GOOGL',
          name: 'Alphabet Inc.',
          currentPrice: 142.56,
          change: -0.89,
          changePercent: -0.62,
          volume: 12345678,
          marketCap: '1.8T',
          isWatched: true
        }
      ];

      setTimeout(() => {
        setWatchlist(mockData);
        setLoading(false);
      }, 1000);
    };

    fetchWatchlist();
  }, [userId]);

  const filteredWatchlist = watchlist.filter(item =>
    item.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddSymbol = () => {
    if (newSymbol.trim()) {
      // Simulate adding new symbol to watchlist
      const newItem: WatchlistItem = {
        id: Date.now().toString(),
        symbol: newSymbol.toUpperCase(),
        name: `${newSymbol.toUpperCase()} Corp.`,
        currentPrice: Math.random() * 500 + 50,
        change: (Math.random() - 0.5) * 20,
        changePercent: (Math.random() - 0.5) * 10,
        volume: Math.floor(Math.random() * 100000000),
        marketCap: `${(Math.random() * 1000 + 100).toFixed(1)}B`,
        isWatched: true
      };
      
      setWatchlist(prev => [newItem, ...prev]);
      setNewSymbol('');
      setAddDialogOpen(false);
    }
  };

  const handleRemoveFromWatchlist = (symbol: string) => {
    setWatchlist(prev => prev.filter(item => item.symbol !== symbol));
  };

  const handleSetPriceAlert = () => {
    if (selectedSymbol && (alertAbove || alertBelow)) {
      const alert = {
        above: alertAbove ? parseFloat(alertAbove) : undefined,
        below: alertBelow ? parseFloat(alertBelow) : undefined
      };
      
      setWatchlist(prev => prev.map(item =>
        item.symbol === selectedSymbol
          ? { ...item, priceAlert: alert }
          : item
      ));
      
      onSetPriceAlert?.(selectedSymbol, alert);
      setAlertDialogOpen(false);
      setAlertAbove('');
      setAlertBelow('');
      setSelectedSymbol('');
    }
  };

  const getChangeColor = (change: number) => {
    return change >= 0 ? '#4caf50' : '#f44336';
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`;
    }
    return volume.toString();
  };

  if (loading) {
    return (
      <Card sx={{
        background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 3
      }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
            📈 Watchlist
          </Typography>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" sx={{ color: '#aaa' }}>
              Loading watchlist...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{
      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: 3
    }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
            📈 Watchlist
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddDialogOpen(true)}
            sx={{
              background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
              '&:hover': {
                background: 'linear-gradient(45deg, #0099cc, #00d4ff)'
              }
            }}
          >
            Add Symbol
          </Button>
        </Box>

        <TextField
          fullWidth
          placeholder="Search symbols or companies..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search sx={{ color: '#aaa' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            mb: 3,
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
              '&:hover fieldset': { borderColor: '#00d4ff' },
              '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
            },
            '& .MuiInputBase-input': { color: 'white' }
          }}
        />

        <TableContainer component={Paper} sx={{
          background: 'transparent',
          boxShadow: 'none',
          '& .MuiTable-root': {
            borderCollapse: 'separate',
            borderSpacing: '0 8px'
          }
        }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Symbol</TableCell>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Price</TableCell>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Change</TableCell>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Volume</TableCell>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Market Cap</TableCell>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredWatchlist.map((item) => (
                <TableRow
                  key={item.id}
                  sx={{
                    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%)',
                    borderRadius: 2,
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 212, 255, 0.03) 100%)',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(0, 212, 255, 0.2)'
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  <TableCell sx={{ border: 'none' }}>
                    <Box>
                      <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                        {item.symbol}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#aaa' }}>
                        {item.name}
                      </Typography>
                      {item.priceAlert && (
                        <Chip
                          label="Alert Set"
                          size="small"
                          sx={{
                            ml: 1,
                            height: 16,
                            fontSize: '0.7rem',
                            backgroundColor: alpha('#ff9800', 0.2),
                            color: '#ff9800',
                            border: `1px solid ${alpha('#ff9800', 0.3)}`
                          }}
                        />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell sx={{ border: 'none' }}>
                    <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                      ${item.currentPrice.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ border: 'none' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {item.change >= 0 ? (
                        <TrendingUp sx={{ color: '#4caf50', fontSize: 16, mr: 0.5 }} />
                      ) : (
                        <TrendingDown sx={{ color: '#f44336', fontSize: 16, mr: 0.5 }} />
                      )}
                      <Typography
                        variant="body2"
                        sx={{
                          color: getChangeColor(item.change),
                          fontWeight: 600
                        }}
                      >
                        {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)} ({item.changePercent >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%)
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell sx={{ border: 'none' }}>
                    <Typography variant="body2" sx={{ color: '#aaa' }}>
                      {formatVolume(item.volume)}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ border: 'none' }}>
                    <Typography variant="body2" sx={{ color: '#aaa' }}>
                      {item.marketCap}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ border: 'none' }}>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title="Set Price Alert">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedSymbol(item.symbol);
                            setAlertDialogOpen(true);
                          }}
                          sx={{
                            color: '#ff9800',
                            '&:hover': {
                              backgroundColor: alpha('#ff9800', 0.1)
                            }
                          }}
                        >
                          <AddAlert fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Add to Portfolio">
                        <IconButton
                          size="small"
                          onClick={() => onAddToPortfolio?.(item.symbol)}
                          sx={{
                            color: '#00d4ff',
                            '&:hover': {
                              backgroundColor: alpha('#00d4ff', 0.1)
                            }
                          }}
                        >
                          <Visibility fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Remove from Watchlist">
                        <IconButton
                          size="small"
                          onClick={() => handleRemoveFromWatchlist(item.symbol)}
                          sx={{
                            color: '#f44336',
                            '&:hover': {
                              backgroundColor: alpha('#f44336', 0.1)
                            }
                          }}
                        >
                          <Delete fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {filteredWatchlist.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" sx={{ color: '#aaa', mb: 2 }}>
              {searchTerm ? 'No symbols found matching your search.' : 'Your watchlist is empty.'}
            </Typography>
            <Button
              variant="outlined"
              startIcon={<Add />}
              onClick={() => setAddDialogOpen(true)}
              sx={{
                borderColor: '#00d4ff',
                color: '#00d4ff',
                '&:hover': {
                  borderColor: '#0099cc',
                  backgroundColor: 'rgba(0, 212, 255, 0.1)'
                }
              }}
            >
              Add Your First Symbol
            </Button>
          </Box>
        )}
      </CardContent>

      {/* Add Symbol Dialog */}
      <Dialog
        open={addDialogOpen}
        onClose={() => setAddDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            color: 'white',
            borderRadius: 3
          }
        }}
      >
        <DialogTitle sx={{ textAlign: 'center' }}>
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#00d4ff' }}>
            Add Symbol to Watchlist
          </Typography>
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Stock Symbol"
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
            placeholder="e.g., AAPL, TSLA, NVDA"
            sx={{
              mt: 2,
              '& .MuiOutlinedInput-root': {
                color: 'white',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: '#00d4ff' },
                '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
              },
              '& .MuiInputLabel-root': { color: '#aaa' }
            }}
          />
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button
            onClick={() => setAddDialogOpen(false)}
            sx={{ color: '#aaa' }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleAddSymbol}
            variant="contained"
            disabled={!newSymbol.trim()}
            sx={{
              background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
              '&:hover': {
                background: 'linear-gradient(45deg, #0099cc, #00d4ff)'
              }
            }}
          >
            Add Symbol
          </Button>
        </DialogActions>
      </Dialog>

      {/* Price Alert Dialog */}
      <Dialog
        open={alertDialogOpen}
        onClose={() => setAlertDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            color: 'white',
            borderRadius: 3
          }
        }}
      >
        <DialogTitle sx={{ textAlign: 'center' }}>
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#00d4ff' }}>
            Set Price Alert for {selectedSymbol}
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="Alert Above"
              type="number"
              value={alertAbove}
              onChange={(e) => setAlertAbove(e.target.value)}
              placeholder="e.g., 180"
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                  '&:hover fieldset': { borderColor: '#00d4ff' },
                  '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                },
                '& .MuiInputLabel-root': { color: '#aaa' }
              }}
            />
            <TextField
              fullWidth
              label="Alert Below"
              type="number"
              value={alertBelow}
              onChange={(e) => setAlertBelow(e.target.value)}
              placeholder="e.g., 170"
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                  '&:hover fieldset': { borderColor: '#00d4ff' },
                  '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                },
                '& .MuiInputLabel-root': { color: '#aaa' }
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button
            onClick={() => setAlertDialogOpen(false)}
            sx={{ color: '#aaa' }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSetPriceAlert}
            variant="contained"
            disabled={!alertAbove && !alertBelow}
            sx={{
              background: 'linear-gradient(45deg, #ff9800, #f57c00)',
              '&:hover': {
                background: 'linear-gradient(45deg, #f57c00, #ff9800)'
              }
            }}
          >
            Set Alert
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default Watchlist;
