import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  PersonAdd,
  Email,
  ContentCopy,
  CheckCircle,
  Pending,
  Cancel,
  Send,
  Link as LinkIcon,
  Group,
  TrendingUp,
  Security,
  Psychology
} from '@mui/icons-material';
import { apiCall } from '../config/api';

interface Invitation {
  id: string;
  email: string;
  role: string;
  status: 'pending' | 'accepted' | 'expired';
  createdAt: Date;
  expiresAt: Date;
  inviteLink: string;
  inviteMessage?: string;
  accessLevel: string;
}

interface InvitationStats {
  totalSent: number;
  totalAccepted: number;
  totalPending: number;
  totalExpired: number;
  acceptanceRate: number;
}

/**
 * User Invitation System
 * 
 * Allows admins to invite users to experience the trading platform
 * with different access levels and trial periods.
 */
const UserInvitationSystem: React.FC = () => {
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [inviteForm, setInviteForm] = useState({
    email: '',
    role: 'trial_user',
    accessLevel: 'demo',
    inviteMessage: '',
    trialDuration: '7' // days
  });
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [stats, setStats] = useState<InvitationStats>({
    totalSent: 0,
    totalAccepted: 0,
    totalPending: 0,
    totalExpired: 0,
    acceptanceRate: 0
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Initialize with mock data
  useEffect(() => {
    initializeMockData();
  }, []);

  const initializeMockData = () => {
    const mockInvitations: Invitation[] = [
      {
        id: 'inv_001',
        email: 'investor@example.com',
        role: 'premium_user',
        status: 'accepted',
        createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
        expiresAt: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000),
        inviteLink: 'https://prometheus.trading/invite/inv_001',
        accessLevel: 'full',
        inviteMessage: 'Welcome to the future of AI trading!'
      },
      {
        id: 'inv_002',
        email: 'trader@example.com',
        role: 'trial_user',
        status: 'pending',
        createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
        expiresAt: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000),
        inviteLink: 'https://prometheus.trading/invite/inv_002',
        accessLevel: 'demo',
        inviteMessage: 'Experience revolutionary AI trading technology'
      },
      {
        id: 'inv_003',
        email: 'analyst@example.com',
        role: 'professional',
        status: 'pending',
        createdAt: new Date(Date.now() - 3 * 60 * 60 * 1000),
        expiresAt: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000),
        inviteLink: 'https://prometheus.trading/invite/inv_003',
        accessLevel: 'professional',
        inviteMessage: 'Join our professional trading community'
      }
    ];

    setInvitations(mockInvitations);
    updateStats(mockInvitations);
  };

  const updateStats = (invitationList: Invitation[]) => {
    const totalSent = invitationList.length;
    const totalAccepted = invitationList.filter(inv => inv.status === 'accepted').length;
    const totalPending = invitationList.filter(inv => inv.status === 'pending').length;
    const totalExpired = invitationList.filter(inv => inv.status === 'expired').length;
    const acceptanceRate = totalSent > 0 ? (totalAccepted / totalSent) * 100 : 0;

    setStats({
      totalSent,
      totalAccepted,
      totalPending,
      totalExpired,
      acceptanceRate
    });
  };

  const handleSendInvitation = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await apiCall('/api/admin/invite-user', {
        method: 'POST',
        headers: { 'X-Admin-ID': 'admin-user' },
        body: JSON.stringify({
          email: inviteForm.email,
          role: inviteForm.role,
          tier: inviteForm.accessLevel
        })
      });

      const newInvitation: Invitation = {
        id: result.user_id || `inv_${Date.now()}`,
        email: inviteForm.email,
        role: inviteForm.role,
        status: 'pending',
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + parseInt(inviteForm.trialDuration) * 24 * 60 * 60 * 1000),
        inviteLink: `https://prometheus-trade.com/register?token=${result.user_id}`,
        accessLevel: inviteForm.accessLevel,
        inviteMessage: inviteForm.inviteMessage
      };

      const updatedInvitations = [newInvitation, ...invitations];
      setInvitations(updatedInvitations);
      updateStats(updatedInvitations);

      setSuccess(`Invitation sent successfully to ${inviteForm.email}! ${result.message || ''}`);
      setInviteDialogOpen(false);
      setInviteForm({
        email: '',
        role: 'trial_user',
        accessLevel: 'demo',
        inviteMessage: '',
        trialDuration: '7'
      });
    } catch (err: any) {
      console.error('Invitation error:', err);
      setError(`Failed to send invitation: ${err?.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyInviteLink = (link: string) => {
    navigator.clipboard.writeText(link);
    setSuccess('Invite link copied to clipboard!');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted': return '#4caf50';
      case 'pending': return '#ff9800';
      case 'expired': return '#f44336';
      default: return '#666';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'accepted': return <CheckCircle sx={{ color: '#4caf50' }} />;
      case 'pending': return <Pending sx={{ color: '#ff9800' }} />;
      case 'expired': return <Cancel sx={{ color: '#f44336' }} />;
      default: return <Pending sx={{ color: '#666' }} />;
    }
  };

  const getAccessLevelColor = (level: string) => {
    switch (level) {
      case 'full': return '#4caf50';
      case 'professional': return '#2196f3';
      case 'demo': return '#ff9800';
      default: return '#666';
    }
  };

  const accessLevelFeatures = {
    demo: [
      'Virtual trading with $100K demo account',
      'Access to 5 revolutionary features',
      'Basic AI trading capabilities',
      '7-day trial period'
    ],
    professional: [
      'Live trading with real funds',
      'Access to 12 revolutionary features',
      'Advanced AI and analytics',
      'Professional support',
      '30-day trial period'
    ],
    full: [
      'Complete platform access',
      'All 18 revolutionary features',
      'Enterprise-grade AI systems',
      'Priority support and training',
      'Unlimited access'
    ]
  };

  return (
    <Box sx={{ p: 3, minHeight: '100vh', backgroundColor: '#0a0a0a' }}>
      {/* Header */}
      <Card sx={{ 
        mb: 3, 
        background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)',
        border: '2px solid #4caf50',
        borderRadius: 3
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box>
              <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 700, mb: 1 }}>
                👥 User Invitation System
              </Typography>
              <Typography variant="subtitle1" sx={{ color: '#00d4ff' }}>
                Invite Users • Demo Access • Trial Management
              </Typography>
            </Box>
            <Button
              variant="contained"
              size="large"
              startIcon={<PersonAdd />}
              onClick={() => setInviteDialogOpen(true)}
              sx={{
                background: 'linear-gradient(45deg, #4caf50 30%, #45a049 90%)',
                color: 'white',
                fontWeight: 600,
                px: 4,
                py: 1.5,
                '&:hover': {
                  transform: 'scale(1.05)',
                  boxShadow: '0 0 20px rgba(76, 175, 80, 0.5)'
                }
              }}
            >
              Send Invitation
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Success/Error Messages */}
      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Invitation Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ backgroundColor: '#1a1a1a', border: '1px solid #4caf50' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Send sx={{ fontSize: 40, color: '#4caf50', mb: 1 }} />
              <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 700 }}>
                {stats.totalSent}
              </Typography>
              <Typography variant="body2" sx={{ color: '#ccc' }}>
                Total Sent
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ backgroundColor: '#1a1a1a', border: '1px solid #2196f3' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <CheckCircle sx={{ fontSize: 40, color: '#2196f3', mb: 1 }} />
              <Typography variant="h4" sx={{ color: '#2196f3', fontWeight: 700 }}>
                {stats.totalAccepted}
              </Typography>
              <Typography variant="body2" sx={{ color: '#ccc' }}>
                Accepted
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ backgroundColor: '#1a1a1a', border: '1px solid #ff9800' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Pending sx={{ fontSize: 40, color: '#ff9800', mb: 1 }} />
              <Typography variant="h4" sx={{ color: '#ff9800', fontWeight: 700 }}>
                {stats.totalPending}
              </Typography>
              <Typography variant="body2" sx={{ color: '#ccc' }}>
                Pending
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ backgroundColor: '#1a1a1a', border: '1px solid #f44336' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Cancel sx={{ fontSize: 40, color: '#f44336', mb: 1 }} />
              <Typography variant="h4" sx={{ color: '#f44336', fontWeight: 700 }}>
                {stats.totalExpired}
              </Typography>
              <Typography variant="body2" sx={{ color: '#ccc' }}>
                Expired
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ backgroundColor: '#1a1a1a', border: '1px solid #9c27b0' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <TrendingUp sx={{ fontSize: 40, color: '#9c27b0', mb: 1 }} />
              <Typography variant="h4" sx={{ color: '#9c27b0', fontWeight: 700 }}>
                {stats.acceptanceRate.toFixed(0)}%
              </Typography>
              <Typography variant="body2" sx={{ color: '#ccc' }}>
                Acceptance Rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Invitations Table */}
      <Card sx={{ backgroundColor: '#1a1a1a', border: '1px solid #00d4ff' }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2, fontWeight: 600 }}>
            📧 Recent Invitations
          </Typography>
          <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: '#ccc', fontWeight: 600 }}>Email</TableCell>
                  <TableCell sx={{ color: '#ccc', fontWeight: 600 }}>Role</TableCell>
                  <TableCell sx={{ color: '#ccc', fontWeight: 600 }}>Access Level</TableCell>
                  <TableCell sx={{ color: '#ccc', fontWeight: 600 }}>Status</TableCell>
                  <TableCell sx={{ color: '#ccc', fontWeight: 600 }}>Created</TableCell>
                  <TableCell sx={{ color: '#ccc', fontWeight: 600 }}>Expires</TableCell>
                  <TableCell sx={{ color: '#ccc', fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {invitations.map((invitation) => (
                  <TableRow key={invitation.id}>
                    <TableCell sx={{ color: '#fff', fontWeight: 600 }}>
                      {invitation.email}
                    </TableCell>
                    <TableCell sx={{ color: '#ccc', textTransform: 'capitalize' }}>
                      {invitation.role.replace('_', ' ')}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={invitation.accessLevel.toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: `${getAccessLevelColor(invitation.accessLevel)}20`,
                          color: getAccessLevelColor(invitation.accessLevel),
                          fontWeight: 600
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getStatusIcon(invitation.status)}
                        <Typography variant="body2" sx={{ color: getStatusColor(invitation.status), textTransform: 'capitalize' }}>
                          {invitation.status}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell sx={{ color: '#ccc' }}>
                      {invitation.createdAt.toLocaleDateString()}
                    </TableCell>
                    <TableCell sx={{ color: '#ccc' }}>
                      {invitation.expiresAt.toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Copy Invite Link">
                        <IconButton
                          size="small"
                          onClick={() => handleCopyInviteLink(invitation.inviteLink)}
                          sx={{ color: '#00d4ff' }}
                        >
                          <ContentCopy />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Invitation Dialog */}
      <Dialog
        open={inviteDialogOpen}
        onClose={() => setInviteDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#1a1a1a',
            border: '1px solid #333'
          }
        }}
      >
        <DialogTitle sx={{ color: '#4caf50', fontWeight: 600 }}>
          👥 Send User Invitation
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email Address"
                value={inviteForm.email}
                onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: '#fff',
                    '& fieldset': { borderColor: '#333' },
                    '&:hover fieldset': { borderColor: '#4caf50' },
                    '&.Mui-focused fieldset': { borderColor: '#4caf50' }
                  },
                  '& .MuiInputLabel-root': { color: '#ccc' }
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel sx={{ color: '#ccc' }}>Access Level</InputLabel>
                <Select
                  value={inviteForm.accessLevel}
                  onChange={(e) => setInviteForm({ ...inviteForm, accessLevel: e.target.value })}
                  sx={{
                    color: '#fff',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: '#333' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#4caf50' },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#4caf50' }
                  }}
                >
                  <MenuItem value="demo">Demo Access</MenuItem>
                  <MenuItem value="professional">Professional</MenuItem>
                  <MenuItem value="full">Full Access</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Invitation Message"
                value={inviteForm.inviteMessage}
                onChange={(e) => setInviteForm({ ...inviteForm, inviteMessage: e.target.value })}
                placeholder="Welcome to Prometheus NeuroForge™! Experience the future of AI trading..."
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: '#fff',
                    '& fieldset': { borderColor: '#333' },
                    '&:hover fieldset': { borderColor: '#4caf50' },
                    '&.Mui-focused fieldset': { borderColor: '#4caf50' }
                  },
                  '& .MuiInputLabel-root': { color: '#ccc' }
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
                Access Level Features:
              </Typography>
              <List dense>
                {accessLevelFeatures[inviteForm.accessLevel as keyof typeof accessLevelFeatures].map((feature, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <CheckCircle sx={{ color: '#4caf50', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={feature}
                      sx={{ color: '#ccc' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button
            onClick={() => setInviteDialogOpen(false)}
            sx={{ color: '#ccc' }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSendInvitation}
            variant="contained"
            disabled={loading || !inviteForm.email}
            startIcon={loading ? undefined : <Send />}
            sx={{
              backgroundColor: '#4caf50',
              '&:hover': { backgroundColor: '#45a049' }
            }}
          >
            {loading ? 'Sending...' : 'Send Invitation'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserInvitationSystem;
