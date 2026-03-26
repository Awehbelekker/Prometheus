import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  AccountCircle,
  Email,
  Phone,
  TrendingUp,
  Security,
  Verified,
  Diamond,
  Star,
  CheckCircle
} from '@mui/icons-material';
import Logo from './Logo';
import './UserRegistration.css';

interface UserRegistrationProps {
  onRegistrationSubmit?: (userData: any) => void;
  onInvitationCodeSubmit?: (code: string) => void;
  onRegister?: (userData: any) => void;
}

const UserRegistration: React.FC<UserRegistrationProps> = ({
  onRegistrationSubmit,
  onInvitationCodeSubmit,
  onRegister
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [registrationType, setRegistrationType] = useState<'invitation' | 'demo' | 'self'>('demo');
  const [invitationCode, setInvitationCode] = useState('');
  const [invitationTier, setInvitationTier] = useState<string>('');
  const [userData, setUserData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    date_of_birth: '',
    trading_experience: 'beginner',
    risk_tolerance: 'moderate',
    investment_goals: [] as string[],
    demo_amount: 1000,
    preferred_tier: 'silver',
    // Additional personal details
    address: '',
    city: '',
    country: '',
    postal_code: '',
    id_number: '',
    drivers_license: '',
    // Account details
    username: '',
    password: '',
    confirm_password: ''
  });

  const [loading, setLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState({
    idDocument: null as File | null,
    driversLicense: null as File | null,
    proofOfAddress: null as File | null,
    profilePhoto: null as File | null
  });

  const steps = ['Registration Type', 'Personal Information', 'Address & Contact', 'Document Verification', 'Account Setup', 'Trading Profile', 'Confirmation'];

  // Demo tier configurations
  const demoTiers = {
    bronze: { amount: 500, name: 'Bronze Explorer', return: 8, risk: 'Conservative' },
    silver: { amount: 1000, name: 'Silver Trader', return: 12, risk: 'Moderate' },
    gold: { amount: 2500, name: 'Gold Premium', return: 15, risk: 'Moderate-Aggressive' },
    elite: { amount: 5000, name: 'Elite Diamond', return: 20, risk: 'Aggressive' }
  };

  const handleInvitationCodeSubmit = async () => {
    setLoading(true);
    setValidationErrors([]);

    try {
      // Validate invitation code format
      if (!invitationCode || invitationCode.length < 8) {
        throw new Error('Invalid invitation code format');
      }

      // Mock validation - in real app, call API
      const tierPrefix = invitationCode.substring(0, 2).toUpperCase();
      const tierMap: { [key: string]: string } = {
        'BR': 'bronze',
        'SI': 'silver',
        'GO': 'gold',
        'EL': 'elite'
      };

      const tier = tierMap[tierPrefix] || 'silver';
      setInvitationTier(tier);

      if (onInvitationCodeSubmit) {
        await onInvitationCodeSubmit(invitationCode);
      }

      setActiveStep(1);
    } catch (error) {
      setValidationErrors(['Invalid invitation code. Please check and try again.']);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    const errors = validateCurrentStep();
    if (errors.length === 0) {
      setActiveStep(prev => prev + 1);
      setValidationErrors([]);
    } else {
      setValidationErrors(errors);
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
    setValidationErrors([]);
  };

  const validateCurrentStep = (): string[] => {
    const errors: string[] = [];

    switch (activeStep) {
      case 0:
        if (registrationType === 'invitation' && !invitationCode) {
          errors.push('Invitation code is required');
        }
        break;
      case 1:
        if (!userData.first_name) errors.push('First name is required');
        if (!userData.last_name) errors.push('Last name is required');
        if (!userData.email) errors.push('Email is required');
        if (userData.email && !/\S+@\S+\.\S+/.test(userData.email)) {
          errors.push('Valid email is required');
        }
        break;
      case 2:
        if (!userData.trading_experience) errors.push('Trading experience is required');
        if (!userData.risk_tolerance) errors.push('Risk tolerance is required');
        break;
    }

    return errors;
  };

  const handleRegistrationSubmit = async () => {
    setLoading(true);
    setValidationErrors([]);

    try {
      const registrationData = {
        ...userData,
        registration_type: registrationType,
        invitation_code: registrationType === 'invitation' ? invitationCode : null,
        invitation_tier: invitationTier,
        token: 'demo-token-' + Date.now()
      };

      if (onRegister) {
        await onRegister(registrationData);
      } else if (onRegistrationSubmit) {
        await onRegistrationSubmit(registrationData);
      }

      setActiveStep(3);
    } catch (error) {
      setValidationErrors(['Registration failed. Please try again.']);
    } finally {
      setLoading(false);
    }
  };

  const investmentGoals = [
    'Capital Preservation',
    'Income Generation',
    'Growth',
    'Speculation',
    'Retirement Planning',
    'Tax Optimization'
  ];

  const handleGoalToggle = (goal: string) => {
    setUserData(prev => ({
      ...prev,
      investment_goals: prev.investment_goals.includes(goal)
        ? prev.investment_goals.filter(g => g !== goal)
        : [...prev.investment_goals, goal]
    }));
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
  };

  return (
    <Box className="registration-container" sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      p: 2
    }}>
      {/* Floating Particles */}
      <div className="floating-particles">
        {[...Array(9)].map((_, i) => (
          <div key={i} className="particle" />
        ))}
      </div>

      <Card className="registration-card" sx={{
        maxWidth: 900,
        width: '100%',
        background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
        border: '1px solid #00d4ff',
        borderRadius: 3,
        overflow: 'hidden'
      }}>
        {/* Header */}
        <Box className="header-gradient" sx={{
          background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
          p: 4,
          textAlign: 'center'
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <Logo size="large" />
          </Box>
          <Typography variant="h3" sx={{ fontWeight: 700, color: '#ffffff', mb: 1 }}>
            🚀 NeuroForge™ Trading Platform
          </Typography>
          <Typography variant="h6" sx={{ color: '#ffffff', opacity: 0.9 }}>
            Join the Future of AI-Powered Trading
          </Typography>
        </Box>

        <CardContent sx={{ p: 4 }}>
          {/* Progress Stepper */}
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel sx={{
                  '& .MuiStepLabel-label': { color: '#ffffff' },
                  '& .MuiStepIcon-root': { color: '#00d4ff' },
                  '& .MuiStepIcon-root.Mui-active': { color: '#00d4ff' },
                  '& .MuiStepIcon-root.Mui-completed': { color: '#4caf50' }
                }}>
                  {label}
                </StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Error Messages */}
          {validationErrors.length > 0 && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {validationErrors.map((error, index) => (
                <div key={index}>{error}</div>
              ))}
            </Alert>
          )}

          {/* Step 1: Registration Type Selection */}
          {activeStep === 0 && (
            <Box>
              <Typography variant="h4" sx={{ textAlign: 'center', color: '#ffffff', mb: 4, fontWeight: 600 }}>
                Choose Your Path to Success
              </Typography>

              <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* 48-Hour Demo */}
                <Grid item xs={12} md={4}>
                  <Card
                    className={`tier-card ${registrationType === 'demo' ? 'selected' : ''}`}
                    onClick={() => setRegistrationType('demo')}
                    sx={{
                      cursor: 'pointer',
                      background: registrationType === 'demo'
                        ? 'linear-gradient(135deg, #00d4ff, #0099cc)'
                        : 'linear-gradient(135deg, #2a2a2a, #3a3a3a)',
                      border: registrationType === 'demo' ? '2px solid #00d4ff' : '1px solid #444',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 25px rgba(0, 212, 255, 0.3)'
                      }
                    }}
                  >
                    <CardContent sx={{ textAlign: 'center', p: 3 }}>
                      <Diamond sx={{ fontSize: 48, color: '#ffd700', mb: 2 }} />
                      <Typography variant="h6" sx={{ fontWeight: 700, color: '#ffffff', mb: 1 }}>
                        48-Hour Live Demo
                      </Typography>
                      <Chip
                        label="RECOMMENDED"
                        size="small"
                        sx={{ backgroundColor: '#ffd700', color: '#000', fontWeight: 600, mb: 2 }}
                      />
                      <Typography variant="body2" sx={{ color: '#ffffff', opacity: 0.9, mb: 2 }}>
                        Experience real money trading with AI learning
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                        <CheckCircle sx={{ color: '#4caf50', fontSize: 16 }} />
                        <Typography variant="body2" sx={{ color: '#4caf50' }}>
                          Real profits, real results
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Invitation Code */}
                <Grid item xs={12} md={4}>
                  <Card
                    className={`tier-card ${registrationType === 'invitation' ? 'selected' : ''}`}
                    onClick={() => setRegistrationType('invitation')}
                    sx={{
                      cursor: 'pointer',
                      background: registrationType === 'invitation'
                        ? 'linear-gradient(135deg, #9c27b0, #7b1fa2)'
                        : 'linear-gradient(135deg, #2a2a2a, #3a3a3a)',
                      border: registrationType === 'invitation' ? '2px solid #9c27b0' : '1px solid #444',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 25px rgba(156, 39, 176, 0.3)'
                      }
                    }}
                  >
                    <CardContent sx={{ textAlign: 'center', p: 3 }}>
                      <Verified sx={{ fontSize: 48, color: '#9c27b0', mb: 2 }} />
                      <Typography variant="h6" sx={{ fontWeight: 700, color: '#ffffff', mb: 1 }}>
                        Invitation Code
                      </Typography>
                      <Chip
                        label="EXCLUSIVE"
                        size="small"
                        sx={{ backgroundColor: '#9c27b0', color: '#ffffff', fontWeight: 600, mb: 2 }}
                      />
                      <Typography variant="body2" sx={{ color: '#ffffff', opacity: 0.9, mb: 2 }}>
                        Join with premium tier benefits
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                        <Star sx={{ color: '#ffd700', fontSize: 16 }} />
                        <Typography variant="body2" sx={{ color: '#ffd700' }}>
                          Premium access
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Self Registration */}
                <Grid item xs={12} md={4}>
                  <Card
                    className={`tier-card ${registrationType === 'self' ? 'selected' : ''}`}
                    onClick={() => setRegistrationType('self')}
                    sx={{
                      cursor: 'pointer',
                      background: registrationType === 'self'
                        ? 'linear-gradient(135deg, #4caf50, #45a049)'
                        : 'linear-gradient(135deg, #2a2a2a, #3a3a3a)',
                      border: registrationType === 'self' ? '2px solid #4caf50' : '1px solid #444',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 25px rgba(76, 175, 80, 0.3)'
                      }
                    }}
                  >
                    <CardContent sx={{ textAlign: 'center', p: 3 }}>
                      <AccountCircle sx={{ fontSize: 48, color: '#4caf50', mb: 2 }} />
                      <Typography variant="h6" sx={{ fontWeight: 700, color: '#ffffff', mb: 1 }}>
                        Self Registration
                      </Typography>
                      <Chip
                        label="STANDARD"
                        size="small"
                        sx={{ backgroundColor: '#4caf50', color: '#ffffff', fontWeight: 600, mb: 2 }}
                      />
                      <Typography variant="body2" sx={{ color: '#ffffff', opacity: 0.9, mb: 2 }}>
                        Request platform access
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                        <Security sx={{ color: '#4caf50', fontSize: 16 }} />
                        <Typography variant="body2" sx={{ color: '#4caf50' }}>
                          Secure approval
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Demo Tier Selection */}
              {registrationType === 'demo' && (
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" sx={{ color: '#ffffff', mb: 3, textAlign: 'center' }}>
                    Select Your Demo Investment Amount
                  </Typography>
                  <Grid container spacing={2}>
                    {Object.entries(demoTiers).map(([key, tier]) => (
                      <Grid item xs={6} md={3} key={key}>
                        <Card
                          onClick={() => setUserData(prev => ({ ...prev, preferred_tier: key, demo_amount: tier.amount }))}
                          sx={{
                            cursor: 'pointer',
                            background: userData.preferred_tier === key
                              ? 'linear-gradient(135deg, #ffd700, #ffb300)'
                              : 'linear-gradient(135deg, #3a3a3a, #4a4a4a)',
                            border: userData.preferred_tier === key ? '2px solid #ffd700' : '1px solid #555',
                            transition: 'all 0.3s ease',
                            '&:hover': { transform: 'scale(1.05)' }
                          }}
                        >
                          <CardContent sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h6" sx={{ fontWeight: 700, color: userData.preferred_tier === key ? '#000' : '#fff' }}>
                              {formatCurrency(tier.amount)}
                            </Typography>
                            <Typography variant="body2" sx={{ color: userData.preferred_tier === key ? '#000' : '#ccc', mb: 1 }}>
                              {tier.name}
                            </Typography>
                            <Typography variant="caption" sx={{ color: userData.preferred_tier === key ? '#000' : '#aaa' }}>
                              {tier.return}% Expected Return
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {/* Invitation Code Input */}
              {registrationType === 'invitation' && (
                <Box sx={{ mb: 4 }}>
                  <TextField
                    fullWidth
                    label="Invitation Code"
                    value={invitationCode}
                    onChange={(e) => setInvitationCode(e.target.value)}
                    placeholder="Enter your exclusive invitation code"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '& fieldset': { borderColor: '#9c27b0' },
                        '&:hover fieldset': { borderColor: '#ba68c8' },
                        '&.Mui-focused fieldset': { borderColor: '#9c27b0' }
                      },
                      '& .MuiInputLabel-root': { color: '#9c27b0' },
                      '& .MuiOutlinedInput-input': { color: '#ffffff' }
                    }}
                  />
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handleInvitationCodeSubmit}
                    disabled={loading || !invitationCode}
                    sx={{
                      mt: 2,
                      background: 'linear-gradient(45deg, #9c27b0, #7b1fa2)',
                      '&:hover': { background: 'linear-gradient(45deg, #ba68c8, #9c27b0)' }
                    }}
                  >
                    {loading ? 'Validating...' : 'Validate Invitation Code'}
                  </Button>
                </Box>
              )}

              {/* Continue Button */}
              {(registrationType === 'demo' || registrationType === 'self') && (
                <Button
                  fullWidth
                  variant="contained"
                  onClick={handleNext}
                  sx={{
                    background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                    '&:hover': { background: 'linear-gradient(45deg, #33ddff, #00b3e6)' },
                    py: 1.5,
                    fontSize: '1.1rem',
                    fontWeight: 600
                  }}
                >
                  Continue to Registration
                </Button>
              )}
            </Box>
          )}

          {/* Step 2: Personal Information */}
          {activeStep === 1 && (
            <Box>
              <Typography variant="h4" sx={{ textAlign: 'center', color: '#ffffff', mb: 2, fontWeight: 600 }}>
                Personal Information
              </Typography>
              <Typography variant="body1" sx={{ textAlign: 'center', color: '#cccccc', mb: 4 }}>
                {registrationType === 'invitation'
                  ? `Welcome! Your ${invitationTier} tier invitation is validated. Complete your profile.`
                  : registrationType === 'demo'
                  ? `Set up your ${formatCurrency(userData.demo_amount)} live trading demo account.`
                  : 'Provide your details to request platform access.'
                }
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="First Name"
                    required
                    value={userData.first_name}
                    onChange={(e) => setUserData(prev => ({...prev, first_name: e.target.value}))}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '& fieldset': { borderColor: '#00d4ff' },
                        '&:hover fieldset': { borderColor: '#33ddff' },
                        '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                      },
                      '& .MuiInputLabel-root': { color: '#00d4ff' },
                      '& .MuiOutlinedInput-input': { color: '#ffffff' }
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    required
                    value={userData.last_name}
                    onChange={(e) => setUserData(prev => ({...prev, last_name: e.target.value}))}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '& fieldset': { borderColor: '#00d4ff' },
                        '&:hover fieldset': { borderColor: '#33ddff' },
                        '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                      },
                      '& .MuiInputLabel-root': { color: '#00d4ff' },
                      '& .MuiOutlinedInput-input': { color: '#ffffff' }
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    type="email"
                    required
                    value={userData.email}
                    onChange={(e) => setUserData(prev => ({...prev, email: e.target.value}))}
                    InputProps={{
                      startAdornment: <Email sx={{ color: '#00d4ff', mr: 1 }} />
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '& fieldset': { borderColor: '#00d4ff' },
                        '&:hover fieldset': { borderColor: '#33ddff' },
                        '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                      },
                      '& .MuiInputLabel-root': { color: '#00d4ff' },
                      '& .MuiOutlinedInput-input': { color: '#ffffff' }
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Phone Number"
                    type="tel"
                    value={userData.phone}
                    onChange={(e) => setUserData(prev => ({...prev, phone: e.target.value}))}
                    InputProps={{
                      startAdornment: <Phone sx={{ color: '#00d4ff', mr: 1 }} />
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '& fieldset': { borderColor: '#00d4ff' },
                        '&:hover fieldset': { borderColor: '#33ddff' },
                        '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                      },
                      '& .MuiInputLabel-root': { color: '#00d4ff' },
                      '& .MuiOutlinedInput-input': { color: '#ffffff' }
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Date of Birth"
                    type="date"
                    value={userData.date_of_birth}
                    onChange={(e) => setUserData(prev => ({...prev, date_of_birth: e.target.value}))}
                    InputLabelProps={{ shrink: true }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '& fieldset': { borderColor: '#00d4ff' },
                        '&:hover fieldset': { borderColor: '#33ddff' },
                        '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                      },
                      '& .MuiInputLabel-root': { color: '#00d4ff' },
                      '& .MuiOutlinedInput-input': { color: '#ffffff' }
                    }}
                  />
                </Grid>
              </Grid>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                <Button
                  onClick={handleBack}
                  sx={{ color: '#cccccc' }}
                >
                  Back
                </Button>
                <Button
                  variant="contained"
                  onClick={handleNext}
                  sx={{
                    background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                    '&:hover': { background: 'linear-gradient(45deg, #33ddff, #00b3e6)' }
                  }}
                >
                  Continue
                </Button>
              </Box>
            </Box>
          )}

          {/* Step 3: Trading Profile */}
          {activeStep === 2 && (
            <Box>
              <Typography variant="h4" sx={{ textAlign: 'center', color: '#ffffff', mb: 2, fontWeight: 600 }}>
                Trading Profile
              </Typography>
              <Typography variant="body1" sx={{ textAlign: 'center', color: '#cccccc', mb: 4 }}>
                Help us customize your trading experience
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel sx={{ color: '#00d4ff' }}>Trading Experience</InputLabel>
                    <Select
                      value={userData.trading_experience}
                      onChange={(e) => setUserData(prev => ({...prev, trading_experience: e.target.value}))}
                      sx={{
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '& .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' },
                        '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#33ddff' },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' },
                        '& .MuiSelect-select': { color: '#ffffff' }
                      }}
                    >
                      <MenuItem value="beginner">Beginner (0-1 years)</MenuItem>
                      <MenuItem value="intermediate">Intermediate (1-5 years)</MenuItem>
                      <MenuItem value="advanced">Advanced (5+ years)</MenuItem>
                      <MenuItem value="expert">Expert (Professional trader)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel sx={{ color: '#00d4ff' }}>Risk Tolerance</InputLabel>
                    <Select
                      value={userData.risk_tolerance}
                      onChange={(e) => setUserData(prev => ({...prev, risk_tolerance: e.target.value}))}
                      sx={{
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '& .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' },
                        '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#33ddff' },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' },
                        '& .MuiSelect-select': { color: '#ffffff' }
                      }}
                    >
                      <MenuItem value="conservative">Conservative</MenuItem>
                      <MenuItem value="moderate">Moderate</MenuItem>
                      <MenuItem value="aggressive">Aggressive</MenuItem>
                      <MenuItem value="speculative">Speculative</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="h6" sx={{ color: '#ffffff', mb: 2 }}>
                    Investment Goals
                  </Typography>
                  <Grid container spacing={1}>
                    {investmentGoals.map(goal => (
                      <Grid item xs={6} md={4} key={goal}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={userData.investment_goals.includes(goal)}
                              onChange={() => handleGoalToggle(goal)}
                              sx={{ color: '#00d4ff', '&.Mui-checked': { color: '#00d4ff' } }}
                            />
                          }
                          label={<Typography sx={{ color: '#ffffff', fontSize: '0.9rem' }}>{goal}</Typography>}
                        />
                      </Grid>
                    ))}
                  </Grid>
                </Grid>
              </Grid>

              {/* Revolutionary Features Showcase */}
              <Card className="features-showcase" sx={{
                mt: 4,
                background: 'linear-gradient(135deg, #ffd700, #ffb300)',
                border: '2px solid #ffd700'
              }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#000', mb: 2, textAlign: 'center' }}>
                    🎯 Revolutionary Features You'll Access
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <TrendingUp sx={{ color: '#000', mr: 1 }} />
                        <Typography sx={{ color: '#000', fontWeight: 600 }}>
                          ⚛️ Quantum Trading Engine (1000x faster)
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Security sx={{ color: '#000', mr: 1 }} />
                        <Typography sx={{ color: '#000', fontWeight: 600 }}>
                          🧠 Neural Interface (thought-based trading)
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Diamond sx={{ color: '#000', mr: 1 }} />
                        <Typography sx={{ color: '#000', fontWeight: 600 }}>
                          🌟 Holographic UI (3D visualization)
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Star sx={{ color: '#000', mr: 1 }} />
                        <Typography sx={{ color: '#000', fontWeight: 600 }}>
                          🧠 AI Consciousness (self-aware decisions)
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Verified sx={{ color: '#000', mr: 1 }} />
                        <Typography sx={{ color: '#000', fontWeight: 600 }}>
                          🔗 Blockchain Trading (100% transparency)
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <CheckCircle sx={{ color: '#000', mr: 1 }} />
                        <Typography sx={{ color: '#000', fontWeight: 600 }}>
                          🚀 48-Hour Live Demo System
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                <Button
                  onClick={handleBack}
                  sx={{ color: '#cccccc' }}
                >
                  Back
                </Button>
                <Button
                  className="button-glow"
                  variant="contained"
                  onClick={handleRegistrationSubmit}
                  disabled={loading}
                  sx={{
                    background: 'linear-gradient(45deg, #ffd700, #ffb300)',
                    color: '#000',
                    fontWeight: 700,
                    '&:hover': { background: 'linear-gradient(45deg, #ffdd33, #ffc107)' }
                  }}
                >
                  {loading ? 'Submitting...' : 'Complete Registration'}
                </Button>
              </Box>
            </Box>
          )}

          {/* Step 4: Confirmation */}
          {activeStep === 3 && (
            <Box sx={{ textAlign: 'center' }}>
              <CheckCircle className="success-animation" sx={{ fontSize: 80, color: '#4caf50', mb: 3 }} />
              <Typography variant="h3" sx={{ color: '#ffffff', fontWeight: 700, mb: 2 }}>
                Registration Complete!
              </Typography>
              <Typography variant="h6" sx={{ color: '#cccccc', mb: 4 }}>
                {registrationType === 'demo' &&
                  `Your ${formatCurrency(userData.demo_amount)} live trading demo is being prepared.`
                }
                {registrationType === 'invitation' &&
                  `Welcome to your ${invitationTier} tier access! Your account is being activated.`
                }
                {registrationType === 'self' &&
                  'Your registration is under review. You\'ll receive an email once approved.'
                }
              </Typography>

              {registrationType === 'demo' && (
                <Card sx={{
                  background: 'linear-gradient(135deg, #00d4ff, #0099cc)',
                  mb: 3
                }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: '#ffffff', mb: 2 }}>
                      🎯 Your 48-Hour Demo Details
                    </Typography>
                    <Typography sx={{ color: '#ffffff', mb: 1 }}>
                      Investment Amount: {formatCurrency(userData.demo_amount)}
                    </Typography>
                    <Typography sx={{ color: '#ffffff', mb: 1 }}>
                      Expected Return: {demoTiers[userData.preferred_tier as keyof typeof demoTiers].return}%
                    </Typography>
                    <Typography sx={{ color: '#ffffff' }}>
                      Risk Level: {demoTiers[userData.preferred_tier as keyof typeof demoTiers].risk}
                    </Typography>
                  </CardContent>
                </Card>
              )}

              <Button
                variant="contained"
                size="large"
                sx={{
                  background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                  '&:hover': { background: 'linear-gradient(45deg, #33ddff, #00b3e6)' },
                  px: 4,
                  py: 1.5
                }}
              >
                Continue to Dashboard
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default UserRegistration; 