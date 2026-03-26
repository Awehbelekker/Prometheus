import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#00D4FF' },
    success: { main: '#4CAF50' },
    error: { main: '#F44336' },
    background: { default: '#121212', paper: '#1a1a2e' },
    text: { primary: '#ffffff', secondary: '#aaaaaa' },
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 700, marginBottom: '1rem' },
    h6: { fontWeight: 600 },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'rgba(26,26,46,.9)',
          border: '1px solid rgba(255,255,255,.08)',
        },
      },
    },
    MuiChip: { styleOverrides: { root: { fontSize: '0.75rem' } } },
    MuiButton: { styleOverrides: { root: { textTransform: 'none', fontWeight: 600 } } },
  },
});
