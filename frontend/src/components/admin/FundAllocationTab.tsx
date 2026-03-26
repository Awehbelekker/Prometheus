import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Alert,
  LinearProgress,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import {
  AccountBalanceWallet,
  AttachMoney,
  Check,
  Close,
  Edit,
  History,
  Warning,
  Info,
  Schedule,
  ExpandMore,
  RequestQuote,
  Approval,
  PendingActions,
  TrendingUp,
  TrendingDown,
  AccountBalance,
  MonetizationOn,
  Payment,
  Receipt,
  Analytics
} from '@mui/icons-material';

interface AllocationRequest {
  request_id: string;
  user_id: string;
  username: string;
  requested_amount: number;
  current_allocation: number;
  max_allocation: number;
  justification: string;
  requested_at: string;
  status: string;
  priority: string;
  risk_assessment: string;
}

interface AllocationHistory {
  allocation_id: string;
  user_id: string;
  username: string;
  amount: number;
  allocation_type: string;
  allocated_by: string;
  allocation_date: string;
  notes: string;
  is_active: boolean;
}

interface User {
  user_id: string;
  username: string;
  email: string;
  current_allocation: number;
  max_allocation: number;
  live_trading_approved: boolean;
}

interface FundAllocationTabProps {
  allocationRequests: AllocationRequest[];
  allocationHistory: AllocationHistory[];
  users: User[];
  onApproveRequest: (request: AllocationRequest) => void;
  onRejectRequest: (request: AllocationRequest, reason: string) => void;
  onAllocateFunds: (user: User) => void;
  loading: boolean;
  formatCurrency: (amount: number) => string;
  formatDate: (date: string) => string;
  showAlert: (type: 'success' | 'error' | 'info' | 'warning', message: string) => void;
}

