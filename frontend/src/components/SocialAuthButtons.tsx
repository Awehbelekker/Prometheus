import React from 'react';
import { Button, Stack, Box } from '@mui/material';

interface SocialAuthButtonsProps {
  onProviderClick: (provider: 'google' | 'apple' | 'microsoft') => void;
  theme?: 'dark' | 'light';
}

const PROVIDERS = [
  {
    id: 'google',
    label: 'Continue with Google',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><g><path d="M21.805 10.023h-9.765v3.954h5.617c-.242 1.242-1.484 3.648-5.617 3.648-3.383 0-6.148-2.797-6.148-6.25s2.765-6.25 6.148-6.25c1.93 0 3.227.82 3.969 1.523l2.715-2.648c-1.711-1.57-3.922-2.523-6.684-2.523-5.523 0-10 4.477-10 10s4.477 10 10 10c5.742 0 9.547-4.023 9.547-9.703 0-.652-.07-1.148-.156-1.45z" fill="#4285F4"/><path d="M3.153 7.345l3.242 2.379c.883-1.68 2.523-2.879 4.405-2.879 1.18 0 2.242.406 3.078 1.078l2.32-2.32c-1.406-1.297-3.211-2.103-5.398-2.103-3.672 0-6.75 2.977-6.75 6.625 0 1.055.258 2.055.711 2.938z" fill="#34A853"/><path d="M12.8 21.5c2.188 0 4.188-.719 5.742-1.953l-2.672-2.188c-.75.508-1.711.812-3.07.812-2.367 0-4.375-1.594-5.094-3.75h-3.25v2.344c1.547 3.055 4.781 5.125 8.344 5.125z" fill="#FBBC05"/><path d="M21.805 10.023h-9.765v3.954h5.617c-.242 1.242-1.484 3.648-5.617 3.648-3.383 0-6.148-2.797-6.148-6.25s2.765-6.25 6.148-6.25c1.93 0 3.227.82 3.969 1.523l2.715-2.648c-1.711-1.57-3.922-2.523-6.684-2.523-5.523 0-10 4.477-10 10s4.477 10 10 10c5.742 0 9.547-4.023 9.547-9.703 0-.652-.07-1.148-.156-1.45z" fill="#EA4335"/></g></svg>
    )
  },
  {
    id: 'apple',
    label: 'Continue with Apple',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M16.365 1.43c0 1.14-.93 2.07-2.07 2.07-.03-1.17.96-2.07 2.07-2.07zm2.13 4.36c-1.17-.03-2.16.66-2.73.66-.57 0-1.44-.63-2.37-.61-1.22.02-2.36.71-2.99 1.8-1.28 2.22-.33 5.5.91 7.3.6.87 1.32 1.85 2.27 1.82.9-.04 1.24-.59 2.33-.59 1.09 0 1.39.59 2.34.57.96-.02 1.56-.89 2.15-1.76.68-.99.96-1.95.97-2-.02-.01-1.87-.72-1.89-2.85-.02-1.8 1.47-2.66 1.54-2.7-.84-1.23-2.14-1.37-2.6-1.39zm-2.01 13.13c-.53 0-1.06.15-1.5.15-.44 0-1.13-.14-1.87-.14-1.44 0-2.77.83-3.51 2.13-.25.43-.36.86-.36 1.32 0 1.04.42 2.06 1.19 2.06.44 0 .75-.3 1.31-.3.56 0 .81.3 1.36.3.56 0 .81-.3 1.36-.3.56 0 .87.3 1.31.3.77 0 1.19-1.02 1.19-2.06 0-.45-.12-.89-.36-1.32-.74-1.3-2.07-2.13-3.51-2.13z" fill="currentColor"/></svg>
    )
  },
  {
    id: 'microsoft',
    label: 'Continue with Microsoft',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><g><rect x="2" y="2" width="9" height="9" fill="#F35325"/><rect x="13" y="2" width="9" height="9" fill="#81BC06"/><rect x="2" y="13" width="9" height="9" fill="#05A6F0"/><rect x="13" y="13" width="9" height="9" fill="#FFBA08"/></g></svg>
    )
  },
];

const SocialAuthButtons: React.FC<SocialAuthButtonsProps> = ({ onProviderClick, theme = 'dark' }) => {
  return (
    <Stack spacing={2}>
      {PROVIDERS.map(provider => (
        <Button
          key={provider.id}
          onClick={() => onProviderClick(provider.id as 'google' | 'apple' | 'microsoft')}
          variant="outlined"
          fullWidth
          size="large"
          startIcon={
            <Box sx={{ width: 24, height: 24, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {provider.icon}
            </Box>
          }
          sx={{
            py: 1.5,
            px: 3,
            backgroundColor: theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : '#fff',
            borderColor: 'rgba(255, 255, 255, 0.2)',
            color: theme === 'dark' ? '#fff' : '#000',
            textTransform: 'none',
            fontSize: '1rem',
            fontWeight: 500,
            '&:hover': {
              backgroundColor: theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
              borderColor: 'rgba(255, 255, 255, 0.3)',
              transform: 'translateY(-1px)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
            },
            transition: 'all 0.3s ease'
          }}
        >
          {provider.label}
        </Button>
      ))}
    </Stack>
  );
};

export default SocialAuthButtons; 