/**
 * AchievementNotification Component
 * Animated achievement unlock notification with confetti
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Slide,
  Fade
} from '@mui/material';
import { EmojiEvents, Star } from '@mui/icons-material';
import Confetti from 'react-confetti';

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  points: number;
  rarity?: string;
}

export interface AchievementNotificationProps {
  achievement: Achievement | null;
  onClose: () => void;
  duration?: number; // milliseconds
}

const AchievementNotification: React.FC<AchievementNotificationProps> = ({
  achievement,
  onClose,
  duration = 5000
}) => {
  const [show, setShow] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    if (achievement) {
      setShow(true);
      setShowConfetti(true);
      
      // Hide confetti after 3 seconds
      const confettiTimer = setTimeout(() => {
        setShowConfetti(false);
      }, 3000);

      // Hide notification after duration
      const hideTimer = setTimeout(() => {
        setShow(false);
        setTimeout(onClose, 300); // Wait for animation
      }, duration);

      return () => {
        clearTimeout(confettiTimer);
        clearTimeout(hideTimer);
      };
    }
  }, [achievement, duration, onClose]);

  if (!achievement) return null;

  const getRarityColor = (rarity?: string) => {
    switch (rarity?.toLowerCase()) {
      case 'legendary':
        return '#ff9800';
      case 'epic':
        return '#9c27b0';
      case 'rare':
        return '#2196f3';
      case 'uncommon':
        return '#4caf50';
      default:
        return '#757575';
    }
  };

  return (
    <>
      {showConfetti && (
        <Confetti
          width={window.innerWidth}
          height={window.innerHeight}
          recycle={false}
          numberOfPieces={200}
          gravity={0.3}
          colors={['#00d4ff', '#ff6b35', '#4caf50', '#9c27b0', '#ff9800']}
        />
      )}

      <Slide direction="down" in={show} mountOnEnter unmountOnExit>
        <Box
          sx={{
            position: 'fixed',
            top: 80,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 10000,
            width: '90%',
            maxWidth: 500
          }}
        >
          <Fade in={show}>
            <Card
              sx={{
                background: 'linear-gradient(135deg, rgba(26, 26, 26, 0.98) 0%, rgba(40, 40, 40, 0.98) 100%)',
                border: `2px solid ${getRarityColor(achievement.rarity)}`,
                borderRadius: 3,
                boxShadow: `0 8px 32px ${getRarityColor(achievement.rarity)}40`,
                animation: 'pulse 2s ease-in-out infinite'
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      width: 60,
                      height: 60,
                      borderRadius: '50%',
                      background: `linear-gradient(135deg, ${getRarityColor(achievement.rarity)}40, ${getRarityColor(achievement.rarity)}20)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 2,
                      fontSize: 32
                    }}
                  >
                    {achievement.icon || '🏆'}
                  </Box>
                  
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <EmojiEvents sx={{ color: getRarityColor(achievement.rarity), fontSize: 20 }} />
                      <Typography
                        variant="caption"
                        sx={{
                          color: getRarityColor(achievement.rarity),
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          letterSpacing: 1
                        }}
                      >
                        Achievement Unlocked!
                      </Typography>
                    </Box>
                    
                    <Typography
                      variant="h6"
                      sx={{
                        color: '#fff',
                        fontWeight: 700,
                        mb: 0.5
                      }}
                    >
                      {achievement.name}
                    </Typography>
                    
                    <Typography
                      variant="body2"
                      sx={{ color: '#aaa', mb: 1 }}
                    >
                      {achievement.description}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Star sx={{ color: '#ffd700', fontSize: 16 }} />
                      <Typography
                        variant="body2"
                        sx={{ color: '#ffd700', fontWeight: 600 }}
                      >
                        +{achievement.points} XP
                      </Typography>
                      
                      {achievement.rarity && (
                        <Chip
                          label={achievement.rarity}
                          size="small"
                          sx={{
                            ml: 1,
                            bgcolor: `${getRarityColor(achievement.rarity)}20`,
                            color: getRarityColor(achievement.rarity),
                            fontWeight: 600,
                            fontSize: 10,
                            height: 20
                          }}
                        />
                      )}
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Fade>
        </Box>
      </Slide>

      <style>
        {`
          @keyframes pulse {
            0%, 100% {
              transform: scale(1);
            }
            50% {
              transform: scale(1.02);
            }
          }
        `}
      </style>
    </>
  );
};

// Missing import
import { Chip } from '@mui/material';

export default AchievementNotification;

