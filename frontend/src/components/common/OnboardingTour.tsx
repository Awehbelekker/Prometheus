import React, { useState, useEffect } from 'react';
import Joyride, { CallBackProps, STATUS, Step } from 'react-joyride';
import { Box, Button, Typography } from '@mui/material';
import { HelpOutline, Close } from '@mui/icons-material';

interface OnboardingTourProps {
  steps: Step[];
  run?: boolean;
  onComplete?: () => void;
  onSkip?: () => void;
  continuous?: boolean;
  showProgress?: boolean;
  showSkipButton?: boolean;
}

/**
 * Interactive Onboarding Tour Component
 * Uses react-joyride to guide users through the platform
 */
const OnboardingTour: React.FC<OnboardingTourProps> = ({
  steps,
  run = false,
  onComplete,
  onSkip,
  continuous = true,
  showProgress = true,
  showSkipButton = true
}) => {
  const [tourRun, setTourRun] = useState(run);

  useEffect(() => {
    setTourRun(run);
  }, [run]);

  const handleJoyrideCallback = (data: CallBackProps) => {
    const { status, type } = data;

    if (status === STATUS.FINISHED || status === STATUS.SKIPPED) {
      setTourRun(false);
      if (status === STATUS.FINISHED && onComplete) {
        onComplete();
      } else if (status === STATUS.SKIPPED && onSkip) {
        onSkip();
      }
    }
  };

  return (
    <Joyride
      steps={steps}
      run={tourRun}
      continuous={continuous}
      showProgress={showProgress}
      showSkipButton={showSkipButton}
      callback={handleJoyrideCallback}
      styles={{
        options: {
          primaryColor: '#00d4ff',
          textColor: '#fff',
          backgroundColor: 'rgba(26, 26, 46, 0.98)',
          overlayColor: 'rgba(0, 0, 0, 0.8)',
          arrowColor: '#00d4ff',
          zIndex: 10000
        },
        tooltip: {
          borderRadius: 8,
          backgroundColor: 'rgba(26, 26, 46, 0.98)',
          border: '1px solid rgba(0, 212, 255, 0.3)',
          color: '#fff'
        },
        tooltipContainer: {
          textAlign: 'left'
        },
        buttonNext: {
          backgroundColor: '#00d4ff',
          color: '#000',
          borderRadius: 4,
          padding: '8px 16px',
          fontSize: '14px',
          fontWeight: 600,
          '&:hover': {
            backgroundColor: '#0099cc'
          }
        },
        buttonBack: {
          color: '#00d4ff',
          marginRight: 10
        },
        buttonSkip: {
          color: 'rgba(255, 255, 255, 0.6)'
        },
        spotlight: {
          borderRadius: 8
        }
      }}
      locale={{
        back: 'Back',
        close: 'Close',
        last: 'Finish',
        next: 'Next',
        skip: 'Skip tour'
      }}
    />
  );
};

/**
 * Predefined tour steps for different sections
 */
export const getUserDashboardTourSteps = (): Step[] => [
  {
    target: 'body',
    content: (
      <Box>
        <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1, fontWeight: 700 }}>
          Welcome to Prometheus Trading Platform! 🚀
        </Typography>
        <Typography variant="body2" sx={{ color: '#fff', mb: 2 }}>
          Let's take a quick tour of your dashboard. This will only take a minute!
        </Typography>
        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
          You can skip this tour anytime by clicking "Skip tour"
        </Typography>
      </Box>
    ),
    placement: 'center',
    disableBeacon: true
  },
  {
    target: '[data-tour="portfolio-card"]',
    content: (
      <Box>
        <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1, fontWeight: 700 }}>
          Portfolio Performance 💰
        </Typography>
        <Typography variant="body2" sx={{ color: '#fff' }}>
          Here you can see your total portfolio value, returns, and performance metrics. 
          All data updates in real-time!
        </Typography>
      </Box>
    ),
    placement: 'bottom'
  },
  {
    target: '[data-tour="quick-actions"]',
    content: (
      <Box>
        <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1, fontWeight: 700 }}>
          Quick Actions 🎯
        </Typography>
        <Typography variant="body2" sx={{ color: '#fff' }}>
          Start trading, access the AI Assistant, or view your analytics with one click.
        </Typography>
      </Box>
    ),
    placement: 'bottom'
  },
  {
    target: '[data-tour="gamification"]',
    content: (
      <Box>
        <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1, fontWeight: 700 }}>
          Gamification & Achievements 🎮
        </Typography>
        <Typography variant="body2" sx={{ color: '#fff' }}>
          Track your trading progress, level up, and unlock achievements as you trade!
        </Typography>
      </Box>
    ),
    placement: 'top'
  }
];

export const getAdminDashboardTourSteps = (): Step[] => [
  {
    target: 'body',
    content: (
      <Box>
        <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1, fontWeight: 700 }}>
          Welcome to Admin Cockpit! 👑
        </Typography>
        <Typography variant="body2" sx={{ color: '#fff', mb: 2 }}>
          Let's explore the powerful admin features available to you.
        </Typography>
      </Box>
    ),
    placement: 'center',
    disableBeacon: true
  },
  {
    target: '[data-tour="user-management"]',
    content: (
      <Box>
        <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1, fontWeight: 700 }}>
          User Management 👥
        </Typography>
        <Typography variant="body2" sx={{ color: '#fff' }}>
          Manage users, approve registrations, allocate funds, and monitor user activity.
        </Typography>
      </Box>
    ),
    placement: 'right'
  },
  {
    target: '[data-tour="system-monitoring"]',
    content: (
      <Box>
        <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1, fontWeight: 700 }}>
          System Monitoring 📊
        </Typography>
        <Typography variant="body2" sx={{ color: '#fff' }}>
          Monitor system health, performance metrics, and trading activity in real-time.
        </Typography>
      </Box>
    ),
    placement: 'left'
  }
];

/**
 * Tour Trigger Button Component
 */
export const TourTriggerButton: React.FC<{
  onClick: () => void;
  variant?: 'contained' | 'outlined' | 'text';
}> = ({ onClick, variant = 'outlined' }) => {
  return (
    <Button
      variant={variant}
      startIcon={<HelpOutline />}
      onClick={onClick}
      sx={{
        borderColor: '#00d4ff',
        color: '#00d4ff',
        '&:hover': {
          borderColor: '#0099cc',
          backgroundColor: 'rgba(0, 212, 255, 0.1)'
        }
      }}
    >
      Take Tour
    </Button>
  );
};

export default OnboardingTour;
