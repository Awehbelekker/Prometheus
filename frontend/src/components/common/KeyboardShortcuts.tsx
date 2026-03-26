import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Chip,
  Divider,
  Paper
} from '@mui/material';
import { Keyboard, Close } from '@mui/icons-material';

interface Shortcut {
  keys: string[];
  description: string;
  category: string;
}

interface KeyboardShortcutsProps {
  open: boolean;
  onClose: () => void;
}

/**
 * Keyboard Shortcuts Component
 * Displays available keyboard shortcuts in a modal
 */
const KeyboardShortcuts: React.FC<KeyboardShortcutsProps> = ({ open, onClose }) => {
  const shortcuts: Shortcut[] = [
    // Navigation
    { keys: ['Ctrl', 'K'], description: 'Open global search', category: 'Navigation' },
    { keys: ['Ctrl', '/'], description: 'Open command palette', category: 'Navigation' },
    { keys: ['Esc'], description: 'Close dialogs/modals', category: 'Navigation' },
    { keys: ['?'], description: 'Show keyboard shortcuts', category: 'Navigation' },
    
    // Trading
    { keys: ['Ctrl', 'T'], description: 'Open trading dashboard', category: 'Trading' },
    { keys: ['Ctrl', 'P'], description: 'Open portfolio', category: 'Trading' },
    { keys: ['Ctrl', 'W'], description: 'Open watchlist', category: 'Trading' },
    
    // Admin
    { keys: ['Ctrl', 'Shift', 'A'], description: 'Open admin cockpit', category: 'Admin' },
    { keys: ['Ctrl', 'Shift', 'U'], description: 'Open user management', category: 'Admin' },
    { keys: ['Ctrl', 'Shift', 'S'], description: 'Open system monitoring', category: 'Admin' },
    
    // General
    { keys: ['Ctrl', 'R'], description: 'Refresh current page', category: 'General' },
    { keys: ['Ctrl', 'H'], description: 'Go to home/dashboard', category: 'General' },
    { keys: ['Ctrl', 'Shift', 'N'], description: 'New notification', category: 'General' },
  ];

  const categories = Array.from(new Set(shortcuts.map(s => s.category)));

  const renderKey = (key: string) => {
    return (
      <Chip
        label={key}
        size="small"
        sx={{
          height: 24,
          minWidth: 32,
          fontSize: '0.75rem',
          fontWeight: 600,
          backgroundColor: 'rgba(0, 212, 255, 0.1)',
          color: '#00d4ff',
          border: '1px solid rgba(0, 212, 255, 0.3)',
          '& .MuiChip-label': {
            px: 1
          }
        }}
      />
    );
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: 'rgba(26, 26, 46, 0.95)',
          border: '1px solid rgba(0, 212, 255, 0.3)',
          borderRadius: 2
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 2,
        color: '#00d4ff',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        pb: 2
      }}>
        <Keyboard sx={{ fontSize: 28 }} />
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          Keyboard Shortcuts
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ pt: 3 }}>
        {categories.map((category, categoryIndex) => (
          <Box key={category} sx={{ mb: categoryIndex < categories.length - 1 ? 4 : 0 }}>
            <Typography variant="h6" sx={{ 
              color: '#fff', 
              mb: 2, 
              fontWeight: 600,
              textTransform: 'uppercase',
              fontSize: '0.875rem',
              letterSpacing: 1
            }}>
              {category}
            </Typography>
            
            <Grid container spacing={2}>
              {shortcuts
                .filter(s => s.category === category)
                .map((shortcut, index) => (
                  <Grid item xs={12} key={index}>
                    <Paper
                      sx={{
                        p: 2,
                        backgroundColor: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                        borderRadius: 1,
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          backgroundColor: 'rgba(0, 212, 255, 0.05)',
                          borderColor: 'rgba(0, 212, 255, 0.2)'
                        }
                      }}
                    >
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                        {shortcut.description}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                        {shortcut.keys.map((key, keyIndex) => (
                          <React.Fragment key={keyIndex}>
                            {renderKey(key)}
                            {keyIndex < shortcut.keys.length - 1 && (
                              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.4)', mx: 0.5 }}>
                                +
                              </Typography>
                            )}
                          </React.Fragment>
                        ))}
                      </Box>
                    </Paper>
                  </Grid>
                ))}
            </Grid>
            
            {categoryIndex < categories.length - 1 && (
              <Divider sx={{ mt: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
            )}
          </Box>
        ))}
      </DialogContent>
      
      <DialogActions sx={{ p: 2, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <Button
          onClick={onClose}
          variant="contained"
          startIcon={<Close />}
          sx={{
            background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
            '&:hover': {
              background: 'linear-gradient(45deg, #0099cc, #007aa3)'
            }
          }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

/**
 * Hook to manage keyboard shortcuts globally
 */
export const useKeyboardShortcuts = () => {
  const [shortcutsOpen, setShortcutsOpen] = useState(false);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Show shortcuts dialog
    if (event.key === '?' && !event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey) {
      // Only if not typing in an input
      const target = event.target as HTMLElement;
      if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA' && !target.isContentEditable) {
        event.preventDefault();
        setShortcutsOpen(true);
      }
    }

    // Global search (Ctrl+K or Cmd+K)
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
      event.preventDefault();
      // Trigger global search - will be implemented
      console.log('Global search triggered');
    }

    // Command palette (Ctrl+/ or Cmd+/)
    if ((event.ctrlKey || event.metaKey) && event.key === '/') {
      event.preventDefault();
      // Trigger command palette - will be implemented
      console.log('Command palette triggered');
    }

    // Close dialogs with Esc
    if (event.key === 'Escape') {
      // This will be handled by individual components
    }
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  return {
    shortcutsOpen,
    setShortcutsOpen
  };
};

export default KeyboardShortcuts;

