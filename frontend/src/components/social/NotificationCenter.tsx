/**
 * NotificationCenter Component
 * Real-time notification system with multiple notification types
 */

import React, { useState } from 'react';
import {
  Box,
  Badge,
  IconButton,
  Popover,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Typography,
  Divider,
  Button,
  Chip
} from '@mui/material';
import {
  Notifications,
  EmojiEvents,
  TrendingUp,
  PersonAdd,
  Star,
  CheckCircle
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiCall } from '../../config/api';
import { formatDistanceToNow } from 'date-fns';

interface Notification {
  id: string;
  type: 'achievement' | 'trade' | 'follow' | 'level_up' | 'system';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  data?: any;
}

interface NotificationCenterProps {
  userId: string;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({ userId }) => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const queryClient = useQueryClient();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ['notifications', userId],
    queryFn: async () => {
      const response = await apiCall(`/api/notifications/${userId}`);
      return response as Notification[];
    },
    refetchInterval: 30000 // Refetch every 30 seconds
  });

  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId: string) => {
      return await apiCall(`/api/notifications/${notificationId}/read`, {
        method: 'POST'
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications', userId] });
    }
  });

  const markAllAsReadMutation = useMutation({
    mutationFn: async () => {
      return await apiCall(`/api/notifications/${userId}/read-all`, {
        method: 'POST'
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications', userId] });
    }
  });

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markAsReadMutation.mutate(notification.id);
    }
    // Handle navigation based on notification type
    // e.g., navigate to achievement page, trade details, etc.
  };

  const handleMarkAllAsRead = () => {
    markAllAsReadMutation.mutate();
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'achievement':
        return <EmojiEvents sx={{ color: '#ff9800' }} />;
      case 'trade':
        return <TrendingUp sx={{ color: '#4caf50' }} />;
      case 'follow':
        return <PersonAdd sx={{ color: '#00d4ff' }} />;
      case 'level_up':
        return <Star sx={{ color: '#ffd700' }} />;
      default:
        return <Notifications sx={{ color: '#888' }} />;
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;
  const open = Boolean(anchorEl);

  return (
    <>
      <IconButton onClick={handleClick} sx={{ color: '#fff' }}>
        <Badge badgeContent={unreadCount} color="error">
          <Notifications />
        </Badge>
      </IconButton>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right'
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right'
        }}
        PaperProps={{
          sx: {
            width: 400,
            maxHeight: 600,
            background: 'rgba(26, 26, 26, 0.98)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 2,
            mt: 1
          }
        }}
      >
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
              Notifications
            </Typography>
            {unreadCount > 0 && (
              <Button
                size="small"
                onClick={handleMarkAllAsRead}
                sx={{ color: '#00d4ff', textTransform: 'none' }}
              >
                Mark all as read
              </Button>
            )}
          </Box>
        </Box>

        {/* Notifications List */}
        <List sx={{ p: 0, maxHeight: 500, overflow: 'auto' }}>
          {notifications.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Notifications sx={{ fontSize: 48, color: '#888', mb: 2 }} />
              <Typography variant="body2" sx={{ color: '#888' }}>
                No notifications yet
              </Typography>
            </Box>
          ) : (
            notifications.map((notification, index) => (
              <React.Fragment key={notification.id}>
                <ListItem
                  button
                  onClick={() => handleNotificationClick(notification)}
                  sx={{
                    bgcolor: notification.read ? 'transparent' : 'rgba(0, 212, 255, 0.05)',
                    '&:hover': {
                      bgcolor: 'rgba(0, 212, 255, 0.1)'
                    }
                  }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'rgba(0, 212, 255, 0.2)' }}>
                      {getNotificationIcon(notification.type)}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography
                          variant="body2"
                          sx={{
                            color: '#fff',
                            fontWeight: notification.read ? 400 : 600
                          }}
                        >
                          {notification.title}
                        </Typography>
                        {!notification.read && (
                          <Box
                            sx={{
                              width: 8,
                              height: 8,
                              borderRadius: '50%',
                              bgcolor: '#00d4ff'
                            }}
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography
                          variant="caption"
                          sx={{ color: '#aaa', display: 'block', mb: 0.5 }}
                        >
                          {notification.message}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#666' }}>
                          {formatDistanceToNow(new Date(notification.timestamp), {
                            addSuffix: true
                          })}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
                {index < notifications.length - 1 && (
                  <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.05)' }} />
                )}
              </React.Fragment>
            ))
          )}
        </List>

        {/* Footer */}
        {notifications.length > 0 && (
          <Box
            sx={{
              p: 2,
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              textAlign: 'center'
            }}
          >
            <Button
              fullWidth
              sx={{ color: '#00d4ff', textTransform: 'none' }}
              onClick={() => {
                handleClose();
                // Navigate to notifications page
              }}
            >
              View all notifications
            </Button>
          </Box>
        )}
      </Popover>
    </>
  );
};

export default NotificationCenter;

