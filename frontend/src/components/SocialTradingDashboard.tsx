import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Button,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tab,
  Tabs,
  Paper,
  LinearProgress,
  Divider,
  Badge,
  Tooltip
} from '@mui/material';
import {
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon,
  ContentCopy as CopyIcon,
  Favorite as FavoriteIcon,
  Share as ShareIcon,
  Comment as CommentIcon,
  Star as StarIcon,
  Verified as VerifiedIcon,
  Add as AddIcon,
  Notifications as NotificationsIcon
} from '@mui/icons-material';

interface SocialUser {
  user_id: number;
  username: string;
  display_name: string;
  avatar_url: string;
  tier: string;
  verified: boolean;
  followers_count: number;
  following_count: number;
  total_trades: number;
  win_rate: number;
  total_profit: number;
  influence_score: number;
  copy_trader_count: number;
}

interface TradingPost {
  id: string;
  user_id: number;
  username: string;
  display_name: string;
  avatar_url: string;
  verified: boolean;
  post_type: string;
  title: string;
  content: string;
  symbol?: string;
  action?: string;
  entry_price?: number;
  target_price?: number;
  confidence?: number;
  likes_count: number;
  comments_count: number;
  shares_count: number;
  created_at: string;
}

const SocialTradingDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [topTraders, setTopTraders] = useState<SocialUser[]>([]);
  const [socialFeed, setSocialFeed] = useState<TradingPost[]>([]);
  const [following, setFollowing] = useState<Set<number>>(new Set());

  // Mock data - replace with API calls
  useEffect(() => {
    // Mock top traders
    setTopTraders([
      {
        user_id: 1,
        username: "alpha_trader",
        display_name: "Alpha Trader",
        avatar_url: "/avatars/alpha.jpg",
        tier: "oracle",
        verified: true,
        followers_count: 15420,
        following_count: 234,
        total_trades: 1250,
        win_rate: 0.847,
        total_profit: 125000,
        influence_score: 9.8,
        copy_trader_count: 892
      },
      {
        user_id: 2,
        username: "crypto_guru",
        display_name: "Crypto Guru",
        avatar_url: "/avatars/crypto.jpg",
        tier: "legend",
        verified: true,
        followers_count: 8930,
        following_count: 156,
        total_trades: 890,
        win_rate: 0.782,
        total_profit: 89000,
        influence_score: 8.9,
        copy_trader_count: 445
      }
    ]);

    // Mock social feed
    setSocialFeed([
      {
        id: "post1",
        user_id: 1,
        username: "alpha_trader",
        display_name: "Alpha Trader",
        avatar_url: "/avatars/alpha.jpg",
        verified: true,
        post_type: "trade_alert",
        title: "🚀 BTC Breakout Alert!",
        content: "BTC breaking above $45,000 resistance. Long position opened! #btc #crypto #breakout",
        symbol: "BTCUSD",
        action: "buy",
        entry_price: 45000,
        target_price: 48000,
        confidence: 0.85,
        likes_count: 234,
        comments_count: 45,
        shares_count: 67,
        created_at: "2024-01-15T10:30:00Z"
      }
    ]);
  }, []);

  const getTierColor = (tier: string) => {
    const colors = {
      rookie: '#9e9e9e',
      trader: '#4caf50',
      expert: '#2196f3',
      master: '#9c27b0',
      legend: '#ff9800',
      oracle: '#f44336'
    };
    return colors[tier as keyof typeof colors] || '#9e9e9e';
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'oracle': return '🔮';
      case 'legend': return '👑';
      case 'master': return '⭐';
      case 'expert': return '💎';
      case 'trader': return '📈';
      default: return '🌱';
    }
  };

  const handleFollow = (userId: number) => {
    setFollowing(prev => {
      const newFollowing = new Set(prev);
      if (newFollowing.has(userId)) {
        newFollowing.delete(userId);
      } else {
        newFollowing.add(userId);
      }
      return newFollowing;
    });
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ p: 3, background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)', minHeight: '100vh' }}>
      <Typography variant="h4" sx={{ mb: 3, color: '#fff', fontWeight: 600 }}>
        🌐 Social Trading Network
      </Typography>
      
      <Typography variant="h6" sx={{ mb: 4, color: '#00d4ff', fontStyle: 'italic' }}>
        "Connect, Learn, and Profit Together"
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Top Traders" sx={{ color: '#fff' }} />
        <Tab label="Social Feed" sx={{ color: '#fff' }} />
        <Tab label="Trading Rooms" sx={{ color: '#fff' }} />
        <Tab label="My Network" sx={{ color: '#fff' }} />
      </Tabs>

      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mb: 2, color: '#fff' }}>
              🏆 Elite Traders - Follow & Copy the Best
            </Typography>
          </Grid>
          {topTraders.map((trader) => (
            <Grid item xs={12} md={6} lg={4} key={trader.user_id}>
              <Card sx={{ 
                background: 'rgba(26, 26, 26, 0.95)',
                border: `2px solid ${getTierColor(trader.tier)}`,
                borderRadius: 3,
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: `0 8px 25px rgba(${getTierColor(trader.tier)}, 0.3)`,
                  transition: 'all 0.3s ease'
                }
              }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Badge
                      badgeContent={getTierIcon(trader.tier)}
                      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                    >
                      <Avatar 
                        src={trader.avatar_url}
                        sx={{ 
                          width: 60, 
                          height: 60, 
                          border: `3px solid ${getTierColor(trader.tier)}`,
                          mr: 2 
                        }}
                      >
                        {trader.display_name[0]}
                      </Avatar>
                    </Badge>
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                        <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                          {trader.display_name}
                        </Typography>
                        {trader.verified && (
                          <VerifiedIcon sx={{ color: '#00d4ff', ml: 1, fontSize: 20 }} />
                        )}
                      </Box>
                      <Typography variant="body2" sx={{ color: '#888' }}>
                        @{trader.username}
                      </Typography>
                      <Chip 
                        label={trader.tier.toUpperCase()} 
                        size="small"
                        sx={{ 
                          bgcolor: getTierColor(trader.tier),
                          color: '#fff',
                          fontWeight: 'bold',
                          fontSize: '0.7rem',
                          mt: 0.5
                        }}
                      />
                    </Box>
                  </Box>

                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="body2" sx={{ color: '#888' }}>Win Rate</Typography>
                      <Typography variant="h6" sx={{ color: '#4caf50', fontWeight: 600 }}>
                        {(trader.win_rate * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" sx={{ color: '#888' }}>Total Profit</Typography>
                      <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                        ${trader.total_profit.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" sx={{ color: '#888' }}>Followers</Typography>
                      <Typography variant="body1" sx={{ color: '#fff', fontWeight: 600 }}>
                        {trader.followers_count.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" sx={{ color: '#888' }}>Copiers</Typography>
                      <Typography variant="body1" sx={{ color: '#ff6b35', fontWeight: 600 }}>
                        {trader.copy_trader_count.toLocaleString()}
                      </Typography>
                    </Grid>
                  </Grid>

                  <LinearProgress 
                    variant="determinate" 
                    value={trader.influence_score * 10} 
                    sx={{ 
                      mb: 2,
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: getTierColor(trader.tier),
                        borderRadius: 4
                      }
                    }}
                  />
                  <Typography variant="body2" sx={{ color: '#888', mb: 2, textAlign: 'center' }}>
                    Influence Score: {trader.influence_score}/10
                  </Typography>

                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant={following.has(trader.user_id) ? "contained" : "outlined"}
                      size="small"
                      startIcon={<AddIcon />}
                      onClick={() => handleFollow(trader.user_id)}
                      sx={{
                        flex: 1,
                        borderColor: '#00d4ff',
                        color: following.has(trader.user_id) ? '#000' : '#00d4ff',
                        bgcolor: following.has(trader.user_id) ? '#00d4ff' : 'transparent',
                        '&:hover': {
                          bgcolor: following.has(trader.user_id) ? '#00b8e6' : 'rgba(0, 212, 255, 0.1)'
                        }
                      }}
                    >
                      {following.has(trader.user_id) ? 'Following' : 'Follow'}
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<CopyIcon />}
                      sx={{
                        flex: 1,
                        borderColor: '#ff6b35',
                        color: '#ff6b35',
                        '&:hover': {
                          bgcolor: 'rgba(255, 107, 53, 0.1)'
                        }
                      }}
                    >
                      Copy
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {activeTab === 1 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2, color: '#fff' }}>
            📈 Live Trading Feed
          </Typography>
          {socialFeed.map((post) => (
            <Card key={post.id} sx={{ 
              mb: 2, 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar src={post.avatar_url} sx={{ mr: 2 }}>
                    {post.display_name[0]}
                  </Avatar>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                        {post.display_name}
                      </Typography>
                      {post.verified && (
                        <VerifiedIcon sx={{ color: '#00d4ff', ml: 1, fontSize: 16 }} />
                      )}
                    </Box>
                    <Typography variant="body2" sx={{ color: '#888' }}>
                      @{post.username} • {new Date(post.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                  <Chip 
                    label={post.post_type.replace('_', ' ').toUpperCase()} 
                    size="small"
                    sx={{ bgcolor: '#ff6b35', color: '#fff' }}
                  />
                </Box>

                <Typography variant="h6" sx={{ color: '#fff', mb: 1 }}>
                  {post.title}
                </Typography>
                <Typography variant="body1" sx={{ color: '#ccc', mb: 2 }}>
                  {post.content}
                </Typography>

                {post.symbol && (
                  <Paper sx={{ p: 2, mb: 2, bgcolor: 'rgba(0, 212, 255, 0.1)', border: '1px solid rgba(0, 212, 255, 0.3)' }}>
                    <Grid container spacing={2}>
                      <Grid item xs={3}>
                        <Typography variant="body2" sx={{ color: '#888' }}>Symbol</Typography>
                        <Typography variant="h6" sx={{ color: '#00d4ff' }}>{post.symbol}</Typography>
                      </Grid>
                      <Grid item xs={3}>
                        <Typography variant="body2" sx={{ color: '#888' }}>Action</Typography>
                        <Typography variant="h6" sx={{ color: post.action === 'buy' ? '#4caf50' : '#f44336' }}>
                          {post.action?.toUpperCase()}
                        </Typography>
                      </Grid>
                      <Grid item xs={3}>
                        <Typography variant="body2" sx={{ color: '#888' }}>Entry</Typography>
                        <Typography variant="h6" sx={{ color: '#fff' }}>${post.entry_price}</Typography>
                      </Grid>
                      <Grid item xs={3}>
                        <Typography variant="body2" sx={{ color: '#888' }}>Target</Typography>
                        <Typography variant="h6" sx={{ color: '#fff' }}>${post.target_price}</Typography>
                      </Grid>
                    </Grid>
                    {post.confidence && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                          Confidence: {(post.confidence * 100).toFixed(0)}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={post.confidence * 100}
                          sx={{ 
                            height: 6,
                            borderRadius: 3,
                            bgcolor: 'rgba(255, 255, 255, 0.1)',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: '#4caf50',
                              borderRadius: 3
                            }
                          }}
                        />
                      </Box>
                    )}
                  </Paper>
                )}

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Button startIcon={<FavoriteIcon />} size="small" sx={{ color: '#888' }}>
                    {post.likes_count}
                  </Button>
                  <Button startIcon={<CommentIcon />} size="small" sx={{ color: '#888' }}>
                    {post.comments_count}
                  </Button>
                  <Button startIcon={<ShareIcon />} size="small" sx={{ color: '#888' }}>
                    {post.shares_count}
                  </Button>
                  <Button startIcon={<CopyIcon />} size="small" sx={{ color: '#00d4ff' }}>
                    Copy Trade
                  </Button>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {activeTab === 2 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2, color: '#fff' }}>
            🏠 Trading Rooms - Coming Soon!
          </Typography>
          <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <PeopleIcon sx={{ fontSize: 80, color: '#888', mb: 2 }} />
              <Typography variant="h6" sx={{ color: '#fff', mb: 1 }}>
                Trading Rooms Feature
              </Typography>
              <Typography variant="body1" sx={{ color: '#888' }}>
                Join exclusive trading rooms, participate in group discussions, and learn from the community.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      )}

      {activeTab === 3 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2, color: '#fff' }}>
            👥 My Network - Coming Soon!
          </Typography>
          <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <CardContent sx={{ textAlign: 'center', py: 6 }}>
              <NotificationsIcon sx={{ fontSize: 80, color: '#888', mb: 2 }} />
              <Typography variant="h6" sx={{ color: '#fff', mb: 1 }}>
                My Network Dashboard
              </Typography>
              <Typography variant="body1" sx={{ color: '#888' }}>
                Manage your followers, following, and copy trading settings.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

export default SocialTradingDashboard;
