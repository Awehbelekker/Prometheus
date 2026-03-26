/**
 * SkipNavigation Component
 * Accessibility feature for keyboard navigation
 */

import React from 'react';
import { Box, Link } from '@mui/material';

const SkipNavigation: React.FC = () => {
  return (
    <Box
      sx={{
        position: 'absolute',
        left: '-9999px',
        zIndex: 10001,
        '&:focus-within': {
          left: 0,
          top: 0,
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
          p: 2,
          bgcolor: 'rgba(0, 212, 255, 0.95)',
          zIndex: 10001
        }
      }}
    >
      <Link
        href="#main-content"
        sx={{
          color: '#000',
          fontWeight: 600,
          textDecoration: 'none',
          p: 1,
          '&:focus': {
            outline: '2px solid #000',
            outlineOffset: 2
          }
        }}
      >
        Skip to main content
      </Link>
      <Link
        href="#navigation"
        sx={{
          color: '#000',
          fontWeight: 600,
          textDecoration: 'none',
          p: 1,
          ml: 2,
          '&:focus': {
            outline: '2px solid #000',
            outlineOffset: 2
          }
        }}
      >
        Skip to navigation
      </Link>
    </Box>
  );
};

export default SkipNavigation;

