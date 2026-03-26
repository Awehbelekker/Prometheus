import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Chip,
  Collapse,
  IconButton,
  Tooltip,
  alpha
} from '@mui/material';
import DashboardStyleSelector from './DashboardStyleSelector';
import ThemeSystem from './ThemeSystem';
import PrometheusLogo from './PrometheusLogo';
import {
  Dashboard,
  TrendingUp,
  Psychology,
  Analytics,
  Settings,
  AdminPanelSettings,
  ViewInAr,
  Timeline,
  AccountBalance,
  Security,
  People,
  Email,
  Notifications,
  ExpandLess,
  ExpandMore,
  MenuOpen,
  Menu as MenuIcon
} from '@mui/icons-material';

/**
 * 🎯 CLEAN NAVIGATION SYSTEM
 * 
 * FEATURES:
 * - Single, unified sidebar
 * - Tier-based menu items
 * - Clean, modern design
 * - Collapsible sections
 * - No duplication
 * - Intuitive grouping
 */

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ElementType;
  tier: string[];
  badge?: string;
  children?: NavigationItem[];
}

interface CleanNavigationProps {
  selectedItem: string;
  onItemSelect: (itemId: string) => void;
  userTier: 'demo' | 'premium' | 'admin';
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  selectedHeader?: string;
  onHeaderChange?: (headerId: string) => void;
  selectedTheme?: string;
  onThemeChange?: (themeId: string) => void;
}

