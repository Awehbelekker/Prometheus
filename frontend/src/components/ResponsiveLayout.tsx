import React, { useState, useEffect } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  useTheme,
  useMediaQuery,
  Fade,
  Slide,
  Fab,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Chip,
  Alert,
  Collapse
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Analytics,
  People,
  Settings,
  Notifications,
  AccountCircle,
  Close,
  KeyboardArrowUp,
  KeyboardArrowDown,
  Search,
  FilterList,
  ViewList,
  ViewModule,
  Fullscreen,
  FullscreenExit
} from '@mui/icons-material';
import './ResponsiveLayout.css';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  title?: string;
  showNotifications?: boolean;
  showSearch?: boolean;
  showFilters?: boolean;
  viewMode?: 'list' | 'grid';
  onViewModeChange?: (mode: 'list' | 'grid') => void;
}

const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({
  children,
  title = 'MASS Framework',
  showNotifications = true,
  showSearch = true,
  showFilters = true,
  viewMode = 'grid',
  onViewModeChange
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'));
  
  const [drawerOpen, setDrawerOpen] = useState(!isMobile);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [currentViewMode, setCurrentViewMode] = useState(viewMode);

  // Handle scroll for scroll-to-top button
  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Handle drawer state based on screen size
  useEffect(() => {
    setDrawerOpen(!isMobile);
  }, [isMobile]);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleViewModeChange = (mode: 'list' | 'grid') => {
    setCurrentViewMode(mode);
    onViewModeChange?.(mode);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const navigationItems = [
    { text: 'Dashboard', icon: <Dashboard />, active: true },
    { text: 'Analytics', icon: <Analytics />, active: false },
    { text: 'Users', icon: <People />, active: false },
    { text: 'Settings', icon: <Settings />, active: false }
  ];

  const notifications = [
    { id: 1, message: 'System update completed successfully', time: '2 min ago', type: 'success' },
    { id: 2, message: 'New user registration detected', time: '5 min ago', type: 'info' },
    { id: 3, message: 'Performance alert: High CPU usage', time: '10 min ago', type: 'warning' }
  ];

  const renderMobileAppBar = () => (
    <AppBar 
      position="fixed" 
      className="app-bar-gradient"
      sx={{ zIndex: theme.zIndex.drawer + 1 }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton
            color="inherit"
            onClick={handleDrawerToggle}
            sx={{ mr: 1 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {showSearch && (
            <IconButton color="inherit" onClick={() => setSearchOpen(!searchOpen)}>
              <Search />
            </IconButton>
          )}
          {showFilters && (
            <IconButton color="inherit" onClick={() => setFiltersOpen(!filtersOpen)}>
              <FilterList />
            </IconButton>
          )}
          {onViewModeChange && (
            <IconButton 
              color="inherit" 
              onClick={() => handleViewModeChange(currentViewMode === 'grid' ? 'list' : 'grid')}
            >
              {currentViewMode === 'grid' ? <ViewList /> : <ViewModule />}
            </IconButton>
          )}
          {showNotifications && (
            <IconButton color="inherit" onClick={() => setNotificationsOpen(!notificationsOpen)}>
              <Badge badgeContent={notifications.length} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          )}
          <IconButton color="inherit" onClick={() => setUserMenuOpen(true)}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
              <AccountCircle />
            </Avatar>
          </IconButton>
        </Box>
      </Toolbar>
      
      {/* Mobile Search Bar */}
      <Collapse in={searchOpen}>
        <Box sx={{ p: 2, backgroundColor: 'rgba(255,255,255,0.05)' }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            backgroundColor: 'rgba(255,255,255,0.1)',
            borderRadius: 2,
            px: 2,
            py: 1
          }}>
            <Search sx={{ mr: 1, color: 'rgba(255,255,255,0.7)' }} />
            <input
              type="text"
              placeholder="Search..."
              className="search-input"
            />
          </Box>
        </Box>
      </Collapse>

      {/* Mobile Filters */}
      <Collapse in={filtersOpen}>
        <Box sx={{ p: 2, backgroundColor: 'rgba(255,255,255,0.05)' }}>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {['All', 'Active', 'Inactive', 'Recent'].map((filter) => (
              <Chip
                key={filter}
                label={filter}
                size="small"
                sx={{
                  backgroundColor: filter === 'All' ? 'primary.main' : 'rgba(255,255,255,0.1)',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: filter === 'All' ? 'primary.dark' : 'rgba(255,255,255,0.2)',
                  }
                }}
              />
            ))}
          </Box>
        </Box>
      </Collapse>
    </AppBar>
  );

  const renderDesktopAppBar = () => (
    <AppBar 
      position="fixed" 
      className="app-bar-gradient"
      sx={{ zIndex: theme.zIndex.drawer + 1 }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {showSearch && (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              backgroundColor: 'rgba(255,255,255,0.1)',
              borderRadius: 2,
              px: 2,
              py: 1,
              minWidth: 300
            }}>
              <Search sx={{ mr: 1, color: 'rgba(255,255,255,0.7)' }} />
              <input
                type="text"
                placeholder="Search..."
                className="search-input"
              />
            </Box>
          )}
          
          {onViewModeChange && (
            <Box sx={{ display: 'flex', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 1 }}>
              <IconButton 
                size="small"
                onClick={() => handleViewModeChange('grid')}
                sx={{ 
                  color: currentViewMode === 'grid' ? 'primary.main' : 'rgba(255,255,255,0.7)',
                  backgroundColor: currentViewMode === 'grid' ? 'rgba(99, 102, 241, 0.2)' : 'transparent'
                }}
              >
                <ViewModule />
              </IconButton>
              <IconButton 
                size="small"
                onClick={() => handleViewModeChange('list')}
                sx={{ 
                  color: currentViewMode === 'list' ? 'primary.main' : 'rgba(255,255,255,0.7)',
                  backgroundColor: currentViewMode === 'list' ? 'rgba(99, 102, 241, 0.2)' : 'transparent'
                }}
              >
                <ViewList />
              </IconButton>
            </Box>
          )}
          
          {showNotifications && (
            <IconButton color="inherit" onClick={() => setNotificationsOpen(!notificationsOpen)}>
              <Badge badgeContent={notifications.length} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          )}
          
          <IconButton color="inherit" onClick={() => setUserMenuOpen(true)}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
              <AccountCircle />
            </Avatar>
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );

  const renderDrawer = () => (
    <Drawer
      variant={isMobile ? 'temporary' : 'persistent'}
      open={drawerOpen}
      onClose={handleDrawerToggle}
      className="drawer-gradient"
      sx={{
        width: isMobile ? 280 : 240,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: isMobile ? 280 : 240,
          boxSizing: 'border-box',
          background: 'linear-gradient(180deg, #1e1e2e 0%, #2d2d44 100%)',
          borderRight: '1px solid rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)'
        }
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto', p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: 'white' }}>
          Navigation
        </Typography>
        <List>
          {navigationItems.map((item, index) => (
            <ListItem key={index} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                className={`navigation-item ${item.active ? 'active' : ''}`}
              >
                <ListItemIcon className={`navigation-icon ${item.active ? 'active' : ''}`}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text} 
                  className={`navigation-text ${item.active ? 'active' : ''}`}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        
        <Divider className="divider-custom" sx={{ my: 2, borderColor: 'rgba(255,255,255,0.1)' }} />
        
        <Typography className="subtitle-custom" variant="subtitle2" sx={{ mb: 1, color: 'rgba(255,255,255,0.7)' }}>
          Quick Actions
        </Typography>
        <List>
          {['Create Project', 'Import Data', 'Export Report', 'System Settings'].map((action, index) => (
            <ListItem key={index} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton className="quick-action-item">
                <ListItemText 
                  primary={action} 
                  className="quick-action-text"
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>
    </Drawer>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App Bar */}
      {isMobile ? renderMobileAppBar() : renderDesktopAppBar()}
      
      {/* Drawer */}
      {renderDrawer()}
      
      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 1, sm: 2, md: 3 },
          width: { sm: `calc(100% - ${isMobile ? 0 : 240}px)` },
          ml: { sm: `${isMobile ? 0 : 240}px` },
          mt: { xs: 7, sm: 8 }
        }}
      >
        <Fade in={true} timeout={800}>
          <Box>
            {children}
          </Box>
        </Fade>
      </Box>

      {/* Notifications Drawer */}
      <Drawer
        anchor="right"
        open={notificationsOpen}
        onClose={() => setNotificationsOpen(false)}
        sx={{
          '& .MuiDrawer-paper': {
            width: { xs: '100%', sm: 400 },
            background: 'linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%)',
            borderLeft: '1px solid rgba(255,255,255,0.1)',
            backdropFilter: 'blur(10px)'
          }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
              Notifications
            </Typography>
            <IconButton onClick={() => setNotificationsOpen(false)} sx={{ color: 'white' }}>
              <Close />
            </IconButton>
          </Box>
          
          <List>
            {notifications.map((notification) => (
              <ListItem key={notification.id} sx={{ mb: 1 }}>
                <Alert 
                  severity={notification.type as any}
                  sx={{ 
                    width: '100%',
                    backgroundColor: 'rgba(255,255,255,0.05)',
                    border: '1px solid rgba(255,255,255,0.1)'
                  }}
                >
                  <Typography variant="body2" sx={{ color: 'white' }}>
                    {notification.message}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                    {notification.time}
                  </Typography>
                </Alert>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* User Menu */}
      <Menu
        anchorEl={null}
        open={userMenuOpen}
        onClose={() => setUserMenuOpen(false)}
        sx={{
          '& .MuiPaper-root': {
            background: 'linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%)',
            border: '1px solid rgba(255,255,255,0.1)',
            backdropFilter: 'blur(10px)',
            color: 'white'
          }
        }}
      >
        <MenuItem onClick={() => setUserMenuOpen(false)}>
          <AccountCircle sx={{ mr: 1 }} />
          Profile
        </MenuItem>
        <MenuItem onClick={() => setUserMenuOpen(false)}>
          <Settings sx={{ mr: 1 }} />
          Settings
        </MenuItem>
        <Divider sx={{ borderColor: 'rgba(255,255,255,0.1)' }} />
        <MenuItem onClick={() => setUserMenuOpen(false)}>
          Logout
        </MenuItem>
      </Menu>

      {/* Scroll to Top Button */}
      <Slide direction="up" in={showScrollTop}>
        <Fab
          color="primary"
          size="medium"
          onClick={scrollToTop}
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            background: 'linear-gradient(135deg, #6366f1 0%, #10b981 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #5b5fdb 0%, #059669 100%)',
              transform: 'translateY(-2px)',
            }
          }}
        >
          <KeyboardArrowUp />
        </Fab>
      </Slide>
    </Box>
  );
};

export default ResponsiveLayout; 