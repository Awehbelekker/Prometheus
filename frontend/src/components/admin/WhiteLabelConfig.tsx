/**
 * WhiteLabelConfig Component
 * Admin panel for configuring white-label settings
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Grid,
  Divider,
  Alert,
  Tabs,
  Tab
} from '@mui/material';
import {
  Save,
  Refresh,
  Palette,
  Business,
  Settings,
  Code
} from '@mui/icons-material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import { apiCall } from '../../config/api';
import { WhiteLabelConfig as WhiteLabelConfigType } from '../../config/whiteLabel';

const WhiteLabelConfig: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();

  const { data: config, isLoading } = useQuery({
    queryKey: ['white-label-config'],
    queryFn: async () => {
      const response = await apiCall('/api/white-label/config');
      return response as WhiteLabelConfigType;
    }
  });

  const [formData, setFormData] = useState<WhiteLabelConfigType | null>(null);

  React.useEffect(() => {
    if (config && !formData) {
      setFormData(config);
    }
  }, [config, formData]);

  const saveMutation = useMutation({
    mutationFn: async (data: WhiteLabelConfigType) => {
      return await apiCall('/api/white-label/config', {
        method: 'PUT',
        body: JSON.stringify(data)
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['white-label-config'] });
      enqueueSnackbar('White-label configuration saved successfully!', { variant: 'success' });
    },
    onError: () => {
      enqueueSnackbar('Failed to save configuration', { variant: 'error' });
    }
  });

  const handleSave = () => {
    if (formData) {
      saveMutation.mutate(formData);
    }
  };

  const handleReset = () => {
    setFormData(config || null);
    enqueueSnackbar('Configuration reset to saved values', { variant: 'info' });
  };

  if (isLoading || !formData) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Card
      sx={{
        background: 'rgba(26, 26, 26, 0.95)',
        border: '1px solid rgba(0, 212, 255, 0.3)',
        borderRadius: 3
      }}
    >
      <CardContent sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Palette sx={{ color: '#00d4ff', fontSize: 32 }} />
            <Typography variant="h5" sx={{ color: '#fff', fontWeight: 700 }}>
              White-Label Configuration
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={handleReset}
              sx={{ color: '#888', borderColor: '#888' }}
            >
              Reset
            </Button>
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
              disabled={saveMutation.isPending}
              sx={{
                background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                color: '#000'
              }}
            >
              Save Changes
            </Button>
          </Box>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          Configure your platform's branding, theme, and features. Changes will be applied after saving.
        </Alert>

        {/* Tabs */}
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{
            mb: 3,
            '& .MuiTab-root': { color: '#888', '&.Mui-selected': { color: '#00d4ff' } },
            '& .MuiTabs-indicator': { backgroundColor: '#00d4ff' }
          }}
        >
          <Tab label="Branding" icon={<Business />} iconPosition="start" />
          <Tab label="Theme" icon={<Palette />} iconPosition="start" />
          <Tab label="Features" icon={<Settings />} iconPosition="start" />
          <Tab label="Advanced" icon={<Code />} iconPosition="start" />
        </Tabs>

        {/* Branding Tab */}
        {activeTab === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Company Name"
                value={formData.branding.companyName}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    branding: { ...formData.branding, companyName: e.target.value }
                  })
                }
                sx={{ '& .MuiInputBase-input': { color: '#fff' } }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Tagline"
                value={formData.branding.tagline || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    branding: { ...formData.branding, tagline: e.target.value }
                  })
                }
                sx={{ '& .MuiInputBase-input': { color: '#fff' } }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Logo URL"
                value={formData.branding.logo}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    branding: { ...formData.branding, logo: e.target.value }
                  })
                }
                sx={{ '& .MuiInputBase-input': { color: '#fff' } }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Favicon URL"
                value={formData.branding.favicon}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    branding: { ...formData.branding, favicon: e.target.value }
                  })
                }
                sx={{ '& .MuiInputBase-input': { color: '#fff' } }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Support Email"
                value={formData.contact.email || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    contact: { ...formData.contact, email: e.target.value }
                  })
                }
                sx={{ '& .MuiInputBase-input': { color: '#fff' } }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Website URL"
                value={formData.contact.website || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    contact: { ...formData.contact, website: e.target.value }
                  })
                }
                sx={{ '& .MuiInputBase-input': { color: '#fff' } }}
              />
            </Grid>
          </Grid>
        )}

        {/* Theme Tab */}
        {activeTab === 1 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Primary Color"
                type="color"
                value={formData.theme.primaryColor}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    theme: { ...formData.theme, primaryColor: e.target.value }
                  })
                }
                sx={{ '& .MuiInputBase-input': { height: 50 } }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Secondary Color"
                type="color"
                value={formData.theme.secondaryColor}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    theme: { ...formData.theme, secondaryColor: e.target.value }
                  })
                }
                sx={{ '& .MuiInputBase-input': { height: 50 } }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Accent Color"
                type="color"
                value={formData.theme.accentColor || '#ffd700'}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    theme: { ...formData.theme, accentColor: e.target.value }
                  })
                }
                sx={{ '& .MuiInputBase-input': { height: 50 } }}
              />
            </Grid>
          </Grid>
        )}

        {/* Features Tab */}
        {activeTab === 2 && (
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.features.socialFeatures}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        features: { ...formData.features, socialFeatures: e.target.checked }
                      })
                    }
                  />
                }
                label="Social Features (Leaderboard, Profiles, Follow)"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.features.aiAssistant}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        features: { ...formData.features, aiAssistant: e.target.checked }
                      })
                    }
                  />
                }
                label="AI Assistant"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.features.gamification}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        features: { ...formData.features, gamification: e.target.checked }
                      })
                    }
                  />
                }
                label="Gamification (XP, Levels, Achievements)"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.features.notifications}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        features: { ...formData.features, notifications: e.target.checked }
                      })
                    }
                  />
                }
                label="Notifications"
              />
            </Grid>
          </Grid>
        )}

        {/* Advanced Tab */}
        {activeTab === 3 && (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={6}
                label="Custom CSS"
                value={formData.customization.customCSS || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    customization: { ...formData.customization, customCSS: e.target.value }
                  })
                }
                placeholder="/* Add custom CSS here */"
                sx={{ '& .MuiInputBase-input': { color: '#fff', fontFamily: 'monospace' } }}
              />
            </Grid>
          </Grid>
        )}
      </CardContent>
    </Card>
  );
};

export default WhiteLabelConfig;

