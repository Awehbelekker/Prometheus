import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Email,
  Person,
  Business,
  Phone,
  AccessTime,
  TrendingUp
} from '@mui/icons-material';
import { apiCall } from '../config/api';

interface AccessRequest {
  id: string;
  fullName: string;
  email: string;
  phone: string;
  company: string;
  investmentRange: string;
  experience: string;
  message: string;
  status: 'pending' | 'approved' | 'rejected';
  submittedAt: string;
  reviewedAt?: string;
  reviewedBy?: string;
}

interface AccessRequestManagementProps {
  user: any;
}

const AccessRequestManagement: React.FC<AccessRequestManagementProps> = ({ user }) => {
  const [requests, setRequests] = useState<AccessRequest[]>([]);
  const [selectedRequest, setSelectedRequest] = useState<AccessRequest | null>(null);
  const [showApprovalDialog, setShowApprovalDialog] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Invitation form for approved users
  const [invitationForm, setInvitationForm] = useState({
    role: 'demo',
    allocated_capital: 1000,
    expires_hours: 168,
    access_scope: 'trial48' as 'trial48' | 'full'
  });

  useEffect(() => {
    loadAccessRequests();
  }, []);

  const loadAccessRequests = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiCall('/api/access-requests');
      setRequests(data.requests || []);
    } catch (err) {
      // Mock data for development
      setRequests([
        {
          id: '1',
          fullName: 'John Smith',
          email: 'john.smith@example.com',
          phone: '+1-555-0123',
          company: 'Investment Corp',
          investmentRange: '$10,000 - $50,000',
          experience: 'Advanced',
          message: 'Interested in AI trading platform for institutional use.',
          status: 'pending',
          submittedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
        },
        {
          id: '2',
          fullName: 'Sarah Johnson',
          email: 'sarah.j@gmail.com',
          phone: '+1-555-0456',
          company: '',
          investmentRange: '$1,000 - $5,000',
          experience: 'Beginner',
          message: 'Looking to start trading with AI assistance.',
          status: 'pending',
          submittedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApproveRequest = async (request: AccessRequest) => {
    setSelectedRequest(request);
    setShowApprovalDialog(true);
  };

  const handleRejectRequest = async (requestId: string) => {
    try {
      setIsLoading(true);
      // Update request status to rejected
      setRequests(prev => prev.map(req => 
        req.id === requestId 
          ? { ...req, status: 'rejected', reviewedAt: new Date().toISOString(), reviewedBy: user.username }
          : req
      ));
      setSuccess('Access request rejected successfully');
    } catch (err) {
      setError('Failed to reject request');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendInvitation = async () => {
    if (!selectedRequest) return;

    try {
      setIsLoading(true);
      setError(null);

      const invitationData = {
        email: selectedRequest.email,
        role: invitationForm.role,
        allocated_capital: invitationForm.allocated_capital,
        expires_hours: invitationForm.expires_hours,
        access_scope: invitationForm.access_scope,
        full_name: selectedRequest.fullName,
        phone: selectedRequest.phone,
        company: selectedRequest.company
      };

      const invitation = await apiCall('/api/invitations', {
        method: 'POST',
        body: JSON.stringify(invitationData)
      });

      // Update request status to approved
      setRequests(prev => prev.map(req =>
        req.id === selectedRequest.id
          ? { ...req, status: 'approved', reviewedAt: new Date().toISOString(), reviewedBy: user.username }
          : req
      ));

      setSuccess(`✅ Invitation sent successfully to ${selectedRequest.email}!

📧 Invitation Code: ${invitation.code}
💰 Allocated Capital: $${invitation.allocated_capital}
⏰ Expires: ${invitation.expires_hours} hours
🎯 Access Level: ${invitation.access_scope}`);

      setShowApprovalDialog(false);
      setSelectedRequest(null);
    } catch (err) {
      setError('Failed to send invitation');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#4caf50';
      case 'rejected': return '#f44336';
      default: return '#ff9800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircle sx={{ color: '#4caf50' }} />;
      case 'rejected': return <Cancel sx={{ color: '#f44336' }} />;
      default: return <AccessTime sx={{ color: '#ff9800' }} />;
    }
  };

  const pendingCount = requests.filter(req => req.status === 'pending').length;
  const approvedCount = requests.filter(req => req.status === 'approved').length;
  const rejectedCount = requests.filter(req => req.status === 'rejected').length;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ color: 'white', fontWeight: 700, mb: 3 }}>
        Access Request Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #ff9800, #f57c00)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {pendingCount}
                  </Typography>
                  <Typography variant="body2">
                    Pending Requests
                  </Typography>
                </Box>
                <AccessTime sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4caf50, #388e3c)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {approvedCount}
                  </Typography>
                  <Typography variant="body2">
                    Approved
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f44336, #d32f2f)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {rejectedCount}
                  </Typography>
                  <Typography variant="body2">
                    Rejected
                  </Typography>
                </Box>
                <Cancel sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #00d4ff, #0099cc)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {requests.length}
                  </Typography>
                  <Typography variant="body2">
                    Total Requests
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Requests Table */}
      <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)' }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: 'white', mb: 2 }}>
            Recent Access Requests
          </Typography>
          
          <TableContainer component={Paper} sx={{ background: 'transparent' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Status</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Name</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Email</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Company</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Submitted</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {requests.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(request.status)}
                        label={request.status.toUpperCase()}
                        sx={{
                          backgroundColor: getStatusColor(request.status),
                          color: 'white',
                          fontWeight: 600
                        }}
                      />
                    </TableCell>
                    <TableCell sx={{ color: 'white' }}>{request.fullName}</TableCell>
                    <TableCell sx={{ color: 'white' }}>{request.email}</TableCell>
                    <TableCell sx={{ color: 'white' }}>{request.company || 'Individual'}</TableCell>
                    <TableCell sx={{ color: 'white' }}>
                      {new Date(request.submittedAt).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {request.status === 'pending' && (
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="Approve & Send Invitation">
                            <IconButton
                              onClick={() => handleApproveRequest(request)}
                              sx={{ color: '#4caf50' }}
                            >
                              <CheckCircle />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Reject Request">
                            <IconButton
                              onClick={() => handleRejectRequest(request.id)}
                              sx={{ color: '#f44336' }}
                            >
                              <Cancel />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Approval Dialog */}
      <Dialog
        open={showApprovalDialog}
        onClose={() => setShowApprovalDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            color: 'white'
          }
        }}
      >
        <DialogTitle>
          <Typography variant="h6" sx={{ color: '#00d4ff' }}>
            Approve Access Request & Send Invitation
          </Typography>
        </DialogTitle>
        
        <DialogContent>
          {selectedRequest && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                User Details:
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: '#aaa' }}>Name:</Typography>
                  <Typography variant="body1">{selectedRequest.fullName}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: '#aaa' }}>Email:</Typography>
                  <Typography variant="body1">{selectedRequest.email}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: '#aaa' }}>Phone:</Typography>
                  <Typography variant="body1">{selectedRequest.phone}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: '#aaa' }}>Company:</Typography>
                  <Typography variant="body1">{selectedRequest.company || 'Individual'}</Typography>
                </Grid>
              </Grid>

              <Typography variant="h6" sx={{ mb: 2 }}>
                Invitation Settings:
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel sx={{ color: '#aaa' }}>User Tier</InputLabel>
                    <Select
                      value={invitationForm.role}
                      onChange={(e) => setInvitationForm(prev => ({ ...prev, role: e.target.value }))}
                      sx={{ color: 'white' }}
                    >
                      <MenuItem value="demo">Demo (Trial Access)</MenuItem>
                      <MenuItem value="premium">Premium (Full Access)</MenuItem>
                      <MenuItem value="admin">Admin (Full Control)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Starting Capital ($)"
                    type="number"
                    value={invitationForm.allocated_capital}
                    onChange={(e) => setInvitationForm(prev => ({ 
                      ...prev, 
                      allocated_capital: parseFloat(e.target.value) || 1000 
                    }))}
                    sx={{
                      '& .MuiOutlinedInput-root': { color: 'white' },
                      '& .MuiInputLabel-root': { color: '#aaa' }
                    }}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setShowApprovalDialog(false)} sx={{ color: '#aaa' }}>
            Cancel
          </Button>
          <Button
            onClick={handleSendInvitation}
            variant="contained"
            disabled={isLoading}
            sx={{
              background: 'linear-gradient(45deg, #4caf50, #388e3c)'
            }}
          >
            {isLoading ? 'Sending...' : 'Approve & Send Invitation'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AccessRequestManagement;
