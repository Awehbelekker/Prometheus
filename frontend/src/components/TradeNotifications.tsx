import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Badge,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  Avatar,
  Divider,
  Button
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Notifications,
  NotificationsOff,
  ExpandMore,
  ExpandLess,
  Close
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { TradeNotification } from '../hooks/useWebSocket';

interface TradeNotificationsProps {
  latestTrade: TradeNotification | null;
  recentTrades: TradeNotification[];
  isConnected: boolean;
}

export const TradeNotifications: React.FC<TradeNotificationsProps> = ({
  latestTrade,
  recentTrades,
  isConnected
}) => {
  const [showNotifications, setShowNotifications] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [dismissedTrades, setDismissedTrades] = useState<Set<string>>(new Set());

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getTradeIcon = (side: 'buy' | 'sell', profit: number) => {
    if (side === 'buy') {
      return profit > 0 ? '🟢' : '🔴';
    } else {
      return profit > 0 ? '🟢' : '🔴';
    }
  };

  const getTradeColor = (profit: number) => {
    return profit > 0 ? '#4caf50' : '#f44336';
  };

  const dismissTrade = (tradeId: string) => {
    setDismissedTrades(prev => {
      const newSet = new Set(prev);
      newSet.add(tradeId);
      return newSet;
    });
  };

  const visibleTrades = recentTrades.filter(trade => !dismissedTrades.has(trade.id));
  const newTradesCount = visibleTrades.length;

  return (
    <Box sx={{ position: 'relative', minHeight: 200 }}>
      {/* Connection Status */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          📡 Live Trading Feed
          <Chip
            label={isConnected ? 'LIVE' : 'SIMULATED'}
            color={isConnected ? 'success' : 'warning'}
            size="small"
            variant="filled"
          />
        </Typography>
        
        <IconButton
          onClick={() => setShowNotifications(!showNotifications)}
          color={showNotifications ? 'primary' : 'default'}
        >
          <Badge badgeContent={newTradesCount} color="error" max={99}>
            {showNotifications ? <Notifications /> : <NotificationsOff />}
          </Badge>
        </IconButton>
      </Box>

      {/* Latest Trade Alert */}
      <AnimatePresence>
        {showNotifications && latestTrade && !dismissedTrades.has(latestTrade.id) && (
          <motion.div
            initial={{ opacity: 0, y: -50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, x: 300, scale: 0.8 }}
            transition={{ duration: 0.5, type: "spring" }}
          >
            <Card
              sx={{
                mb: 2,
                border: `2px solid ${getTradeColor(latestTrade.profit)}`,
                background: `linear-gradient(135deg, ${getTradeColor(latestTrade.profit)}15, transparent)`,
                position: 'relative',
                overflow: 'visible'
              }}
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3, type: "spring" }}
                style={{
                  position: 'absolute',
                  top: -10,
                  left: -10,
                  fontSize: '2rem',
                  background: 'white',
                  borderRadius: '50%',
                  padding: '5px',
                  border: `2px solid ${getTradeColor(latestTrade.profit)}`
                }}
              >
                {getTradeIcon(latestTrade.side, latestTrade.profit)}
              </motion.div>
              
              <CardContent sx={{ pt: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="h6" sx={{ color: getTradeColor(latestTrade.profit) }}>
                      {latestTrade.side.toUpperCase()} {latestTrade.quantity} {latestTrade.symbol}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      ${latestTrade.price.toFixed(2)} • {formatTime(latestTrade.timestamp)}
                    </Typography>
                  </Box>
                  
                  <Box textAlign="right">
                    <Typography 
                      variant="h5" 
                      sx={{ 
                        color: getTradeColor(latestTrade.profit),
                        fontWeight: 'bold'
                      }}
                    >
                      {latestTrade.profit > 0 ? '+' : ''}${latestTrade.profit.toFixed(2)}
                    </Typography>
                    <Chip 
                      label={latestTrade.status.toUpperCase()}
                      color="success"
                      size="small"
                    />
                  </Box>
                  
                  <IconButton 
                    size="small"
                    onClick={() => dismissTrade(latestTrade.id)}
                  >
                    <Close />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Trade History */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Recent Trades</Typography>
            <IconButton onClick={() => setExpanded(!expanded)}>
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
          
          <Collapse in={expanded}>
            <List>
              {visibleTrades.slice(1, 6).map((trade, index) => (
                <motion.div
                  key={trade.id}
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <ListItem>
                    <Avatar 
                      sx={{ 
                        bgcolor: getTradeColor(trade.profit),
                        width: 32,
                        height: 32,
                        mr: 2
                      }}
                    >
                      {trade.side === 'buy' ? <TrendingUp /> : <TrendingDown />}
                    </Avatar>
                    
                    <ListItemText
                      primary={
                        <Typography variant="body1">
                          {trade.side.toUpperCase()} {trade.quantity} {trade.symbol}
                        </Typography>
                      }
                      secondary={
                        <Typography variant="body2" color="textSecondary">
                          ${trade.price.toFixed(2)} • {formatTime(trade.timestamp)}
                        </Typography>
                      }
                    />
                    
                    <Typography 
                      variant="body1"
                      sx={{ 
                        color: getTradeColor(trade.profit),
                        fontWeight: 'bold',
                        minWidth: 80,
                        textAlign: 'right'
                      }}
                    >
                      {trade.profit > 0 ? '+' : ''}${trade.profit.toFixed(2)}
                    </Typography>
                    
                    <IconButton 
                      size="small"
                      onClick={() => dismissTrade(trade.id)}
                    >
                      <Close />
                    </IconButton>
                  </ListItem>
                  {index < visibleTrades.slice(1, 6).length - 1 && <Divider />}
                </motion.div>
              ))}
            </List>
            
            {visibleTrades.length === 0 && (
              <Box textAlign="center" py={3}>
                <Typography variant="body2" color="textSecondary">
                  No recent trades
                </Typography>
              </Box>
            )}
            
            {visibleTrades.length > 6 && (
              <Box textAlign="center" pt={2}>
                <Button variant="outlined" size="small">
                  View All {visibleTrades.length} Trades
                </Button>
              </Box>
            )}
          </Collapse>
        </CardContent>
      </Card>
    </Box>
  );
};
