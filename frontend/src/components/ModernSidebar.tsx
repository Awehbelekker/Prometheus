import React, { useState } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Chip,
  Divider,
  IconButton,
  Collapse,
  useTheme,
  alpha,
  Tooltip,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Button
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  PlayArrow as PlayIcon,
  Group as AgentsIcon,
  Add as AddIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  TrendingUp as TrendingUpIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Insights as InsightsIcon,
  SmartToy as SmartToyIcon,
  AccountBalance as AccountBalanceIcon,
  CompareArrows as CompareArrowsIcon,
  DataUsage as DataUsageIcon,
  School as SchoolIcon,
  Business as BusinessIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  ExpandLess,
  ExpandMore,
  Rocket as RocketIcon,
  ShowChart as ShowChartIcon,
  People as PeopleIcon,
  AccountCircle,
  ExitToApp,
  Person,
  Shield,
  Settings
} from '@mui/icons-material';

interface SidebarProps {
  selectedItem: string;
  setSelectedItem: (item: string) => void;
  currentUser?: any;
  onLogout?: () => void;
}

interface MenuCategory {
  id: string;
  label: string;
  icon: React.ElementType;
  items: MenuItem[];
  defaultOpen?: boolean;
}

interface MenuItem {
  id: string;
  label: string;
  icon: React.ElementType;
  badge?: string;
  isAdmin?: boolean;
  isTrader?: boolean;
  color?: string;
}