const FundAllocationTab: React.FC<FundAllocationTabProps> = ({
  allocationRequests,
  allocationHistory,
  users,
  onApproveRequest,
  onRejectRequest,
  onAllocateFunds,
  loading,
  formatCurrency,
  formatDate,
  showAlert
}) => {
  const [selectedRequest, setSelectedRequest] = useState<AllocationRequest | null>(null);
  const [rejectDialog, setRejectDialog] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [allocationDialog, setAllocationDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [allocationAmount, setAllocationAmount] = useState('');
  const [allocationReason, setAllocationReason] = useState('');
  const [expandedAccordion, setExpandedAccordion] = useState<string | false>('requests');
  const [historyFilter, setHistoryFilter] = useState('all');

  const getPendingRequests = () => {
    return allocationRequests.filter(req => req.status === 'pending');
  };

  const getProcessedRequests = () => {
    return allocationRequests.filter(req => req.status !== 'pending');
  };

  const getFilteredHistory = () => {
    let filtered = allocationHistory;
    
    if (historyFilter !== 'all') {
      filtered = filtered.filter(item => {
        switch (historyFilter) {
          case 'allocations': return item.allocation_type === 'additional' || item.allocation_type === 'initial';
          case 'withdrawals': return item.allocation_type === 'withdrawal';
          case 'recent': return new Date(item.allocation_date) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
          default: return true;
        }
      });
    }
    
    return filtered.sort((a, b) => new Date(b.allocation_date).getTime() - new Date(a.allocation_date).getTime());
  };

  const getTotalAllocated = () => {
    return users.reduce((total, user) => total + user.current_allocation, 0);
  };

  const getTotalCapacity = () => {
    return users.reduce((total, user) => total + user.max_allocation, 0);
  };

  const getUtilizationRate = () => {
    const total = getTotalCapacity();
    return total > 0 ? (getTotalAllocated() / total) * 100 : 0;
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return '#f44336';
      case 'medium': return '#ff9800';
      case 'low': return '#4caf50';
      default: return '#757575';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'high': return '#f44336';
      case 'medium': return '#ff9800';
      case 'low': return '#4caf50';
      default: return '#757575';
    }
  };

  const handleApproveRequest = (request: AllocationRequest) => {
    onApproveRequest(request);
  };

  const handleRejectRequest = () => {
    if (!selectedRequest || !rejectReason.trim()) {
      showAlert('warning', 'Please provide a reason for rejection');
      return;
    }
    
    onRejectRequest(selectedRequest, rejectReason);
    setRejectDialog(false);
    setSelectedRequest(null);
    setRejectReason('');
  };

  const handleDirectAllocation = () => {
    if (!selectedUser || !allocationAmount || !allocationReason.trim()) {
      showAlert('warning', 'Please fill in all required fields');
      return;
    }
    
    // Create a mock request for direct allocation
    const directRequest: AllocationRequest = {
      request_id: 'direct_' + Date.now(),
      user_id: selectedUser.user_id,
      username: selectedUser.username,
      requested_amount: parseFloat(allocationAmount),
      current_allocation: selectedUser.current_allocation,
      max_allocation: selectedUser.max_allocation,
      justification: allocationReason,
      requested_at: new Date().toISOString(),
      status: 'approved',
      priority: 'high',
      risk_assessment: 'admin_override'
    };
    
    onApproveRequest(directRequest);
    setAllocationDialog(false);
    setSelectedUser(null);
    setAllocationAmount('');
    setAllocationReason('');
  };

  return (
    <Box>
      {/* Header with Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)', 
            border: '1px solid rgba(76, 175, 80, 0.3)'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" sx={{ color: '#4caf50', mb: 1 }}>
                    Total Allocated
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                    {formatCurrency(getTotalAllocated())}
                  </Typography>
                </Box>
                <AccountBalance sx={{ color: '#4caf50', fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%)', 
            border: '1px solid rgba(33, 150, 243, 0.3)'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" sx={{ color: '#2196f3', mb: 1 }}>
                    Total Capacity
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                    {formatCurrency(getTotalCapacity())}
                  </Typography>
                </Box>
                <MonetizationOn sx={{ color: '#2196f3', fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)', 
            border: '1px solid rgba(255, 152, 0, 0.3)'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" sx={{ color: '#ff9800', mb: 1 }}>
                    Utilization Rate
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                    {getUtilizationRate().toFixed(1)}%
                  </Typography>
                </Box>
                <Analytics sx={{ color: '#ff9800', fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(233, 30, 99, 0.1) 0%, rgba(233, 30, 99, 0.05) 100%)', 
            border: '1px solid rgba(233, 30, 99, 0.3)'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" sx={{ color: '#e91e63', mb: 1 }}>
                    Pending Requests
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: 'white' }}>
                    {getPendingRequests().length}
                  </Typography>
                </Box>
                <PendingActions sx={{ color: '#e91e63', fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
          Fund Allocation Management
        </Typography>
        
        <Button
          variant="contained"
          startIcon={<AttachMoney />}
          onClick={() => setAllocationDialog(true)}
          sx={{ bgcolor: '#00d4ff', '&:hover': { bgcolor: '#0099cc' } }}
        >
          Direct Allocation
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Allocation Requests */}
      <Accordion 
        expanded={expandedAccordion === 'requests'} 
        onChange={(_, isExpanded) => setExpandedAccordion(isExpanded ? 'requests' : false)}
        sx={{ 
          backgroundColor: 'rgba(26, 26, 46, 0.8)', 
          border: '1px solid rgba(255, 152, 0, 0.3)',
          mb: 2,
          '&:before': { display: 'none' }
        }}
      >
        <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#ff9800' }} />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <RequestQuote sx={{ color: '#ff9800' }} />
            <Typography variant="h6" sx={{ color: '#ff9800' }}>
              Pending Allocation Requests ({getPendingRequests().length})
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: '#aaa' }}>User</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Requested Amount</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Current/Max</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Priority</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Risk</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Justification</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Requested</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {getPendingRequests().map((request) => (
                  <TableRow key={request.request_id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: '#00d4ff' }}>
                          {request.username.charAt(0).toUpperCase()}
                        </Avatar>
                        <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                          {request.username}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="h6" sx={{ color: '#4caf50', fontWeight: 600 }}>
                        {formatCurrency(request.requested_amount)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" sx={{ color: 'white' }}>
                          {formatCurrency(request.current_allocation)}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#aaa' }}>
                          of {formatCurrency(request.max_allocation)} max
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={request.priority}
                        size="small"
                        sx={{
                          backgroundColor: `${getPriorityColor(request.priority)}20`,
                          color: getPriorityColor(request.priority),
                          border: `1px solid ${getPriorityColor(request.priority)}40`
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={request.risk_assessment}
                        size="small"
                        sx={{
                          backgroundColor: `${getRiskColor(request.risk_assessment)}20`,
                          color: getRiskColor(request.risk_assessment),
                          border: `1px solid ${getRiskColor(request.risk_assessment)}40`
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title={request.justification}>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: '#aaa',
                            maxWidth: 200,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {request.justification}
                        </Typography>
                      </Tooltip>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" sx={{ color: '#aaa' }}>
                        {formatDate(request.requested_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Approve Request">
                          <IconButton
                            size="small"
                            onClick={() => handleApproveRequest(request)}
                            sx={{ color: '#4caf50' }}
                          >
                            <Check />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Reject Request">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedRequest(request);
                              setRejectDialog(true);
                            }}
                            sx={{ color: '#f44336' }}
                          >
                            <Close />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>

      {/* Allocation History */}
      <Accordion 
        expanded={expandedAccordion === 'history'} 
        onChange={(_, isExpanded) => setExpandedAccordion(isExpanded ? 'history' : false)}
        sx={{ 
          backgroundColor: 'rgba(26, 26, 46, 0.8)', 
          border: '1px solid rgba(33, 150, 243, 0.3)',
          '&:before': { display: 'none' }
        }}
      >
        <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#2196f3' }} />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
            <History sx={{ color: '#2196f3' }} />
            <Typography variant="h6" sx={{ color: '#2196f3' }}>
              Allocation History ({allocationHistory.length})
            </Typography>
            
            <Box sx={{ ml: 'auto', mr: 2 }}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <Select
                  value={historyFilter}
                  onChange={(e) => setHistoryFilter(e.target.value)}
                  sx={{
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(33, 150, 243, 0.5)' },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#2196f3' }
                  }}
                >
                  <MenuItem value="all">All History</MenuItem>
                  <MenuItem value="allocations">Allocations</MenuItem>
                  <MenuItem value="withdrawals">Withdrawals</MenuItem>
                  <MenuItem value="recent">Recent (7 days)</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Timeline>
            {getFilteredHistory().slice(0, 20).map((item, index) => (
              <TimelineItem key={item.allocation_id}>
                <TimelineOppositeContent sx={{ color: '#aaa', fontSize: '0.8rem' }}>
                  {formatDate(item.allocation_date)}
                </TimelineOppositeContent>
                <TimelineSeparator>
                  <TimelineDot 
                    sx={{ 
                      bgcolor: item.allocation_type === 'withdrawal' ? '#f44336' : '#4caf50',
                      border: 'none'
                    }}
                  >
                    {item.allocation_type === 'withdrawal' ? <TrendingDown /> : <TrendingUp />}
                  </TimelineDot>
                  {index < getFilteredHistory().slice(0, 20).length - 1 && <TimelineConnector />}
                </TimelineSeparator>
                <TimelineContent>
                  <Paper sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                    <Typography variant="h6" sx={{ color: 'white' }}>
                      {item.allocation_type === 'withdrawal' ? 'Withdrawal' : 'Allocation'}: {formatCurrency(Math.abs(item.amount))}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#aaa' }}>
                      User: {item.username} | By: {item.allocated_by}
                    </Typography>
                    {item.notes && (
                      <Typography variant="caption" sx={{ color: '#666' }}>
                        {item.notes}
                      </Typography>
                    )}
                  </Paper>
                </TimelineContent>
              </TimelineItem>
            ))}
          </Timeline>
        </AccordionDetails>
      </Accordion>

      {/* Reject Request Dialog */}
      <Dialog open={rejectDialog} onClose={() => setRejectDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          Reject Allocation Request
        </DialogTitle>
        <DialogContent sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Rejecting request from {selectedRequest?.username} for {formatCurrency(selectedRequest?.requested_amount || 0)}
          </Typography>
          <TextField
            fullWidth
            label="Rejection Reason"
            multiline
            rows={4}
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="Please provide a detailed reason for rejection..."
            InputProps={{ style: { color: 'white' } }}
            InputLabelProps={{ style: { color: '#aaa' } }}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions sx={{ bgcolor: '#1a1a2e' }}>
          <Button onClick={() => setRejectDialog(false)}>Cancel</Button>
          <Button onClick={handleRejectRequest} variant="contained" color="error">
            Reject Request
          </Button>
        </DialogActions>
      </Dialog>

      {/* Direct Allocation Dialog */}
      <Dialog open={allocationDialog} onClose={() => setAllocationDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          Direct Fund Allocation
        </DialogTitle>
        <DialogContent sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel sx={{ color: '#aaa' }}>Select User</InputLabel>
                <Select
                  value={selectedUser?.user_id || ''}
                  onChange={(e) => {
                    const user = users.find(u => u.user_id === e.target.value);
                    setSelectedUser(user || null);
                  }}
                  sx={{
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(0, 212, 255, 0.5)' },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' }
                  }}
                >
                  {users.filter(u => u.live_trading_approved).map((user) => (
                    <MenuItem key={user.user_id} value={user.user_id}>
                      {user.username} - {formatCurrency(user.current_allocation)}/{formatCurrency(user.max_allocation)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Allocation Amount"
                type="number"
                value={allocationAmount}
                onChange={(e) => setAllocationAmount(e.target.value)}
                InputProps={{ style: { color: 'white' } }}
                InputLabelProps={{ style: { color: '#aaa' } }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Reason for Allocation"
                multiline
                rows={3}
                value={allocationReason}
                onChange={(e) => setAllocationReason(e.target.value)}
                InputProps={{ style: { color: 'white' } }}
                InputLabelProps={{ style: { color: '#aaa' } }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ bgcolor: '#1a1a2e' }}>
          <Button onClick={() => setAllocationDialog(false)}>Cancel</Button>
          <Button onClick={handleDirectAllocation} variant="contained">
            Allocate Funds
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FundAllocationTab;
