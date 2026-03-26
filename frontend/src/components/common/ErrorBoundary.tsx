import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Stack,
  Divider
} from '@mui/material';
import {
  ErrorOutline,
  Refresh,
  BugReport,
  Home
} from '@mui/icons-material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Enhanced Error Boundary Component
 * 
 * Provides comprehensive error handling with user-friendly fallback UI
 * and error reporting capabilities
 */
class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // In production, you might want to log this to an error reporting service
    if (process.env.NODE_ENV === 'production') {
      // Example: logErrorToService(error, errorInfo);
    }
  }

  private handleRefresh = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private handleReportBug = () => {
    const errorDetails = {
      error: this.state.error?.message,
      stack: this.state.error?.stack,
      componentStack: this.state.errorInfo?.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // In a real app, you'd send this to your error reporting service
    console.log('Bug report data:', errorDetails);
    
    // For now, copy to clipboard
    navigator.clipboard.writeText(JSON.stringify(errorDetails, null, 2));
    alert('Error details copied to clipboard. Please send this to support.');
  };

  public render() {
    if (this.state.hasError) {
      // Custom fallback UI if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
            p: 3
          }}
        >
          <Card
            sx={{
              maxWidth: 600,
              width: '100%',
              background: 'rgba(26, 26, 26, 0.9)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(244, 67, 54, 0.3)',
              borderRadius: 3
            }}
          >
            <CardContent sx={{ p: 4 }}>
              <Stack spacing={3} alignItems="center">
                <ErrorOutline sx={{ fontSize: 64, color: '#f44336' }} />
                
                <Typography
                  variant="h4"
                  sx={{
                    color: '#f44336',
                    fontWeight: 700,
                    textAlign: 'center'
                  }}
                >
                  Oops! Something went wrong
                </Typography>

                <Typography
                  variant="body1"
                  sx={{
                    color: '#ccc',
                    textAlign: 'center',
                    maxWidth: 400
                  }}
                >
                  We encountered an unexpected error. Don't worry, your data is safe. 
                  You can try refreshing the page or return to the home page.
                </Typography>

                <Alert
                  severity="error"
                  sx={{
                    width: '100%',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    border: '1px solid rgba(244, 67, 54, 0.3)',
                    '& .MuiAlert-message': { color: '#fff' }
                  }}
                >
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    {this.state.error?.message || 'Unknown error occurred'}
                  </Typography>
                </Alert>

                <Divider sx={{ width: '100%', borderColor: 'rgba(255, 255, 255, 0.1)' }} />

                <Stack direction="row" spacing={2} flexWrap="wrap" justifyContent="center">
                  <Button
                    variant="contained"
                    startIcon={<Refresh />}
                    onClick={this.handleRefresh}
                    sx={{
                      background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                      '&:hover': {
                        background: 'linear-gradient(45deg, #0099cc, #00d4ff)',
                      }
                    }}
                  >
                    Try Again
                  </Button>

                  <Button
                    variant="outlined"
                    startIcon={<Home />}
                    onClick={this.handleGoHome}
                    sx={{
                      color: '#00d4ff',
                      borderColor: '#00d4ff',
                      '&:hover': {
                        borderColor: '#0099cc',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)'
                      }
                    }}
                  >
                    Go Home
                  </Button>

                  <Button
                    variant="text"
                    startIcon={<BugReport />}
                    onClick={this.handleReportBug}
                    sx={{
                      color: '#999',
                      '&:hover': {
                        color: '#ccc',
                        backgroundColor: 'rgba(255, 255, 255, 0.05)'
                      }
                    }}
                  >
                    Report Bug
                  </Button>
                </Stack>

                {process.env.NODE_ENV === 'development' && this.state.error && (
                  <Box
                    sx={{
                      width: '100%',
                      mt: 2,
                      p: 2,
                      backgroundColor: 'rgba(0, 0, 0, 0.3)',
                      borderRadius: 1,
                      border: '1px solid rgba(255, 255, 255, 0.1)'
                    }}
                  >
                    <Typography variant="caption" sx={{ color: '#999', mb: 1, display: 'block' }}>
                      Development Error Details:
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        fontFamily: 'monospace',
                        fontSize: '0.75rem',
                        color: '#f44336',
                        whiteSpace: 'pre-wrap',
                        maxHeight: 200,
                        overflow: 'auto'
                      }}
                    >
                      {this.state.error.stack}
                    </Typography>
                  </Box>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
