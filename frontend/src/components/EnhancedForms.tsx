import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  IconButton,
  InputAdornment,
  FormHelperText,
  Fade,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Person,
  Phone,
  Business,
  Description,
  Add,
  Delete,
  Save,
  Cancel
} from '@mui/icons-material';
import ModernCard from './ModernCard';

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  phone: string;
  company: string;
  role: string;
  description: string;
  tags: string[];
  newTag: string;
}

interface ValidationErrors {
  [key: string]: string;
}

const EnhancedForms: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [formData, setFormData] = useState<FormData>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    company: '',
    role: '',
    description: '',
    tags: [],
    newTag: ''
  });

  const [errors, setErrors] = useState<ValidationErrors>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const validateField = (name: string, value: string): string => {
    switch (name) {
      case 'firstName':
        return value.length < 2 ? 'First name must be at least 2 characters' : '';
      case 'lastName':
        return value.length < 2 ? 'Last name must be at least 2 characters' : '';
      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return !emailRegex.test(value) ? 'Please enter a valid email address' : '';
      case 'password':
        return value.length < 8 ? 'Password must be at least 8 characters' : '';
      case 'confirmPassword':
        return value !== formData.password ? 'Passwords do not match' : '';
      case 'phone':
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return value && !phoneRegex.test(value.replace(/\s/g, '')) ? 'Please enter a valid phone number' : '';
      case 'company':
        return value.length < 2 ? 'Company name must be at least 2 characters' : '';
      case 'role':
        return !value ? 'Please select a role' : '';
      default:
        return '';
    }
  };

  const handleInputChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleBlur = (name: string) => {
    const error = validateField(name, formData[name as keyof FormData] as string);
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  const handleAddTag = () => {
    if (formData.newTag.trim() && !formData.tags.includes(formData.newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, prev.newTag.trim()],
        newTag: ''
      }));
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate all fields
    const newErrors: ValidationErrors = {};
    Object.keys(formData).forEach(key => {
      if (key !== 'tags' && key !== 'newTag') {
        const error = validateField(key, formData[key as keyof FormData] as string);
        if (error) newErrors[key] = error;
      }
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsSubmitting(false);
    setSubmitSuccess(true);
    
    // Reset form after 3 seconds
    setTimeout(() => {
      setFormData({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        confirmPassword: '',
        phone: '',
        company: '',
        role: '',
        description: '',
        tags: [],
        newTag: ''
      });
      setErrors({});
      setSubmitSuccess(false);
    }, 3000);
  };

  const renderInputField = (
    name: keyof FormData,
    label: string,
    type: string = 'text',
    icon?: React.ReactNode,
    multiline: boolean = false,
    rows: number = 1
  ) => (
    <TextField
      fullWidth
      label={label}
      type={type}
      value={formData[name]}
      onChange={(e) => handleInputChange(name, e.target.value)}
      onBlur={() => handleBlur(name)}
      error={!!errors[name]}
      helperText={errors[name]}
      multiline={multiline}
      rows={rows}
      InputProps={{
        startAdornment: icon ? (
          <InputAdornment position="start">
            {icon}
          </InputAdornment>
        ) : undefined,
        endAdornment: (name === 'password' || name === 'confirmPassword') ? (
          <InputAdornment position="end">
            <IconButton
              onClick={() => {
                if (name === 'password') setShowPassword(!showPassword);
                else setShowConfirmPassword(!showConfirmPassword);
              }}
              edge="end"
            >
              {((name === 'password' && showPassword) || (name === 'confirmPassword' && showConfirmPassword)) ? 
                <VisibilityOff /> : <Visibility />
              }
            </IconButton>
          </InputAdornment>
        ) : undefined
      }}
      sx={{
        '& .MuiOutlinedInput-root': {
          '& fieldset': {
            borderColor: 'rgba(255,255,255,0.2)',
          },
          '&:hover fieldset': {
            borderColor: 'rgba(255,255,255,0.3)',
          },
          '&.Mui-focused fieldset': {
            borderColor: theme.palette.primary.main,
          },
        },
        '& .MuiInputLabel-root': {
          color: 'rgba(255,255,255,0.7)',
        },
        '& .MuiInputBase-input': {
          color: 'white',
        },
        '& .MuiFormHelperText-root': {
          color: theme.palette.error.main,
        },
      }}
    />
  );

  return (
    <Fade in={true} timeout={800}>
      <Box sx={{ p: { xs: 2, md: 3 } }}>
        <Typography 
          variant="h4" 
          sx={{ 
            mb: 4, 
            fontWeight: 700,
            background: 'linear-gradient(135deg, #6366f1 0%, #10b981 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          Enhanced Forms
        </Typography>

        {submitSuccess && (
          <Alert 
            severity="success" 
            sx={{ mb: 3 }}
            onClose={() => setSubmitSuccess(false)}
          >
            Form submitted successfully! Your data has been saved.
          </Alert>
        )}

        <ModernCard
          title="User Registration"
          subtitle="Complete your profile information"
          content={
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  {renderInputField('firstName', 'First Name', 'text', <Person />)}
                </Grid>
                <Grid item xs={12} sm={6}>
                  {renderInputField('lastName', 'Last Name', 'text', <Person />)}
                </Grid>
                <Grid item xs={12}>
                  {renderInputField('email', 'Email Address', 'email', <Email />)}
                </Grid>
                <Grid item xs={12} sm={6}>
                  {renderInputField('password', 'Password', showPassword ? 'text' : 'password', <Lock />)}
                </Grid>
                <Grid item xs={12} sm={6}>
                  {renderInputField('confirmPassword', 'Confirm Password', showConfirmPassword ? 'text' : 'password', <Lock />)}
                </Grid>
                <Grid item xs={12} sm={6}>
                  {renderInputField('phone', 'Phone Number', 'tel', <Phone />)}
                </Grid>
                <Grid item xs={12} sm={6}>
                  {renderInputField('company', 'Company', 'text', <Business />)}
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth error={!!errors.role}>
                    <InputLabel sx={{ color: 'rgba(255,255,255,0.7)' }}>Role</InputLabel>
                    <Select
                      value={formData.role}
                      onChange={(e) => handleInputChange('role', e.target.value)}
                      onBlur={() => handleBlur('role')}
                      sx={{
                        color: 'white',
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'rgba(255,255,255,0.2)',
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'rgba(255,255,255,0.3)',
                        },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                          borderColor: theme.palette.primary.main,
                        },
                      }}
                    >
                      <MenuItem value="developer">Developer</MenuItem>
                      <MenuItem value="designer">Designer</MenuItem>
                      <MenuItem value="manager">Manager</MenuItem>
                      <MenuItem value="analyst">Analyst</MenuItem>
                      <MenuItem value="admin">Administrator</MenuItem>
                    </Select>
                    {errors.role && (
                      <FormHelperText sx={{ color: theme.palette.error.main }}>
                        {errors.role}
                      </FormHelperText>
                    )}
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  {renderInputField('description', 'Description', 'text', <Description />, true, 3)}
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
                    Tags
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    {formData.tags.map((tag, index) => (
                      <Chip
                        key={index}
                        label={tag}
                        onDelete={() => handleRemoveTag(tag)}
                        sx={{
                          backgroundColor: 'rgba(99, 102, 241, 0.2)',
                          color: 'white',
                          '& .MuiChip-deleteIcon': {
                            color: 'rgba(255,255,255,0.7)',
                          },
                        }}
                      />
                    ))}
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      size="small"
                      placeholder="Add a tag"
                      value={formData.newTag}
                      onChange={(e) => handleInputChange('newTag', e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                      sx={{
                        flex: 1,
                        '& .MuiOutlinedInput-root': {
                          '& fieldset': {
                            borderColor: 'rgba(255,255,255,0.2)',
                          },
                          '&:hover fieldset': {
                            borderColor: 'rgba(255,255,255,0.3)',
                          },
                        },
                        '& .MuiInputBase-input': {
                          color: 'white',
                        },
                      }}
                    />
                    <Button
                      variant="outlined"
                      onClick={handleAddTag}
                      disabled={!formData.newTag.trim()}
                      startIcon={<Add />}
                      sx={{
                        borderColor: 'rgba(255,255,255,0.3)',
                        color: 'white',
                        '&:hover': {
                          borderColor: theme.palette.primary.main,
                          backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        },
                      }}
                    >
                      Add
                    </Button>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                    <Button
                      variant="outlined"
                      onClick={() => {
                        setFormData({
                          firstName: '',
                          lastName: '',
                          email: '',
                          password: '',
                          confirmPassword: '',
                          phone: '',
                          company: '',
                          role: '',
                          description: '',
                          tags: [],
                          newTag: ''
                        });
                        setErrors({});
                      }}
                      startIcon={<Cancel />}
                      sx={{
                        borderColor: 'rgba(255,255,255,0.3)',
                        color: 'white',
                        '&:hover': {
                          borderColor: theme.palette.error.main,
                          backgroundColor: 'rgba(244, 67, 54, 0.1)',
                        },
                      }}
                    >
                      Reset
                    </Button>
                    <Button
                      type="submit"
                      variant="contained"
                      disabled={isSubmitting}
                      startIcon={isSubmitting ? undefined : <Save />}
                      sx={{
                        background: 'linear-gradient(135deg, #6366f1 0%, #10b981 100%)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #5b5fdb 0%, #059669 100%)',
                          transform: 'translateY(-1px)',
                          boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)',
                        },
                        '&:disabled': {
                          background: 'rgba(255,255,255,0.1)',
                        },
                      }}
                    >
                      {isSubmitting ? 'Submitting...' : 'Submit'}
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          }
          status="info"
        />
      </Box>
    </Fade>
  );
};

export default EnhancedForms; 