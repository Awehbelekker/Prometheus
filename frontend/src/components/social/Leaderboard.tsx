import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  alpha
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  EmojiEvents,
  Star,
  Visibility
} from '@mui/icons-material';

interface LeaderboardEntry {
  id: string;
  username: string;
  avatar?: string;
  rank: number;
  totalReturn: number;
  winRate: number;
  totalTrades: number;
  level: string;
  isFollowing?: boolean;
  isCurrentUser?: boolean;
}

interface LeaderboardProps {
  currentUserId?: string;
  onFollowUser?: (userId: string) => void;
  onViewProfile?: (userId: string) => void;
}

const Leaderboard: React.FC<LeaderboardProps> = ({
  currentUserId,
  onFollowUser,
  onViewProfile
}) => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call to fetch leaderboard data
    const fetchLeaderboard = async () => {
      setLoading(true);
      
      // Mock data - replace with real API call
      const mockData: LeaderboardEntry[] = [
        {
          id: '1',
          username: 'TradingMaster2024',
          rank: 1,
          totalReturn: 47.8,
          winRate: 89.2,
          totalTrades: 156,
          level: 'Legend',
          isFollowing: false,
          isCurrentUser: currentUserId === '1'
        },
        {
          id: '2',
          username: 'AITraderPro',
          rank: 2,
          totalReturn: 42.3,
          winRate: 85.7,
          totalTrades: 203,
          level: 'Master',
          isFollowing: true,
          isCurrentUser: currentUserId === '2'
        },
        {
          id: '3',
          username: 'QuantumTrader',
          rank: 3,
          totalReturn: 38.9,
          winRate: 82.1,
          totalTrades: 134,
          level: 'Expert',
          isFollowing: false,
          isCurrentUser: currentUserId === '3'
        },
        {
          id: '4',
          username: 'NeuroForgeElite',
          rank: 4,
          totalReturn: 35.6,
          winRate: 79.8,
          totalTrades: 187,
          level: 'Expert',
          isFollowing: false,
          isCurrentUser: currentUserId === '4'
        },
        {
          id: '5',
          username: 'CryptoKing',
          rank: 5,
          totalReturn: 32.1,
          winRate: 76.4,
          totalTrades: 98,
          level: 'Trader',
          isFollowing: true,
          isCurrentUser: currentUserId === '5'
        }
      ];

      setTimeout(() => {
        setLeaderboard(mockData);
        setLoading(false);
      }, 1000);
    };

    fetchLeaderboard();
  }, [currentUserId]);

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <EmojiEvents sx={{ color: '#ffd700', fontSize: 24 }} />;
      case 2:
        return <EmojiEvents sx={{ color: '#c0c0c0', fontSize: 24 }} />;
      case 3:
        return <EmojiEvents sx={{ color: '#cd7f32', fontSize: 24 }} />;
      default:
        return <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 700 }}>
          #{rank}
        </Typography>;
    }
  };

  const getLevelColor = (level: string) => {
    const colors = {
      'Legend': '#ff9800',
      'Master': '#9c27b0',
      'Expert': '#2196f3',
      'Trader': '#4caf50',
      'Rookie': '#9e9e9e'
    };
    return colors[level as keyof typeof colors] || '#2196f3';
  };

  const getReturnColor = (returnValue: number) => {
    return returnValue >= 0 ? '#4caf50' : '#f44336';
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
            🏆 Top Traders
          </Typography>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" sx={{ color: '#aaa' }}>
              Loading leaderboard...
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
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <EmojiEvents sx={{ color: '#ffd700', fontSize: 28, mr: 1 }} />
          <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
            Top Traders
          </Typography>
        </Box>

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
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Rank</TableCell>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Trader</TableCell>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Return</TableCell>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Win Rate</TableCell>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Trades</TableCell>
                <TableCell sx={{ color: '#aaa', border: 'none', fontWeight: 600 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {leaderboard.map((entry) => (
                <TableRow
                  key={entry.id}
                  sx={{
                    background: entry.isCurrentUser 
                      ? 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%)'
                      : 'linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%)',
                    borderRadius: 2,
                    border: entry.isCurrentUser ? '1px solid rgba(0, 212, 255, 0.3)' : '1px solid rgba(255, 255, 255, 0.1)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 212, 255, 0.03) 100%)',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(0, 212, 255, 0.2)'
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  <TableCell sx={{ border: 'none' }}>
                    {getRankIcon(entry.rank)}
                  </TableCell>
                  <TableCell sx={{ border: 'none' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar
                        sx={{
                          width: 32,
                          height: 32,
                          mr: 2,
                          background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                          fontSize: '0.875rem'
                        }}
                      >
                        {entry.username.charAt(0).toUpperCase()}
                      </Avatar>
                      <Box>
                        <Typography variant="body2" sx={{ 
                          color: 'white', 
                          fontWeight: 600,
                          display: 'flex',
                          alignItems: 'center'
                        }}>
                          {entry.username}
                          {entry.isCurrentUser && (
                            <Chip
                              label="You"
                              size="small"
                              sx={{
                                ml: 1,
                                height: 16,
                                fontSize: '0.7rem',
                                background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                                color: 'white'
                              }}
                            />
                          )}
                        </Typography>
                        <Chip
                          label={entry.level}
                          size="small"
                          sx={{
                            height: 18,
                            fontSize: '0.7rem',
                            backgroundColor: alpha(getLevelColor(entry.level), 0.2),
                            color: getLevelColor(entry.level),
                            border: `1px solid ${alpha(getLevelColor(entry.level), 0.3)}`
                          }}
                        />
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell sx={{ border: 'none' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {entry.totalReturn >= 0 ? (
                        <TrendingUp sx={{ color: '#4caf50', fontSize: 16, mr: 0.5 }} />
                      ) : (
                        <TrendingDown sx={{ color: '#f44336', fontSize: 16, mr: 0.5 }} />
                      )}
                      <Typography
                        variant="body2"
                        sx={{
                          color: getReturnColor(entry.totalReturn),
                          fontWeight: 600
                        }}
                      >
                        {entry.totalReturn >= 0 ? '+' : ''}{entry.totalReturn.toFixed(1)}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell sx={{ border: 'none' }}>
                    <Typography variant="body2" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                      {entry.winRate.toFixed(1)}%
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ border: 'none' }}>
                    <Typography variant="body2" sx={{ color: '#aaa' }}>
                      {entry.totalTrades}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ border: 'none' }}>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title="View Profile">
                        <IconButton
                          size="small"
                          onClick={() => onViewProfile?.(entry.id)}
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
                      {!entry.isCurrentUser && (
                        <Tooltip title={entry.isFollowing ? "Unfollow" : "Follow"}>
                          <IconButton
                            size="small"
                            onClick={() => onFollowUser?.(entry.id)}
                            sx={{
                              color: entry.isFollowing ? '#4caf50' : '#aaa',
                              '&:hover': {
                                backgroundColor: alpha(entry.isFollowing ? '#4caf50' : '#00d4ff', 0.1)
                              }
                            }}
                          >
                            <Star fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
            Compete with the best traders and climb the leaderboard!
          </Typography>
          <Chip
            label="Updated every 5 minutes"
            size="small"
            sx={{
              backgroundColor: alpha('#00d4ff', 0.1),
              color: '#00d4ff',
              border: `1px solid ${alpha('#00d4ff', 0.3)}`
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default Leaderboard;