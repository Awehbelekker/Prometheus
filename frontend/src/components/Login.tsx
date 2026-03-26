import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Divider,
  Stack,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  InputAdornment,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  Fade,
  Slide
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  TrendingUp,
  Security,
  Analytics,
  Psychology,
  AutoAwesome,
  Speed,
  Insights,
  SmartToy,
  CheckCircle,
  Lock,
  Person
} from '@mui/icons-material';
import Logo from './Logo';
import PrometheusLogo from './unified/PrometheusLogo';
import ParticleBackground from './ParticleBackground';
import SocialAuthButtons from './SocialAuthButtons';
import './Login.css';

interface LoginProps {
  onLogin: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
}

interface LoginForm {
  username: string;
  password: string;
}

// Enhanced login steps for progress indication
const LOGIN_STEPS = ['Credentials', 'Verification', 'Welcome'];

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [loginForm, setLoginForm] = useState<LoginForm>({
    username: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [loginStep, setLoginStep] = useState(0);
  const [loginProgress, setLoginProgress] = useState(0);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [fieldValues, setFieldValues] = useState({ username: '', password: '' });

  // Clean card styles without glassmorphism
  const cleanCardStyles = {
    background: 'rgba(26, 26, 26, 0.95)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: 3,
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.3)',
    position: 'relative',
    width: '100%',
    maxWidth: 450,
    transition: 'all 0.3s ease',
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 15px 35px rgba(0, 0, 0, 0.4)',
      border: '1px solid rgba(0, 212, 255, 0.2)'
    }
  };

  // Simplified text field styles with clean focus effects and proper spacing
  const getCleanTextFieldStyles = (fieldName: string, hasValue: boolean) => ({
    '& .MuiOutlinedInput-root': {
      backgroundColor: 'rgba(255, 255, 255, 0.05)',
      borderRadius: 2,
      transition: 'all 0.3s ease',
      '& fieldset': {
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        transition: 'all 0.3s ease'
      },
      '&:hover fieldset': {
        borderColor: 'rgba(0, 212, 255, 0.5)',
      },
      '&.Mui-focused': {
        backgroundColor: 'rgba(255, 255, 255, 0.08)',
        boxShadow: '0 4px 12px rgba(0, 212, 255, 0.2)',
        '& fieldset': {
          borderWidth: 2,
          borderColor: '#00d4ff'
        }
      }
    },
    '& .MuiInputLabel-root': {
      color: '#999',
      zIndex: 1,
      pointerEvents: 'none',
      '&.Mui-focused': {
        color: '#00d4ff'
      },
      '&.MuiInputLabel-shrink': {
        color: '#999',
        backgroundColor: 'rgba(26, 26, 26, 0.95)',
        padding: '0 8px',
        borderRadius: '4px'
      }
    },
    '& .MuiInputBase-input': {
      color: '#fff',
      fontSize: '1rem',
      padding: '16px 14px',
      zIndex: 2
    },
    '& .MuiInputAdornment-root': {
      zIndex: 3,
      '& .MuiSvgIcon-root': {
        fontSize: '1.2rem'
      }
    }
  });



  // Email/password login handler with progress steps
  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setLoginStep(0);
    setLoginProgress(0);

    try {
      // Step 1: Credentials validation
      setLoginStep(1);
      setLoginProgress(33);
      await new Promise(resolve => setTimeout(resolve, 800)); // Simulate validation

      // Step 2: Authentication
      setLoginStep(2);
      setLoginProgress(66);
      
      const result = await onLogin(loginForm.username, loginForm.password);

      if (!result.success) {
        throw new Error(result.error || 'Login failed');
      }

      // Step 3: Welcome
      setLoginStep(3);
      setLoginProgress(100);
      await new Promise(resolve => setTimeout(resolve, 600)); // Show success state

      // Login successful - parent component handles navigation

    } catch (err: any) {
      console.error('Email login error:', err);
      setError(err.message || 'Login failed. Please check your credentials.');
      setLoginStep(0);
      setLoginProgress(0);
    } finally {
      setIsLoading(false);
    }
  };

  // Enhanced field change handler
  const handleFieldChange = (field: keyof LoginForm, value: string) => {
    setLoginForm(prev => ({ ...prev, [field]: value }));
    setFieldValues(prev => ({ ...prev, [field]: value }));
  };

  // Field focus handlers
  const handleFieldFocus = (fieldName: string) => {
    setFocusedField(fieldName);
  };

  const handleFieldBlur = () => {
    setFocusedField(null);
  };

  // Social authentication handler
  const handleSocialAuth = async (provider: 'google' | 'apple' | 'microsoft') => {
    setIsLoading(true);
    setError(null);

    try {
      // Implement social auth logic here
      console.log(`Initiating ${provider} authentication...`);

      // For now, show a message that social auth is being implemented
      setError(`${provider.charAt(0).toUpperCase() + provider.slice(1)} authentication coming soon!`);

    } catch (err: any) {
      console.error('Social auth error:', err);
      setError(err.message || 'Social authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Check if already logged in - only run once on mount
  useEffect(() => {
    // Don't clear tokens - let the parent App component handle session restoration
    console.log('Login component mounted - session management handled by App component');
  }, []);

  return (
    <div className="login-root">
      <Box sx={{
        display: 'flex',
        minHeight: '100vh',
        width: '100vw',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Particle Background */}
        <ParticleBackground
          particleCount={120}
          colors={['#00d4ff', '#ff6b35', '#4caf50', '#9c27b0', '#e91e63', '#ffffff']}
          speed={0.5}
        />

        {/* Background Animation */}
        <Box sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `
            radial-gradient(circle at 20% 80%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 107, 53, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(0, 212, 255, 0.05) 0%, transparent 50%)
          `,
          animation: 'float 6s ease-in-out infinite',
          zIndex: 1
        }} />

        {/* Left Side - Branding */}
        <Box sx={{
          flex: 1,
          display: { xs: 'none', md: 'flex' },
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          padding: 4,
          position: 'relative',
          zIndex: 2,
          minWidth: '50%'
        }}>
            <Box sx={{ textAlign: 'center', maxWidth: 500, width: '100%' }}>
              {/* Clean original logo only */}
              <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center' }}>
                <Logo size="large" theme="dark" />
              </Box>

              {/* Platform Name */}
              <Box sx={{ mb: 4 }}>
                <Typography
                  variant="h4"
                  sx={{
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #fff 0%, #00d4ff 50%, #ff6b35 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    mb: 1,
                    textShadow: '0 0 30px rgba(0, 212, 255, 0.3)',
                    letterSpacing: '1px'
                  }}
                >
                  Prometheus Trading
                </Typography>
                <Typography
                  variant="subtitle1"
                  sx={{
                    color: '#888',
                    fontWeight: 400,
                    letterSpacing: '0.5px',
                    fontSize: '1rem'
                  }}
                >
                  with Neuroforge™
                </Typography>
              </Box>

            {/* Revolutionary Features */}
            <Stack spacing={3} sx={{ mt: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <SmartToy sx={{ color: '#00d4ff', fontSize: 32 }} />
                <Box sx={{ textAlign: 'left' }}>
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                    AI Neural Networks
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#888' }}>
                    Self-learning algorithms that adapt to market patterns
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <AutoAwesome sx={{ color: '#ff6b35', fontSize: 32 }} />
                <Box sx={{ textAlign: 'left' }}>
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                    Quantum Analytics
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#888' }}>
                    Process millions of data points in microseconds
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Psychology sx={{ color: '#4caf50', fontSize: 32 }} />
                <Box sx={{ textAlign: 'left' }}>
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                    Behavioral Prediction
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#888' }}>
                    Predict market sentiment before it happens
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Speed sx={{ color: '#9c27b0', fontSize: 32 }} />
                <Box sx={{ textAlign: 'left' }}>
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                    Nano-Second Execution
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#888' }}>
                    Ultra-low latency trading at light speed
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Insights sx={{ color: '#e91e63', fontSize: 32 }} />
                <Box sx={{ textAlign: 'left' }}>
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                    Predictive Intelligence
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#888' }}>
                    See tomorrow's opportunities today
                  </Typography>
                </Box>
              </Box>
            </Stack>
          </Box>
        </Box>

        {/* Right Side - Login Form */}
        <Box sx={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 4,
          position: 'relative',
          zIndex: 2,
          minWidth: '50%'
        }}>
          <Fade in={true} timeout={800}>
            <Card sx={cleanCardStyles}>
              <CardContent sx={{ p: 4 }}>
                {/* Progress Indicator */}
                {isLoading && (
                  <Box sx={{ mb: 3 }}>
                    <LinearProgress
                      variant="determinate"
                      value={loginProgress}
                      sx={{
                        height: 4,
                        borderRadius: 2,
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 2,
                          background: 'linear-gradient(45deg, #00d4ff, #ff6b35)'
                        }
                      }}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                      {LOGIN_STEPS.map((step, index) => (
                        <Typography
                          key={step}
                          variant="caption"
                          sx={{
                            color: index < loginStep ? '#00d4ff' : '#666',
                            fontWeight: index < loginStep ? 600 : 400,
                            fontSize: '0.7rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.5
                          }}
                        >
                          {index < loginStep && <CheckCircle sx={{ fontSize: 12 }} />}
                          {step}
                        </Typography>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Header */}
                <Box sx={{ textAlign: 'center', mb: 4 }}>
                  <Slide direction="down" in={true} timeout={600}>
                    <Typography
                      variant="h4"
                      sx={{
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #fff 0%, #00d4ff 50%, #ff6b35 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                        mb: 1,
                        textShadow: '0 0 30px rgba(0, 212, 255, 0.3)'
                      }}
                    >
                      Welcome Back
                    </Typography>
                  </Slide>
                  <Slide direction="up" in={true} timeout={800}>
                    <Typography
                      variant="body1"
                      sx={{
                        color: '#999',
                        mb: 3,
                        fontWeight: 300
                      }}
                    >
                      Sign in to your trading account
                    </Typography>
                  </Slide>
                </Box>

                {/* Error Alert with clean styling */}
                {error && (
                  <Fade in={true}>
                    <Alert
                      severity="error"
                      sx={{
                        mb: 3,
                        bgcolor: 'rgba(244, 67, 54, 0.1)',
                        border: '1px solid rgba(244, 67, 54, 0.3)',
                        borderRadius: 2,
                        color: '#ff6b6b',
                        '& .MuiAlert-icon': { 
                          color: '#ff6b6b' 
                        }
                      }}
                    >
                      {error}
                    </Alert>
                  </Fade>
                )}

                {/* Enhanced Login Form */}
                <form onSubmit={handleEmailLogin}>
                  <Stack spacing={3}>
                    <TextField
                      label="Username or Email"
                      type="text"
                      value={loginForm.username}
                      onChange={(e) => handleFieldChange('username', e.target.value)}
                      onFocus={() => handleFieldFocus('username')}
                      onBlur={handleFieldBlur}
                      fullWidth
                      required
                      autoComplete="username"
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Person sx={{ 
                              color: focusedField === 'username' ? '#00d4ff' : '#666',
                              transition: 'color 0.3s ease'
                            }} />
                          </InputAdornment>
                        )
                      }}
                      sx={getCleanTextFieldStyles('username', !!fieldValues.username)}
                    />

                    <TextField
                      label="Password"
                      type={showPassword ? 'text' : 'password'}
                      value={loginForm.password}
                      onChange={(e) => handleFieldChange('password', e.target.value)}
                      onFocus={() => handleFieldFocus('password')}
                      onBlur={handleFieldBlur}
                      fullWidth
                      required
                      autoComplete="current-password"
                      variant="outlined"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Lock sx={{ 
                              color: focusedField === 'password' ? '#00d4ff' : '#666',
                              transition: 'color 0.3s ease'
                            }} />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowPassword(!showPassword)}
                              edge="end"
                              sx={{ 
                                color: focusedField === 'password' ? '#00d4ff' : '#666',
                                transition: 'color 0.3s ease'
                              }}
                            >
                              {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        )
                      }}
                      sx={getCleanTextFieldStyles('password', !!fieldValues.password)}
                    />

                    {/* Clean Login Button */}
                    <Button
                      type="submit"
                      variant="contained"
                      fullWidth
                      disabled={isLoading}
                      size="large"
                      sx={{
                        py: 2,
                        background: isLoading 
                          ? 'linear-gradient(45deg, rgba(0, 212, 255, 0.5), rgba(255, 107, 53, 0.5))'
                          : 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                        color: '#000',
                        fontWeight: 600,
                        fontSize: '1.1rem',
                        borderRadius: 2,
                        textTransform: 'none',
                        boxShadow: '0 4px 15px rgba(0, 212, 255, 0.3)',
                        '&:hover': {
                          background: 'linear-gradient(45deg, #00b8e6, #e55a2b)',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 6px 20px rgba(0, 212, 255, 0.4)'
                        },
                        '&:active': {
                          transform: 'translateY(0)'
                        },
                        '&:disabled': {
                          transform: 'none',
                          color: 'rgba(0, 0, 0, 0.6)'
                        },
                        transition: 'all 0.3s ease'
                      }}
                    >
                      {isLoading ? (
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <CircularProgress size={20} sx={{ color: 'rgba(0, 0, 0, 0.7)' }} />
                          <Typography variant="button" sx={{ color: 'rgba(0, 0, 0, 0.7)' }}>
                            {loginStep === 1 ? 'Validating...' : 
                             loginStep === 2 ? 'Authenticating...' : 
                             loginStep === 3 ? 'Welcome!' : 'Signing In...'}
                          </Typography>
                        </Stack>
                      ) : (
                        'Sign In'
                      )}
                    </Button>
                  </Stack>
                </form>

                {/* Social Authentication */}
                <Box sx={{ mt: 4 }}>
                  <Divider sx={{
                    mb: 3,
                    '&::before, &::after': { 
                      borderColor: 'rgba(255, 255, 255, 0.15)',
                      borderWidth: 1
                    },
                    '& .MuiDivider-wrapper': { 
                      color: '#888',
                      fontSize: '0.85rem'
                    }
                  }}>
                    Or continue with
                  </Divider>

                  <SocialAuthButtons
                    onProviderClick={handleSocialAuth}
                    theme="dark"
                  />
                </Box>

                {/* Footer */}
                <Box sx={{ mt: 4, textAlign: 'center' }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>
                    Don't have an account?{' '}
                    <Button
                      variant="text"
                      size="small"
                      sx={{
                        color: '#00d4ff',
                        textTransform: 'none',
                        p: 0,
                        minWidth: 'auto',
                        position: 'relative',
                        '&:hover': { 
                          backgroundColor: 'transparent',
                          color: '#ff6b35',
                          '&::after': {
                            width: '100%'
                          }
                        },
                        '&::after': {
                          content: '""',
                          position: 'absolute',
                          bottom: 0,
                          left: 0,
                          width: 0,
                          height: 1,
                          background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                          transition: 'width 0.3s ease'
                        }
                      }}
                    >
                      Contact Administrator
                    </Button>
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Fade>
        </Box>
      </Box>
    </div>
  );
};

export default Login;