const CleanNavigation: React.FC<CleanNavigationProps> = ({
  selectedItem,
  onItemSelect,
  userTier,
  collapsed = false,
  onToggleCollapse,
  selectedHeader = 'command-center',
  onHeaderChange,
  selectedTheme = 'dark',
  onThemeChange
}) => {
  const [expandedSections, setExpandedSections] = useState<string[]>(['core', 'trading']);

  const navigationItems: NavigationItem[] = [
    // Core Section
    {
      id: 'core',
      label: 'Core',
      icon: Dashboard,
      tier: ['demo', 'premium', 'admin'],
      children: [
        {
          id: 'dashboard',
          label: 'Dashboard',
          icon: Dashboard,
          tier: ['demo', 'premium', 'admin']
        },
        {
          id: 'analytics',
          label: 'Analytics',
          icon: Analytics,
          tier: ['demo', 'premium', 'admin']
        },
        {
          id: 'notifications',
          label: 'Notifications',
          icon: Notifications,
          tier: ['demo', 'premium', 'admin']
        }
      ]
    },
    
    // Trading Section
    {
      id: 'trading',
      label: 'Trading',
      icon: TrendingUp,
      tier: ['demo', 'premium', 'admin'],
      children: [
        {
          id: 'paper-trading',
          label: 'Paper Trading',
          icon: TrendingUp,
          tier: ['demo', 'premium', 'admin'],
          badge: 'DEMO'
        },
        {
          id: 'live-trading',
          label: 'Live Trading',
          icon: AccountBalance,
          tier: ['premium', 'admin'],
          badge: 'LIVE'
        },
        {
          id: 'portfolio',
          label: 'Portfolio',
          icon: Timeline,
          tier: ['demo', 'premium', 'admin']
        }
      ]
    },
    
    // AI & Advanced Section
    {
      id: 'ai-advanced',
      label: 'AI & Advanced',
      icon: Psychology,
      tier: ['premium', 'admin'],
      children: [
        {
          id: 'ai-agents',
          label: 'AI Agents',
          icon: Psychology,
          tier: ['premium', 'admin'],
          badge: 'AI'
        },
        {
          id: 'holographic-ui',
          label: 'Holographic UI',
          icon: ViewInAr,
          tier: ['premium', 'admin'],
          badge: 'REV'
        },
        {
          id: 'quantum-trading',
          label: 'Quantum Trading',
          icon: Timeline,
          tier: ['premium', 'admin'],
          badge: 'QUANTUM'
        }
      ]
    },
    
    // Admin Section
    {
      id: 'admin',
      label: 'Administration',
      icon: AdminPanelSettings,
      tier: ['admin'],
      children: [
        {
          id: 'access-requests',
          label: 'Access Requests',
          icon: Notifications,
          tier: ['admin']
        },
        {
          id: 'user-management',
          label: 'User Management',
          icon: People,
          tier: ['admin']
        },
        {
          id: 'performance-review',
          label: 'Performance Review',
          icon: Analytics,
          tier: ['admin'],
          badge: 'ADMIN ONLY'
        },
        {
          id: 'system-health',
          label: 'System Health',
          icon: Security,
          tier: ['admin']
        },
        {
          id: 'admin-settings',
          label: 'Admin Settings',
          icon: Settings,
          tier: ['admin']
        }
      ]
    },
    
    // Settings Section
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      tier: ['demo', 'premium', 'admin'],
      children: [
        {
          id: 'dashboard-style',
          label: 'Dashboard Style',
          icon: ViewInAr,
          tier: ['demo', 'premium', 'admin']
        },
        {
          id: 'theme-settings',
          label: 'Theme Settings',
          icon: Settings,
          tier: ['demo', 'premium', 'admin']
        },
        {
          id: 'profile',
          label: 'Profile',
          icon: Settings,
          tier: ['demo', 'premium', 'admin']
        },
        {
          id: 'preferences',
          label: 'Preferences',
          icon: Settings,
          tier: ['demo', 'premium', 'admin']
        }
      ]
    }
  ];

  // Filter items based on user tier
  const visibleItems = navigationItems.filter(item => 
    item.tier.includes(userTier)
  ).map(item => ({
    ...item,
    children: item.children?.filter(child => child.tier.includes(userTier))
  }));

  const handleSectionToggle = (sectionId: string) => {
    setExpandedSections(prev => 
      prev.includes(sectionId) 
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const getBadgeColor = (badge: string) => {
    switch (badge) {
      case 'DEMO': return '#ff9800';
      case 'LIVE': return '#4caf50';
      case 'AI': return '#9c27b0';
      case 'REV': return '#00d4ff';
      case 'QUANTUM': return '#e91e63';
      default: return '#757575';
    }
  };

  const drawerWidth = collapsed ? 64 : 300;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: '#0f0f1a',
          borderRight: '2px solid rgba(0, 212, 255, 0.3)',
          transition: 'width 0.3s ease',
          background: 'linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%)',
          boxShadow: '4px 0 20px rgba(0, 0, 0, 0.5)'
        },
      }}
    >
      {/* Header with Logo */}
      <Box sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: collapsed ? 'center' : 'space-between',
        p: collapsed ? 1 : 2,
        borderBottom: '2px solid rgba(0, 212, 255, 0.3)',
        background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(156, 39, 176, 0.1) 100%)',
        backdropFilter: 'blur(10px)'
      }}>
        {!collapsed && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'pulse 3s infinite'
            }}>
              <Typography variant="h6" sx={{
                color: 'white',
                fontWeight: 900,
                fontSize: '1.2rem'
              }}>
                🚀
              </Typography>
            </Box>
            <Box>
              <Typography variant="h6" sx={{
                fontWeight: 800,
                fontSize: '1.1rem',
                color: 'white',
                letterSpacing: '0.5px'
              }}>
                TRADING COCKPIT
              </Typography>
              <Typography variant="caption" sx={{
                color: '#aaa',
                fontSize: '0.7rem',
                letterSpacing: '1px'
              }}>
                MISSION CONTROL
              </Typography>
            </Box>
          </Box>
        )}
        {collapsed && (
          <Box sx={{
            width: 32,
            height: 32,
            borderRadius: 2,
            background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            animation: 'pulse 3s infinite'
          }}>
            <Typography variant="body1" sx={{
              color: 'white',
              fontWeight: 900
            }}>
              🚀
            </Typography>
          </Box>
        )}
        <Tooltip title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}>
          <IconButton
            onClick={onToggleCollapse}
            sx={{
              color: '#00d4ff',
              '&:hover': {
                backgroundColor: alpha('#00d4ff', 0.1),
                transform: 'scale(1.1)'
              },
              transition: 'all 0.3s ease'
            }}
          >
            {collapsed ? <MenuIcon /> : <MenuOpen />}
          </IconButton>
        </Tooltip>
      </Box>

      {/* Navigation List */}
      <List sx={{ flex: 1, py: 1 }}>
        {visibleItems.map((section) => (
          <Box key={section.id}>
            {/* Section Header */}
            <ListItem disablePadding component="li">
              <ListItemButton
                onClick={() => handleSectionToggle(section.id)}
                sx={{
                  minHeight: 48,
                  px: 2,
                  color: '#aaa',
                  '&:hover': {
                    backgroundColor: alpha('#00d4ff', 0.1),
                    color: '#00d4ff'
                  }
                }}
                aria-expanded={expandedSections.includes(section.id)}
                aria-controls={expandedSections.includes(section.id) ? `section-${section.id}` : undefined}
              >
                <ListItemIcon sx={{ 
                  minWidth: collapsed ? 0 : 40,
                  color: 'inherit',
                  justifyContent: 'center'
                }}>
                  <section.icon />
                </ListItemIcon>
                {!collapsed && (
                  <>
                    <ListItemText 
                      primary={section.label}
                      primaryTypographyProps={{
                        fontSize: '0.9rem',
                        fontWeight: 600
                      }}
                    />
                    {expandedSections.includes(section.id) ? <ExpandLess /> : <ExpandMore />}
                  </>
                )}
              </ListItemButton>
            </ListItem>

            {/* Section Items */}
            {!collapsed && (
              <Collapse in={expandedSections.includes(section.id)} timeout="auto" unmountOnExit>
                <List component="ul" disablePadding id={`section-${section.id}`}>
                  {section.children?.map((item) => (
                    <ListItem key={item.id} disablePadding component="li">
                      <ListItemButton
                        selected={selectedItem === item.id}
                        onClick={() => onItemSelect(item.id)}
                        sx={{
                          pl: 4,
                          minHeight: 40,
                          color: selectedItem === item.id ? '#00d4ff' : '#ccc',
                          backgroundColor: selectedItem === item.id ? alpha('#00d4ff', 0.1) : 'transparent',
                          '&:hover': {
                            backgroundColor: alpha('#00d4ff', 0.1),
                            color: '#00d4ff'
                          },
                          '&.Mui-selected': {
                            backgroundColor: alpha('#00d4ff', 0.2),
                            '&:hover': {
                              backgroundColor: alpha('#00d4ff', 0.3)
                            }
                          }
                        }}
                      >
                        <ListItemIcon sx={{ 
                          minWidth: 36,
                          color: 'inherit'
                        }}>
                          <item.icon fontSize="small" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={item.label}
                          primaryTypographyProps={{
                            fontSize: '0.85rem'
                          }}
                        />
                        {item.badge && (
                          <Chip
                            label={item.badge}
                            size="small"
                            sx={{
                              height: 18,
                              fontSize: '0.7rem',
                              backgroundColor: getBadgeColor(item.badge),
                              color: 'white'
                            }}
                          />
                        )}
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </Collapse>
            )}
            
            {/* Divider between sections */}
            {section.id !== visibleItems[visibleItems.length - 1].id && (
              <Divider sx={{ 
                my: 1, 
                borderColor: alpha('#00d4ff', 0.1) 
              }} />
            )}
          </Box>
        ))}
      </List>

      {/* Footer */}
      {!collapsed && (
        <Box sx={{
          p: 2,
          borderTop: '2px solid rgba(0, 212, 255, 0.3)',
          background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(156, 39, 176, 0.05) 100%)',
          backdropFilter: 'blur(10px)'
        }}>
          <Typography variant="caption" sx={{ color: '#aaa', display: 'block', mb: 1 }}>
            Current Tier:
          </Typography>
          <Chip
            label={userTier.toUpperCase()}
            size="small"
            sx={{
              backgroundColor: userTier === 'admin' ? '#f44336' : userTier === 'premium' ? '#9c27b0' : '#ff9800',
              color: 'white',
              fontWeight: 600,
              border: `1px solid ${userTier === 'admin' ? '#f44336' : userTier === 'premium' ? '#9c27b0' : '#ff9800'}`
            }}
          />

          {!collapsed && (
            <Typography variant="caption" sx={{
              color: '#666',
              display: 'block',
              mt: 2,
              textAlign: 'center',
              fontSize: '0.7rem'
            }}>
              Prometheus with NeuroForge™
            </Typography>
          )}
        </Box>
      )}

      {/* CSS Animations */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>
    </Drawer>
  );
};

export default CleanNavigation;
