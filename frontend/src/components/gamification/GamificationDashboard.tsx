import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Grid,
  Avatar,
  Tabs,
  Tab,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  Badge,
  Tooltip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress
} from '@mui/material';
import {
  EmojiEvents,
  Star,
  TrendingUp,
  Assessment,
  Timeline,
  LocalFireDepartment,
  WorkspacePremium,
  MilitaryTech,
  AutoAwesome,
  CheckCircle,
  Lock,
  Visibility,
  Close,
  Leaderboard as LeaderboardIcon,
  Medal,
  Whatshot
} from '@mui/icons-material';
import { useGamification } from '../../hooks/useGamification';
import { useLeaderboard } from '../../hooks/useLeaderboard';
import { useSnackbar } from 'notistack';

interface GamificationDashboardProps {
  userId: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`gamification-tabpanel-${index}`}
      aria-labelledby={`gamification-tab-${index}`}
      aria-live="polite"
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const GamificationDashboard: React.FC<GamificationDashboardProps> = ({ userId }) => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedAchievement, setSelectedAchievement] = useState<any>(null);
  const [achievementDialogOpen, setAchievementDialogOpen] = useState(false);
  const { enqueueSnackbar } = useSnackbar();

  const {
    level,
    xp,
    achievements,
    skillRatings,
    badges,
    streak,
    nextLevelXP,
    xpToNextLevel,
    totalAchievements,
    isLoading,
    error
  } = useGamification(userId);

  // Fetch leaderboard data
  const { leaderboard, isLoading: leaderboardLoading } = useLeaderboard(50);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAchievementClick = (achievement: any) => {
    setSelectedAchievement(achievement);
    setAchievementDialogOpen(true);
  };

  const getLevelColor = (level: number) => {
    if (level >= 50) return '#f44336'; // Legend
    if (level >= 30) return '#9c27b0'; // Master
    if (level >= 20) return '#2196f3'; // Expert
    if (level >= 10) return '#4caf50'; // Trader
    return '#9e9e9e'; // Rookie
  };

  const getLevelTitle = (level: number) => {
    if (level >= 50) return 'Legend';
    if (level >= 30) return 'Master';
    if (level >= 20) return 'Expert';
    if (level >= 10) return 'Trader';
    return 'Rookie';
  };

  const getRarityColor = (rarity?: string) => {
    switch (rarity?.toLowerCase()) {
      case 'legendary': return '#f44336';
      case 'epic': return '#9c27b0';
      case 'rare': return '#2196f3';
      case 'uncommon': return '#4caf50';
      default: return '#9e9e9e';
    }
  };

  const getSkillIcon = (skill: string) => {
    switch (skill) {
      case 'risk_management': return '🛡️';
      case 'market_analysis': return '📊';
      case 'timing': return '⏰';
      case 'portfolio_management': return '💼';
      case 'consistency': return '📈';
      default: return '⭐';
    }
  };

  if (isLoading) {
    return (
      <Box>
        {/* Skeleton Header Stats */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {[1, 2, 3].map((i) => (
            <Grid item xs={12} md={4} key={i}>
              <Card sx={{
                background: 'rgba(26, 26, 46, 0.8)',
                border: '1px solid rgba(0, 212, 255, 0.2)',
                borderRadius: 3,
                animation: 'pulse 2s ease-in-out infinite',
                '@keyframes pulse': {
                  '0%, 100%': { opacity: 1 },
                  '50%': { opacity: 0.6 }
                }
              }}>
                <CardContent sx={{ p: 3, textAlign: 'center' }}>
                  <Box sx={{
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    mx: 'auto',
                    mb: 2
                  }} />
                  <Box sx={{
                    height: 24,
                    width: '60%',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: 1,
                    mx: 'auto',
                    mb: 1
                  }} />
                  <Box sx={{
                    height: 16,
                    width: '40%',
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: 1,
                    mx: 'auto'
                  }} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
        {/* Skeleton Progress Bar */}
        <Card sx={{
          background: 'rgba(26, 26, 46, 0.8)',
          border: '1px solid rgba(0, 212, 255, 0.2)',
          borderRadius: 3,
          mb: 4
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ height: 24, width: '40%', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: 1 }} />
              <Box sx={{ height: 32, width: 60, backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: 1 }} />
            </Box>
            <LinearProgress
              variant="indeterminate"
              sx={{
                height: 16,
                borderRadius: 8,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(90deg, #00d4ff, #0099cc)',
                  borderRadius: 8
                }
              }}
            />
          </CardContent>
        </Card>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
          <CircularProgress sx={{ color: '#00d4ff' }} />
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Card sx={{
        background: 'rgba(26, 26, 46, 0.8)',
        border: '1px solid rgba(244, 67, 54, 0.3)',
        borderRadius: 3,
        animation: 'slideDown 0.3s ease-out',
        '@keyframes slideDown': {
          from: {
            opacity: 0,
            transform: 'translateY(-10px)'
          },
          to: {
            opacity: 1,
            transform: 'translateY(0)'
          }
        }
      }}>
        <CardContent sx={{ p: 4, textAlign: 'center' }}>
          <Box sx={{
            width: 64,
            height: 64,
            borderRadius: '50%',
            backgroundColor: 'rgba(244, 67, 54, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mx: 'auto',
            mb: 2
          }}>
            <Typography variant="h3">⚠️</Typography>
          </Box>
          <Typography variant="h6" sx={{ color: '#f44336', mb: 1, fontWeight: 600 }}>
            Failed to load gamification data
          </Typography>
          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 3 }}>
            {error?.toString() || 'An error occurred while loading your progress'}
          </Typography>
          <Button
            variant="outlined"
            onClick={() => window.location.reload()}
            sx={{
              borderColor: '#f44336',
              color: '#f44336',
              '&:hover': {
                borderColor: '#f44336',
                backgroundColor: 'rgba(244, 67, 54, 0.1)'
              }
            }}
          >
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const progressPercentage = nextLevelXP > 0 ? Math.round((xpToNextLevel / nextLevelXP) * 100) : 0;
  const levelColor = getLevelColor(level);
  const levelTitle = getLevelTitle(level);

  return (
    <Box role="region" aria-label="Gamification Dashboard">
      {/* Header Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }} role="group" aria-label="User Statistics">
        <Grid item xs={12} md={4}>
          <Card sx={{
            background: `linear-gradient(135deg, ${levelColor}20 0%, ${levelColor}10 100%)`,
            border: `2px solid ${levelColor}`,
            borderRadius: 3,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            animation: 'fadeInUp 0.6s ease-out',
            '@keyframes fadeInUp': {
              from: {
                opacity: 0,
                transform: 'translateY(20px)'
              },
              to: {
                opacity: 1,
                transform: 'translateY(0)'
              }
            },
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: `0 12px 40px ${levelColor}40`
            }
          }}>
            <CardContent sx={{ p: 3, textAlign: 'center' }}>
              <Box 
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  backgroundColor: `${levelColor}20`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 2,
                  border: `3px solid ${levelColor}`,
                  position: 'relative',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    width: '100%',
                    height: '100%',
                    borderRadius: '50%',
                    border: `3px solid ${levelColor}`,
                    opacity: 0.5,
                    animation: 'pulseRing 2s ease-out infinite',
                    '@keyframes pulseRing': {
                      '0%': {
                        transform: 'scale(1)',
                        opacity: 0.5
                      },
                      '100%': {
                        transform: 'scale(1.3)',
                        opacity: 0
                      }
                    }
                  }
                }}
                aria-label={`Level ${level}, ${levelTitle} Trader`}
              >
                <Typography variant="h3" sx={{ position: 'relative', zIndex: 1, fontWeight: 700 }} aria-hidden="true">
                  {level}
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: levelColor, fontWeight: 700, mb: 1 }} component="h2">
                {levelTitle} Trader
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontFamily: 'monospace' }} aria-label={`${xp.toLocaleString()} Total Experience Points`}>
                {xp.toLocaleString()} Total XP
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{
            background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)',
            border: '2px solid #ff9800',
            borderRadius: 3,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            animation: 'fadeInUp 0.6s ease-out 0.1s both',
            '@keyframes fadeInUp': {
              from: {
                opacity: 0,
                transform: 'translateY(20px)'
              },
              to: {
                opacity: 1,
                transform: 'translateY(0)'
              }
            },
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 12px 40px rgba(255, 152, 0, 0.3)'
            }
          }}>
            <CardContent sx={{ p: 3, textAlign: 'center' }}>
              <LocalFireDepartment 
                sx={{
                  fontSize: 48,
                  color: '#ff9800',
                  mb: 1,
                  animation: streak > 0 ? 'flame 1.5s ease-in-out infinite' : 'none',
                  '@keyframes flame': {
                    '0%, 100%': { transform: 'scale(1) rotate(0deg)' },
                    '50%': { transform: 'scale(1.1) rotate(-5deg)' }
                  }
                }}
                aria-hidden="true"
              />
              <Typography variant="h4" sx={{ color: '#ff9800', fontWeight: 700, mb: 1, fontFamily: 'monospace' }} aria-label={`${streak} day trading streak`}>
                {streak}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Day Streak 🔥
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{
            background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)',
            border: '2px solid #4caf50',
            borderRadius: 3,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            animation: 'fadeInUp 0.6s ease-out 0.2s both',
            '@keyframes fadeInUp': {
              from: {
                opacity: 0,
                transform: 'translateY(20px)'
              },
              to: {
                opacity: 1,
                transform: 'translateY(0)'
              }
            },
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 12px 40px rgba(76, 175, 80, 0.3)'
            }
          }}>
            <CardContent sx={{ p: 3, textAlign: 'center' }}>
              <EmojiEvents sx={{ fontSize: 48, color: '#4caf50', mb: 1 }} aria-hidden="true" />
              <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 700, mb: 1, fontFamily: 'monospace' }} aria-label={`${totalAchievements} achievements unlocked`}>
                {totalAchievements}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Achievements Unlocked
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Level Progress */}
      <Card sx={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        border: `2px solid ${levelColor}`,
        borderRadius: 3,
        mb: 4,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          boxShadow: `0 8px 32px ${levelColor}30`,
          transform: 'translateY(-2px)'
        }
      }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Box>
              <Typography variant="h5" sx={{ color: levelColor, fontWeight: 700, mb: 0.5 }}>
                Level {level} → Level {level + 1}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                {xpToNextLevel.toLocaleString()} / {nextLevelXP.toLocaleString()} XP needed
              </Typography>
            </Box>
            <Chip
              label={`${progressPercentage}%`}
              sx={{
                bgcolor: levelColor,
                color: '#fff',
                fontWeight: 700,
                fontSize: '1rem',
                height: 36
              }}
            />
          </Box>
          <LinearProgress
            variant="determinate"
            value={progressPercentage}
            aria-label={`Level progress: ${progressPercentage}% to next level`}
            aria-valuenow={progressPercentage}
            aria-valuemin={0}
            aria-valuemax={100}
            sx={{
              height: 16,
              borderRadius: 8,
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              position: 'relative',
              overflow: 'visible',
              '& .MuiLinearProgress-bar': {
                background: `linear-gradient(90deg, ${levelColor}, ${levelColor}cc)`,
                borderRadius: 8,
                transition: 'width 1s cubic-bezier(0.4, 0, 0.2, 1)',
                boxShadow: `0 0 20px ${levelColor}60`,
                position: 'relative',
                '&::after': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  borderRadius: 8,
                  background: `linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent)`,
                  animation: 'shimmer 2s infinite',
                  '@keyframes shimmer': {
                    '0%': { transform: 'translateX(-100%)' },
                    '100%': { transform: 'translateX(100%)' }
                  }
                }
              }
            }}
          />
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card sx={{
        background: 'rgba(26, 26, 46, 0.8)',
        border: '1px solid rgba(0, 212, 255, 0.2)',
        borderRadius: 3
      }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            sx={{
              '& .MuiTab-root': {
                color: 'rgba(255, 255, 255, 0.7)',
                fontWeight: 600,
                '&.Mui-selected': {
                  color: '#00d4ff'
                }
              },
              '& .MuiTabs-indicator': {
                backgroundColor: '#00d4ff'
              }
            }}
          >
            <Tab label="Achievements" icon={<EmojiEvents />} iconPosition="start" />
            <Tab label="Badges" icon={<WorkspacePremium />} iconPosition="start" />
            <Tab label="Skills" icon={<Assessment />} iconPosition="start" />
            <Tab label="Progress" icon={<Timeline />} iconPosition="start" />
            <Tab label="Leaderboard" icon={<LeaderboardIcon />} iconPosition="start" />
          </Tabs>
        </Box>

        {/* Achievements Tab */}
        <TabPanel value={tabValue} index={0}>
          {/* Show unlocked achievements */}
          {achievements.length > 0 && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" sx={{ color: '#4caf50', mb: 2, fontWeight: 700 }}>
                ✅ Unlocked Achievements ({achievements.length})
              </Typography>
              <Grid container spacing={2}>
                {achievements.map((achievement, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card
                    sx={{
                      background: 'rgba(255, 152, 0, 0.1)',
                      border: '1px solid rgba(255, 152, 0, 0.3)',
                      borderRadius: 2,
                      cursor: 'pointer',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      animation: `fadeInScale 0.5s ease-out ${index * 0.1}s both`,
                      '@keyframes fadeInScale': {
                        from: {
                          opacity: 0,
                          transform: 'scale(0.9)'
                        },
                        to: {
                          opacity: 1,
                          transform: 'scale(1)'
                        }
                      },
                      '&:hover': {
                        background: 'rgba(255, 152, 0, 0.15)',
                        borderColor: 'rgba(255, 152, 0, 0.5)',
                        transform: 'translateY(-4px) scale(1.02)',
                        boxShadow: '0 8px 24px rgba(255, 152, 0, 0.3)'
                      }
                    }}
                    onClick={() => handleAchievementClick(achievement)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleAchievementClick(achievement);
                      }
                    }}
                    tabIndex={0}
                    role="button"
                    aria-label={`View details for achievement: ${achievement.name}`}
                  >
                    <CardContent sx={{ p: 2.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1.5 }}>
                        <Typography variant="h3" sx={{ mr: 1.5 }} aria-hidden="true">
                          {achievement.icon}
                        </Typography>
                        <Box sx={{ flex: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <Typography variant="subtitle1" sx={{ color: '#fff', fontWeight: 700 }}>
                              {achievement.name}
                            </Typography>
                            {achievement.rarity && (
                              <Chip
                                label={achievement.rarity}
                                size="small"
                                sx={{
                                  bgcolor: getRarityColor(achievement.rarity),
                                  color: '#fff',
                                  fontWeight: 600,
                                  height: 20,
                                  fontSize: '0.65rem'
                                }}
                              />
                            )}
                          </Box>
                          <Chip
                            label={`+${achievement.points} XP`}
                            size="small"
                            sx={{
                              bgcolor: 'rgba(255, 152, 0, 0.2)',
                              color: '#ff9800',
                              fontWeight: 700,
                              height: 20,
                              fontSize: '0.7rem'
                            }}
                          />
                        </Box>
                      </Box>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.85rem' }}>
                        {achievement.description}
                      </Typography>
                      {achievement.earned_at && (
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', mt: 1, display: 'block' }}>
                          Earned: {new Date(achievement.earned_at).toLocaleDateString()}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Show locked achievements with progress (mock data for now - can be enhanced with backend) */}
          <Box>
            <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2, fontWeight: 700 }}>
              🔒 Available Achievements
            </Typography>
            <Grid container spacing={2}>
              {/* Example locked achievements - these would come from backend in a real implementation */}
              {[
                { id: 'first_trade', name: 'First Trade', description: 'Complete your first trade', icon: '🎯', points: 50, progress: 0, target: 1, rarity: 'Common' },
                { id: 'ten_trades', name: 'Ten Trades', description: 'Complete 10 trades', icon: '📊', points: 200, progress: 0, target: 10, rarity: 'Uncommon' },
                { id: 'hundred_trades', name: 'Century Club', description: 'Complete 100 trades', icon: '💯', points: 1000, progress: 0, target: 100, rarity: 'Rare' },
                { id: 'profit_maker', name: 'Profit Maker', description: 'Earn $1000 in profit', icon: '💰', points: 500, progress: 0, target: 1000, rarity: 'Uncommon' },
                { id: 'streak_master', name: 'Streak Master', description: 'Maintain a 7-day trading streak', icon: '🔥', points: 300, progress: streak, target: 7, rarity: 'Rare' },
                { id: 'risk_manager', name: 'Risk Manager', description: 'Achieve 80% in Risk Management skill', icon: '🛡️', points: 400, progress: skillRatings.risk_management, target: 80, rarity: 'Epic' }
              ].filter(ach => !achievements.find(a => a.id === ach.id)).map((achievement) => {
                const progressPercent = Math.min((achievement.progress / achievement.target) * 100, 100);
                const isNearComplete = progressPercent >= 75;
                
                return (
                  <Grid item xs={12} sm={6} md={4} key={achievement.id}>
                    <Card
                      sx={{
                        background: 'rgba(100, 100, 100, 0.1)',
                        border: `1px solid ${isNearComplete ? 'rgba(255, 152, 0, 0.5)' : 'rgba(255, 255, 255, 0.1)'}`,
                        borderRadius: 2,
                        cursor: 'pointer',
                        position: 'relative',
                        opacity: 0.7,
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                        '&:hover': {
                          opacity: 1,
                          borderColor: isNearComplete ? 'rgba(255, 152, 0, 0.8)' : 'rgba(255, 255, 255, 0.3)',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
                        }
                      }}
                      onClick={() => handleAchievementClick(achievement)}
                    >
                      <CardContent sx={{ p: 2.5 }}>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1.5 }}>
                          <Typography variant="h3" sx={{ mr: 1.5, filter: 'grayscale(100%)' }}>
                            {achievement.icon}
                          </Typography>
                          <Box sx={{ flex: 1 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                              <Typography variant="subtitle1" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 700 }}>
                                {achievement.name}
                              </Typography>
                              <Lock sx={{ fontSize: 16, color: 'rgba(255, 255, 255, 0.5)' }} />
                              {achievement.rarity && (
                                <Chip
                                  label={achievement.rarity}
                                  size="small"
                                  sx={{
                                    bgcolor: getRarityColor(achievement.rarity),
                                    color: '#fff',
                                    fontWeight: 600,
                                    height: 20,
                                    fontSize: '0.65rem',
                                    opacity: 0.7
                                  }}
                                />
                              )}
                            </Box>
                            <Chip
                              label={`+${achievement.points} XP`}
                              size="small"
                              sx={{
                                bgcolor: 'rgba(255, 152, 0, 0.1)',
                                color: 'rgba(255, 152, 0, 0.7)',
                                fontWeight: 700,
                                height: 20,
                                fontSize: '0.7rem'
                              }}
                            />
                          </Box>
                        </Box>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.85rem', mb: 1.5 }}>
                          {achievement.description}
                        </Typography>
                        {/* Progress Bar */}
                        <Box sx={{ mt: 1.5 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)', fontWeight: 600 }}>
                              Progress
                            </Typography>
                            <Typography variant="caption" sx={{ color: isNearComplete ? '#ff9800' : 'rgba(255, 255, 255, 0.6)', fontWeight: 700 }}>
                              {achievement.progress} / {achievement.target} ({Math.round(progressPercent)}%)
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={progressPercent}
                            sx={{
                              height: 8,
                              borderRadius: 4,
                              backgroundColor: 'rgba(255, 255, 255, 0.1)',
                              '& .MuiLinearProgress-bar': {
                                background: isNearComplete
                                  ? 'linear-gradient(90deg, #ff9800, #ffb74d)'
                                  : 'linear-gradient(90deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.5))',
                                borderRadius: 4,
                                transition: 'width 0.6s ease'
                              }
                            }}
                          />
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
              {achievements.length === 0 && (
                <Grid item xs={12}>
                  <Box sx={{ textAlign: 'center', py: 6 }}>
                    <Lock sx={{ fontSize: 64, color: 'rgba(255, 255, 255, 0.3)', mb: 2 }} />
                    <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.5)', mb: 1 }}>
                      No achievements yet
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.3)' }}>
                      Start trading to unlock your first achievement!
                    </Typography>
                  </Box>
                </Grid>
              )}
            </Grid>
          </Box>
        </TabPanel>

        {/* Badges Tab */}
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={2}>
            {badges.length > 0 ? (
              badges.map((badge, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card sx={{
                    background: 'rgba(156, 39, 176, 0.1)',
                    border: '1px solid rgba(156, 39, 176, 0.3)',
                    borderRadius: 2,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      background: 'rgba(156, 39, 176, 0.15)',
                      borderColor: 'rgba(156, 39, 176, 0.5)',
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 24px rgba(156, 39, 176, 0.3)'
                    }
                  }}>
                    <CardContent sx={{ p: 3, textAlign: 'center' }}>
                      <Typography variant="h2" sx={{ mb: 1 }}>
                        {badge.icon}
                      </Typography>
                      <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700, mb: 1 }}>
                        {badge.name}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2 }}>
                        {badge.description}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <Chip
                          label={badge.rarity}
                          size="small"
                          sx={{
                            bgcolor: getRarityColor(badge.rarity),
                            color: '#fff',
                            fontWeight: 600
                          }}
                        />
                        <Chip
                          label={`+${badge.xp_reward} XP`}
                          size="small"
                          sx={{
                            bgcolor: 'rgba(156, 39, 176, 0.2)',
                            color: '#9c27b0',
                            fontWeight: 600
                          }}
                        />
                      </Box>
                      {badge.earned_at && (
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', mt: 2, display: 'block' }}>
                          Earned: {new Date(badge.earned_at).toLocaleDateString()}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))
            ) : (
              <Grid item xs={12}>
                <Box sx={{ textAlign: 'center', py: 6 }}>
                  <WorkspacePremium sx={{ fontSize: 64, color: 'rgba(255, 255, 255, 0.3)', mb: 2 }} />
                  <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.5)', mb: 1 }}>
                    No badges earned yet
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.3)' }}>
                    Complete special challenges to earn badges!
                  </Typography>
                </Box>
              </Grid>
            )}
          </Grid>
        </TabPanel>

        {/* Skills Tab */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            {Object.entries(skillRatings).map(([skill, rating]) => (
              <Grid item xs={12} md={6} key={skill}>
                <Card sx={{
                  background: 'rgba(76, 175, 80, 0.05)',
                  border: '1px solid rgba(76, 175, 80, 0.2)',
                  borderRadius: 2,
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    background: 'rgba(76, 175, 80, 0.1)',
                    borderColor: 'rgba(76, 175, 80, 0.4)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 16px rgba(76, 175, 80, 0.2)'
                  }
                }}>
                  <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography variant="h4">{getSkillIcon(skill)}</Typography>
                        <Box>
                          <Typography variant="subtitle1" sx={{ color: '#fff', fontWeight: 700, textTransform: 'capitalize' }}>
                            {skill.replace('_', ' ')}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                            {rating >= 80 ? 'Expert' : rating >= 60 ? 'Advanced' : rating >= 40 ? 'Intermediate' : 'Beginner'}
                          </Typography>
                        </Box>
                      </Box>
                      <Typography variant="h5" sx={{
                        color: rating >= 80 ? '#4caf50' : rating >= 60 ? '#ff9800' : '#f44336',
                        fontWeight: 700,
                        fontFamily: 'monospace'
                      }}>
                        {rating.toFixed(1)}%
                      </Typography>
                    </Box>
                    <Tooltip title={`${rating.toFixed(1)}% - ${rating >= 80 ? 'Expert' : rating >= 60 ? 'Advanced' : rating >= 40 ? 'Intermediate' : 'Beginner'}`} arrow>
                      <LinearProgress
                        variant="determinate"
                        value={rating}
                        sx={{
                          height: 10,
                          borderRadius: 5,
                          backgroundColor: 'rgba(255, 255, 255, 0.1)',
                          position: 'relative',
                          '& .MuiLinearProgress-bar': {
                            background: `linear-gradient(90deg, ${rating >= 80 ? '#4caf50' : rating >= 60 ? '#ff9800' : '#f44336'}, ${rating >= 80 ? '#66bb6a' : rating >= 60 ? '#ffb74d' : '#ef5350'})`,
                            borderRadius: 5,
                            transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                            boxShadow: `0 0 10px ${rating >= 80 ? 'rgba(76, 175, 80, 0.5)' : rating >= 60 ? 'rgba(255, 152, 0, 0.5)' : 'rgba(244, 67, 54, 0.5)'}`
                          }
                        }}
                      />
                    </Tooltip>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Progress Tab */}
        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{
                background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%)',
                border: '1px solid rgba(0, 212, 255, 0.3)',
                borderRadius: 2
              }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2, fontWeight: 700 }}>
                    XP Breakdown
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      Current Level XP
                    </Typography>
                    <Typography variant="h4" sx={{ color: '#00d4ff', fontWeight: 700, fontFamily: 'monospace' }}>
                      {xp.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      XP to Next Level
                    </Typography>
                    <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 700, fontFamily: 'monospace' }}>
                      {xpToNextLevel.toLocaleString()} / {nextLevelXP.toLocaleString()}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{
                background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)',
                border: '1px solid rgba(255, 152, 0, 0.3)',
                borderRadius: 2
              }}>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#ff9800', mb: 2, fontWeight: 700 }}>
                    Milestones
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: level >= 10 ? '#4caf50' : 'rgba(255, 255, 255, 0.1)' }}>
                          {level >= 10 ? <CheckCircle /> : <Lock />}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary="Level 10 - Trader"
                        secondary={level >= 10 ? 'Unlocked!' : 'Reach level 10'}
                        primaryTypographyProps={{ color: '#fff', fontWeight: 600 }}
                        secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.6)' }}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: level >= 20 ? '#2196f3' : 'rgba(255, 255, 255, 0.1)' }}>
                          {level >= 20 ? <CheckCircle /> : <Lock />}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary="Level 20 - Expert"
                        secondary={level >= 20 ? 'Unlocked!' : 'Reach level 20'}
                        primaryTypographyProps={{ color: '#fff', fontWeight: 600 }}
                        secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.6)' }}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: level >= 30 ? '#9c27b0' : 'rgba(255, 255, 255, 0.1)' }}>
                          {level >= 30 ? <CheckCircle /> : <Lock />}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary="Level 30 - Master"
                        secondary={level >= 30 ? 'Unlocked!' : 'Reach level 30'}
                        primaryTypographyProps={{ color: '#fff', fontWeight: 600 }}
                        secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.6)' }}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Leaderboard Tab */}
        <TabPanel value={tabValue} index={4}>
          {leaderboardLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
              <CircularProgress sx={{ color: '#00d4ff' }} />
            </Box>
          ) : leaderboard.length === 0 ? (
            <Box sx={{
              textAlign: 'center',
              py: 6,
              animation: 'fadeIn 0.5s ease-out',
              '@keyframes fadeIn': {
                from: { opacity: 0 },
                to: { opacity: 1 }
              }
            }}>
              <LeaderboardIcon sx={{
                fontSize: 64,
                color: 'rgba(255, 255, 255, 0.3)',
                mb: 2,
                animation: 'float 3s ease-in-out infinite',
                '@keyframes float': {
                  '0%, 100%': { transform: 'translateY(0px)' },
                  '50%': { transform: 'translateY(-10px)' }
                }
              }} />
              <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.5)', mb: 1, fontWeight: 600 }}>
                No leaderboard data available
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.3)' }}>
                Start trading to see your rank!
              </Typography>
            </Box>
          ) : (
            <TableContainer
              component={Paper}
              sx={{
                background: 'rgba(42, 42, 42, 0.5)',
                borderRadius: 2,
                border: '1px solid rgba(0, 212, 255, 0.2)'
              }}
            >
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: 'rgba(0, 212, 255, 0.05)' }}>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 700 }}>Rank</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 700 }}>Trader</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 700 }}>Level</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 700 }}>XP</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 700 }}>Trades</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 700 }}>Best Return</TableCell>
                    <TableCell sx={{ color: '#00d4ff', fontWeight: 700 }}>Streak</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {leaderboard.map((entry, index) => {
                    const isCurrentUser = entry.user_id === userId;
                    const rankColor = entry.rank === 1 ? '#ffd700' : entry.rank === 2 ? '#c0c0c0' : entry.rank === 3 ? '#cd7f32' : '#00d4ff';
                    
                    return (
                      <TableRow
                        key={entry.user_id}
                        sx={{
                          backgroundColor: isCurrentUser ? 'rgba(0, 212, 255, 0.1)' : 'transparent',
                          borderLeft: isCurrentUser ? '3px solid #00d4ff' : 'none',
                          transition: 'all 0.2s ease',
                          animation: `fadeInRow 0.4s ease-out ${index * 0.05}s both`,
                          '@keyframes fadeInRow': {
                            from: {
                              opacity: 0,
                              transform: 'translateX(-20px)'
                            },
                            to: {
                              opacity: 1,
                              transform: 'translateX(0)'
                            }
                          },
                          '&:hover': {
                            backgroundColor: isCurrentUser ? 'rgba(0, 212, 255, 0.15)' : 'rgba(0, 212, 255, 0.05)',
                            transform: 'scale(1.01)'
                          }
                        }}
                      >
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {entry.rank <= 3 && (
                              <Medal sx={{ color: rankColor, fontSize: 20 }} />
                            )}
                            <Typography
                              sx={{
                                color: rankColor,
                                fontWeight: 700,
                                fontFamily: 'monospace',
                                fontSize: '1.1rem'
                              }}
                            >
                              #{entry.rank}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <Avatar
                              sx={{
                                bgcolor: isCurrentUser ? '#00d4ff' : getLevelColor(entry.level),
                                width: 36,
                                height: 36,
                                fontSize: '0.9rem',
                                fontWeight: 700
                              }}
                            >
                              {entry.username.charAt(0).toUpperCase()}
                            </Avatar>
                            <Box>
                              <Typography
                                sx={{
                                  color: '#fff',
                                  fontWeight: isCurrentUser ? 700 : 600,
                                  fontSize: '0.95rem'
                                }}
                              >
                                {entry.username}
                                {isCurrentUser && (
                                  <Chip
                                    label="You"
                                    size="small"
                                    sx={{
                                      ml: 1,
                                      height: 18,
                                      fontSize: '0.65rem',
                                      bgcolor: '#00d4ff',
                                      color: '#000',
                                      fontWeight: 700
                                    }}
                                  />
                                )}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={entry.level}
                            size="small"
                            sx={{
                              bgcolor: getLevelColor(entry.level),
                              color: '#fff',
                              fontWeight: 700,
                              fontFamily: 'monospace'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography sx={{ color: '#fff', fontWeight: 600, fontFamily: 'monospace' }}>
                            {entry.xp_points.toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography sx={{ color: 'rgba(255, 255, 255, 0.8)', fontFamily: 'monospace' }}>
                            {entry.total_trades}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography
                            sx={{
                              color: entry.best_daily_return >= 0 ? '#4caf50' : '#f44336',
                              fontWeight: 600,
                              fontFamily: 'monospace'
                            }}
                          >
                            {entry.best_daily_return >= 0 ? '+' : ''}
                            {entry.best_daily_return.toFixed(2)}%
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Whatshot sx={{ color: '#ff9800', fontSize: 18 }} />
                            <Typography sx={{ color: '#ff9800', fontWeight: 600, fontFamily: 'monospace' }}>
                              {entry.trading_streak}
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </TabPanel>
      </Card>

      {/* Achievement Detail Dialog */}
      <Dialog
        open={achievementDialogOpen}
        onClose={() => setAchievementDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(26, 26, 46, 0.95)',
            border: '1px solid rgba(255, 152, 0, 0.3)',
            borderRadius: 2
          }
        }}
      >
        {selectedAchievement && (
          <>
            <DialogTitle sx={{ color: '#ff9800', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="h2">{selectedAchievement.icon}</Typography>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    {selectedAchievement.name}
                  </Typography>
                  {selectedAchievement.rarity && (
                    <Chip
                      label={selectedAchievement.rarity}
                      size="small"
                      sx={{
                        bgcolor: getRarityColor(selectedAchievement.rarity),
                        color: '#fff',
                        fontWeight: 600,
                        mt: 0.5
                      }}
                    />
                  )}
                </Box>
              </Box>
              <IconButton onClick={() => setAchievementDialogOpen(false)} sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                <Close />
              </IconButton>
            </DialogTitle>
            <DialogContent>
              <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.9)', mb: 2 }}>
                {selectedAchievement.description}
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip
                  icon={<Star />}
                  label={`+${selectedAchievement.points} XP`}
                  sx={{
                    bgcolor: 'rgba(255, 152, 0, 0.2)',
                    color: '#ff9800',
                    fontWeight: 700
                  }}
                />
                {selectedAchievement.earned_at && (
                  <Chip
                    label={`Earned: ${new Date(selectedAchievement.earned_at).toLocaleDateString()}`}
                    sx={{
                      bgcolor: 'rgba(76, 175, 80, 0.2)',
                      color: '#4caf50',
                      fontWeight: 600
                    }}
                  />
                )}
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setAchievementDialogOpen(false)} sx={{ color: '#aaa' }}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default GamificationDashboard;