const ModernSidebar: React.FC<SidebarProps> = ({ 
  selectedItem, 
  setSelectedItem, 
  currentUser,
  onLogout 
}) => {
  const theme = useTheme();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [openCategories, setOpenCategories] = useState<{ [key: string]: boolean }>({
    'core': true,
    'revolutionary': false,
    'admin': true,
    'standard': false
  });
  const [profileMenuAnchor, setProfileMenuAnchor] = useState<null | HTMLElement>(null);

  // Organized menu categories
  const menuCategories: MenuCategory[] = [
    {
      id: 'core',
      label: 'Core Features',
      icon: DashboardIcon,
      defaultOpen: true,
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: DashboardIcon },
        { id: 'live-trading', label: 'Live Trading', icon: ShowChartIcon, badge: 'LIVE', color: '#4caf50' },
        { id: 'analytics', label: 'Analytics', icon: AnalyticsIcon }
      ]
    },
    {
      id: 'admin',
      label: 'Administration',
      icon: RocketIcon,
      defaultOpen: true,
      items: [
        { id: 'admin', label: 'Admin Cockpit', icon: RocketIcon, badge: 'ADMIN', isAdmin: true, color: '#ff6b35' },
        { id: 'user-invitations', label: 'User Invitations', icon: PeopleIcon, badge: 'ADMIN', isAdmin: true },
        { id: 'user-management', label: 'User Management', icon: AgentsIcon, isAdmin: true }
      ]
    },
    {
      id: 'revolutionary',
      label: 'Revolutionary AI',
      icon: AutoAwesomeIcon,
      items: [
        { id: 'ai-personas', label: 'AI Personas', icon: PsychologyIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'quantum-neural', label: 'Quantum Neural', icon: SmartToyIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'holographic-ui', label: 'Holographic UI', icon: AutoAwesomeIcon, badge: 'ENHANCED', color: '#00d4ff' },
        { id: 'social-trading', label: 'Social Trading', icon: TrendingUpIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'market-oracle', label: 'Market Oracle', icon: InsightsIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'risk-guardian', label: 'Risk Guardian', icon: SecurityIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'speed-optimizer', label: 'Speed Optimizer', icon: SpeedIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'portfolio-architect', label: 'Portfolio Architect', icon: AccountBalanceIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'sentiment-analyzer', label: 'Sentiment Analyzer', icon: PsychologyIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'arbitrage-hunter', label: 'Arbitrage Hunter', icon: CompareArrowsIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'data-compressor', label: 'Data Compressor', icon: DataUsageIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'continuous-learning', label: 'Continuous Learning', icon: SchoolIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' },
        { id: 'enterprise-trading-trust', label: 'Enterprise Trust', icon: BusinessIcon, badge: 'REVOLUTIONARY', color: '#9c27b0' }
      ]
    },
    {
      id: 'standard',
      label: 'Tools & Settings',
      icon: SettingsIcon,
      items: [
        { id: 'marketplace', label: 'Marketplace', icon: AddIcon },
        { id: 'orchestrator', label: 'Orchestrator', icon: PlayIcon },
        { id: 'settings', label: 'Settings', icon: SettingsIcon },
        { id: 'notifications', label: 'Notifications', icon: NotificationsIcon }
      ]
    }
  ];

  const handleCategoryToggle = (categoryId: string) => {
    setOpenCategories(prev => ({
      ...prev,
      [categoryId]: !prev[categoryId]
    }));
  };

  const handleItemClick = (itemId: string) => {
    setSelectedItem(itemId);
  };

  const handleProfileClick = (event: React.MouseEvent<HTMLElement>) => {
    setProfileMenuAnchor(event.currentTarget);
  };

  const handleProfileClose = () => {
    setProfileMenuAnchor(null);
  };

  const handleLogout = () => {
    handleProfileClose();

    // Clear all authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    sessionStorage.clear();

    // Call the logout function if provided
    if (onLogout) {
      onLogout();
    }

    // Force redirect to login page
    window.location.href = '/';
  };

  const sidebarWidth = isCollapsed ? 80 : 280;

  return (
    <Box
      sx={{
        width: sidebarWidth,
        height: '100vh',
        backgroundColor: '#1a1a1a',
        borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.3s ease-in-out',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Header with Toggle and Profile */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          minHeight: 64
        }}
      >
        {!isCollapsed && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <RocketIcon sx={{ color: '#00d4ff', fontSize: 28 }} />
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontSize: '1.1rem'
              }}
            >
              PROMETHEUS
            </Typography>
          </Box>
        )}
        
        <IconButton
          onClick={() => setIsCollapsed(!isCollapsed)}
          sx={{
            color: '#00d4ff',
            '&:hover': { backgroundColor: alpha('#00d4ff', 0.1) }
          }}
        >
          {isCollapsed ? <MenuIcon /> : <ChevronLeftIcon />}
        </IconButton>
      </Box>

      {/* User Profile Section */}
      {currentUser && (
        <Box
          sx={{
            p: isCollapsed ? 1 : 2,
            borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: isCollapsed ? 0 : 2,
              cursor: 'pointer',
              p: 1,
              borderRadius: 2,
              '&:hover': { backgroundColor: alpha('#00d4ff', 0.05) },
              justifyContent: isCollapsed ? 'center' : 'flex-start'
            }}
            onClick={handleProfileClick}
          >
            <Avatar
              sx={{
                width: isCollapsed ? 32 : 40,
                height: isCollapsed ? 32 : 40,
                backgroundColor: '#00d4ff',
                fontSize: isCollapsed ? '1rem' : '1.2rem'
              }}
            >
              {currentUser.name?.charAt(0) || 'U'}
            </Avatar>
            
            {!isCollapsed && (
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    color: '#ffffff',
                    fontWeight: 600,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {currentUser.name || 'User'}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    color: '#b0b0b0',
                    textTransform: 'uppercase',
                    fontWeight: 500
                  }}
                >
                  {currentUser.role || 'User'}
                </Typography>
              </Box>
            )}
          </Box>

          {/* Profile Menu */}
          <Menu
            anchorEl={profileMenuAnchor}
            open={Boolean(profileMenuAnchor)}
            onClose={handleProfileClose}
            PaperProps={{
              sx: {
                backgroundColor: '#2a2a2a',
                border: `1px solid ${alpha('#00d4ff', 0.2)}`,
                minWidth: 200
              }
            }}
          >
            <MenuItem onClick={handleProfileClose} sx={{ color: '#ffffff' }}>
              <Person sx={{ mr: 2, color: '#00d4ff' }} />
              Profile
            </MenuItem>
            <MenuItem onClick={handleProfileClose} sx={{ color: '#ffffff' }}>
              <Settings sx={{ mr: 2, color: '#00d4ff' }} />
              Settings
            </MenuItem>
            <MenuItem onClick={handleProfileClose} sx={{ color: '#ffffff' }}>
              <Shield sx={{ mr: 2, color: '#00d4ff' }} />
              Security
            </MenuItem>
            <Divider sx={{ backgroundColor: alpha('#ffffff', 0.1) }} />
            <MenuItem onClick={handleLogout} sx={{ color: '#ff6b35' }}>
              <ExitToApp sx={{ mr: 2 }} />
              Logout
            </MenuItem>
          </Menu>
        </Box>
      )}

      {/* Navigation Menu */}
      <Box sx={{ flex: 1, overflow: 'auto', py: 1 }}>
        {menuCategories.map((category) => {
          const filteredItems = category.items.filter(item => {
            if (item.isAdmin && currentUser?.role !== 'admin') return false;
            if (item.isTrader && currentUser?.role !== 'trader' && currentUser?.role !== 'admin') return false;
            return true;
          });

          if (filteredItems.length === 0) return null;

          return (
            <Box key={category.id} sx={{ mb: 1 }}>
              {/* Category Header */}
              <ListItemButton
                onClick={() => handleCategoryToggle(category.id)}
                sx={{
                  px: isCollapsed ? 1 : 2,
                  py: 1,
                  minHeight: 48,
                  justifyContent: isCollapsed ? 'center' : 'flex-start',
                  '&:hover': { backgroundColor: alpha('#00d4ff', 0.05) }
                }}
              >
                <ListItemIcon sx={{ minWidth: isCollapsed ? 'auto' : 40, color: '#b0b0b0' }}>
                  <category.icon />
                </ListItemIcon>
                {!isCollapsed && (
                  <>
                    <ListItemText
                      primary={category.label}
                      primaryTypographyProps={{
                        fontSize: '0.875rem',
                        fontWeight: 600,
                        color: '#b0b0b0',
                        textTransform: 'uppercase'
                      }}
                    />
                    {openCategories[category.id] ? <ExpandLess /> : <ExpandMore />}
                  </>
                )}
              </ListItemButton>

              {/* Category Items */}
              <Collapse in={!isCollapsed && openCategories[category.id]} timeout="auto">
                <List disablePadding>
                  {filteredItems.map((item) => (
                    <Tooltip
                      key={item.id}
                      title={isCollapsed ? item.label : ''}
                      placement="right"
                      arrow
                    >
                      <ListItemButton
                        selected={selectedItem === item.id}
                        onClick={() => handleItemClick(item.id)}
                        sx={{
                          pl: isCollapsed ? 2 : 4,
                          pr: 2,
                          py: 1,
                          minHeight: 44,
                          borderRadius: isCollapsed ? 0 : '0 24px 24px 0',
                          mr: isCollapsed ? 0 : 1,
                          '&.Mui-selected': {
                            backgroundColor: alpha('#00d4ff', 0.1),
                            borderRight: isCollapsed ? 'none' : '3px solid #00d4ff',
                            '&:hover': {
                              backgroundColor: alpha('#00d4ff', 0.15),
                            },
                          },
                          '&:hover': {
                            backgroundColor: alpha('#ffffff', 0.05),
                          },
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: isCollapsed ? 'auto' : 40, color: selectedItem === item.id ? '#00d4ff' : '#ffffff' }}>
                          <item.icon />
                        </ListItemIcon>
                        {!isCollapsed && (
                          <>
                            <ListItemText
                              primary={item.label}
                              primaryTypographyProps={{
                                fontSize: '0.9rem',
                                fontWeight: selectedItem === item.id ? 600 : 400,
                                color: selectedItem === item.id ? '#00d4ff' : '#ffffff'
                              }}
                            />
                            {item.badge && (
                              <Chip
                                label={item.badge}
                                size="small"
                                sx={{
                                  height: 20,
                                  fontSize: '0.7rem',
                                  fontWeight: 600,
                                  backgroundColor: item.color || '#ff6b35',
                                  color: '#ffffff',
                                  '& .MuiChip-label': { px: 1 }
                                }}
                              />
                            )}
                          </>
                        )}
                      </ListItemButton>
                    </Tooltip>
                  ))}
                </List>
              </Collapse>

              {/* Show items as icons when collapsed */}
              {isCollapsed && (
                <List disablePadding>
                  {filteredItems.map((item) => (
                    <Tooltip
                      key={item.id}
                      title={item.label}
                      placement="right"
                      arrow
                    >
                      <ListItemButton
                        selected={selectedItem === item.id}
                        onClick={() => handleItemClick(item.id)}
                        sx={{
                          px: 2,
                          py: 1,
                          minHeight: 44,
                          justifyContent: 'center',
                          '&.Mui-selected': {
                            backgroundColor: alpha('#00d4ff', 0.2),
                            '&:hover': {
                              backgroundColor: alpha('#00d4ff', 0.25),
                            },
                          },
                          '&:hover': {
                            backgroundColor: alpha('#ffffff', 0.05),
                          },
                        }}
                      >
                        <Badge
                          badgeContent={item.badge ? '●' : 0}
                          color="error"
                          sx={{
                            '& .MuiBadge-badge': {
                              backgroundColor: item.color || '#ff6b35',
                              width: 8,
                              height: 8,
                              minWidth: 8,
                              fontSize: '0.6rem'
                            }
                          }}
                        >
                          <item.icon sx={{ color: selectedItem === item.id ? '#00d4ff' : '#ffffff' }} />
                        </Badge>
                      </ListItemButton>
                    </Tooltip>
                  ))}
                </List>
              )}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

export default ModernSidebar;
