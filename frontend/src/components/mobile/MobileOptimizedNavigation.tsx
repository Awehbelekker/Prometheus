import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { Menu as MenuIcon } from '@mui/icons-material';

interface MobileOptimizedNavigationProps {
  items: Array<{
    id: string;
    label: string;
    icon: React.ReactNode;
    onClick: () => void;
  }>;
}

/**
 * Mobile-optimized navigation with touch-friendly interactions
 */
const MobileOptimizedNavigation: React.FC<MobileOptimizedNavigationProps> = ({
  items
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  if (!isMobile) return null;

  return (
    <>
      <IconButton
        color="inherit"
        aria-label="open drawer"
        edge="start"
        onClick={handleDrawerToggle}
        sx={{ 
          position: 'fixed',
          top: 16,
          left: 16,
          zIndex: 1300,
          backgroundColor: 'rgba(0, 212, 255, 0.1)',
          '&:hover': {
            backgroundColor: 'rgba(0, 212, 255, 0.2)'
          }
        }}
      >
        <MenuIcon />
      </IconButton>
      
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 280,
            backgroundColor: '#1a1a1a',
            color: 'white'
          },
        }}
      >
        <Box sx={{ overflow: 'auto', pt: 8 }}>
          <List>
            {items.map((item) => (
              <ListItem
                key={item.id}
                button
                onClick={() => {
                  item.onClick();
                  setMobileOpen(false);
                }}
                sx={{
                  minHeight: 56, // Touch-friendly height
                  '&:hover': {
                    backgroundColor: 'rgba(0, 212, 255, 0.1)'
                  }
                }}
              >
                <ListItemIcon sx={{ color: '#00d4ff' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.label}
                  sx={{ color: 'white' }}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
    </>
  );
};

export default React.memo(MobileOptimizedNavigation);